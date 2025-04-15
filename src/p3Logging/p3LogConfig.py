# ---------------------------------------------------------------------------- +
""" P3 Logging Module - simple add-on features to Python's logging module. """
# Python standard libraries
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers
# Python third-party libraries
import pyjson5
# Local libraries
from .p3LogConstants import *  
from .p3LogUtils import *
from .p3LogFormatters import JSONOutputFormatter, ModuleOrClassFormatter

# ---------------------------------------------------------------------------- +
#region Globals
_log_config_dict = {}
_log_config_path = None
#endregion Globals
# ---------------------------------------------------------------------------- +
#region get_configDict() function
def get_configDict() -> dict:
    """Return the current dictConfig() logging configuration dictionary."""
    global _log_config_dict
    return _log_config_dict
#endregion get_configDict() function
# ---------------------------------------------------------------------------- +
#region get_config_path() function
def get_config_path() -> dict:
    """Return the current logging configuration file path."""
    global _log_config_path
    return _log_config_path
#endregion get_config_path() function
# ---------------------------------------------------------------------------- +
#region retain_pytest_handlers
def retain_pytest_handlers(f):
    """
    A wrapper function to retain pytest handlers in the 
    logging configuration.
    """
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
#endregion retain_pytest_handlers
# ---------------------------------------------------------------------------- +
#region wrap_config_dictConfig() function
@retain_pytest_handlers
def wrap_config_dictConfig(log_config):
    """
    Apply the logging configuration using dictConfig while retaining pytest handlers.
    """
    try:
        # Now invoke the dictConfig function to apply the logging configuration
        logging.config.dictConfig(log_config)
    except Exception as e:
        # Exceptions from dictConfig can be deeply nested. The issues is 
        # most likely with the configuration json itself, not the logging module.
        m = f"Error: logging.config.dictConfig() "
        m += append_cause("", e)
        raise RuntimeError(m) from e
#endregion wrap_config_dictConfig() function
# ---------------------------------------------------------------------------- +
#region validate_file_logging_config() function
def validate_file_logging_config(config_json:dict) -> bool:
    """
    Validate the file logging configuration.
    """
    # Validate the JSON configuration
    try:
        _ = pyjson5.encode(config_json) # validate json serializable, not output
    except TypeError as e:
        t = type(config_json).__name__
        m = f"Error decoding config_json: '{config_json} as type: '{t}'"
        raise RuntimeError(m) from e
    except (pyjson5.JSONDecodeError, Exception) as e:
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
#endregion validate_file_logging_config() function
# ---------------------------------------------------------------------------- +
#region validate_config_file() function
def validate_config_file(config_file:str) -> dict:
    """
    Validate the file contains valid json, return it as a dictionary.
    """
    me = fpfx(validate_config_file)
    global _log_config_path
    # Check if the config file exists, is accessible, and is valid JSON
    if (config_file_path := is_path_reachable(config_file)) is None:
        raise FileNotFoundError(f"Config file not found:'{config_file}'")
    try:
        # Read the config file and parse it as JSON
        with open(config_file_path, "r") as f_in:
            _log_config_path = config_file_path
            config_json = pyjson5.decode_io(f_in)
            return config_json
    except TypeError as e:
        log_exc(validate_config_file, e, print=True)
        t = type(config_file).__name__
        m = f"{me}Error accessing config_file: '{config_file}' as type: '{t}'"
        print(m)
        raise
    except Exception as e:
        log_exc(validate_config_file, e, print=True)
        raise
#endregion validate_config_file() function
# ---------------------------------------------------------------------------- +
#region setup_logging function
def setup_logging(config_file: str = STDOUT_LOG_CONFIG_FILE,
                  start_queue:bool=True) -> None:
    """
    Set up logging for both stdout and a log file.
    
    Args:
        config_file (str): One of the builtin config file names, a relative path 
        to cwd, or an absolute path to a JSON file.
        start_queue (bool): If True, start the queue listener thread.
    """
    try:
        global _log_config_dict
        pfx = fpfx(setup_logging)
        # Validate and parse the json config_file
        log_config_json = validate_config_file(config_file)
        # For FileHandler types, validate the filenames included in the config
        validate_file_logging_config(log_config_json)
        # Apply the logging configuration preserving any pytest handlers
        wrap_config_dictConfig(log_config_json)
        _log_config_dict = log_config_json

        # If the queue_handler is used, start the listener thread
        queue_handler = logging.getHandlerByName("queue_handler")
        if start_queue and queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)
    except Exception as e:
        et = type(e).__name__
        print(f"{pfx}{et}: {str(e)}")
        raise 
#endregion setup_logging function
# ---------------------------------------------------------------------------- +
#region start_queue() function
def start_queue() -> None:
    # If the queue_handler is used, start the listener thread
    queue_handler = logging.getHandlerByName("queue_handler")
    if start_queue and queue_handler is not None:
        queue_handler.listener.start()
#endregion start_queue()() function
# ---------------------------------------------------------------------------- +
#region stop_queue() function
def stop_queue() -> None:
    # If the queue_handler is used, start the listener thread
    queue_handler = logging.getHandlerByName("queue_handler")
    if start_queue and queue_handler is not None:
        queue_handler.listener.stop()
#endregion stop_queue() function
# ---------------------------------------------------------------------------- +
#region get_formatter_reference_by_class() function
def get_formatter_id_by_custom_class_name(formatter:logging.Formatter) -> str:
    """
    From the logging config file, lookup a formatter id associated with the 
    given formatter object instance.
    
    This uses the currently logging config json file last loaded by 
    setup_logging() and only searches custom formatter class references
    specified in the dictConfig()-style json config file. 

    Args:
        handler (logging.Handler): The logging handler to get the formatter id for.

    Returns:
        str: The formatter id, which is a key in the formatters dictionary.
    """
    # https://docs.python.org/3/library/logging.config.html#dictionary-schema-details
    # Get the formatter class from the logger's handlers
    global log_config_dict
    fmt_dict = get_configDict()["formatters"] 
    fmt_id_key = [key for key, value in fmt_dict.items() 
                if 'format' in value and value['format'] == formatter._fmt]
    return fmt_id_key
#endregion get_formatter_reference_by_class() function
# ---------------------------------------------------------------------------- +
#region get_Logger_config_info() function
def get_Logger_config_info(indent: int = 0) -> str:
    """
    Get logging configuration information obtained by dictConfig().
    
    Args:
        indent (int): The indentation level for the output.
    
    Returns:
        str: A string representation of the current logging configuration.
    """
    me:str = "get_log_config_info():"
    version:int = 0
    formatters: dict = {}
    filters: dict = {}
    handlers: dict = {}
    loggers: dict = {}
    root: dict = {}
    formatter_count = 0
    filter_count = 0
    handler_count = 0
    logger_count = 0
    formatter_ids:str = None
    filter_ids:str = None
    handler_ids:str = None
    logger_ids:str = None
    incremental: bool = False
    disable_existing_loggers: bool = False
    root_formatters_count = 0
    root_formatters_ids = None
    root_filters_count = 0
    root_filters_ids = None
    root_handlers_count = 0
    root_handlers_ids = None
    root_loggers_count = 0
    root_loggers_ids = None
    pad = indent * " "
    try:
        me = fpfx(get_Logger_config_info)
        # Get the current logging configuration
        if (log_configDict := get_configDict()) is None: return None
        if (config_file_path := get_config_path()) is None:
            config_file_name = "unknown"
        else:
            config_file_name = config_file_path.name
        # Gather the info
        version = log_configDict.get("version", 1)
        if "formatters" in log_configDict:
            formatters = log_configDict["formatters"]
            formatter_count = len(formatters)
            if formatter_count > 0:
                # Get the formatter class from the logger's handlers
                formatter_ids = str([key for key, value in formatters.items()])
        if "filters" in log_configDict:
            filters = log_configDict["filters"]
            filter_count = len(filters)
            if filter_count > 0:
                filter_ids = [key for key in filters.keys()]
        if "handlers" in log_configDict:
            handlers = log_configDict["handlers"]
            handler_count = len(handlers)
            if handler_count > 0:
                handler_ids = [key for key in handlers.keys()]
        if "loggers" in log_configDict:
            loggers = log_configDict["loggers"]
            logger_count = len(loggers) 
            if logger_count > 0:
                logger_ids = [key for key in loggers.keys()]
        if "root" in log_configDict:
            root = log_configDict["root"]
            if "handlers" in root:
                root_handlers = root["handlers"]
                root_handlers_count = len(root_handlers)
                if root_handlers_count > 0:
                    root_handlers_ids = [key for key in root_handlers]
            if "level" in root:
                root_level = root["level"]
            if "filters" in root:
                root_filters = root["filters"]
                root_filters_count = len(root_filters)
                if root_filters_count > 0:
                    root_filters_ids = [key for key in root_filters]
            if "formatters" in root:
                root_formatters = root["formatters"]
                root_formatters_count = len(root_formatters)
                if root_formatters_count > 0:
                    root_formatters_ids = [key for key in root_formatters]
            if "Loggers" in root:
                root_loggers = root["Loggers"]
                root_loggers_count = len(root_loggers)
                if root_loggers_count > 0:
                    root_loggers_ids = [key for key in root_loggers]
            if "incremental" in root:
                root_incremental = root["incremental"]
            if "disable_existing_loggers" in root:
                root_disable_existing_loggers = root["disable_existing_loggers"]
        # Construct summary of the current logging configuration
        ret = str(
            f"Logging config({config_file_name}) version({version}) "
            f"formatters({formatter_count})[{formatter_ids}] "
            f"filters({filter_count})[{filter_ids}] " 
            f"handlers({handler_count})[{handler_ids}] "
            f"loggers({logger_count})[{logger_ids}] "
            f"root_handlers({root_handlers_count}) "
            
        )
            
        return ret
    except Exception as e:
        et = type(e).__name__
        m = f"{me}Error: {str(e)}"
        print(m)
        raise
#endregion get_Logger_config_info() function
# ---------------------------------------------------------------------------- +