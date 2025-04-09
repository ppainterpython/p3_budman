#------------------------------------------------------------------------------+
import json, atexit, pathlib, logging, logging.config, logging.handlers
import pytest
import pyjson5

AT_APP_NAME = "ActivityTracker"
AT_CONFIG_FILE = "logging_configs/at_log_config.json"
AT_STDERR_JSON_FILE_LOG_CONFIG = "logging_configs/stderr-json-file.jsonc"

root_logger = logging.getLogger()
logger = logging.getLogger(AT_APP_NAME)
logger.propagate = True
#------------------------------------------------------------------------------+
#region log_logging_setup() function
def log_logging_setup(print:bool = False ) -> None:
    '''Log the current logging setup. Also print to stdout if requested.'''
    ...
#endregion log_logging_setup() function
#------------------------------------------------------------------------------+
#region testickle_logger_exception_message
def testickle_logger_exception_message()    -> None:
    """Test function to demonstrate logging an exception."""
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception(f"Exception message: {str(e)}")
        raise
#endregion testickle_logger_exception_message
#------------------------------------------------------------------------------+
#region retain_pytest_handlers decorator
def retain_pytest_handlers(f):
    '''A wrapper function to retain pytest handlers in the 
    logging configuration.'''
    # Attribution: Thanks to a-recknagel at 
    # https://github.com/pytest-dev/pytest/discussions/11618#discussioncomment-9699934
    # for this useful function.
    def wrapper(*args, **kwargs):
        pytest_handlers = [
            handler
            for handler in logging.root.handlers
            if handler.__module__ == "_pytest.logging"
        ]
        ret = f(*args, **kwargs)
        for handler in pytest_handlers:
            if handler not in logging.root.handlers:
                logging.root.addHandler(handler)
        return ret
    return wrapper
@retain_pytest_handlers
def wrap_config_dictConfig(log_config):
    logging.config.dictConfig(log_config)
#endregion retain_pytest_handlers decorator
#------------------------------------------------------------------------------+
#region atlogging_setup function
def atlogging_setup(logger_name: str = AT_APP_NAME,
                    config_file: str = AT_CONFIG_FILE,
                    verbose:bool = False) -> logging.Logger:
    """Set up logging for both stdout and a log file (thread-safe singleton)."""
    try:
        # config_file = pathlib.Path(AT_CONFIG_FILE)
        config_file = pathlib.Path(config_file)
        with open(config_file, "r") as f_in:
            at_log_config = pyjson5.load(f_in)

        # Ensure the logs directory exists
        log_file_path = pathlib.Path(at_log_config["handlers"]["file"]["filename"])
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Apply the logging configuration preserving any pytest handlers
        wrap_config_dictConfig(at_log_config)

        if verbose:
            logger.debug(f"Logging configuration loaded from:'{config_file}'")

    except Exception as e:
        print(f"{__name__}: Logging Setup Exception: {e}")
        raise
#endregion atlogging_setup function
#------------------------------------------------------------------------------+
#region main() function
def main():
    """Main function to run this application as a stand-alone test."""
    try:
        # Initialize the logger from a logging configuration file.
        ln = AT_APP_NAME; cf = AT_STDERR_JSON_FILE_LOG_CONFIG; verbose = True
        atlogging_setup(ln, cf, verbose)
        logger.debug("debug message", extra={"extra_key": "extra_value"})
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
    try:
        testickle_logger_exception_message()
    except ZeroDivisionError as e:
        logger.error(f"An error occurred: {e}")
#endregion main() function
#------------------------------------------------------------------------------+
if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------+
