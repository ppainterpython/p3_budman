# ---------------------------------------------------------------------------- +
#region p3_budget_categorization.py module
""" Financial Budget Workflow: "categorization" of transaction workbooks.

    Workflow: categorization
    Input Folder: Financial Institution (FI) Incoming Folder (IF)
    Output Folder: Financial Institution (FI) Categorized Folder (CF)
    FI transaction workbooks are typically excel files. 

    Workflow Pattern: Apply a workflow_process (function) to each item in the 
    input folder, placing items in the output folder as appropriate to the 
    configured function. Each WorkFLow instance in the config applies one 
    function to the input with resulting output.

    TODO: Consider xlwings package for Excel integration.
"""
#endregion p3_execl_budget.p3_banking_transactions budget_transactions.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import re, pathlib as Path, logging, time, hashlib, datetime
from dataclasses import dataclass

# third-party modules and packages
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell

# local modules and packages
from budman_namespace.design_language_namespace import *
from .budget_category_mapping import (
    map_category, category_map_count, check_register_map)
from budget_domain_model import (BudgetDomainModel)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)

# Note: Python lists are 0-based. With openpyxl, data is often returned in a
# list. In excel, worksheet columns are 1-based. So, we need to adjust the indices.
# A list of cells from a worksheet row is 0-based, with cell(0) being the value
# from column 1, or column 'A'.

# Symbols for BOA .csv files.
BOA_ORIGINAL_DESCRIPTION_COL_NAME = "Original Description"
BOA_DATE_COL_NAME = "Date"
BOA_CURRENCY_COL_NAME = "Currency"
BOA_AMOUNT_COL_NAME = "Amount"
BOA_ACCOUNT_NAME_COL_NAME = "Account Name"

# BOA csv files originals contain these columns, beginning with "Status".
BOA_WB_COLUMNS = [
    "Status", 
    BOA_DATE_COL_NAME, 
    BOA_ORIGINAL_DESCRIPTION_COL_NAME,
    "Split Type", 
    "Category", 
    BOA_CURRENCY_COL_NAME, 
    BOA_AMOUNT_COL_NAME, 
    "User Description", 
    "Memo", 
    "Classification", 
    BOA_ACCOUNT_NAME_COL_NAME,
    "Simple Description"
    ]

# BudMan adds additional columns prior to processing transactions. These
# columns are filled by BudMan workflows, such as categorization.
BUDGET_CATEGORY_COL_NAME = "Budget Category"  
ACCOUNT_CODE_COL_NAME = "Account Code" 
LEVEL_1_COL_NAME = "Level1" 
LEVEL_2_COL_NAME = "Level2" 
LEVEL_3_COL_NAME = "Level3" 
DEBIT_CREDIT_COL_NAME = "DebitOrCredit"  
YEAR_MONTH_COL_NAME = "YearMonth"  

# BudMan utilizes the following columns from the BOA side:
DATE_COL_NAME = BOA_DATE_COL_NAME 
ORIGINAL_DESCRIPTION_COL_NAME = BOA_ORIGINAL_DESCRIPTION_COL_NAME
CURRENCY_COL_NAME = BOA_CURRENCY_COL_NAME
AMOUNT_COL_NAME = BOA_AMOUNT_COL_NAME 
ACCOUNT_NAME_COL_NAME = BOA_ACCOUNT_NAME_COL_NAME  

# BudMan processes the original .csv file from BOA to product an excel
# workbook will then have the following columns:
BUDMAN_WB_COLUMNS = [
    "Status", 
    DATE_COL_NAME, 
    ORIGINAL_DESCRIPTION_COL_NAME,
    "Split Type", 
    "Category", 
    CURRENCY_COL_NAME, 
    AMOUNT_COL_NAME, 
    "User Description", 
    "Memo", 
    "Classification", 
    ACCOUNT_NAME_COL_NAME,
    "Simple Description",
    BUDGET_CATEGORY_COL_NAME,
    ACCOUNT_CODE_COL_NAME,
    LEVEL_1_COL_NAME,
    LEVEL_2_COL_NAME,
    LEVEL_3_COL_NAME,
    DEBIT_CREDIT_COL_NAME,
    YEAR_MONTH_COL_NAME
    ]

# Column indices for a list of cells from a row in the BOA workbook.
DATE_COL_INDEX = 1
ORIGINAL_DESCRIPTION_COL_INDEX = 2  
CURRENCY_COL_INDEX = 4  
AMOUNT_COL_INDEX = 6  
ACCOUNT_NAME_COL_INDEX = 10  
BUDGET_CATEGORY_COL_INDEX = 12  

BOA_WB_COL_DIMENSIONS = {
    DATE_COL_NAME: 12,
    ORIGINAL_DESCRIPTION_COL_NAME: 95,
    CURRENCY_COL_NAME: 9,
    AMOUNT_COL_NAME: 14,
    ACCOUNT_NAME_COL_NAME: 68,
    BUDGET_CATEGORY_COL_NAME: 40,
    LEVEL_1_COL_NAME: 20,
    LEVEL_2_COL_NAME: 20,
    LEVEL_3_COL_NAME: 20,
    DEBIT_CREDIT_COL_NAME: 10,
    YEAR_MONTH_COL_NAME: 20
}
BUDMAN_SHEET_NAME = "TransactionData"

BUDMAN_REQUIRED_COLUMNS = [
    DATE_COL_NAME, 
    ORIGINAL_DESCRIPTION_COL_NAME, 
    CURRENCY_COL_NAME,
    AMOUNT_COL_NAME, 
    ACCOUNT_CODE_COL_NAME, 
    BUDGET_CATEGORY_COL_NAME,
    LEVEL_1_COL_NAME, 
    LEVEL_2_COL_NAME, 
    LEVEL_3_COL_NAME,
    DEBIT_CREDIT_COL_NAME,
    YEAR_MONTH_COL_NAME
]

#endregion Globals and Constants
#region dataclasses
TRANS_PARAMETERS = ["tid", "date", "description", "currency",
                    "account_code", "amount", "category",
                    "level1", "level2", "level3", 
                    "debit_credit", "year_month"]
@dataclass
class TransactionData:
    """Data class to hold transaction data."""
    tid: str = None   # Transaction ID.
    date: datetime.date = None
    description: str = None
    currency: str = None
    account_code: str = None
    amount: float = 0.0
    category: str = None
    level1: str = None
    level2: str = None
    level3: str = None
    debit_credit: str = None  # 'D' for debit, 'C' for credit.
    year_month: str = None  # Formant 'YYYY-MM-mmm' e.g., 2025-01-Jan

    def data_str(self) -> str:
        """Return a string representation of the transaction data."""
        ret =  f"{self.tid:12}|{self.date.strftime("%m/%d/%Y")}|"
        ret += f"{self.year_month:11}|{self.account_code:26}|" 
        ret += f"{self.amount:>+12.2f}|{self.debit_credit:1}|" 
        ret += f"({len(self.description):03}){self.description:102}|->" 
        ret += f"|({len(self.category):03})|{self.category:40}|"
        return ret
    
#endregion dataclasses
# ---------------------------------------------------------------------------- +
#region generate_hash_key(text:str) -> str
def generate_hash_key(text: str, length:int=12) -> str:
    """Generate a hash key for the given text.
    
    The hash key is generated by removing all non-alphanumeric characters 
    from the text, converting it to lowercase, and then hashing it using 
    SHA-256. The resulting hash is then converted to a hexadecimal string.

    Args:
        text (str): The input text to generate a hash key for.

    Returns:
        str: The generated hash key.
    """
    try:
        if not isinstance(text, str):
            raise TypeError(f"Expected 'text' arg to be a str, got {type(text)}")
        # Remove non-alphanumeric characters and convert to lowercase.
        # cleaned_text = re.sub(r'\W+', '', text).lower()
        # Generate the SHA-256 hash of the cleaned text.
        hash_object = hashlib.sha256(text.encode())
        # Convert the hash to a hexadecimal string.
        return hash_object.hexdigest()[:length]  #.[:HASH_KEY_LENGTH]
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion generate_hash_key(text:str) -> str
# ---------------------------------------------------------------------------- +
#region check_sheet_columns() function
def check_sheet_columns(sheet: Worksheet, add_columns: bool = True) -> bool:
    """Check that the sheet is ready to process transactions.
    
    BudMan uses these columns to process transactions in a sheet:
    DATE_COL_NAME - date of the transaction.
    ORIGINAL_DESCRIPTION_COL_NAME - the description of the transaction.
    CURRENCY_COL_NAME - the unit of currency, USD, EUR, etc.
    AMOUNT_COL_NAME - the amount of the transaction, as a float.
    ACCOUNT_CODE_COL_NAME - the short-name of the account for the transaction. 
    BUDGET_CATEGORY_COL_NAME - the budget category for the transaction.
    LEVEL_1_COL_NAME - the first level of the budget category.
    LEVEL_2_COL_NAME - the second level of the budget category.
    LEVEL_3_COL_NAME - the third level of the budget category.
    DEBIT_CREDIT_COL_NAME - 'D' for debit, 'C' for credit.
    YEAR_MONTH_COL_NAME - trans date in format 'YYYY-MM-mmm', e.g. '2025-01-Jan'.

    Args:
        sheet (openpyxl.worksheet): The worksheet to check.
        add_columns (bool): Whether to add missing columns or not.

    Returns:
        bool: True if all required columns are present, False otherwise.
    """
    try:
        logger.info("Check worksheet for required columns.")
        # Index the header row 1, it has the column names
        col_names = [cell.value for cell in sheet[1]]
        logger.debug(f"Column names in sheet('{sheet.title}'): {col_names}")
        
        # Check if all required columns are present
        missing_columns = [col for col in BUDMAN_REQUIRED_COLUMNS if col not in col_names]
        
        if not missing_columns:
            logger.info(f"Required columns are present:('{sheet.title}')")
            return True
        
        if add_columns:
            # Add missing columns to the sheet to the right.
            for col_name in missing_columns:
                i = sheet.max_column + 1 # insert before column after last column
                sheet.insert_cols(i)
                sheet.cell(row=1, column=i).value = col_name
                # Set column width based on predefined dimensions
                width = BOA_WB_COL_DIMENSIONS.get(col_name, 20)
                sheet.column_dimensions[sheet.cell(row=1, column=i).column_letter].width = width
                logger.debug(f"Column '{col_name}' added at index = {i}, "
                            f"column_letter = '{sheet.cell(row =1, column=i).column_letter}'")
            logger.info(f"Added missing columns: {', '.join(missing_columns)}")
        else:
            logger.error(f"Sheet('{sheet.title}') missing required columns: {', '.join(missing_columns)}")
            return False
        logger.info("Completed checks for required columns.")
        return True
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion check_sheet_columns() function
# ---------------------------------------------------------------------------- +
#region check_sheet_schema() function
def check_sheet_schema(wb: Workbook, correct: bool = False) -> bool:
    """Check that the sheet is ready to process transactions.
    
    Steps to check the active sheet of an excel workbook for BudMan processing:
    1. SHould be just 1 worksheet, the active worksheet.
    2. Title must be 'TransactionData'. BOA_SHEET_NAME
    3. Column names must match spelling an order from BOA_WB_COLUMNS.
    Args:
        wb (openpyxl.workbook): The workbook to check.
        correct (bool): Whether to correct the sheet schema or not.

    Returns:
        bool: True if all required columns are present, False otherwise.
    """
    try:
        logger.info("Check worksheet for schema structure.")
        # Check the active worksheet.
        ws = wb.active  # Get the active worksheet.
        good_schema = True  # Assume the schema is good.
        rule1 = rule2 = rule3 = good_schema
        # 1. Check if there is only one worksheet.
        sheet_names = wb.sheetnames 
        sheet_count = len(sheet_names)
        budman_sheet_index = -1
        if sheet_count > 1:
            logger.error(f"Workbook has {sheet_count} sheets, expected 1. "
                         f"Sheet names: {', '.join(sheet_names)}")
            good_schema = rule1 = False
        # 2. Check if the sheet title is BUDMAN_SHEET_NAME.
        if BUDMAN_SHEET_NAME not in sheet_names:
            logger.error(f"Workbook does not have a sheet named '{BUDMAN_SHEET_NAME}'. "
                         f"Sheet names: {', '.join(sheet_names)}")
            good_schema = rule2 = False
        else:
            # Get the index of the BudMan sheet.
            budman_sheet_index = sheet_names.index(BUDMAN_SHEET_NAME)
            ws = wb[sheet_names[budman_sheet_index]] 
        # 3. Check the column names are correct spelling and order.
        col_names = [cell.value for cell in ws[1]]
        # Check if all required columns are present
        missing_columns = [col for col in BUDMAN_REQUIRED_COLUMNS if col not in col_names]
        if len(missing_columns) > 0:
            logger.error(f"Missing required columns: {', '.join(missing_columns)}")
            good_schema = rule3 = False
        # If just one sheet with wrong title, rename it to BUDMAN_SHEET_NAME.
        if rule1 and rule3 and not rule2:
            logger.error(f"BudMan sheet '{BUDMAN_SHEET_NAME}' not found in workbook.")
            previous_title = ws.title  # Save the previous title.
            ws.title = BUDMAN_SHEET_NAME  # Rename the active sheet.
            logger.info(f"Renamed active sheet from '{previous_title}' to '{BUDMAN_SHEET_NAME}'.")
            good_schema = True
        # If more than one sheet, active sheet with wrong title, but is has 
        # the correct columns, rename the active sheet to BUDMAN_SHEET_NAME.
        if not rule1 and rule3 and not rule2:
            logger.error(f"Active sheet '{BUDMAN_SHEET_NAME}' has wrong name "
                         f"but has the correct columns. " 
                         f"Renaming it to '{BUDMAN_SHEET_NAME}'.")
            previous_title = ws.title  # Save the previous title.
            ws.title = BUDMAN_SHEET_NAME  # Rename the active sheet.
            logger.info(f"Renamed active sheet from '{previous_title}' to '{BUDMAN_SHEET_NAME}'.")
            good_schema = True
        return good_schema
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion check_sheet_schema() function
# ---------------------------------------------------------------------------- +
#region check_budget_category() function
def check_budget_category(sheet:Worksheet,add_columns : bool = True) -> bool:
    """Check that the sheet is ready to process budget category.
    
    BudMan uses 4 columns to categorize transactions in a sheet:
    1. 'Budget Category' - the budget category for the transaction. It is a str
        with up to 3 dotted levels of budget categories, e.g. "Housing.Improvements.Flooring".
    2. 'Level1' - the first level of the budget category, e.g. "Housing".
    3. 'Level2' - the second level of the budget category, e.g. "Improvements".
    4. 'Level3' - the third level of the budget category, e.g. "Flooring".
    A column 'Budget Category' is added to the sheet if it does not exist.
    3 columns are added to the sheet if they do not exist: 'Level1', 'Level2', 
    'Level3', adjacent to the 'Budget Category' column.

    Args:
        sheet (openpyxl.worksheet): The worksheet to map.
    """
    try:
        logger.info("Check worksheet for budget category columns.")
        # Index row 1 as the header row, it has the column names
        col_names = {}
        for cnum, cell in enumerate(sheet[1], start=1):
            col_names[cell.value] = cnum
        logger.debug(f"Column names in sheet('{sheet.title}'): {list(col_names.keys())}")
        # Is BUDGET_CATEGORY_COL_NAME in the sheet?
        if BUDGET_CATEGORY_COL_NAME in col_names:
            logger.info(f"Column '{BUDGET_CATEGORY_COL_NAME}' already exists in sheet.")
        elif add_columns:
            # Add the BUDGET_CATEGORY_COL_NAME, LEVEL_1_COL, LEVEL_2_COL, and 
            # LEVEL_3_COL columns to the sheet.
            i = sheet.max_column + 1
            sheet.insert_cols(i)
            sheet.cell(row=1, column=i).value = BUDGET_CATEGORY_COL_NAME
            col_names[BUDGET_CATEGORY_COL_NAME] = i  # Update the col_names dict.
            # Set the column width to 20.
            sheet.column_dimensions[sheet.cell(row=1, column=i).column_letter].width = 20
            logger.info(f"Adding column '{BUDGET_CATEGORY_COL_NAME}' at index = {i}, "
                        f"column_letter = '{sheet.cell(row=1, column=i).column_letter}'")
            logger.info(f"Completed checks for budget category.")
        return True
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise    
#endregion check_budget_category() function
# ---------------------------------------------------------------------------- +
#region WORKSHEET_data(ws:Worksheet) -> List[TransactionData]
def WORKSHEET_data(ws:Worksheet, just_values:bool=False) -> list[TransactionData]:
    """Extract transaction data from a worksheet.

    Args:
        ws (Worksheet): The worksheet to extract data from.

    Returns:
        list[TransactionData]: A list of TransactionData objects.
    """
    try:
        if not isinstance(ws, Worksheet):
            raise TypeError(f"Expected 'ws' arg to be a Worksheet, got {type(ws)}")
        transactions = []
        headers = [cell.value for cell in ws[1]]  # Get the header row values.
        for row in ws.iter_rows(min_row=2, values_only=just_values):
            transaction = WORKSHEET_row_data(row,headers)  # Extract transaction data from the row.
            transactions.append(transaction)
        return transactions
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKSHEET_data(ws:Worksheet) -> List[TransactionData]
# ---------------------------------------------------------------------------- +
#region WORKSHEET_row_data(row:list) -> TransactionData
def WORKSHEET_row_data(row:tuple,hdr:list=BUDMAN_WB_COLUMNS) -> TransactionData:
    """Extract transaction data from a worksheet row.

    Args:
        row (list): List of either cells or just the cell values.
        hdr (list): A list of header column names used to index values from the row.

    Returns:
        list[TransactionData]: A list of TransactionData objects.
    """
    try:
        # Validation
        p3u.is_not_obj_of_type("row", row, tuple, raise_error=True)
        p3u.is_not_obj_of_type("hdr", hdr, list, raise_error=True)
        if len(row) == 0 or len(hdr) == 0 or len(row) != len(hdr):
            raise ValueError("Row and Hdr must be equal, non-zero length.")
        # Check if all required columns are present in the hdr.
        missing_columns = [col for col in BUDMAN_REQUIRED_COLUMNS if col not in hdr]
        if missing_columns:
            raise ValueError(f"Hdr is missing required columns: {missing_columns}")
        # First, determine if row contains Cells or value-only cell.value's and
        # extract the values accordingly.
        if isinstance(row[0], Cell):
            # This is a Tuple of Cell objects.
            row_values = [cell.value for cell in row]
        else:
            row_values = row 
        # Second, verify the hdr contains the required columns.
        row_dict = dict(zip(hdr, row_values))  # Create a dict from the header and row values.

        # Extract some of the values as strings to generate a hash from
        t_date_str = p3u.iso_date_only_string(row_dict[DATE_COL_NAME])
        t_desc = row_dict[ORIGINAL_DESCRIPTION_COL_NAME]
        t_currency = row_dict[CURRENCY_COL_NAME]
        t_amt_str = str(row_dict[AMOUNT_COL_NAME])
        t_acct_str = row_dict[ACCOUNT_NAME_COL_NAME]
        t_all_str = t_date_str + t_desc + t_currency + t_amt_str + t_acct_str
        t_id = generate_hash_key(t_all_str) 

        transaction = TransactionData(
            tid=t_id,
            date=row_dict[DATE_COL_NAME],
            description=row_dict[ORIGINAL_DESCRIPTION_COL_NAME],
            currency=row_dict[CURRENCY_COL_NAME],
            amount=row_dict[AMOUNT_COL_NAME],
            account_code=row_dict[ACCOUNT_CODE_COL_NAME],
            category=row_dict[BUDGET_CATEGORY_COL_NAME],
            level1=row_dict[LEVEL_1_COL_NAME],
            level2=row_dict[LEVEL_2_COL_NAME],
            level3=row_dict[LEVEL_3_COL_NAME],
            debit_credit=row_dict[DEBIT_CREDIT_COL_NAME],
            year_month=row_dict[YEAR_MONTH_COL_NAME]
        )
        return transaction
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKSHEET_row_data(row:list) -> TransactionData
# ---------------------------------------------------------------------------- +
#region split_budget_category() -> tuple function
def split_budget_category(budget_category: str) -> tuple[str, str, str]:
    """Split a budget category string into three levels.
    
    The budget category is expected to be in the format "Level1.Level2.Level3".
    If the budget category does not have all three levels, the missing levels 
    will be set to an empty string.

    Args:
        budget_category (str): The budget category string to split.

    Returns:
        tuple[str, str, str]: A tuple containing Level1, Level2, and Level3.
    """
    try:
        if not isinstance(budget_category, str):
            raise TypeError(f"Expected 'budget_category' to be a str, got {type(budget_category)}")
        l1 = l2 = l3 = ""
        c = budget_category.count('.')
        if c >= 2:
            # Split the budget category by '.' and ensure we have 3 parts.
            l1, l2, l3 = budget_category.split('.',3)
        elif c == 1:
            # Split the budget category by '.' and ensure we have 2 parts.
            l1, l2 = budget_category.split('.',2)
        else:
            # If no '.' is present, treat the whole string as Level1.
            l1 = budget_category
        return l1, l2, l3
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion split_budget_category() function
# ---------------------------------------------------------------------------- +
#region col_i() function
def col_i(col_name:str, hdr:list) -> int:
    """Get the 0-based index of a column name in a header row.
    
    Args:
        col_name (str): The name of the column to find.
        hdr (list): The header list of column names from row(1) to search in.

    Returns:
        int: The index of the column name in the header row, or -1 if not found.
    """
    try:
        if not isinstance(col_name, str):
            raise TypeError(f"Expected 'col_name' to be a str, got {type(col_name)}")
        if not isinstance(hdr, list):
            raise TypeError(f"Expected 'hdr' to be a list, got {type(hdr)}")
        return hdr.index(col_name) if col_name in hdr else -1
    except ValueError:
        return -1
#endregion col_i() function
# ---------------------------------------------------------------------------- +
#region year_month_str() function
def year_month_str(date:object) -> str:
    """Convert a date object to a year-month string in the format 'YYYY-MM-mmm'.
    
    Args:
        date (object): A date object or a string that can be converted to a date.

    Returns:
        str: The year-month string in the format 'YYYY-MM-mmm'.
    """
    try:
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        elif not isinstance(date, datetime.date):
            raise TypeError(f"Expected 'date' to be a date object or a str, got {type(date)}")
        return date.strftime("%Y-%m-%b")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion year_month_str() function
# ---------------------------------------------------------------------------- +
#region map_budget_category() function
def map_budget_category(sheet:Worksheet,src,dst) -> None:
    """Map a src column to budget category putting result in dst column.
    
    The sheet has banking transaction data in rows and columns. 
    Column 'src' has the text presumed to be about the transaction.
    Column 'dst' will be assigned a mapped budget category. Append
    column 'Budget Category' if it is not already in the sheet.
    TODO: pass in a mapper function to map the src text to a budget category.

    Args:
        sheet (openpyxl.worksheet): The worksheet to map.
        src (str): The source column to map from.
        dst (str): The destination column to map to. 
    """
    try:
        # Validate the input parameters.
        _ = p3u.is_str_or_none("src", src, raise_error=True)
        _ = p3u.is_str_or_none("dst", dst, raise_error=True)
        if not check_sheet_columns(sheet, add_columns=False):
            logger.error(f"Sheet '{sheet.title}' cannot be mapped due to "
                         f"missing required columns.")
            return
        rules_count = category_map_count()
        logger.info(f"Applying '{rules_count}' budget category mappings "
                    f"to {sheet.max_row-1} rows in sheet: '{sheet.title}' ")
        # transactions = WORKSHEET_data(sheet)
        # A row is a tuple of the Cell objects in the row. Tuples are 0-based
        # hdr is a list, also 0-based. So, using the index(name) will 
        # give the cell from a row tuple matching the column name in hdr.
        hdr = [cell.value for cell in sheet[1]] 

        if src in hdr:
            src_col_index = hdr.index(src)
        else:
            logger.error(f"Source column '{src}' not found in header row.")
            return
        if dst in hdr:
            dst_col_index = hdr.index(dst)
        else:
            logger.error(f"Destination column '{dst}' not found in header row.")
            return
        
        # TODO: need to refactor this to do replacements by col_name or something.
        # This is specific to the Budget Category mapping, which now is to be
        # split into 3 levels: Level1, Level2, Level3.

        # These are values to set in the rows.
        date_i = col_i(DATE_COL_NAME,hdr)
        l1_i = col_i(LEVEL_1_COL_NAME,hdr)
        l2_i = col_i(LEVEL_2_COL_NAME,hdr)
        l3_i = col_i(LEVEL_3_COL_NAME,hdr)
        amt_i = col_i(AMOUNT_COL_NAME,hdr)
        dORc_i = col_i(DEBIT_CREDIT_COL_NAME,hdr)
        year_month_i = col_i(YEAR_MONTH_COL_NAME,hdr)
        acct_name_i = col_i(ACCOUNT_NAME_COL_NAME,hdr)
        acct_code_i = col_i(ACCOUNT_CODE_COL_NAME,hdr)
        acct_cell : Cell = sheet.cell(row=1, column=acct_name_i + 1)

        logger.info(f"Mapping '{src}'({src_col_index}) to "
                    f"'{dst}'({dst_col_index})")
        num_rows = sheet.max_row # or set a smaller limit
        other_count = 0
        for row in sheet.iter_rows(min_row=2):
            # row is a 'tuple' of Cell objects, 0-based index
            row_idx = row[0].row  # Get the row index, the row number, 1-based.
            # Do the mapping from src to dst.
            dst_cell = row[dst_col_index]
            src_value = row[src_col_index].value 
            dst_value = map_category(src_value)
            dst_cell.value = dst_value 
            # row[dst_col_index].value = dst_value 
            # Set the additional values for BudMan in the row
            date_val = row[date_i].value
            year_month = year_month_str(date_val) if date_val else None
            row[year_month_i].value = year_month
            l1, l2, l3 = split_budget_category(dst_value)
            row[l1_i].value = l1 if l1_i != -1 else None
            row[l2_i].value = l2 if l2_i != -1 else None
            row[l3_i].value = l3 if l3_i != -1 else None
            row[dORc_i].value = 'C' if row[amt_i].value > 0 else 'D'
            acct_value = row[acct_name_i].value
            t_acct_code = acct_value.split('-')[-1].strip()
            row[acct_code_i].value = t_acct_code if acct_code_i != -1 else None

            transaction = WORKSHEET_row_data(row,hdr) 
            trans_str = transaction.data_str()
            del transaction  # Clean up the transaction object.
            if dst_value == 'Other':
                other_count += 1
                logger.debug(f"{row_idx:04}:{trans_str}" )
        logger.info(f"Completed budget category mapping for '{num_rows}' rows. "
                    f"Other count: '{other_count}'.")
        return None
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise    
#endregion map_budget_category() function
# ---------------------------------------------------------------------------- +
#region apply_check_register() function
def apply_check_register(cr_wb_content:BDM_CHECK_REGISTER, trans_wb_ref:BDM_TRANSACTION_WORKBOOK) -> None:
    """Apply the check transactions to the worksheet.
    
    The sheet has banking transaction data in rows and columns. 
    The check_reg has a collection of checks. Scan and match the checks
    with the content in the worksheet. If found, modify the transactions.

    Args:
        sheet (openpyxl.worksheet): The worksheet to process.
        check_reg (dict): A dictionary of check transactions to apply.
    """
    try:
        # Validate the input parameters.
        p3u.is_not_obj_of_type("cr_wb_content", cr_wb_content, dict, raise_error=True)
        p3u.is_not_obj_of_type("trans_wb_ref",trans_wb_ref, Workbook, raise_error=True)
        # Validate the input parameters.
        cr = cr_wb_content
        sh = trans_wb_ref.active  # Get the active worksheet.
        if not check_sheet_columns(sh, add_columns=False):
            logger.error(f"Sheet '{sh.title}' cannot be mapped due to "
                         f"missing required columns.")
            return
        logger.info(f"Applying checks from check register to sheet: '{sh.title}' ")
        # transactions = WORKSHEET_data(sheet)
        # A row is a tuple of the Cell objects in the row. Tuples are 0-based
        # hdr is a list, also 0-based. So, using the index(name) will 
        # give the cell from a row tuple matching the column name in hdr.
        hdr = [cell.value for cell in sh[1]] 
        budget_cat = hdr.index(BUDGET_CATEGORY_COL_NAME)
        orig_desc = hdr.index(ORIGINAL_DESCRIPTION_COL_NAME)

        # For each check, with the check number and the Budget Category
        # 'Banking.Checks to Categorize', find the row in the worksheet to modify.
        target_cat = 'Banking.Checks to Categorize'
        check_pat = re.compile(r'^.*Check\s*x*(\d{1,6})\b.*$')  

        trans_match = []
        for row in sh.iter_rows(min_row=2):
            # row is a 'tuple' of Cell objects, 0-based index
            budget_cat_cell = row[budget_cat]
            if budget_cat_cell.value and target_cat in budget_cat_cell.value:
                orig_desc_cell = row[orig_desc]
                desc = row[orig_desc].value if orig_desc != -1 else ""
                m = check_pat.match(desc)
                if m:
                    check_key = m.group(1)
                    if check_key in cr:
                        # Modify the transaction with the check number.
                        pay_to = cr[check_key]['Pay-To']
                        new_cat = check_register_map[pay_to] if pay_to in check_register_map else 'Unknown'
                        new_desc = f"{pay_to} Check: {check_key}"
                        row[budget_cat].value = new_cat
                        row[orig_desc].value = new_desc
                        logger.info(f"Modified transaction for check: '{check_key}' "
                                    f"new_desc: '{new_desc}' new_cat: '{new_cat}'")
                logger.info(f"'{sh.title}' Match '{target_cat}' desc={desc}")
        logger.info(f"Found {len(trans_match)} transactions in sheet "
                    f"'{sh.title}' with category '{target_cat}' to modify.")
        return None
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise    
#endregion apply_check_register() function
# ---------------------------------------------------------------------------- +
#region def execute_worklow_categorization(bm : BudgetModel, fi_key: str) -> None:
def execute_worklow_categorization(bm : BudgetDomainModel, fi_key: str, wf_key:str) -> None:
    """Process categorization wf_key for Financial Institution's 
    transaction workbooks.

    Execute the categorization wf_key to examine all fi transaction 
    workbooks presently in the IF (Incoming Folder) for the indicated 
    FI (Financial Institution). Each workbook file is opened and the 
    transactions are categorized and saved to the CF (Categorized Folder) 
    for the indicated FI.

    Args:
        bm (BudgetModel): The BudgetModel instance to use for processing.
        fi_key (str): The key for the financial institution.
    """
    # TODO: add logs directory to the budget folder.
    st = p3u.start_timer()
    wb_name = "BOAChecking2025.xlsx"
    cp = "Budget Model Categorization:"
    loaded_workbooks = {}
    # Execute a workflow for a specific financial institution (fi_key).
    #   The pattern is to apply a function based on wf_key to each item in 
    #   the input folder based on fi_key and wf_key.
    #   Execute steps:
    #     1: Load the input items from storage.
    #     2: Apply the workflow function to each input item.
    #     3: Save the output items to storage. 
    try:
        logger.info(f"{cp} Start: workflow: '{wf_key}' for FI('{fi_key}') ...")
        wb_type = WF_INPUT # input workbooks
        wb_c = bm.bdm_FI_WF_WORKBOOK_DATA_LIST_count(fi_key, wf_key, wb_type)
        # if workbooks_dict is None or len(workbooks_dict) == 0:
        if wb_c is None or wb_c == 0:
            logger.info(f"{cp}    No workbooks for input.")
            return
        logger.info(f"{cp}    {wb_c} workbooks for input.")
        # Now process each input workbook.
        # for wb_name, wb_ap in reversed(workbooks_dict.items()):
        # Step 1: Load the workbooks sequentially.
        for wb_name, wb in bm.bsm_FI_WF_WORKBOOKS_generate(fi_key, wf_key, wb_type):
            logger.info(f"{cp}    Workbook({wb_name})")
                
            # Step 2: Process the workbooks applying the workflow function
            try: 
                logger.info(f"{cp}    Workbook({wb_name})")
                sheet = wb.active
                # Check for budget category column, add it if not present.
                check_budget_category(sheet)
                # Map the 'Original Description' column to the 'Budget Category' column.
                map_budget_category(sheet, "Original Description", BUDGET_CATEGORY_COL_NAME)
            except Exception as e:
                logger.error(f"{cp}    Error processing workbook: {wb_name}: {e}")
                continue

            # Step 3: Save the output items to output storage.
            try:
                bm.bsm_FI_WF_WORKBOOK_save(wb, wb_name, fi_key, wf_key, WF_OUTPUT)
            except Exception as e:
                logger.error(f"{cp}    Error saving workbook: {wb_name}: {e}")
                continue
        logger.info(f"{cp} Complete: wf_key: '{wf_key}' {p3u.stop_timer(st)}")
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion execute_worklow_categorization() function
# ---------------------------------------------------------------------------- +