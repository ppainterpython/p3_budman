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
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
from .budman_gui_style_registry import StyleRegistry
from .budman_gui_constants import *
from .budman_gui_msg import BudManGUIMsg

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(BMG_WINDOW_TITLE)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")
budman_msg = BudManGUIMsg()  # Singleton instance of BudManGuiMsg
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
    # ------------------------------------------------------------------------ +
    #region BudMan CMD Methods
    # ------------------------------------------------------------------------ +
    def CMD_OUTPUT(self, cmd_result: p3m.CMD_RESULT_TYPE) -> None:
        """Output command results to the GUI View using msg service."""
        try:
            tag = cmd_result.get("tag", p3m.CP_INFO).upper()
            msg = cmd_result.get(p3m.CK_CMD_RESULT_CONTENT_TYPE, "")
            budman_msg.output(msg, tag)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))        

    def WORKFLOW_UPDATE_CMD(self,fi_key: str) -> p3m.CMD_RESULT_TYPE:
        """Create a BudMan GUI View WORKFLOW_UPDATE CMD_OBJECT and process."""
        cmd: p3m.CMD_OBJECT_TYPE = p3m.create_CMD_OBJECT(
            cmd_name=cp.CV_WORKFLOW_CMD_NAME,
            cmd_key=cp.CV_WORKFLOW_CMD_KEY,
            subcmd_name=cp.CV_UPDATE_SUBCMD_NAME,
            subcmd_key=cp.CV_WORKFLOW_UPDATE_SUBCMD_KEY,
            cmd_exec_func=None,
            other_attrs={cp.CK_FI_KEY: fi_key,
                         cp.CK_UPDATE_CATEGORY_MAP_WORKBOOK: True})
        cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
        return cmd_result
    #endregion BudMan CMD Methods
    # ------------------------------------------------------------------------ +
