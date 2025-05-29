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
import p3logging as p3l, p3_utils as p3u
# local packages and module libraries

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# ---------------------------------------------------------------------------- +
# Application Constants
THIS_APP_NAME = "p3_budget_manager" 
THIS_APP_SHORT_NAME = "budman" 
THIS_APP_VERSION = "0.3.0"
THIS_APP_AUTHOR = "Paul Painter"
THIS_APP_COPYRIGHT = "2025 Paul Painter"
# ---------------------------------------------------------------------------- +
# BUDMAN_SETTINGS property name constants used in settings.toml configuration file
BUDMAN_SETTINGS = "settings.toml"
BUDMAN_FOLDER = "budman.folder" 
BUDMAN_STORE = "budman.store_filename" 
BUDMAN_STORE_FILETYPE = "budman.store_filetype"
BUDMAN_DEFAULT_FI = "budman.default_fi"
BUDMAN_DEFAULT_WORKFLOW = "budman.default_workflow"
BUDMAN_DEFAULT_WORKBOOK_TYPE = "budman.default_workbook_type"
APP_NAME = "app_name"
SHORT_APP_NAME = "short_app_name"
# globals for logger
logger = logging.getLogger(THIS_APP_NAME)
# globals for settings
BudManApp_settings : Dynaconf = None  # type: ignore
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
def dscr(_inst) -> str:
    try:
        if _inst is None: return "None"
        _id = hex(id(_inst))
        _cn = _inst.__class__.__name__
        return f"<instance '{_cn}':{_id}>"
    except Exception as e:
        return f"{type(e).__name__}()"
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
        cli_view: object = None  # type: ignore
        d = dscr(self)
        logger.info(f"{d}.__init__() completed ...")
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
            m = p3u.exc_err_msg(e)
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
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_setup() function
    # ------------------------------------------------------------------------- +
    #region budman_app_start() function
    def budman_app_start(self,testmode:bool=False):
        """start the cli repl loop."""
        try:
            startup = not testmode
            self.budman_app_cli_cmdloop(startup=startup) # Application CLI loop
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_start() function
    # ------------------------------------------------------------------------- +
    #region budman_app_exit_handler() function
    def budman_app_exit_handler(self):
        """start the cli repl loop."""
        try:
            m = f"Exiting {BudManApp.settings[APP_NAME]}..."
            logger.info(m)
            print(m)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion budman_app_exit_handler() function
# ---------------------------------------------------------------------------- +
#region configure_logging() function
def configure_logging(logger_name : str, logtest : bool = False) -> None:
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
        logger.info("+ -----------------------------------------------------"
                    "------------ +")
        logger.info(f"+ {d} running {app_name}...")
        logger.info("+ -----------------------------------------------------"
                    "------------ +")
        if(logtest): 
            p3l.quick_logging_test(app_name, log_config_file, reload = False)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion configure_logging() function
# ------------------------------------------------------------------------ +
#region configure_settings() function
def configure_settings() -> None:
    """Setup the application settings."""
    global BudManApp_settings
    try:
        # Configure settings

        if not BudManApp_settings:
            BudManApp_settings = Dynaconf(
                envvar_prefix="DYNACONF",
                settings_files=[BUDMAN_SETTINGS, '.secrets.toml'],
            )
        d = dscr(BudManApp())
        print(f"{d} initialized settings: {BudManApp_settings.to_dict()}")
    except Exception as e:
        print(p3u.exc_err_msg(e))
        raise
#endregion configure_settings() function
# ------------------------------------------------------------------------ +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        configure_settings()  # Configure the settings
        if not BudManApp_settings:
            raise ValueError("Settings not found or empty.")
        app_name = BudManApp_settings[APP_NAME] 
        configure_logging(THIS_APP_NAME, logtest=True)  # Configure the logger
        app = BudManApp()
        app.budman_app_setup()  # Create the BudManApp instance
        app.budman_app_start()  # Create the BudManApp instance
    except Exception as e:
        m = p3u.exc_err_msg( e)
        logger.error(m)
    d = dscr(app)
    logger.info(f"{d} exiting {app_name} ...")
    exit(0)
#endregion Local __main__ stand-alone
# ---------------------------------------------------------------------------- +
#region tryit() function
def tryit() -> None:
    """Try something."""
    try:
        result = inspect.stack()[1][3]
        print(f"result: '{result}'")
    except Exception as e:
        print(f"Error: tryit(): {str(e)}")
#endregion tryit() function
# ---------------------------------------------------------------------------- +
