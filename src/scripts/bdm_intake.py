#------------------------------------------------------------------------------+
# bdm_intake.py - test some intake process functions.
#------------------------------------------------------------------------------+
#region    Imports
import logging, io, sys
import csv
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, p3logging as p3l, pyjson5 as json5

# local modules and packages
from budman_settings import *
import budman_namespace.design_language_namespace as bdm
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
        output_path: Path = None
        fieldnames = ["date", "amount", "ignore1", "ignore2", "Original Description"]
        data_list: bdm.DATA_OBJECT_LIST_TYPE = None
        data_list2: bdm.DATA_OBJECT_LIST_TYPE = None
        data_list3: bdm.DATA_OBJECT_LIST_TYPE = None

        output_path = bsm.csv_DATA_LIST_file_validate_header(file_path, fieldnames)


        data_list = bsm.csv_DATA_LIST_url_get(file_path, return_type=bdm.DATA_OBJECT_LIST_TYPE)
        if not bsm.csv_DATA_LIST_has_header_row(data_list, fieldnames):
            logger.info(f"Header row is missing from the .csv file. "
                        f"Adding header row: {fieldnames}")
            data_list2 = bsm.csv_DATA_LIST_add_header_row(data_list, fieldnames)
        # Remove unrequired columns for .csv_txns schema.
        data_list3 = bsm.csv_DATA_LIST_remove_columns_by_name(data_list2, 
                                                              ["ignore1", "ignore2"])
        # Add missing columns with default values for .csv_txns schema.
        print(f"Count={len(data_list3)}")

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
    fieldnames = ["date", "amount", "ignore1", "ignore2", "Original Description"]

    try:
        cvs_path = Path.from_uri(cvs_url).expanduser().resolve()
        bdm_open_intake_file(cvs_path)
        # with open(cvs_path,"r",newline="",encoding='utf-8-sig') as f:
        #     reader = csv.reader(f, delimiter=',', skipinitialspace=True)
        #     data_row_list = list(reader)

        # with open(cvs_path,"r",newline="",encoding='utf-8-sig') as f:
        #     reader = csv.DictReader(f, skipinitialspace=True)
        #     data_row_dict: bdm.DATA_OBJECT_LIST_TYPE = list(reader)

        # configure_logging(__name__, logtest=False)
        # logger.info(f"wb_path: '{wb_path}' url:'{wb_url}'")
        pass
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    logger.info(f"Complete.")

exit(0)
