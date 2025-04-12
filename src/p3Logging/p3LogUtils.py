# ---------------------------------------------------------------------------- +
'''
p3LogUtils.py - Utility functions for the p3Logging package.
These should be leaf level functions not dependent on any other p3l modules.'''
# Standard Module Libraries
import logging

# Local Modules
from .p3LogConstants import *  

# ---------------------------------------------------------------------------- +
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
