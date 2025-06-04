#------------------------------------------------------------------------------+
#region show_categories.py - list the Budget Categories
"""Show the current Budget Categories."""
#endregion show_categories.py - list the Budget Categories
#------------------------------------------------------------------------------+
#region Imports
# python standard libraries packages and modules
import logging, sys, io
from pathlib import Path
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
# local modules and packages
from src.budget_domain_model.budget_category_mapping import extract_category_tree
#endregion Imports
sys.path.append("./src")
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ------------------------------------------------------------------------ +
#region configure_logging() method
def configure_logging(logger_name : str = __name__, logtest : bool = False) -> None:
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
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion configure_logging() function
# ---------------------------------------------------------------------------- +
#region set_log_level() method
def set_log_level(handler_name : str = 'stdout', level:int=logging.INFO) -> None:
    """Set log level for the named Handler."""
    try:
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if handler.name == handler_name:
                handler.setLevel(level)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion configure_logging() function
# ---------------------------------------------------------------------------- +
if __name__ == "__main__":
    try:
        configure_logging(__name__, logtest=False)
        set_log_level('stdout', logging.CRITICAL) 
        level = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        filename = f"level_{level}_categories.txt"
        output = extract_category_tree(level)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output) 
        print(output)
        print("Categories written to file:", filename)
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    print("Complete.")
    logger.info(f"Complete.")

exit(0)
