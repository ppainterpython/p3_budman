# ---------------------------------------------------------------------------- +
#region budman_gui_app.py module
""" budman_gui_app.py implements the class BudManGuiApp.

"""
#endregion budman_gui_app.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import queue
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import logging, os, getpass, time, copy
from typing import List, Optional, Type, Generator, Dict, Tuple, Any, TYPE_CHECKING
# third-party modules and packages
from treelib import Tree
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
import budman_namespace as bdm
import budman_settings as bdms
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
from budget_storage_model import BSMFileTree
# bugman_gui_view modules and packages
from .budman_gui_style_registry  import StyleRegistry
from .budman_gui_command_processor import BudManGUICommandProcessor
from .budman_gui_window  import BudManGUIWindow
from .budman_gui_frame   import BudManGUIFrame
from .budman_gui_msg     import BudManGuiMsg
from .budman_gui_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
budman_msg = BudManGuiMsg()  # Singleton instance of BudManGuiMsg
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUIView(BudManAppDataContext_Binding,
                    p3m.CommandProcessor_Binding):
    #--------------------------------------------------------------------------+
    #region BudManGuiView class Intrinsics
    #--------------------------------------------------------------------------+
    #region BudManGuiView doc string
    """ Budget Manager GUI View class.
        The BudManGuiView class sets up and runs the BudManGuiView.
    """
    #endregion BudManGuiView doc string
    #--------------------------------------------------------------------------+
    #region    __init__() 
    def __init__(self, 
                 budman_settings : Optional[bdms.BudManSettings] = None,
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 data_context : Optional[BudManAppDataContext_Binding] = None,
                 app_name : str = "P3 Budget Manager GUI View",) -> None:
        self.root: BudManGUIWindow = None  # type: ignore
        self.budman_gui_command_processor: BudManGUICommandProcessor = None  # type: ignore
        self._app_name = app_name
        self._settings : bdms.BudManSettings = budman_settings if budman_settings else bdms.BudManSettings()
        self._current_cmd :Optional[str] = None
        self._save_on_exit : bool = True
        self._dc_binding:bool = False
        self._cp_binding:bool = False
        self._file_tree : Tree = None
        try:
            # Setup DataContext_Binding
            if data_context is not None:
                self.DC = data_context 
                self.dc_binding = True
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            logger.debug("BudMaGUIView configured with no DataContext.")

        try:
            # Setup CommandProcessor_Binding 
            if command_processor is not None:
                self.budman_gui_command_processor = BudManGUICommandProcessor(
                    command_processor=command_processor,
                    data_context=data_context)
                self.CP = self.budman_gui_command_processor
                self.cp_binding = True
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            logger.debug("BudMaGUIView configured with no CommandProcessor.")

        # Setup the root window
        self.root = BudManGUIWindow(themename='cosmo',
                                    budman_settings=self.settings,
                                    command_processor=command_processor,
                                    data_context=data_context)
        logger.info(f"Initializing BudMan GUI View")
        logger.debug(f"BudManGUIView created")
        budman_msg.output(f"BudManGUIView created for application '{self._app_name}'.")
    #endregion __init__()
    # ------------------------------------------------------------------------ +
    #region    BudManGUIView class properties
    @property
    def dc_binding(self) -> bool:
        """Get the dc_binding property."""
        return self._dc_binding
    @dc_binding.setter
    def dc_binding(self, value: bool) -> None:
        """Set the dc_binding property."""
        if not isinstance(value, bool):
            raise TypeError("dc_binding must be a boolean.")
        self._dc_binding = value
    @property
    def cp_binding(self) -> bool:
        """Get the cp_binding property."""
        return self._cp_binding
    @cp_binding.setter
    def cp_binding(self, value: bool) -> None:
        """Set the cp_binding property."""
        if not isinstance(value, bool):
            raise TypeError("cp_binding must be a boolean.")
        self._cp_binding = value
    @property
    def save_on_exit(self) -> bool:
        """Get the save_on_exit property."""
        return self._save_on_exit
    @save_on_exit.setter
    def save_on_exit(self, value: bool) -> None:
        """Set the save_on_exit property."""
        if not isinstance(value, bool):
            raise TypeError("save_on_exit must be a boolean.")
        self._save_on_exit = value

    @property
    def app_name(self) -> str:
        """Get the app_name property."""
        return self._app_name
    @app_name.setter
    def app_name(self, value: str) -> None:
        """Set the app_name property."""
        if not isinstance(value, str):
            raise TypeError("app_name must be a string.")
        self._app_name = value

    @property
    def current_cmd(self) -> Optional[str]:
        """Get the current_cmd property."""
        return self._current_cmd
    @current_cmd.setter
    def current_cmd(self, value: Optional[str]) -> None:
        """Set the current_cmd property."""
        if value is not None and not isinstance(value, str):
            raise TypeError("current_cmd must be a string or None.")
        self._current_cmd = value
        if value:
            logger.debug(f"Current command set to: {value}")
        else:
            logger.debug("Current command cleared.")

    @property
    def settings(self) -> bdms.BudManSettings:
        """Get the settings property."""
        return self._settings
    @settings.setter
    def settings(self, value: bdms.BudManSettings) -> None:
        """Set the settings property."""
        if not isinstance(value, bdms.BudManSettings):
            raise TypeError("settings must be a BudManSettings instance.")
        self._settings = value
        logger.debug(f"Settings updated: {self._settings}")

    @property
    def file_tree(self) -> Optional[Tree]:
        """Get the file_tree property."""
        return self._file_tree
    @file_tree.setter
    def file_tree(self, value: Optional[Tree]) -> None:
        """Set the file_tree property."""
        if not isinstance(value, (Tree, type(None))):
            raise TypeError("file_tree must be a Tree instance or None.")
        self._file_tree = value

    #endregion BudManGUIView class properties
    #--------------------------------------------------------------------------+
    #endregion BudManGuiView class Intricsics
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region    BudManGUIView class methods
    def initialize(self) -> None:
        """Initialize the BudManGUIView class."""
        try:
            logger.info(f"BizEVENT: View setup for BudManGUIView({self._app_name}).")
            self.root.initialize()
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def run(self) -> p3m.CMD_RESULT_TYPE:
        """Run the BudManView application loop"""
        self.root.mainloop()
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_result_status=True,
            result_content_type=p3m.CMD_STRING_OUTPUT,
            result_content=f"BudManGuiApp run completed.",
            cmd_object=None
        )
        logger.debug(f"Finished BudManGuiApp.run()") # pragma: no cover
        return cmd_result

    #endregion    BudManGUIView class methods
    #--------------------------------------------------------------------------+
