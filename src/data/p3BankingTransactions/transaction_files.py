from openpyxl import Workbook, load_workbook
import pyjson5, pathlib as Path
import p3Logging as p3l



user_config = {
    "bank_transactions_folder": "c:/users/ppain/OneDrive/budget/boa/data",
}

def get_banking_transactions() -> Workbook:
    """Get the banking transactions from configured sources."""
    try:
        logger.info("Loading banking transactions...")
        trans_file = "BOAChecking2025.xlsx"
        trans_path = Path.Path(user_config["bank_transactions_folder"]) / trans_file

        wb = load_workbook(filename=trans_file)
    except Exception as e:
        p3l.log_exc(get_banking_transactions, e, print=True)
        raise    