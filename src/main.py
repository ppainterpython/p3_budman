# ---------------------------------------------------------------------------- +
#region PyExeclBudget - read Excel files from a bank and analyze budget.
""" p3ExcelBudget - read Excel files from a bank and analyze budget.

    This module is the main entry point for the p3ExcelBudget application.
    It reads Excel files from a bank and analyzes the budget.
"""
#endregion PyExeclBudget - read Excel files from a bank and analyze budget.
# ---------------------------------------------------------------------------- +
#region Imports
# python standard libraries packages and modules 
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers

# third-party  packages and module libraries
import inspect, pyjson5
import p3logging as p3l

# local packages and module libraries
from p3_excel_budget_constants import  *
import data.p3_banking_transactions as p3b

logger = logging.getLogger(THIS_APP_NAME)
logger.propagate = True
#endregion Imports
# ---------------------------------------------------------------------------- +
#region main() function
def main():
    """Main function to run PyExcelBudget application."""
    try:
        wb = p3b.get_banking_transactions()
    except Exception as e:
        p3l.exc_msg(main, e)
        raise
#endregion main() function
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        # Configure logging
        log_config = p3l.STDOUT_FILE_LOG_CONFIG_FILE
        filenames = {"file": "logs/p3ExcelBudget.log"}
        log_dictConfig = p3l.setup_logging(THIS_APP_NAME,
                                           config_file = log_config,
                                           filenames=filenames)
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger = logging.getLogger(THIS_APP_NAME)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"Running {THIS_APP_NAME}...")
        logger.info("+ ----------------------------------------------------- +")
        p3l.quick_logging_test(THIS_APP_NAME, log_config, filenames, reload = False)
        # Call Main() function
        main()
    except Exception as e:
        p3l.exc_msg("__main__",e)
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion Local __main__ stand-alone
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
