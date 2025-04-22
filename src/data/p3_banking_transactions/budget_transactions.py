# ---------------------------------------------------------------------------- +
#region p3_execl_budget.p3_banking_transactions budget_transactions.py module
""" Provide functions to apply a budget to banking transactions.

    Assumptions:
    - The banking transactions are in a folder specified in the user_config.
    - Banking transaction files are typical excel spreadsheets. 
    - Data content starts in cell A1.
    - Row 1 contains column headers. All subsequent rows are data.
"""
#endregion p3_execl_budget.p3_banking_transactions budget_transactions.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import re, pathlib as Path, logging

# third-party modules and packages
import p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_excel_budget_constants import  *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)

user_config = {
}

# Map values to column ['Category'] by re pattern-matching to 
# column ['Original Description'].
# This list of patterns will be quite long. 
# TODO: How to use data to train an LLM or ML model to do this?
category_mapping = {
    r'(?i)\bamazon\b': 'Amazon Prime',
    r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'Home Owners Association',
}

def map_category(description):
    for pattern, category in category_mapping.items():
        if re.search(pattern, str(description), re.IGNORECASE):
            return category
    return 'Other'  # Default category if no match is found

category_mapping = {
    r'(?i)\bReliant\sEnergy\b': 'Grape Cove.Utilities.Electric',
    r'(?i)\bPedernales_Elec\b': 'Castle Pines.Utilities.Electric',
    r'(?i)\bONE\sGAS\b': 'Grape Cove.Utilities.Natural Gas',
    r'(?i)\bATMOS\sENERGY\b': 'Grape Cove.Utilities.Natural Gas',
    r'(?i)\bService\sExperts\b': 'Grape Cove.Utilities.HVAC',
    r'(?i)\bBrushy\sCreek\sMUD\b': 'Grape Cove.Utilities.MUD',
    r'(?i)\bAT\&T\sU-Verse\b': 'Grape Cove.Utilities.Internet',
    r'(?i)\bGoogle\s*\bFIBER\b': 'Castle Pines.Utilities.Internet',
    r'(?i)\bGOOGLE\s\*FIBER\b': 'Castle Pines.Utilities.Internet',
    r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'Castle Pines.HOA',
    r'(?i)\bDAIRY\sQUEEN\sEnergy\b': 'Restaurants.Dairy Queen',
    r'(?i)\bMOD\sPIZZA\b': 'Restaurants.Mod Pizza',
    r'(?i)\bH\-E\-B\s\#\sPIZZA\b': 'Groceries.H-E-B',
    r'(?i)\bHP*?\bINS\sPREM\b': 'Insurance.Medical',
    r'(?i)\bState\s\bFARM\b': 'Insurance.State Farm',
    r'(?i)\bHAROLD\sF\sADELMAN\sMD\b': 'Medical.Adelman',
    r'(?i)\bBSWHealth\b': 'Medical.BSW Health',
    r'(?i)\bJOHN\sF\sLANN\sDDS\b': 'Dental.Lann',
    r'(?i)\bCVS.*PHARMACY\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bGREAT\sOAKS\sANIMAL\b': 'Pets.Veternary',
    r'(?i)\bCAMPUS\s\bCRUSADE\b': 'Charity.Campus Crusade',
    r'(?i)\bTUNNELTOTOWERS\b': 'Charity.Tunnel to Towers',
    r'(?i)\bCHEVRON\b': 'Auto.Gasoline.Chevron',
    r'(?i)\bGO\s\bCARWASH\b': 'Auto.Carwash.Go Carwash',
    r'(?i)\bHCTRA\sEFT\b': 'Auto.Tolls.HCTRA',
    r'(?i)\bdoxoPLUS\b': 'Auto.Tolls.DoxoPlus',
    r'(?i)\b7-ELEVEN\s.*?MOBILE\sPURCHASE\b': 'vape',
    r'(?i)\bGerson\sLehrman\sG\b': 'Income.Consulting.GL Group',
    r'(?i)\bHP\sINC*?\bPAYROLL\b': 'Income.HP Inc.',
    r'(?i)\bAMAZON\s.*?\bPRIME\b': 'Shopping.Amazon Prime',
}



# df['Category'] = df['Original Description'].apply(map_category)

#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region check_budget_category() function
def check_budget_category(sheet) -> bool:
    """Check that the sheet is ready to budget category.
    
    A column 'Budget Category' is added to the sheet if it does not exist.

    Args:
        sheet (openpyxl.worksheet): The worksheet to map.
    """
    try:
        me = check_budget_category
        logger.info("Check sheet for budget category.")
        # Is BUDGET_CATEGORY_COL in the sheet?
        if BUDGET_CATEGORY_COL not in sheet.columns:
            # Add the column to the sheet.
            i = sheet.max_column + 1
            sheet.insert_cols(i)
            sheet.cell(row=1, column=i).value = BUDGET_CATEGORY_COL
            # Set the column width to 20.
            sheet.column_dimensions[sheet.cell(row=1, column=i).column_letter].width = 20
            logger.info(f"Adding column '{BUDGET_CATEGORY_COL}' at index = {i}, "
                        f"column_letter = '{sheet.cell(row=1, column=i).column_letter}'")
        else:
            logger.info(f"Column '{BUDGET_CATEGORY_COL}' already exists in sheet.")

        logger.info(f"Completed checks for budget category.")
        return True
    except Exception as e:
        logger.error(p3l.exc_msg(me, e))
        raise    
#endregion check_budget_category() function
# ---------------------------------------------------------------------------- +
#region load_banking_transactions() function
def map_budget_category(sheet,src,dst) -> None:
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
    me = map_budget_category
    try:
        logger.info("Applying budget category mapping...")
        header_row = [cell.value for cell in sheet[1]] 
        if src in header_row:
            src_col_index = header_row.index(src) + 1
        else:
            logger.Error(f"Source column '{src}' not found in header row.")
            return
        if dst in header_row:
            dst_col_index = header_row.index(dst) + 1
        else:
            logger.Error(f"Destination column '{dst}' not found in header row.")
            return

        logger.info(f"Mapping '{src}'({src_col_index}) to "
                    f"'{dst}'({dst_col_index})")
        num_rows = sheet.max_row # or set a smaller limit
        for row_idx, row in enumerate(sheet.iter_rows(min_col=src_col_index, 
                                                      max_col=src_col_index, 
                                                      min_row=2, 
                                                      max_row=num_rows), 
                                                      start=2):
            # Get the value from the source column.
            src_value = row[0].value
            # Map the value to a budget category.
            dst_value = map_category(src_value)
            # Set the value in the destination column.
            sheet.cell(row=row_idx, column=dst_col_index).value = dst_value
            # if dst_value != 'Other':
            logger.info(f"Row {row_idx:04}: " 
                        f"({len(src_value):03})|{str(src_value):102}| -> " 
                        f"({len(dst_value):03})|{str(dst_value):40}|")

        logger.info(f"Completed budget category mapping")
        return None
    except Exception as e:
        logger.error(p3l.exc_msg(me, e))
        raise    
#endregion load_banking_transactions() function
# ---------------------------------------------------------------------------- +
