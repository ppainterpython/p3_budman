# ---------------------------------------------------------------------------- +
#region p3_budman.py The Budget Manager Application.
""" Budget Manager (BudMan) - an app to help users track a financial budget.

    This module is the main entry point for the BudMan application.
"""
#endregion p3_budman.py The Budget Manager Application.
# ---------------------------------------------------------------------------- +
#region Imports
# python standard libraries packages and modules 
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers
# third-party  packages and module libraries
from dynaconf import Dynaconf
import p3logging as p3l
from p3_utils import exc_err_msg, dscr
# local packages and module libraries
from budman_settings import *
from budman_namespace import BDMSingletonMeta
from budman_view_model import (BudManViewModel, BudManCLIViewDataContext)
from budman_cli_view import BudManCLIView
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# ---------------------------------------------------------------------------- +
# globals for logger
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManApp(metaclass=BDMSingletonMeta): 
    """BudManApp: The main application class for the Budget Manager."""
    # ------------------------------------------------------------------------ +
    # region Class Properties    
    def __init__(self, app_settings : Dynaconf = None) -> None:
        """BudManApp__init__()."""
        self._settings : Dynaconf = app_settings
        self._cli_view: object = None  # type: ignore
        self._app_name: str = None
        d = dscr(self)
        logger.info(f"{d}.__init__() completed ...")
    # ------------------------------------------------------------------------ +
    @property
    def settings(self) -> Dynaconf:
        """Return the application settings."""
        return self._settings
    @settings.setter
    def settings(self, settings: Dynaconf) -> None:
        """Set the application settings."""
        if not isinstance(settings, Dynaconf):
            raise TypeError("settings must be a Dynaconf instance")
        self._settings = settings

    @property
    def app_name(self) -> str:
        """Return the application name."""
        if self._app_name is None:
            self._app_name = self.settings.get(APP_NAME, "BudManApp")
        return self._app_name
    @app_name.setter
    def app_name(self, app_name: str) -> None:
        """Set the application name."""
        if not isinstance(app_name, str):
            raise TypeError("app_name must be a string")
        self._app_name = app_name

    @property
    def cli_view(self) -> object:
        """Return the CLI view."""
        return self._cli_view
    @cli_view.setter
    def cli_view(self, cli_view: object) -> None:
        """Set the CLI view."""
        if not isinstance(cli_view, object):
            raise TypeError("cli_view must be an object")
        self._cli_view = cli_view  
    #endregion Class Properties
    # ------------------------------------------------------------------------ +
    #region budman_app_cli_cmdloop() function
    def budman_app_cli_cmdloop(self, startup : bool = True) -> None:
        """CLI cmdloop function."""
        try:
            # startup the view or not
            if not hasattr(self, 'cli_view') or self.cli_view is None:
                raise ValueError("CLI View not initialized. Call budman_app_setup() first.")
            self.cli_view.cmdloop() if startup else None # Application CLI loop
            _ = "pause"
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_cli_cmdloop() function
    # ------------------------------------------------------------------------ +
    #region budman_app_exit_handler() function
    def budman_app_exit_handler(self):
        """start the cli repl loop."""
        try:
            m = f"Exiting {self.settings[APP_NAME]}..."
            logger.info(m)
            print(m)
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_exit_handler() function
    # ------------------------------------------------------------------------ +
    #region budman_app_setup() function
    def budman_app_setup(self, bdms_url : str = None, testmode : bool = False):
        """Assemble the application for startup.
                
        Args:
            bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
            testmode (bool): If True, run in test mode.
        """
        try:
            # create and initialize view model
            logger.debug(f"Started: bdms_url = '{bdms_url}'...")
            bmvm = BudManViewModel(bdms_url, self.settings)
            bmvm.initialize(load_user_store=True) # Initialize the BudgetModelCommandViewModel
            # create and initialize a data context, for the view model
            bm_cliview_dc = BudManCLIViewDataContext(bmvm)
            bm_cliview_dc.initialize(cp=bmvm.cp_execute_cmd,dc=bmvm.data_context) 
            # create and initialize the view
            self.cli_view = BudManCLIView(bm_cliview_dc).initialize()
            # Register exit handler
            atexit.register(self.budman_app_exit_handler)
            logger.debug(f"Complete:")
            return self
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_setup() function
    # ------------------------------------------------------------------------ +
    #region budman_app_start() function
    def budman_app_start(self,testmode:bool=False):
        """start the cli repl loop."""
        try:
            startup = not testmode
            self.budman_app_cli_cmdloop(startup=startup) # Application CLI loop
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_start() function
    # ------------------------------------------------------------------------ +
    #region run() function
    def run(self, 
            bdms_url : str = None, 
            testmode: bool = False, 
            logtest : bool = False) -> None:
        """run budman_app.

        Args:
            bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
            testmode (bool): If True, run in test mode.
            logtest (bool): If True, run a logging test.
        """
        try:
            if self.settings is None:
                raise ValueError("Settings not configured.")
            self.app_name = self.settings.get(APP_NAME, "BudManApp")
            logger.info(f"Started: {self.app_name} bdms_url = '{bdms_url}'...")
            self.budman_app_setup(bdms_url, testmode)  # Create the BudManApp instance
            self.budman_app_start(testmode)  # Create the BudManApp instance
            logger.debug(f"Complete:")
        except Exception as e:
            m = exc_err_msg( e)
            logger.error(m)
        d = dscr(self)
        logger.info(f"{d} exiting ...")
        exit(0)
    #endregion run() function
    # ------------------------------------------------------------------------ +
