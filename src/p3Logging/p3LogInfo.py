# ---------------------------------------------------------------------------- +
'''
p3LogInfo.py - Some commands to retrieve and display information about the
current logging setup.
'''
# ---------------------------------------------------------------------------- +
#region module imports
# Python Standard Libraries
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers
from typing import override
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
#region get_info_logger_formatters() function
def get_info_logger_formatters(logger: logging.Logger) -> str:
    """Get basic logger information in a displayable str."""
    try:
        if logger is None: return None
        if not isinstance(logger, logging.Logger):
            raise TypeError(f"Expected logging.Logger, got {type(logger).__name__}")
        formatters = []
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                formatter = handler.formatter
                if formatter is not None:
                    formatters.append(formatter._fmt)
            elif isinstance(handler, logging.FileHandler):
                formatter = handler.formatter
                if formatter is not None:
                    formatters.append(formatter._fmt)
        ret = f"Formatters: {formatters}"
        return ret
    except Exception as e:
        m = f"Error: get_info_logger_formatters(): {str(e)}"
#endregion get_info_logger_formatters() function
# ---------------------------------------------------------------------------- +
#region get_info_logger() function
def get_info_logger(logger: logging.Logger, hierLevel:int=0) -> str:
    """Get basic logger information in a displayable str."""
    try:
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
        if cCount > 0:
            ret += "\n"
            for child in children:
                ret += get_info_logger(child, hierLevel + 1)
        return ret
    except Exception as e:
        m = f"Error: get_info_logger(): {str(e)}"   
#endregion get_info_logger() function
# ---------------------------------------------------------------------------- +
#region show_logging_setup() function
def show_logging_setup(config_file: str = STDOUT_LOG_CONFIG,
                       json:bool = False) -> None:
    '''Load a logging config and display the resulting logging setup.
    Argument json=True will print the config file as JSON.'''
    try:
        # Apply the logging configuration from config_file
        setup_logging(config_file)

        all_formatters_info = get_info_logger_formatters(root_logger)
        rlChildren = root_logger.getChildren()
        print(get_info_logger(root_logger, 0))
        for child in rlChildren:
            print(get_info_logger(child, 1))

        if json:
            print(pyjson5.dumps(log_config_dict, indent=4))
    except Exception as e:
        eInfo = repr(e)
        print(f"{__name__}.show_logging_setup(): {eInfo}")
#endregion show_logging_setup() function
