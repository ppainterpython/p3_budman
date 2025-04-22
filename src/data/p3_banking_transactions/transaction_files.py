# ---------------------------------------------------------------------------- +
#region p3_execl_budget.p3_banking_transactions transaction_files.py module
""" Support for reading and writing excel files for banking transactions.

    Assumptions:
    - The banking transactions are in a folder specified in the user_config.
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

user_config = {
    "bank_transactions_folder": "c:/users/ppain/OneDrive/budget/boa/data",
    "output_prefix": "saved_",
    "log_file": "logs/p3ExcelBudget.log",
    "json_log_file": "logs/p3ExcelBudget.jsonl",
}
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region save_banking_transactions() function
def save_banking_transactions(workbook : Workbook = None, trans_file:str=None) -> None:
    """Save the banking transactions workbook to the filesystem.
    
    The file is assumed to be in the folder specified in the user_config. 
    Use the folder specified in the user_config.json file. 
    the user_config may have an output_prefix specified which will be
    prepended to the trans_file name.

    TODO: If trans_file is not specified, then scan the folder for files. 
    Return a dictionary of workbooks with the file name as the key.

    Args:
        trans_file (str): The path of the transaction file to save.

    Returns:
        Workbook: The workbook containing the banking transactions.

    """
    try:
        if (user_config["output_prefix"] is not None and 
            isinstance(user_config["output_prefix"], str) and
            len(user_config["output_prefix"]) > 0):
            file_path = user_config["output_prefix"] + trans_file
        else:
            file_path = trans_file
        trans_path = Path.Path(user_config["bank_transactions_folder"]) / file_path
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
    The file is assumed to be in the folder specified in the user_config. 
    A folder is specified in the user_config.json file. That folder is scanned 
    for transactions in excel files if a particular file is not specified.

    TODO: If trans_file is not specified, then scan the folder for files. 
    Return a dictionary of workbooks with the file name as the key.

    Args:
        trans_file (str): The name of the transaction file to load.

    Returns:
        Workbook: The workbook containing the banking transactions.

    """
    try:
        trans_path = Path.Path(user_config["bank_transactions_folder"]) / trans_file

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
