# ---------------------------------------------------------------------------- +
"""
p3LogInfo.py - Some commands to retrieve and display information about the
current logging setup.
"""
# ---------------------------------------------------------------------------- +
#region module imports
# Python Standard Libraries
import logging, os, atexit, pathlib, inspect, logging.config
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from typing import override, List
import datetime as dt

# Python Third-Party Libraries
from  dateutil import tz
import pyjson5

# Local Libraries
from .p3LogConstants import *
from .p3LogUtils import *
from .p3logger import *
#endregion module imports
# ---------------------------------------------------------------------------- +
#region Globals
root_logger = logging.getLogger()
#endregion Globals
# ---------------------------------------------------------------------------- +
#region quick_logging_test() function
def quick_logging_test(app_name:str,log_config_file:str) -> None:
    """Quick correctness test of the current logging setup."""

    pfx = fpfx(quick_logging_test)
    try:
        # Initialize the logger from a logging configuration file.
        setup_logging(log_config_file)
        logger = logging.getLogger(app_name)
        # Log messages at different levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")
        try:
            1 / 0
        except ZeroDivisionError as e:
            logger.exception(f"Exception message: {str(e)}")
    except Exception as e:
        log_exc(quick_logging_test, e, print=True)
        raise
#endregion quick_logging_test()
# ---------------------------------------------------------------------------- +
#region get_handler_info_QueueHandler() function
def get_handler_info_QueueHandler(handler: logging.handlers.QueueHandler,
                                  indent:int=0, showall:bool=True) -> str:
    """Create a summary of a logging.QueueHandler object."""
    if handler is None: return None
    if not isinstance(handler, logging.handlers.QueueHandler):
        raise TypeError(f"Expected logging.handlers, got {type(handler).__name__}")
    try:
        # Gather the interesting attributes of the QueueHandler
        listener = handler.listener
        pad = indent * "  " # hierarchy level
        ret = f"{pad}QueueHandler: type:'{type(handler).__name__}', "
        lhl = listener.handlers if listener else None # hl - listener hndlr list
        lhlc = len(lhl) if lhl else 0 # hlc - listener handler list count
        linfo = f"Listener: type:'{type(listener).__name__}'" if lhl else None
        linfo += f", Handlers({lhlc})" if lhlc > 0 else None # listener info
        ret += linfo
      
        # If showall, add information about the listener's handlers if present
        if showall and lhlc > 0:
            indent += 1
            pad = indent * "  " # hierarchy level
            ret = f"\n{indent}:" # new line
            ret += linfo # listener info
            indent += 1
            ret += get_logger_info_handlers(lhl, indent, showall)
        return ret
    except Exception as e:
        print(log_exc(get_handler_info_QueueHandler, e, print=True))
        raise
#endregion get_handler_info_QueueHandler() function
# ---------------------------------------------------------------------------- +
#region get_logger_info_filters() function
def get_logger_info_filters(filters:List) -> List[logging.Filter]:
    """Collect and return all the logging.Filter objects from handlers."""
    if filters is None: return None
    # Must be a list or tuple of logging.Handler objects
    if (not (isinstance(filters, List)) or
        not (all(isinstance(obj, logging.Filter) for obj in filters))):
        raise TypeError((f"Expected List of logging.Filter objects, ")
                        (f"got {type(filters).__name__}"))
    try:
        # Navigate the filters to collect info on the configured filters.
        filters = []
        for filter in filters:
            ...
        return filters
    except Exception as e:
        print(log_exc(get_logger_info_filters, e, print=True))
        raise
#endregion get_logger_info_filters() function
# ---------------------------------------------------------------------------- +
#region get_logger_info_formatters() function
def get_logger_info_formatters(handlers:List) -> List[logging.Formatter]:
    """Collect and return all the logging.Formatter objects from handlers."""
    if handlers is None: return None
    # Must be a list or tuple of logging.Handler objects
    if (not (isinstance(handlers, List) or 
        isinstance(handlers, tuple)) or
        not (all(isinstance(obj, logging.Handler) for obj in handlers))):
        raise TypeError((f"Expected List of logging.Handler objects, ")
                        (f"got {type(handlers).__name__}"))
    try:
        # Navigate the handlers to collect info on the configured formatters.
        formatters = []
        for handler in handlers:
            if isinstance(handler, logging.StreamHandler):
                formatter = handler.formatter
                # if formatter is not None:
                #     formatters.append(formatter._fmt)
                formatters.append(formatter) if formatter else None
            elif isinstance(handler, logging.FileHandler):
                formatter = handler.formatter
                # if formatter is not None:
                #     formatters.append(formatter._fmt)
                formatters.append(formatter) if formatter else None
            # logging.handlers.QueueHandler
            elif isinstance(handler, logging.handlers.QueueHandler):
                # A listener has a list of handlers, collect them if present.
                listener = handler.listener
                hl = listener.handlers if listener else None
                formatters += get_logger_info_formatters(hl) if hl else None
        return formatters
    except Exception as e:
        print(log_exc(get_handler_info_QueueHandler, e, print=True))
        raise
#endregion get_logger_info_formatters() function
# ---------------------------------------------------------------------------- +
#region get_logger_info_handlers() function
def get_logger_info_handlers(handlers:List, indent:int=0,
                             showall:bool=True) -> str:
    """Create a summary of the handlers associated with the given logger."""
    if handlers is None: return None
    # Must be a list or tuple of logging.Handler objects
    if (not (isinstance(handlers, List) or 
        isinstance(handlers, tuple)) or
        not (all(isinstance(obj, logging.Handler) for obj in handlers))):
        raise TypeError((f"Expected List of logging.Handler objects, ")
                        (f"got {type(handlers).__name__}"))
    try:
        # python logging has various types of handlers with their
        # own classes and associated metadata. This function will
        # summarize the handlers associated with the logger.
        ret = f"\n{indent}:" # new line
        pad = indent * "  " # hierarchy level
        ret += "{pad}  handlers: "
        for handler in handlers:
            indent += 1
            # logging.StreamHandler
            if isinstance(handler, logging.StreamHandler):
                ret = f"\n{indent}:" # new line
                ret += f"{pad}StreamHandler: type:'{type(handler).__name__}', "
            # logging.FileHandler
            elif isinstance(handler, logging.FileHandler):
                ret = f"\n{indent}:" # new line
                ret += f"{pad}FileHandler: type:'{type(handler).__name__}', "
            # logging.handlers.QueueHandler
            elif isinstance(handler, logging.handlers.QueueHandler):
                ret = f"\n{indent}:" # new line
                ret += get_handler_info_QueueHandler(handler, indent+4)
            # Some other class based on logging.Handler
            else:
                ret = f"\n{indent}:" # new line
                ret += f"Handler: type:'{type(handler).__name__}', "
        return ret
    except Exception as e:
        print(log_exc(get_logger_info_handlers, e, print=True))
        raise
#endregion get_logger_info_handlers() function
# ---------------------------------------------------------------------------- +
#region get_logger_info() function
def get_logger_info(logger: logging.Logger, indent:int=0,
                    showall:bool=True) -> str:
    """Get basic logger information in a displayable str.
    
    This function retrieves information about the logger, including its name,
    level, handlers, filters, formatters, and children. It recursively calls
    itself to display information about child loggers, increasing the 
    indentation level for each child logger.
    
    Args:
        logger (logging.Logger): The logger to retrieve information from.
        indent (int): Number of spaces for indentation.
        showall (bool): If True, show all information. If False, show only one
        line summary.
        
    Returns:
        str: A string containing the logger information. Could be mlultiline.
    """
    try:
        if logger is None: return None
        if not isinstance(logger, logging.Logger):
            m = f"Expected logging.Logger, got {type(logger).__name__}"
            raise TypeError(m)

        # First create a one line summary of the logger attributes
        levelName = logging.getLevelName(logger.level)
        handlers = logger.handlers
        hCount = len(handlers)
        formatters = get_logger_info_formatters(handlers)
        fmtCount = len(formatters)
        filters = logger.filters
        filCount = len(filters)
        children = logger.getChildren()
        cCount = len(children)
        propagate = logger.propagate
        parentName = logger.parent.name if logger.parent else "None"
        ret = f"\n{indent}:" # new line
        pad = indent * "  " # indent spaces
        cpad = f"{pad}  child: " # child logger indent spaces
        ret +=  cpad if parentName != "None" else pad
        ret += f"{logger.name}_logger: Level: {levelName}"
        ret += f", Propagate: {propagate}"
        ret += f". Handlers({hCount})"
        ret += f", Formatters({fmtCount})"
        ret += f", Filters({filCount})"
        ret += f", Children({cCount})"
        ret += f", Parent('{parentName}')"
        if not showall: 
            return ret
        
        # With showall, elaborate handlers, formatters, filters, and children 
        # on additional further indented lines.
        indent += 1
        ret = f"\n{indent}:" # new line
        pad = indent * "  " # indent spaces
        # Handlers
        if hCount > 0:
            ret += get_logger_info_handlers(logger.handlers,indent,showall)
        # Formatters
        if fmtCount > 0:
            ret = f"\n{indent}:" # new line
            ret += f"{pad}Formatters: "
            for formatter in formatters:
                ret = f"\n{indent}:" # new line
                ret += f"{pad}  {formatter}"
        # Filters
        if filCount > 0:
            ret = f"\n{indent}:" # new line
            ret += f"{pad}Filters: "
            for filter in filters:
                ret = f"\n{indent}:" # new line
                ret += f"{pad}  {filter}"
        # Child loggers
        if cCount > 0:
            ret = f"\n{indent}:" # new line
            ret += f"{pad}children: "
            indent += 1
            for child in children:
                ret += get_logger_info(child, indent, showall)
        return ret
    except Exception as e:
        print(log_exc(get_logger_info, e, print=True))
        raise
#endregion get_logger_info() function
# ---------------------------------------------------------------------------- +
#region show_logging_setup() function
def show_logging_setup(config_file: str = STDOUT_LOG_CONFIG_FILE,
                       showall:bool = True,
                       json:bool = False) -> None:
    """Load a logging config and display the resulting logging setup.
    
    Information is printed to the console, use showall to navigate more
    detail in depth.
    
    Args:
        config_file (str): Path to the logging configuration file.
        showall (bool): If True, show all information. If False, show only one
        line summary.
        json (bool): If True, print the config file as JSON.
    """
    try:
        # Apply the logging configuration from config_file
        setup_logging(config_file)
        
        # Invoke get_logger_info() to display the current logging setup
        root_logger = logging.getLogger()
        print(get_logger_info(root_logger, 0))

        if json:
            print(pyjson5.dumps(log_config_dict, indent=4))
    except Exception as e:
        print(log_exc(show_logging_setup, e, print=True))
        raise
#endregion show_logging_setup() function
