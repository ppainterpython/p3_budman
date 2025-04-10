#------------------------------------------------------------------------------+
import json, atexit, pathlib, logging, logging.config, logging.handlers
import pytest, inspect
import pyjson5

AT_APP_NAME = "ActivityTracker"
AT_STDOUT_LOG_CONFIG = "logging_configs/stdout.jsonc"
AT_STDERR_JSON_FILE_LOG_CONFIG = "logging_configs/stderr-json-file.jsonc"
AT_QUEUED_STDERR_JSON_FILE_LOG_CONFIG = "logging_configs/queued-stderr-json-file.jsonc"

root_logger = logging.getLogger()
logger = logging.getLogger(AT_APP_NAME)
logger.propagate = True
log_config_dict = {}
#------------------------------------------------------------------------------+
def get_logger_info(logger: logging.Logger, hierLevel:int=0) -> str:
    """Get basic logger information in a displayable str."""
    if logger is None: return None
    if not isinstance(logger, logging.Logger):
        raise TypeError(f"Expected logging.Logger, got {type(logger).__name__}")
    levelName = logging.getLevelName(logger.level)
    hCount = len(logger.handlers); fCount = len(logger.filters)
    children = logger.getChildren()
    cCount = len(children)
    propagate = logger.propagate
    parentName = logger.parent.name if logger.parent else "None"
    pad = hierLevel * "  " # hierarchy level
    ret = f"{pad}child: " if parentName != "None" else f"{pad}"
    ret += f"{logger.name}_logger: Level: {levelName}, "
    ret += f"Propagate: {propagate}, "
    ret += f"Handlers({hCount}), "
    ret += f"Filters({fCount}), Formatters({fCount}), Children({cCount})"
    ret += f", Parent('{parentName}')"
    return ret
#region show_logging_setup() function
def show_logging_setup(config_file: str = AT_STDOUT_LOG_CONFIG,
                       json:bool = False) -> None:
    '''Load a logging config and display the resulting logging setup.
    Argument json=True will print the config file as JSON.'''
    try:
        # Apply the logging configuration from config_file
        atlogging_setup(config_file)
        rlChildren = root_logger.getChildren()
        print(get_logger_info(root_logger, 0))
        for child in rlChildren:
            print(get_logger_info(child, 1))

        if json:
            print(pyjson5.dumps(log_config_dict, indent=4))
    except Exception as e:
        eInfo = repr(e)
        print(f"{__name__}.show_logging_setup(): {eInfo}")
#endregion show_logging_setup() function
#------------------------------------------------------------------------------+
#region append_cause() function
def append_cause(msg:str = None, e:Exception=None) -> str:
    '''Append the cause of an exception to the message.'''
    # If the exception has a cause, append it to the message
    print(f"{repr(e)} - > {repr(e.__cause__)}")
    if e:
        if e.__cause__:
            msg += append_cause(f" Exception: {repr(e)}",e.__cause__) 
        else:
            msg += f" Exception: {repr(e)}"
    return msg 
#endregion append_cause() function
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
    try:
        # Now invoke the dictConfig function to apply the logging configuration
        logging.config.dictConfig(log_config)
    except Exception as e:
        # Exceptions from dictConfig can be deeply nested. The issues is 
        # most likely with the configuration json itself, not the logging module.
        m = f"Error: logging.config.dictConfig() "
        m += append_cause("",e)
        raise RuntimeError(m) from e
#endregion retain_pytest_handlers decorator
#------------------------------------------------------------------------------+
#region validate_file_logging() function
def validate_file_logging_config(config_json:dict) -> bool:
    '''Validate the file logging configuration.'''
    # Validate the JSON configuration
    try:
        _ = pyjson5.encode(config_json) # validate json serializable, not output
    except TypeError as e:
        t = type(config_json).__name__
        m = f"Error decoding config_json: '{config_json} as type: '{t}'"
        raise RuntimeError(m) from e
    except (json.JSONDecodeError, Exception) as e:
        m = f"Error decoding config_json input"
        raise RuntimeError(m) from e
    # Iterate handlers and check for file handlers
    file_handler_classes = ("logging.FileHandler", 
                            "logging.TimedRotatingFileHandler",
                            "logging.handlers.RotatingFileHandler")
    for name, handler in config_json["handlers"].items():
        if isinstance(handler, dict) and \
            handler.get("class") in file_handler_classes:
            # Check if the filename is valid
            filename = handler.get("filename")
            if filename:
                file_path = pathlib.Path(filename)
                # Ensure the directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                # Check if the file is writable
                try:
                    with open(file_path, "a"):
                        pass
                except IOError as e:
                    raise RuntimeError(f"Cannot write to log file: {file_path}") from e
#endregion validate_file_logging() function
#------------------------------------------------------------------------------+
#region validate_json_file() function
def validate_json_file(json_file:str) -> dict:
    '''Validate the file contains valid json, return it as str.'''
    # Check if the config file exists, is accessible, and is valid JSON
    json_file = pathlib.Path(json_file)
    if not json_file.exists():
        raise FileNotFoundError(f"JSON file '{json_file}' not found.")
    try:
        with open(json_file, "r") as f_in:
            config_json = pyjson5.decode_io(f_in)
            return config_json
    except TypeError as e:
        t = type(json_file).__name__
        m = f"Error accessing json_file: '{json_file} as type: '{t}'"
        raise RuntimeError(m) from e
    except FileNotFoundError as e:
        m = f"Error accessing json_file: '{json_file}'"
        raise RuntimeError(m) from e
    except json.JSONDecodeError as e:
        m = f"Error decoding json_file: '{json_file}'"
        raise RuntimeError(m) from e
    except Exception as e:
        m = f"Error processing json_file: '{json_file}'"
        raise RuntimeError(m) from e
    
#endregion validate_file_logging() function
#------------------------------------------------------------------------------+
#region atlogging_setup function
def atlogging_setup(config_file: str = AT_STDOUT_LOG_CONFIG) -> None:
    """Set up logging for both stdout and a log file (thread-safe singleton)."""
    try:
        global log_config_dict
        # Validate and parse the json config_file
        at_log_config_json = validate_json_file(config_file)
        # For FileHandler types, validate the filenames included in the config
        validate_file_logging_config(at_log_config_json)
        # Apply the logging configuration preserving any pytest handlers
        wrap_config_dictConfig(at_log_config_json)
        log_config_dict = at_log_config_json

        # If the queue_handler is used, start the listener thread
        queue_handler = logging.getHandlerByName("queue_handler")
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)
    except Exception as e:
        print(f"{__name__}.atlogging_setup(): Error: Logging Setup {str(e)}")
        raise
#endregion atlogging_setup function
#------------------------------------------------------------------------------+
#region main() function
def main(config_file: str = AT_STDOUT_LOG_CONFIG):
    """Main function to run this application as a stand-alone test."""
    cfm = f"Config file: '{config_file}'"
    try:
        # Initialize the logger from a logging configuration file.
        atlogging_setup(config_file)
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
#------------------------------------------------------------------------------+
#region tryit() function
def tryit() -> None:
    """Try something."""
    try:
        result = inspect.stack()[1][3]
        print(f"result: '{result}'")
    except Exception as e:
        print(f"Error: tryit(): {str(e)}")
#endregion tryit() function
#------------------------------------------------------------------------------+
if __name__ == "__main__":
    show_logging_setup(AT_STDERR_JSON_FILE_LOG_CONFIG)
    # main()
    # main(AT_STDERR_JSON_FILE_LOG_CONFIG)
    # main(AT_QUEUED_STDERR_JSON_FILE_LOG_CONFIG)
#------------------------------------------------------------------------------+
