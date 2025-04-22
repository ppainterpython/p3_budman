# ---------------------------------------------------------------------------- +
# p3PyExeclBudget.p3BankingTransactions transaction_files.py 
""" Support for reading and writing excel files for banking transactions."""
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import pathlib as Path, logging

# third-party modules and packages
import pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3ExcelBudgetConstants import  *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)

user_config = {
    "bank_transactions_folder": "c:/users/ppain/OneDrive/budget/boa/data",
    "log_file": "logs/p3ExcelBudget.log",
    "json_log_file": "logs/p3ExcelBudget.jsonl",
}
# ---------------------------------------------------------------------------- +
#region get_banking_transactions() function
def get_banking_transactions() -> Workbook:
    """Get the banking transactions from configured sources."""
    try:
        logger.info("Loading banking transactions...")
        trans_file = "BOAChecking2025.xlsx"
        trans_path = Path.Path(user_config["bank_transactions_folder"]) / trans_file

        wb = load_workbook(filename=trans_path)
    except Exception as e:
        p3l.exc_msg(get_banking_transactions, e, print=True)
        raise    
#endregion get_banking_transactions() function
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:

        get_banking_transactions()
    except Exception as e:
        print(str(e))
        exit(1)
#endregion
# ---------------------------------------------------------------------------- +
