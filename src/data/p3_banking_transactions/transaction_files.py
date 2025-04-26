# ---------------------------------------------------------------------------- +
#region p3_execl_budget.p3_banking_transactions transaction_files.py module
""" Support for reading and writing excel files for banking transactions.

    Assumptions:
    - The banking transactions are in a folder specified in the budget_config.
    - Banking transaction files are typical excel spreadsheets. 
    - Data content starts in cell A1.
    - Row 1 contains column headers. All subsequent rows are data.
"""
#endregion p3_execl_budget.p3_banking_transactions transaction_files.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import pathlib as Path, logging

# third-party modules and packages
import pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_excel_budget_constants import  *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Configuration
# Budget configuration covers the file structure where user data is stored as 
# settings for options and preferences. Keep it simple.
# There is both an object model used in the application (in memory) and a
# file system structure used to store the data. In addition, the idea is that 
# users are placing new banking transactions in an "incoming" folder folder 
# for processing through stages to arrive in updating the budget. Long-view is 
# anticipate more than one bank or financial institution sourcing regular 
# statements in spreadsheet format. So, the "budget" will cover multiple "banks"
# information for a given user.
budget_config = {
    "budget_folder": "~/OneDrive/budget",
    "institutions": {
        "boa": {
            "name": "Bank of America",
            "type": "bank",
            "folder": "boa",
            # Incoming folder name and list of workbook names,
            # e.g. ["new_boa-1391-2024-04-28.xlsx"]
            "incoming_folder": "new",
            "incoming_workbooks": [],                
            # Categorized folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
            "categorized_folder": "categorized",
            "categorized_workbooks": [],                
            # Processed folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
            "processed_folder": "processed",
            "processed_workbooks": [],                
        },
        "merrill": {
            "name": "Merrill Lynch",
            "type": "brokerage",
            "folder": "merrill",
            # Incoming folder name and list of workbook names,
            # e.g. ["new_boa-1391-2024-04-28.xlsx"]
            "incoming_folder": "new",
            "incoming_workbooks": [],                
            # Categorized folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
            "categorized_folder": "categorized",
            "categorized_workbooks": [],                
            # Processed folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
            "processed_folder": "processed",
            "processed_workbooks": [],                
        },   
    },
    "options": {
        "incoming_prefix": "new_",
        "categorized_folder": "categorized_",
        "processed_folder": "processed_",
        "log_level": logging.DEBUG,
        "log_file": "logs/p3ExcelBudget.log",
        "json_log_file": "logs/p3ExcelBudget.jsonl",
    },
}
#endregion BUdget Configuration
# ---------------------------------------------------------------------------- +
#region Budget Model (MVVM sense of Model)
# ---------------------------------------------------------------------------- +
budget_model :dict = {}
budget_abs_path : Path.Path = None
selected_institution : str = "boa"
incoming_folder_abs_path : Path.Path = None
categorized_folder_abs_path : Path.Path = None
#region init_budget_model(budget_config) -> None
def init_budget_model(budget_config:dict) -> dict:
    """Initialize the budget model with the given configuration.

    Args:
        budget_config (dict): The budget configuration dictionary.

    Returns:
        dict: The initialized budget model.
    """
    me = init_budget_model
    try:
        global budget_model, budget_abs_path, selected_institution
        global incoming_folder_abs_path, categorized_folder_abs_path
        if budget_model is not None and isinstance(budget_model, dict):
            # Already initialized, so just return
            logger.info(f"Budget model already initialized.")
            return budget_model
        # -------------------------------------------------------------------- +
        # Use the budget_config to set up the budget model
        budget_model = budget_config.copy()
        logger.info(f"Initializing budget model...")
        
        # Set up Paths for the appropariate folders
        # Start with budget folder, then institution folder, then incoming folder
        # and categorized folder. Construct and validate absolute paths for all folders.
        budget_rel_path = Path.Path(budget_model["budget_folder"])
        budget_abs_path = budget_rel_path.resolve()
        if not budget_abs_path.exists():
            m = f"Budget folder does not exist: '{str(budget_abs_path)}' ."
            logger.error(m)
            raise FileNotFoundError(m)
        # Institution folder
        institution = budget_model["institutions"][selected_institution]
        
        # Create subfolders if they do not exist
        for institution in budget_config["institutions"].values():
            for folder in ["incoming_folder", "categorized_folder", "processed_folder"]:
                folder_path = budget_folder / institution[folder]
                if not folder_path.exists():
                    logger.info(f"Creating folder: {folder_path}")
                    folder_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(p3l.exc_msg(me, e))

#endregion init_budget_model(budget_config) -> None
# ---------------------------------------------------------------------------- +
#endregion Budget Model (MVVM sense of Model)
# ---------------------------------------------------------------------------- +
#region save_banking_transactions() function
def save_banking_transactions(workbook : Workbook = None, trans_file:str=None) -> None:
    """Save the banking transactions workbook to the filesystem.
    
    The file is assumed to be in the folder specified in the budget_config. 
    Use the folder specified in the budget_config.json file. 
    the budget_config may have an output_prefix specified which will be
    prepended to the trans_file name.

    TODO: If trans_file is not specified, then scan the folder for files. 
    Return a dictionary of workbooks with the file name as the key.

    Args:
        trans_file (str): The path of the transaction file to save.

    Returns:
        Workbook: The workbook containing the banking transactions.

    """
    try:
        if (budget_config["output_prefix"] is not None and 
            isinstance(budget_config["output_prefix"], str) and
            len(budget_config["output_prefix"]) > 0):
            file_path = budget_config["output_prefix"] + trans_file
        else:
            file_path = trans_file
        trans_path = Path.Path(budget_config["bank_transactions_folder"]) / file_path
        logger.info("Saving banking transactions...")
        workbook.save(filename=trans_path)
        logger.info(f"Saved banking transactions to '{str(trans_path)}'")
        return
    except Exception as e:
        logger.error(p3l.exc_msg(load_banking_transactions, e))
        raise    
#endregion save_banking_transactions() function
# ---------------------------------------------------------------------------- +
#region load_banking_transactions() function
def load_banking_transactions(trans_file:str=None) -> Workbook:
    """Get the banking transactions from configured sources into a workbook.
    
    Banking transactions downloaded from the bank are in a folder. 
    From now, it is using Bank of America (BOA) downloads.
    The file is assumed to be in the folder specified in the budget_config. 
    A folder is specified in the budget_config.json file. That folder is scanned 
    for transactions in excel files if a particular file is not specified.

    TODO: If trans_file is not specified, then scan the folder for files. 
    Return a dictionary of workbooks with the file name as the key.

    Args:
        trans_file (str): The name of the transaction file to load.

    Returns:
        Workbook: The workbook containing the banking transactions.

    """
    try:
        trans_path = Path.Path(budget_config["bank_transactions_folder"]) / trans_file

        logger.info("Loading banking transactions...")
        wb = load_workbook(filename=trans_path)
        logger.info(f"Loaded banking transactions from {str(trans_path)}")

        return wb
    except Exception as e:
        logger.error(p3l.exc_msg(load_banking_transactions, e))
        raise    
#endregion load_banking_transactions() function
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        load_banking_transactions()
    except Exception as e:
        logger.error(p3l.exc_msg("__main__",e))
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
