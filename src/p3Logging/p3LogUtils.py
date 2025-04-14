# ---------------------------------------------------------------------------- +
"""
p3LogUtils.py - Utility functions for the p3Logging package.
These should be leaf level functions not dependent on any other p3l modules.
"""
# Standard Module Libraries
import logging
from logging import Logger as logr
from typing import Callable as function
from pathlib import Path

# Local Modules
from .p3LogConstants import *  

# ---------------------------------------------------------------------------- +
#region is_filename_only() function
def is_filename_only(path_str:str = None) -> bool:
    """
    Check path_str as name of file only, no parent.
    """
    path = Path(path_str)
    # Check if the path has no parent folders    
    return path.parent == Path('.')
#endregion is_filename_only() function
# ---------------------------------------------------------------------------- +
#region is_path_reachable() function
def is_path_reachable(path_name: str) -> Path | None:
    """
    Check if the path is reachable and exists.
    If true, return the path object, else None.
    """
    # Step 1: Check if the input is just a file name
    module_folder = Path(__file__).parent / "p3logging_configs" / path_name
    if module_folder.exists():
        return module_folder

    # Step 2: Check if the path is absolute
    path = Path(path_name)
    if path.is_absolute() and path.exists():
        return path

    # Step 3: Resolve as relative to the current working directory
    relative_path = Path.cwd() / path_name
    if relative_path.exists():
        return relative_path

    # If none of the above checks succeed, return None
    return None
#endregion is_path_reachable() function
# ---------------------------------------------------------------------------- +
#region append_cause() function
def append_cause(msg:str = None, e:Exception=None) -> str:
    """
    Append the cause of an exception to the message.
    """
    # If the exception has a cause, append it to the message
    print(f"{str(e)} - > {str(e.__cause__)}")
    if e:
        if e.__cause__:
            msg += append_cause(f" Exception: {str(e)}",e.__cause__) 
        else:
            msg += f" Exception: {str(e)}"
    return msg 
#endregion append_cause() function
# ---------------------------------------------------------------------------- +
#region fpfx() function
def fpfx(func) -> str:
    """
    Return a prefix for the function name and its module.
    """
    if func is None:
        return None
    mod_name = func.__globals__['__name__']
    func_name = func.__name__
    return f"{mod_name}.{func_name}(): "
#endregion fpfx() function
# ---------------------------------------------------------------------------- +
#region log_exc() function
def log_exc(func:function,e:Exception,
            print_flag:bool=False,log_flag:logging.Logger=None) -> str:
    """
    Common simple output message for Exceptions.
    
    Within a function, use to emit a message in except: blocks. Various 
    arguments select output by console print(), logger, or both.
    
    Args:
        func (function): The function where the exception occurred.
        e (Exception): The exception object.
        print (bool): If True, print the message to console.
        log (logging.Logger): Logger object to log the message.
        
    Returns:
        str: Returns the routine exception log message.    
    """
    if func is None or e is None: return None
    m = f"{fpfx(func)}{str(e)}"
    if print_flag: print(m)
    return m
#endregion log_exc() function
# ---------------------------------------------------------------------------- +
