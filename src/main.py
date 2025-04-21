# ---------------------------------------------------------------------------- +
# PyExeclBudget - read Excel files from a bank and analyze budget.
# ---------------------------------------------------------------------------- +
# python standard libraries
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers

# third-party libraries
import inspect, pyjson5

# local libraries
import p3Logging as p3l

THIS_APP_NAME = "PyExcelBudget"

logger = logging.getLogger(THIS_APP_NAME)
logger.propagate = True
#region main() function
def main(config_file: str = p3l.STDOUT_LOG_CONFIG_FILE):
    """Main function to run PyExcelBudget application."""
    cfm = f"Config file: '{config_file}'"
    try:
        # Initialize the logger from a logging configuration file.
        ...
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
        config_file = p3l.QUEUED_STDERR_FILE_JSON_LOG_CONFIG_FILE
        log_dictConfig = p3l.setup_logging(config_file) 
        m = "show_logging_setup one-liner, config_file = "
        m += f"'{config_file}'"
        print(m)
        p3l.show_logging_setup(config_file,showall=False)
        # main()
    except Exception as e:
        print(str(e))
        exit(1)
# ---------------------------------------------------------------------------- +
