import json, logging, logging.config, logging.handlers, pathlib
AT_APP_NAME = "ActivityTracker"
AT_CONFIG_FILE = "at_log_config.json"

logger = logging.getLogger(AT_APP_NAME)
logger.propagate = True

def testickle_logger_exception_message()    -> None:
    """Test function to demonstrate logging an exception."""
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception(f"Exception message: {str(e)}")
        raise

def atlogging_setup(logger_name: str = AT_APP_NAME) -> logging.Logger:
    """Set up logging for both stdout and a log file (thread-safe singleton)."""
    try:
        config_file = pathlib.Path(AT_CONFIG_FILE)
        with open(config_file, "r") as f_in:
            at_log_config = json.load(f_in)
        print(json.dumps(at_log_config, indent=4))

        # Ensure the logs directory exists
        log_file_path = pathlib.Path(at_log_config["handlers"]["file"]["filename"])
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Set up the logger with the configuration from the JSON file
        logging.config.dictConfig(at_log_config) 

    except Exception as e:
        print(e)
        raise
#endregion atlogging_setup()

def main():
    """Main function to run the application."""
    try:
        # Initialize the logger
        atlogging_setup()
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


if __name__ == "__main__":
    root_logger = logging.getLogger()
    logger = logging.getLogger(AT_APP_NAME)
    main()