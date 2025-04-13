# ---------------------------------------------------------------------------- +
# python standard libraries
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers

# third-party libraries
import inspect, pyjson5

# local libraries
import p3Logging as p3l



AT_APP_NAME = "ActivityTracker"

logger = logging.getLogger(AT_APP_NAME)
logger.propagate = True
log_config_dict = {}
#region main() function
def main(config_file: str = p3l.STDOUT_LOG_CONFIG_FILE):
    """Main function to run this application as a stand-alone test."""
    cfm = f"Config file: '{config_file}'"
    try:
        # Initialize the logger from a logging configuration file.
        p3l.setup_logging(config_file)
        logger.debug(f"Debug message, {cfm}", extra={"extra_key": "extra_value"})
        logger.debug(f"Debug message, {cfm}")
        logger.info(f"Info message, {cfm}")
        logger.warning(f"Warning message, {cfm}")
        logger.error(f"Error message, {cfm}")
        logger.critical(f"Critical message, {cfm}")
        try:
            1 / 0
        except ZeroDivisionError as e:
            logger.exception(f"Exception message: {str(e)}")
    except Exception as e:
        m = f"Error: during logger check, {cfm} "
        print(f"{m} {str(e)}")
        # raise RuntimeError(m) from e
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
        p3l.show_logging_setup(p3l.QUEUED_STDERR_JSON_FILE_LOG_CONFIG_FILE)
        # main()
        main(p3l.STDERR_JSON_FILE_LOG_CONFIG_FILE)
        # main(p3l.STDERR_JSON_FILE_LOG_CONFIG_FILE)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
# ---------------------------------------------------------------------------- +
