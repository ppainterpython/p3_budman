# ---------------------------------------------------------------------------- +
#region p3_budman.py The Budget Manager Application.
""" Budget Manager (BudMan) - an app to help users track a financial budget.

    This module is the main entry point for the BudMan application.
"""
#endregion p3_budman.py The Budget Manager Application.
# ---------------------------------------------------------------------------- +
#region Imports
# python standard libraries packages and modules 
import atexit, pathlib, time, logging, inspect, logging.config  #, logging.handlers
# third-party  packages and module libraries
import p3logging as p3l
from p3_utils import exc_err_msg, dscr, start_timer, stop_timer
# local packages and module libraries
from budman_settings import *
from budman_namespace import BDMSingletonMeta
from budman_view_model import (BudManViewModel, BudManCLICommandProcessor_Binding)
from budman_cli_view import BudManCLIView
from budget_domain_model import (BudgetDomainModel)
from budman_data_context import BDMWorkingData
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
    def __init__(self, app_settings : BudManSettings = None, start_time:float=time.time()) -> None:
        """BudManApp__init__()."""
        self._settings : BudManSettings = app_settings
        self._cli_view : object = None  # type: ignore
        self._view_model : object = None  # type: ignore
        self._model : object = None  # type: ignore
        self._data_context : object = None  # type: ignore
        self._command_processor : object = None  # type: ignore
        self._app_name : str = None
        self._start_time : float = start_time
        d = dscr(self)
        logger.debug(f"{d}.__init__() completed ...")
    # ------------------------------------------------------------------------ +
    @property
    def settings(self) -> BudManSettings:
        """Return the application settings."""
        return self._settings
    @settings.setter
    def settings(self, settings: BudManSettings) -> None:
        """Set the application settings."""
        if not isinstance(settings, BudManSettings):
            raise TypeError("settings must be a BudManSettings instance")
        self._settings = settings

    @property
    def view_model(self) -> object:
        """Return the view mode."""
        return self._view_mode
    @view_model.setter
    def view_model(self, view_model: object) -> None:
        """Set the view mode."""
        if not isinstance(view_model, object):
            raise TypeError("view_mode must be an object")
        self._view_mode = view_model

    @property
    def model(self) -> object:
        """Return the model."""
        return self._model
    @model.setter
    def model(self, model: object) -> None:
        """Set the model."""
        if not isinstance(model, object):
            raise TypeError("model must be an object")
        self._model = model

    @property
    def DC(self) -> object:
        """Return the data context."""
        return self._data_context
    @DC.setter
    def DC(self, data_context: object) -> None:
        """Set the data context."""
        if not isinstance(data_context, object):
            raise TypeError("data_context must be an object")
        self._data_context = data_context

    @property
    def CP(self) -> object:
        """Return the command processor."""
        return self._command_processor
    @CP.setter
    def CP(self, command_processor: object) -> None:
        """Set the command processor."""
        if not isinstance(command_processor, object):
            raise TypeError("command_processor must be an object")
        self._command_processor = command_processor

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

    @property
    def start_time(self) -> float:
        """Return the application start time."""
        return self._start_time
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
            m = f"BizEVENT: Exiting application {self.settings[APP_NAME]}..."
            logger.info(m)
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_exit_handler() function
    # ------------------------------------------------------------------------ +
    #region budman_app_service() function
    def budman_app_service(self, bdms_url : str = None, testmode : bool = False):
        """Assemble the application for startup. Do Dependency Injection.
                
        Args:
            bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
            testmode (bool): If True, run in test mode.
        """
        try:
            logger.debug(f"Started: bdms_url = '{bdms_url}'...")
            # In our MVVM pattern design, the app_service is the ViewModel,
            # data context and command processor.
            # Create the ViewModel, Model, DataContext and CommandProcessor,
            # independently, and then bind them together.
            # Start by creating the ViewModel.
            self.view_model = BudManViewModel(bdms_url, self.settings)
            # Next, create a model. In our case, we use the ViewModel for that.
            self.model = self.view_model.initialize_model(bdms_url)
            # Next, bind the model to the ViewModel.
            self.view_model.model = self.model
            # Next, create the Data Context for the ViewModel.
            self.DC : BDMWorkingData = BDMWorkingData()
            # Next, bind the model to the data context.
            self.DC.model = self.model
            # Next, initialize the data context.
            self.DC.dc_initialize() 
            self.DC.dc_INITIALIZED = True
            # Next, bind the data context to the ViewModel.
            self.view_model.DC = self.DC
            # Next, initialize the ViewModel.
            self.view_model.initialize()
            # Next, create the CommandProcessor_Binding object.
            cli_cp = BudManCLICommandProcessor_Binding()
            # Next, bind the view_model as the CommandProcessor_Base.
            cli_cp.CP = self.view_model.cp_execute_cmd 
            logger.debug(f"Complete:")
            return self
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_service() function
    # ------------------------------------------------------------------------ +
    #region budman_app_setup() function
    def budman_app_setup(self, bdms_url : str = None, testmode : bool = False):
        """Assemble the application for startup. Do Dependency Injection.
                
        Args:
            bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
            testmode (bool): If True, run in test mode.
        """
        try:
            logger.debug(f"Started: bdms_url = '{bdms_url}'...")
            # In our MVVM pattern design, the app_service is the ViewModel,
            # data context and command processor.
            _ = self.budman_app_service(bdms_url, testmode)
            # Next, create and initialize the view and bind the CommandProcessor.
            self.cli_view = BudManCLIView(self.CP,self.app_name,self.settings)
            self.cli_view.initialize() 
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
            logger.debug(f"{self.settings[APP_NAME]} application initialization "
                           f"complete {stop_timer(self.start_time)} seconds.")
            logger.info(f"BizEVENT: Entering user input command loop.")
            self.budman_app_cli_cmdloop(startup=startup) # Application CLI loop
            logger.info(f"BizEVENT: Exit from user input command loop.")
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
            logger.debug(f"Started: {self.app_name} bdms_url = '{bdms_url}'...")
            self.budman_app_setup(bdms_url, testmode)  # Create the BudManApp instance
            self.budman_app_start(testmode)  # Create the BudManApp instance
            logger.debug(f"Complete:")
        except Exception as e:
            m = exc_err_msg( e)
            logger.error(m)
        d = dscr(self)
        logger.info(f"{d} exiting ...")
    #endregion run() function
    # ------------------------------------------------------------------------ +
