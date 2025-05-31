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
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# ---------------------------------------------------------------------------- +
# globals for logger
logger = logging.getLogger(__name__)
# globals for settings
BudManApp_settings : Dynaconf = None  # type: ignore
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class SingletonAppMeta(type):
    """Metaclass for implementing the Singleton pattern for subclasses."""
    _instances = {}

    # As a metaclass, __call__() runs when an instance is created as an
    # override to the normal __new__ method which is called by the type() 
    # metaclass for all python classes. So, call super() to use the normal
    # class behavior in addition to what SingletonMeta is doing.
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Runs only for the first instance of the cls (class).
            # Invokes cls.__new__(), then cls.__init__(), which constructs 
            # a new cls instance. By default, the type() metaclass does this.
            _new_inst = super().__call__(*args, **kwargs)
            # Apply the singleton pattern, one instance per class.
            cls._instances[cls] = _new_inst
            # Save the cls so code knows what subclass was instantiated.
            _new_inst._subclassname = cls.__name__
            logger.debug(f"Created first {dscr(_new_inst)}")
        logger.debug(f"Return {dscr(cls._instances[cls])}")
        return cls._instances[cls]
# ---------------------------------------------------------------------------- +
class BudManApp(metaclass=SingletonAppMeta): 
    """BudManApp: The main application class for the Budget Manager."""
    def __init__(self) -> None:
        """Initialize the BudManApp."""
        _settings : Dynaconf = BudManSettings()
        _cli_view: object = None  # type: ignore
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
        global BudManApp_settings
        BudManApp_settings = settings

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
    #region budman_app_setup() function
    def budman_app_setup(self,testmode:bool=False):
        """Assemble the application for startup."""
        try:
            # Delayed import to avoid circular imports and enable 
            # Dependency Injection (DI) of the BudManViewModel.
            from budman_view_model import (BudManViewModel, BudManCLIViewDataContext)
            from budman_cli_view import BudManCLIView

            # create and initialize view model
            bmvm = BudManViewModel()
            bmvm.initialize(load_user_store=True) # Initialize the BudgetModelCommandViewModel
            # create and initialize a data context, for the view model
            bm_cliview_dc = BudManCLIViewDataContext(bmvm)
            bm_cliview_dc.initialize(cp=bmvm.BMVM_execute_cmd,dc=bmvm.data_context) 
            # create and initialize the view
            self.cli_view = BudManCLIView(bm_cliview_dc).initialize()
            # Register exit handler
            atexit.register(self.budman_app_exit_handler)
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
    #region budman_app_exit_handler() function
    def budman_app_exit_handler(self):
        """start the cli repl loop."""
        try:
            m = f"Exiting {BudManApp.settings[APP_NAME]}..."
            logger.info(m)
            print(m)
        except Exception as e:
            m = exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_exit_handler() function
    # ------------------------------------------------------------------------ +
    #region run() function
    def run(self, testmode: bool = False, logtest : bool = False) -> None:
        """run budman_app."""
        try:
            if self.settings is None:
                raise ValueError("Settings not configured.")
            if not BudManApp_settings:
                raise ValueError("Settings not found or empty.")
            app_name = BudManApp_settings[APP_NAME] 
            self.configure_logging(app_name, logtest=True)  # Configure the logger
            self.app.budman_app_setup(testmode)  # Create the BudManApp instance
            self.app.budman_app_start(testmode)  # Create the BudManApp instance
        except Exception as e:
            m = exc_err_msg( e)
            logger.error(m)
        d = dscr(self)
        logger.info(f"{d} exiting {app_name} ...")
        exit(0)
    #endregion run() function
    # ------------------------------------------------------------------------ +
    #region configure_logging() method
    def configure_logging(self,logger_name : str, logtest : bool = False) -> None:
        """Setup the application logger."""
        global BudManApp_settings
        try:
            # Configure logging
            app_name = logger_name or BudManApp_settings[APP_NAME]
            log_config_file = "budget_model_logging_config.jsonc"
            _ = p3l.setup_logging(
                logger_name = logger_name,
                config_file = log_config_file
                )
            p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
            logger = logging.getLogger(app_name)
            logger.propagate = True
            logger.setLevel(logging.DEBUG)
            d = dscr(BudManApp())
            logger.info(f"+ {60 * '-'} +")
            logger.info(f"+ {d} running {app_name}...")
            logger.info(f"+ {60 * '-'} +")
            if(logtest): 
                p3l.quick_logging_test(app_name, log_config_file, reload = False)
        except Exception as e:
            logger.error(exc_err_msg(e))
            raise
    #endregion configure_logging() function
    # ------------------------------------------------------------------------ +
