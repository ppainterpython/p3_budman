# ---------------------------------------------------------------------------- +
#region budman_gui_commands.py module
""" budman_gui_commands.py implements the class BudManGuiCommands.
"""
#endregion budman_gui_commands.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging
from typing import Optional
import tkinter as tk
import tkinter.font as tkFont
from tkinter import EventType, scrolledtext, StringVar, BooleanVar
from tkinter import ttk
import ttkbootstrap as tb  # tb.Window used for root window only
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from .budman_gui_style_registry import StyleRegistry
from budman_gui_view.budman_gui_constants import *
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(BMG_WINDOW_TITLE)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUICommandProcessor(BudManAppDataContext_Binding,
                        p3m.CommandProcessor_Binding): 

    #--------------------------------------------------------------------------+
    #region    BudManGUICommands class Intrinsics
    #--------------------------------------------------------------------------+
    #region    BudManGUICommands doc string
    """ Budget Manager GUI Commands class.
        The BudManGUICommands class implements the client for 
        CommandProcessor_Binding for the BudMan GUI View.
    """
    #endregion BudManGUICommands doc string
    #--------------------------------------------------------------------------+
    #region    __init__() 
    def __init__(self,
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 data_context : Optional[BudManAppDataContext_Binding] = None,) -> None:
        self._dc_binding:bool = False
        self._cp_binding:bool = False
        try:
            # Setup CommandProcessor_Binding
            if command_processor is not None:
                self.CP = command_processor
            # Setup DataContext_Binding
            if data_context is not None:
                self.DC = data_context
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion    __init__() 
    #--------------------------------------------------------------------------+
    #endregion BudManGUICommands class Intrinsics
