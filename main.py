# ---------------------------------------------------------------------------- +
#region main.py (at project root) DudMan main entry point.
"""Budget Manager (BudMan) - a p3 application.

Author: Paul Painter
Copyright (c) 2025 Paul Painter
"""
import time
app_start_time : float = time.time()  # Start time for the application
#endregion main.py (at project root) DudMan main entry point.
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import sys, logging
from pathlib import Path
# third-party modules and packages
from rich.console import Console
import p3logging as p3l
from p3_utils import exc_err_msg, dscr, start_timer, stop_timer
# local modules and packages
import budman_namespace as bdm
from budman_settings.budman_settings_constants import *
from budman_settings.budman_settings import BudManSettings
from src.budman_app.budman_app import BudManApp
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
sys.stdout.reconfigure(encoding='utf-8')  # Ensure stdout uses UTF-8 encoding
console = Console(force_terminal=True, width=bdm.BUDMAN_WIDTH, highlight=True,
                  soft_wrap=False)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region configure_logging() method
def configure_logging(logger_name : str, logtest : bool = True) -> None:
    """Setup the application logger."""
    try:
        # Configure logging
        log_config_file = "budget_model_logging_config.jsonc"
        _ = p3l.setup_logging(
            logger_name = logger_name,
            config_file = log_config_file
            )
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger = logging.getLogger(logger_name)
        logger.propagate = True
        logger.setLevel(logging.DEBUG)
        prog = Path(__file__).name
        logger.info(f"+ {60 * '-'} +")
        logger.info(f"+ running {prog}({logger_name}) ...")
        logger.info(f"+ {60 * '-'} +")
        if(logtest): 
            p3l.quick_logging_test(logger_name, log_config_file, reload = False)

        root_logger = logging.getLogger()  # or logging.getLogger("root")
        console.print("Logging configuration:")
        for handler in root_logger.handlers:
            console.print(f"  Handler: '{handler.name}' {handler}, Level: {handler.level}, Type: {type(handler)}")
    except Exception as e:
        logger.error(exc_err_msg(e))
        raise
#endregion configure_logging() function
# ---------------------------------------------------------------------------- +
#region backlog - main todo list
"""Main todo list for the Budget Manager application.

    TODO: refactor WORKBOOKS and LOADED_WORKBOOKS in a single DATA_COLLECTION
    with objects storing the WB_INFO such as loaded, in excel, abs_path, wb_name

    TODO: handle the same WB_NAME being in several wf folders.

"""
#endregion backlog - main todo list
# ---------------------------------------------------------------------------- +
def main(bdms_url : str = None, start_time:float = start_timer()) -> None:
    """Main entry point for the Budget Manager application.
    Args:
        bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
        start_time (float): Optional, the start time for the application.
    """
    try:
        msg = f"Started: {stop_timer(start_time)}"
        # Define a set of folders to search for it, auto-load.
        BudManMain_settings : BudManSettings = BudManSettings()
        if BudManMain_settings is None:
                raise ValueError("BudMan Settings not configured.")
        app_name = BudManMain_settings.get(APP_NAME, "BudManApp")
        configure_logging(app_name, logtest=False)
        logger.debug(msg)
        logger.debug(f"Settings and logger configured: {stop_timer(start_time)}")
        fs = ""  # from settings 
        if bdms_url is None:
            bdms_url = BudManMain_settings[BDM_STORE_URL]
            fs ="(from settings) "
        logger.info(f"BizEVENT: Started {app_name} User BDM_STORE {fs}bdms_url = '{bdms_url}'...")
        app = BudManApp(BudManMain_settings,start_time)
        logger.debug(f"{dscr(app)} created. ...")
        app.run(bdms_url)  # Start the application
        logger.debug(f"Complete:")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    bdms_url = None #"file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    main(bdms_url,start_time=app_start_time)
    logger.info(f"BizEVENT: {Path(__file__).name} completed successfully "
                f"in {stop_timer(app_start_time)} seconds.")
    exit(0)
