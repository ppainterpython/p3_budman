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
    """ Convert the path_name to a Path object and text for existence.
    
    Check if the path is reachable and exists. 3 cases are supported:
    1. If the path is just a file name, check if it exists in the module folder. 
       This case supports using built-in log config files in the package. 
    2. If the path is absolute, check if it exists. This case allows callers to
       specify an absolute path to a file or directory.
    3. If the path is relative, check if it exists relative to CWD. This case
       allows callers to specify a relative path to another project folder.
    
    Args:
        path_name (str): The path str to check. Must be a string valid for use
        in a path.
        
    Returns:
        Path | None: Returns a Path object if the path exists, otherwise None.
        
    Raises:
        TypeError: Raises a TypeError if the path_name is not a string.
        ValueError: Raises a ValueError if the path_name is empty or not usable
        in a path.
        Exception: Forwards exceptions caught from the pathlib methods.
    """
    try:
        me = fpfx(is_path_reachable)
        # Check if the path is a viable str usable in a path.
        if path_name is None or not isinstance(path_name, str) or len(path_name) == 0:
            raise TypeError(f"Invalid path_name: type:'{type(path_name)}' value = '{path_name}'")
        # Case 1: Check if the input is just a file name
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
    except Exception as e:
        log_exc(is_path_reachable,e,print_flag=True)
        raise
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
    try:
        if not func is None and isinstance(func, function):
            mod_name = func.__globals__['__name__']
            func_name = func.__name__
            return f"{mod_name}.{func_name}(): "
        else: 
            m = f"InvalidFunction({str(func)}): "
            print(f"fpfx(): Passed {str(m)}")
            return m
    except Exception as e:
        print(f"fpfx() Error: {str(e)}")
        raise
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
    try:
        if not func is None and isinstance(func, function):
            m = f"{fpfx(func)}{str(e)}"
            if print_flag: print(m)
            return m
        else:
            m = f"log_exc(): InvalidFunction({str(func)}): "
            if print_flag: print(m)
            return m
    except Exception as e:
        print(f"log_exc() Error: {str(e)}")
        raise
#endregion log_exc() function
# ---------------------------------------------------------------------------- +
