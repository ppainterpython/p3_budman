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
from typing import Optional

# third-party  packages and module libraries
import p3logging as p3l
from p3_utils import exc_err_msg, dscr, start_timer, stop_timer

# local packages and module libraries
from budman_settings import *
from budman_namespace import BDMSingletonMeta
from budman_view_model import (BudManViewModel, BudManCLICommandProcessor_Binding)
from budman_cli_view import BudManCLIView
from budget_domain_model import (BudgetDomainModel)
from budman_data_context import BDMDataContext
from budman_workflows import BDMTXNCategoryManager
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
    def __init__(self, app_settings : Optional[BudManSettings] = None, start_time:float=time.time()) -> None:
        """BudManApp__init__()."""
        self._model : Optional[object] = None  # type: ignore
        self._view : Optional[object] = None  # type: ignore
        self._view_model : Optional[object] = None  # type: ignore
        self._data_context : Optional[object] = None  # type: ignore
        self._command_processor : Optional[object] = None  # type: ignore
        self._WF_CATEGORY_MANAGER : Optional[object] = None  # type: ignore
        self._app_name : Optional[str] = None
        self._start_time : float = start_time
        self._settings : Optional[BudManSettings] = app_settings
        d = dscr(self)
        logger.debug(f"{d}.__init__() completed ...")
    # ------------------------------------------------------------------------ +
    @property
    def model(self) -> Optional[object]:
        """Return the model."""
        return self._model
    @model.setter
    def model(self, model: Optional[object]) -> None:
        """Set the model."""
        if not isinstance(model, object):
            raise TypeError("model must be an object")
        self._model = model

    @property
    def view(self) -> Optional[object]:
        """Return the view."""
        return self._view
    @view.setter
    def view(self, view_obj: Optional[object]) -> None:
        """Set the view."""
        if not isinstance(view_obj, object):
            raise TypeError("cli_view must be an object")
        self._view = view_obj 

    @property
    def view_model(self) -> Optional[object]:
        """Return the view mode."""
        return self._view_mode
    @view_model.setter
    def view_model(self, view_model: Optional[object]) -> None:
        """Set the view mode."""
        if not isinstance(view_model, object):
            raise TypeError("view_mode must be an object")
        self._view_mode = view_model

    @property
    def DC(self) -> Optional[object]:
        """Return the data context."""
        return self._data_context
    @DC.setter
    def DC(self, data_context: Optional[object]) -> None:
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
    def WF_CATEGORY_MANAGER(self) -> Optional[object]:
        """Return the registered workflow category manager.

        This is a property to register and share a reference to
        the WORKFLOW CATEGORY MANAGER service, which is needed
        by some workflow command processor implementations. It does not 
        impact the DC state but will reference values in the DC.
        """
        return self._WF_CATEGORY_MANAGER
    @WF_CATEGORY_MANAGER.setter
    def WF_CATEGORY_MANAGER(self, value: Optional[object]) -> None:
        """Set the registered workflow category manager."""
        if value is not None and not isinstance(value, object):
            raise TypeError("WF_CATEGORY_MANAGER must be an object instance or None")
        self._WF_CATEGORY_MANAGER = value

    @property
    def settings(self) -> Optional[BudManSettings]:
        """Return the application settings."""
        return self._settings
    @settings.setter
    def settings(self, settings: Optional[BudManSettings]) -> None:
        """Set the application settings."""
        if not isinstance(settings, BudManSettings):
            raise TypeError("settings must be a BudManSettings instance")
        self._settings = settings

    @property
    def app_name(self) -> Optional[str]:
        """Return the application name."""
        if self._app_name is None:
            self._app_name = self.settings.get(APP_NAME, "BudManApp")
        return self._app_name
    @app_name.setter
    def app_name(self, app_name: Optional[str]) -> None:
        """Set the application name."""
        if not isinstance(app_name, str):
            raise TypeError("app_name must be a string")
        self._app_name = app_name

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
            if self.view is None:
                raise ValueError("View not initialized.")
            self.view.cmdloop() if startup else None # Application CLI loop
            self.view_model.shutdown()
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
            self.view_model.shutdown()
            m = f"BizEVENT: Exiting application {self.settings[APP_NAME]}..."
            logger.info(m)
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_exit_handler() function
    # ------------------------------------------------------------------------ +
    #region budman_app_service_setup() function
    def budman_app_service_setup(self, bdms_url : str = None, testmode : bool = False):
        """Assemble the application for startup. Do Dependency Injection.
                
        Args:
            bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
            testmode (bool): If True, run in test mode.
        """
        try:
            logger.debug(f"Started: bdms_url = '{bdms_url}'...")
            # In our MVVM pattern design, the app_service is the VIEW_MODEL, 
            # MODEL, DATA_CONTEXT, and COMMAND_PROCESSOR.
            # Create the VIEW_MODEL, MODEL, DATA_CONTEXT and COMMAND_PROCESSOR,
            # independently, and then bind them together.
            # Start by creating the VIEW_MODEL.
            self.view_model = BudManViewModel(bdms_url, self.settings)
            # Next, create a MODEL. In our case, we use the VIEW_MODEL for that.
            self.model = self.view_model.initialize_model(bdms_url)
            # Next, bind the MODEL to the VIEW_MODEL.
            self.view_model.model = self.model
            # Next, create the DATA_CONTEXT for the VIEW_MODEL, using the
            # BDMWorkingData class.
            self.DC : BDMDataContext = BDMDataContext()
            # Next, create the workflow category manager service.
            self.WF_CATEGORY_MANAGER = BDMTXNCategoryManager(self.settings)
            # Stash it in the DC, a sort of service registry.
            self.DC.WF_CATEGORY_MANAGER = self.WF_CATEGORY_MANAGER
            # Next, bind the MODEL to the DATA_CONTEXT.
            self.DC.model = self.model
            # Next, initialize the DATA_CONTEXT.
            self.DC.dc_initialize() 
            self.DC.dc_INITIALIZED = True
            # Next, bind the DATA_CONTEXT to the VIEW_MODEL.
            self.view_model.DC = self.DC
            # Next, initialize the VIEW_MODEL.
            self.view_model.initialize()
            # This completes the app_service setup.
            logger.debug(f"Complete:")
            return self
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_service_setup() function
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
            # In our MVVM pattern design, the app_service is the VIEW_MODEL,
            # MODEL, DATA_CONTEXT and COMMAND_PROCESSOR.
            # So, first setup the app_service, which can work with different
            # VIEW implementations.
            _ = self.budman_app_service_setup(bdms_url, testmode)

            # Next, create the CommandProcessor_Binding (client) object.
            # TODO: convert BudManCLICommandProcessor_Binding to 
            # ViewModelCommandProcessor_Binding and have BudManCLIView
            # subclass that.
            self.CP = BudManCLICommandProcessor_Binding()
            # Next, bind the VIEW_MODEL as the concrete CommandProcessor_Base.
            # self.CP is this views binding to the CommandProcessor_Base. 
            # self.CP.CP is the function provided by the _Base to execute a 
            # command. The _Binding is a proxy to the _Base.
            self.CP.CP = self.view_model.cp_execute_cmd 
            # Next, create and initialize the VIEW and bind the CommandProcessor.
            self.view = BudManCLIView(self.CP,self.app_name,self.settings)
            # Bind the DATA_CONTEXT to the VIEW.
            self.view.DC = self.DC
            self.view.initialize() 
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
