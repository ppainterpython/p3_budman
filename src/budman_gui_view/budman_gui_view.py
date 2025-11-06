# ---------------------------------------------------------------------------- +
#region budman_gui_app.py module
""" budman_gui_app.py implements the class BudManGuiApp.

"""
#endregion budman_gui_app.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import cmd
import logging, os, getpass, time, copy
from typing import List, Optional, Type, Generator, Dict, Tuple, Any, TYPE_CHECKING
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from .budman_gui_style_registry  import StyleRegistry
from .budman_gui_window  import BudManGUIWindow
from .budman_gui_constants import *
import budman_namespace as bdm
import budman_settings as bdms
from budman_settings.budman_settings_constants import BUDMAN_CMD_HISTORY_FILENAME
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUIView(BudManAppDataContext_Binding,
                    p3m.CommandProcessor_Binding):
    """ Budget Manager GUI View class.
        The BudManGuiView class sets up and runs the BudManGuiView.
    """
    #region BudManGuiView class Intricsics
    #--------------------------------------------------------------------------+
    #region __init__() 
    def __init__(self, 
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 data_context : Optional[BudManAppDataContext_Binding] = None,
                 app_name : str = "P3 Budget Manager GUI View",
                 settings : Optional[bdms.BudManSettings] = None) -> None:
        self._app_name = app_name
        self._settings : bdms.BudManSettings = settings if settings else bdms.BudManSettings()
        self._current_cmd :Optional[str] = None
        self._save_on_exit : bool = True

        # Setup DataContext_Binding
        self.DC = data_context

        # Setup CommandProcessor_Binding 
        self.CP = command_processor

        # Setup the root window
        self.root: BudManGUIWindow = BudManGUIWindow(themename='cosmo',
                                                    command_processor=self.CP,
                                                    data_context=self.DC)
        logger.info(f"Initializing BudMan GUI View")
        logger.debug(f"BudManGUIView created")
    #endregion __init__()
    # ------------------------------------------------------------------------ +
    #region   BudManGUIView class properties
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
    #endregion BudManGUIView class properties
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
    #endregion BudManGuiView class Intricsics
    #--------------------------------------------------------------------------+
    # Event Handler Methods