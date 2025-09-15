# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import sys, logging, toml, re
from pathlib import Path
import p3logging as p3l
from p3_utils import exc_err_msg, dscr, start_timer, stop_timer
from budman_settings.budman_settings_constants import *
from budman_settings.budman_settings import BudManSettings
from budman_cli_view import (BudManCLIView, budman_cli_parser, budman_cli_view, 
                                budman_cli_view)
from budman_namespace import BDMWorkbook
from p3_mvvm import CommandProcessor, DataContext
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
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
def setup() -> BudManSettings:
    try:
        msg = f"Setup() started: "
        # Define a set of folders to search for it, auto-load.
        settings : BudManSettings = BudManSettings()
        if settings is None:
                raise ValueError("BudMan Settings not configured.")
        configure_logging(__name__, logtest=False)
        logger.debug(msg)
        logger.debug(f"Settings and logger configured: ")
        logger.debug(f"Setup() complete:")
        return settings
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

def main(bdms_url : str = None) -> None:
    """Main entry point for this script.
    Args:
        bdms_url (str): Optional, the URL to BDM_STORE to load at startup.
    """
    try:
        msg = f"Started: "
        # Define a set of folders to search for it, auto-load.
        settings : BudManSettings = setup()
        new_wb: BDMWorkbook = BDMWorkbook()
        logger.debug(f"Complete:")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
# ---------------------------------------------------------------------------- +
if __name__ == "__main__":
    bdms_url = None #"file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    main(bdms_url)
    print(f"bdms_url = {bdms_url}")
    exit(0)
