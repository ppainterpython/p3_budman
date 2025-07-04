#------------------------------------------------------------------------------+
# fooey.py - a place to fool around with experiments, not a dependent.
#------------------------------------------------------------------------------+
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l, pyjson5 as json5
# local modules and packages
# from budman_namespace import *
from budman_namespace import (
    BDM_STORE, BDM_FOLDER, BDM_FI_COLLECTION,
    FI_WORKBOOK_DATA_COLLECTION,
    FI_WORKFLOW_DATA_COLLECTION, FI_NAME, FI_FOLDER,BDM_WF_COLLECTION,
    WF_INPUT_FOLDER,WF_WORKING_FOLDER, WF_OUTPUT_FOLDER,WF_NAME,
    WF_INPUT, WF_WORKING, WF_OUTPUT, WF_PURPOSE_FOLDER_MAP, BDM_DATA_CONTEXT
    )
from budget_storage_model import bsm_BDM_STORE_url_get, bsm_BDM_STORE_url_put
from budman_namespace.bdm_workbook_class import BDMWorkbook
# from budman_workflows.budget_category_mapping import extract_category_tree
#endregion Imports
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
# ------------------------------------------------------------------------ +
#region bdm_tree() function
def bdm_tree():
    wb_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    cr_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/CheckRegister_ToDate20250609.csv"
    try:
        wb_path = p3u.verify_url_file_path(cr_url, test=False)
        # wb_path.parent  = abs_path to the parent directory
        # wb_path.stem = filename
        # wb_path.suffix = filetype
        # wb_path.name = full_filename
        # path mapping:  
        # BDM: FI: bdm_id / fi_folder(fi_key) / fi_data_coll(wf_key) / workbook_list(wf_purpose) / (wb_name.wb_type, wb_url)
        # bsm:   '~/budget/'              'boa/'                                        'data/new/' data.xlsx
        #      WF: bdm_id \ wf_key \  wf_folder(wf_purpose) \ wb_name.wb_type
        #bdm_folder
        #
        bdms = bsm_BDM_STORE_url_get(wb_url)
        fi_folders = list(bdms[BDM_FI_COLLECTION].keys())     
        bdm_folder = bdms[BDM_FOLDER]
        all_paths = []
        fi_col = bdms[BDM_FI_COLLECTION]
        wf_col = bdms[BDM_WF_COLLECTION]
        for fi_key, fi_obj in bdms[BDM_FI_COLLECTION].items():
            fi_folder = fi_obj[FI_FOLDER]
            fi_name = fi_obj[FI_NAME]
            print(f"'{fi_folder}' [{fi_key}]'{fi_name}'")
            if fi_obj[FI_WORKFLOW_DATA_COLLECTION] is None:
                logger.warning(f"FI_DATA_COLLECTION is None for FI_KEY: {fi_key}")
                continue
            for wf_key, data_obj in fi_obj[FI_WORKFLOW_DATA_COLLECTION].items():
                wf_obj = wf_col[wf_key]
                wf_name = wf_obj[WF_NAME] 
                # print(f"  '{wf_key}' wf_name: '{wf_obj[WF_NAME]}'")
                wf_folders = {}
                wf_folders[WF_INPUT] = wf_obj[WF_INPUT_FOLDER]
                wf_folders[WF_WORKING] = wf_obj[WF_WORKING_FOLDER]
                wf_folders[WF_OUTPUT] = wf_obj[WF_OUTPUT_FOLDER]
                for wf_purpose, tuple_list in data_obj.items():
                    f = wf_folders[wf_purpose]
                    tm = wf_obj[WF_PURPOSE_FOLDER_MAP][wf_purpose]
                    print(f"  '{f}' [{wf_key}]'{tm}' ")
                    for tup in tuple_list:
                        print(f"     '{tup[0]}' wb_path: {tup[1]}")


        logger.info(f"wb_path: '{wb_path}' url:'{wb_url}'")

    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")
#endregion bdm_tree() function
# ------------------------------------------------------------------------ +
#region bdm_store_change() function
def bdm_store_change(bdms:BDM_STORE):
    try:
        # change key from '0' to 'wf_folder' + '|' + 'wb_name'
        # change 'loaded' to 'wb_loaded'


        # wb_path.parent  = abs_path to the parent directory
        # wb_path.stem = filename
        # wb_path.suffix = filetype
        # wb_path.name = full_filename
        # path mapping:  
        # BDM: FI: bdm_id / fi_folder(fi_key) / fi_data_coll(wf_key) / workbook_list(wf_purpose) / (wb_name.wb_type, wb_url)
        # bsm:   '~/budget/'              'boa/'                                        'data/new/' data.xlsx
        #      WF: bdm_id \ wf_key \  wf_folder(wf_purpose) \ wb_name.wb_type
        #bdm_folder
        #
        if (BDM_FI_COLLECTION in bdms and
            bdms[BDM_FI_COLLECTION] is not None and
            isinstance(bdms[BDM_FI_COLLECTION], dict) and 
            len(bdms[BDM_FI_COLLECTION]) > 0):
            for fi_key, fi_object in bdms[BDM_FI_COLLECTION].items():
                if not isinstance(fi_object, dict):
                    continue
                if (FI_WORKBOOK_DATA_COLLECTION not in fi_object or
                    fi_object[FI_WORKBOOK_DATA_COLLECTION] is None or
                    not isinstance(fi_object[FI_WORKBOOK_DATA_COLLECTION], dict) or
                    len(fi_object[FI_WORKBOOK_DATA_COLLECTION]) == 0):
                    continue
                wdc = fi_object[FI_WORKBOOK_DATA_COLLECTION]
                for wb_index, wb_data in wdc.items():
                    if not isinstance(wb_data, dict):
                        continue
                    if 'loaded' in wb_data:
                        # Change 'loaded' to 'wb_loaded'
                        wb_data['wb_loaded'] = wb_data.pop('loaded')
                    if 'wb_index' in wb_data:
                        del wb_data['wb_index']
                    # Convert the WORKBOOK_ITEM to a WORKBOOK_OBJECT.
                    wb_object = BDMWorkbook(**wb_data)
                    # Replace the DATA_OBJECT with the WORKBOOK_OBJECT.
                    # Use wb_id as the key, no longer the int for wb_index
                    del wdc[wb_index]
                    wb_id = wb_object.wb_id
                    wdc[wb_id] = wb_object

    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")
#endregion bdm_store_change() function
# ------------------------------------------------------------------------ +

if __name__ == "__main__":
    wb_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    cr_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/CheckRegister_ToDate20250609.csv"
    try:
        configure_logging(__name__, logtest=False)

        bdm_tree()
        # wb_path = p3u.verify_url_file_path(cr_url, test=False)
        # bdms = bsm_BDM_STORE_url_get(wb_url)
        # bdm_store_change(bdms)
        # bsm_BDM_STORE_url_put(bdms, wb_url)
        # logger.info(f"wb_path: '{wb_path}' url:'{wb_url}'")

    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")

exit(0)
#region attic
    # bdms_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    # try:
    #     bdms_json = bsm_BDM_STORE_url_load(bdms_url)
    #     parsed_url = urlparse(bdms_url)
    # except Exception as e:
    #     logger.error(p3u.exc_err_msg(e))
    #     raise ValueError(f"store_url is not a valid URL: {bdms_url}")
    # if not parsed_url.scheme:
    #     raise ValueError(f"store_url has no scheme: {bdms_url}")
    # if parsed_url.scheme not in ["file", "http", "https"]:
    #     raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
    # # If the scheme is file, load the BDM_STORE from a file.
    # if parsed_url.scheme == "file":
    #     # Decode the URL and convert it to a Path object.
    #     bdms_path = Path.from_uri(bdms_url)
    #     print(f"Loading BDM_STORE from path:'{bdms_path}' url:'{bdms_url}'")
    #     j = bsm_BDM_STORE_file_load(bdms_path)
    # # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    # print(f"complete")
# ---------------------------------------------------------------------------- +
# def bsm_BDM_STORE_url_load_foo(store_url : str = None) -> Dict:
#     """BSM: Load a BDM_STORE object from a URL.
    
#     Entry point for a BDM_STORE file load operation. Parse the URL and decide
#     how to load the BDM_STORE object based on the URL scheme.

#     Args:
#         store_url (str): The URL to the BDM_STORE object to load.
#     """
#     try:
#         # store_url must be a non-empty string.
#         p3u.is_non_empty_str(store_url, "store_url",raise_error=True)
#         # store_url must be a valid URL.
#         try:
#             parsed_url = urlparse(store_url)
#         except Exception as e:
#             logger.error(p3u.exc_err_msg(e))
#             raise ValueError(f"store_url is not a valid URL: {store_url}")
#         if not parsed_url.scheme:
#             raise ValueError(f"store_url has no scheme: {store_url}")
#         if parsed_url.scheme not in ["file", "http", "https"]:
#             raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
#         # If the scheme is file, load the BDM_STORE from a file.
#         if parsed_url.scheme == "file":
#             # Decode the URL and convert it to a Path object.
#             file_path = unquote(parsed_url.path)
#             store_path = Path(file_path).expanduser().resolve()
#             logger.info(f"Loading BDM_STORE from file: {store_path}")
#             return {} #bsm_BDM_STORE_load(store_path)
#         raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
#     # except json5.Json5DecoderException as e:
#     #     logger.error(p3u.exc_err_msg(e))
#     #     raise
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#endregion attic