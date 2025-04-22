# ---------------------------------------------------------------------------- +
# PyExeclBudget - read Excel files from a bank and analyze budget.
# ---------------------------------------------------------------------------- +
# python standard libraries
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers

# third-party libraries
import inspect, pyjson5
import p3logging as p3l

# local libraries
from p3ExcelBudgetConstants import  *
from data import p3BankingTransactions as p3b

logger = logging.getLogger(THIS_APP_NAME)
logger.propagate = True
#region main() function
def main():
    """Main function to run PyExcelBudget application."""
    try:
        wb = p3b.get_banking_transactions()
    except Exception as e:
        p3l.log_exc(main, e, print=True)
        raise
#endregion main() function
# ---------------------------------------------------------------------------- +
#region tryit() function
def tryit() -> None:
    """Try something."""
    try:
        result = inspect.stack()[1][3]
        print(f"result: '{result}'")
    except Exception as e:
        print(f"Error: tryit(): {str(e)}")
#endregion tryit() function
# ---------------------------------------------------------------------------- +
if __name__ == "__main__":
    try:
        # Configure logging
        log_config = p3l.STDOUT_FILE_LOG_CONFIG_FILE
        filenames = {"file": "logs/p3PyExcelBudget.log"}
        log_dictConfig = p3l.setup_logging(config_file = log_config,
                                           filenames=filenames)
        logger = logging.getLogger(THIS_APP_NAME)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"Running {THIS_APP_NAME}...")
        logger.info("+ ----------------------------------------------------- +")
        p3l.quick_logging_test(THIS_APP_NAME,log_config)

    except Exception as e:
        print(str(e))
        exit(1)
# ---------------------------------------------------------------------------- +
