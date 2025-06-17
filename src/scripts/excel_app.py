#------------------------------------------------------------------------------+
# excel_app.py - learn about working with excel through win32com.client.
#------------------------------------------------------------------------------+
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict
import win32com.client as win32
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
# local modules and packages
# from budman_namespace import *
from budget_storage_model.csv_data_collection import csv_DATA_COLLECTION_url_get
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
cvs_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/CheckRegister_ToDate20250609.csv"
if __name__ == "__main__":
    try:
        configure_logging(__name__, logtest=False)
        data_col = csv_DATA_COLLECTION_url_get(cvs_url)
        print(f"Data Collection URL: {cvs_url}")
    except Exception as e:
        m = p3u.exc_err_msg(e)
        print(m)
        print("No open Excel workbooks detected.")
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    print(f"Complete.")
exit(0)
# ---------------------------------------------------------------------------- +
#region attic
# if __name__ == "__main__":
#     try:
#         # configure_logging(__name__, logtest=False)
#         st = p3u.start_timer()
#         wb_name = 'categorized_May2025_ALL.xlsx'
#         excel = win32.GetActiveObject("Excel.Application")
#         ewbs = excel.Workbooks
#         for wb in ewbs:
#             # wb.Name, wb.Author, wb.FullName is abs_path, wb.Path is to Folder, 
#             # wb.wb_name is the full file name.
#             print(f"Workbook: {wb.Name}, Author: {wb.Author}, FullName: {wb.FullName}, Path: {wb.Path}")
#         wb_names = [wb.Name for wb in ewbs]
#         if wb_name in wb_names:
#             print(f"Workbook '{wb_name}' is already open in Excel.")
#         print(f"Open Excel Workbooks: {wb_names}")
#         print(f"Complete: {p3u.stop_timer(st)}")
#     except Exception as e:
#         m = p3u.exc_err_msg(e)
#         print(m)
#         print("No open Excel workbooks detected.")
#     # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
#     print(f"Complete.")
# exit(0)
# ---------------------------------------------------------------------------- +
# if __name__ == "__main__":
#     # bdms_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
#     try:
#         configure_logging(__name__, logtest=False)
#         root_logger = logging.getLogger()
#         for handler in root_logger.handlers:
#             print(f"Handler: {type(handler).__name__}('{handler.name}'), Level: {logging.getLevelName(handler.level)}")
#             if handler.name == 'stdout':
#                 handler.setLevel(logging.CRITICAL)
#         output = extract_category_tree()

#     except Exception as e:
#         m = p3u.exc_err_msg(e)
#         logger.error(m)
#     # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
#     logger.info(f"Complete.")

# exit(0)

#endregion attic