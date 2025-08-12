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
