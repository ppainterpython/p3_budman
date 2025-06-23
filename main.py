# ---------------------------------------------------------------------------- +
#region main.py (at project root) DudMan main entry point.
"""Budget Manager (BudMan) - a p3 application.

Author: Paul Painter
Copyright (c) 2025 Paul Painter
"""
#endregion main.py (at project root) DudMan main entry point.
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import sys, logging
from pathlib import Path
from dynaconf import Dynaconf
import p3logging as p3l
from p3_utils import exc_err_msg, dscr, start_timer, stop_timer
from budman_settings.budman_settings_constants import *
from budman_settings.budman_settings import BudManSettings
from src.budman_app.budman_app import BudManApp
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
app_start_time : float = start_timer()
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
    except Exception as e:
        logger.error(exc_err_msg(e))
        raise
#endregion configure_logging() function
# ---------------------------------------------------------------------------- +
#region backlog - main todo list
"""Main todo list for the Budget Manager application.

    TODO: refactor WORKBOOKS and LOADED_WORKBOOKS in a single DATA_COLLECTION
    with objects storing the WB_INFO such as loaded, in excel, abs_path, wb_name

    TODO: Convert the WORKBOOK_DATA_LIST to DATA_COLLECTION from DATA_TUPLE_LIST. And
    refine the FI_WF, WF_DATA_OBJECT, FI_DATA naming to just DATA_OBJECT. 
    DATA_OBJECTs are association with an fi_key, wf_key, and wb_type.

    TODO: Change BudManDataContext to use BDM_STORE if loaded to respond

    TODO: handle the same WB_NAME being in several wf folders.

    TODO: Consider making BudManDataContext have a binding for Model and 
    ViewModel objects. As a concrete implementation, it provides model and 
    view_model properties. Consider some of the dc_methods conditionally
    forwarding calls onto the model or view_model properties, if the methods
    are available on those objects.
"""
#endregion backlog - main todo list
# ---------------------------------------------------------------------------- +
def main(bdms_url : str = None):
    """Main entry point for the Budget Manager application.
    Args:
        bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
    """
    try:
        # TODO: modify to use BudManSettings() for user_settings, not app.
        # Define a set of folders to search for it, auto-load.
        BudManMain_settings : Dynaconf = BudManSettings().settings
        if BudManMain_settings is None:
                raise ValueError("BudMan Settings not configured.")
        app_name = BudManMain_settings.get(APP_NAME, "BudManApp")
        configure_logging(app_name, logtest=False)
        fs = ""  # from settings 
        if bdms_url is None:
            bdms_url = BudManMain_settings[BDM_STORE_URL]
            fs ="(from settings) "
        logger.info(f"BizEVENT: Started {app_name} User BDM_STORE {fs}bdms_url = '{bdms_url}'...")
        app = BudManApp(BudManMain_settings)
        logger.debug(f"{dscr(app)} created. ...")
        app.run(bdms_url)  # Start the application
        logger.debug(f"Complete:")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    bdms_url = None #"file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    main(bdms_url)
    logger.info(f"BizEVENT: {Path(__file__).name} completed successfully "
                f"in {stop_timer(app_start_time)} seconds.")
    exit(0)
