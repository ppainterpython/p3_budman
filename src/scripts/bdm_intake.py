#------------------------------------------------------------------------------+
# bdm_intake.py - test some intake process functions.
#------------------------------------------------------------------------------+
import logging, io, sys
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, p3logging as p3l, pyjson5 as json5

# local modules and packages
from budman_settings import *
import budget_storage_model as bsm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
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
#region bdm_open_intake_file() function
def bdm_open_intake_file(file_path: Path):
    try:
        fieldnames = ["date", "amount", "ignore", "Original Description"]
        file_data: bdm.DATA_LIST_TYPE = bsm.csv_DATA_LIST_url_get(file_path, fieldnames=fieldnames)
        file_data2: bdm.DATA_LIST_TYPE = bsm.csv_DATA_LIST_add_header_row(file_data, fieldnames)
        # Remove unrequired columns for .csv_txns schema.
        file_data3: bdm.DATA_LIST_TYPE = bsm.csv_DATA_LIST_remove_columns(file_data2, "ignore")
        # Add missing columns with default values for .csv_txns schema.
        print(f"Count={len(file_data)}")

    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")
#endregion bdm_open_intake_file() function
# ---------------------------------------------------------------------------- +
if __name__ == "__main__":
    wb_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    cvs_url = "file:///C:/Users/ppain/OneDrive/budget/wellsfargo/raw_data/wellsfargo_Paul_Checking_20260410.csv"

    try:
        bdm_open_intake_file(cvs_url)
        # configure_logging(__name__, logtest=False)
        # logger.info(f"wb_path: '{wb_path}' url:'{wb_url}'")
        pass
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    logger.info(f"Complete.")

exit(0)
