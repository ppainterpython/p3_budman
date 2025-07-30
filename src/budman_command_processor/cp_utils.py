# ---------------------------------------------------------------------------- +
#region cp_utils.py module
""" cp_utils.py implements utility functions for command processing.
"""
#endregion cp_utils.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, sys, getpass, time, copy, importlib
from pathlib import Path
from typing import List, Type, Optional, Dict, Tuple, Any, Callable

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from .budman_cp_namespace import *
import budman_namespace.design_language_namespace as bdm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region CMD_RESULT_OBJECT()
def CMD_RESULT_OBJECT(
    result_type: str = bdm.CMD_RESULT_TYPE,
    result_content: Any = None
) -> bdm.CMD_RESULT:
    """Create a command result object."""
    cmd_result = {
        bdm.CMD_RESULT_TYPE: result_type,
        bdm.CMD_RESULT_CONTENT: result_content
    }
    return cmd_result.copy() 
# ---------------------------------------------------------------------------- +
#region is_CMD_RESULT() function
def is_CMD_RESULT(cmd_result: Any) -> bool:
    """Check if the cmd_result parameter is a valid command result."""
    if isinstance(cmd_result, dict):
        return bdm.CMD_RESULT_TYPE in cmd_result and bdm.CMD_RESULT_CONTENT in cmd_result
    return False
#endregion is_CMD_RESULT() function