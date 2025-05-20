# ---------------------------------------------------------------------------- +
#region    budget_storage_model.py module\
""" budget_storage_model.py implements file system storage for class BudgetModel.
"""
#endregion budget_storagae_model.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time
from pathlib import Path
from typing import Dict

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l
import pyjson5 as json5 
# local modules and packages
from .budget_model_constants import *
from .budget_domain_model_identity import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(settings[APP_NAME])
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region    bsm_BUDMAN_STORE_load() function
def bsm_BUDMAN_STORE_load(store_path : Path = None) -> Dict:
    """Load a BUDMAN_STORE file from the given Path value."""
    try:
        store_path = bsm_BUDMAN_STORE_abs_path() if store_path is None else store_path
        if store_path is None or not isinstance(store_path, Path):
            raise ValueError("store_path is None or not a Path object.")
        logger.info("loading BUDMAN_STORE from a file.")
        if not store_path.exists():
            raise FileNotFoundError(f"BDM_URL path does not exist: {store_path}")
        if not store_path.is_file():
            raise ValueError(f"BDM_URL path is not a file: {store_path}")
        if not store_path.suffix == ".jsonc":
            raise ValueError(f"BDM_URL path is not a .jsonc file: {store_path}")
        with open(store_path, "r") as f:
            jsonc_content = json5.decode(f.read())
        if (jsonc_content is None or 
            not isinstance(jsonc_content, dict) or 
            len(jsonc_content) == 0):
            raise ValueError(f"BDM_URL content is None, not a Dict or empty.")
        logger.info(f"loaded BDM_URL content from file: {store_path}")
        return jsonc_content
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BUDMAN_STORE_load() function
# ---------------------------------------------------------------------------- +
#region    budget_storage_model_new module
def budget_storage_model_new(name : str = BSM_DEFAULT_BUDGET_MODEL_FILE_NAME,
                             folder : str = BM_DEFAULT_BUDGET_FOLDER,
                             filetype : str = BSM_DEFAULT_BUDGET_MODEL_FILE_TYPE) -> str:
    """Create a new budget storage model file."""
    try:
        st = p3u.start_timer()
        logger.debug("Start: ...")
        # Create a new budget storage model file.
        bdm = BudgetDomainModelIdentity(filename=name, filetype=filetype)
        bsm_folder_path = Path(folder).expanduser()
        bsm_folder_abs_path = bsm_folder_path.resolve()
        bsm_store_abs_path = bsm_folder_abs_path / bdm.filename
        if not os.path.exists(bsm_store_abs_path):
            with open(bsm_store_abs_path, "w") as f:
                f.write("{}")
            logger.info(f"Created new budget storage model file: {bsm_store_abs_path}")
        else:
            logger.warning(f"Budget storage model file already exists: {bsm_store_abs_path}")
        logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        return str(bsm_store_abs_path)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion budget_storage_model_new module
# ---------------------------------------------------------------------------- +
#region    bsm_BUDMAN_STORE_save() function
def bsm_BUDMAN_STORE_save(budman_store:Dict, store_path:Path) -> None:
    """Save the Budget Manager Store to a .jsonc file."""
    try:
        if budman_store is None or not isinstance(budman_store, Dict):
            raise ValueError("budman_store is None or not a Dict.")
        logger.info("Saving Budget Manager Store to file.")
        # Only persist the properties in BM_PERSISTED_PROPERTIES.
        filtered_bsm = {k: v for k, v in budman_store.items() if k in BSM_PERSISTED_PROPERTIES}
        jsonc_content = json5.encode(filtered_bsm)
        with open(store_path, "w") as f:
            f.write(jsonc_content)
        logger.info(f"Saved BDM_URL to file: {store_path}")
        return None
    except json5.Json5UnstringifiableType as e:
        logger.error(p3u.exc_err_msg(e))
        logger.error(f"Unstringifiable type: {type(e.unstringifiable).__name__} value: '{str(e.unstringifiable)}'")
        raise
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BUDMAN_STORE_save() function
# ---------------------------------------------------------------------------- +
#region    BUDMAN_STORE path methods
def bsm_BUDMAN_STORE_abs_path() -> Path:
    """Construct the default store path."""
    try:
        # Use the BUDMAN_STORE configured in BUDMAN_SETTINGS.
        budman_store_value = settings[BUDMAN_STORE]
        budman_folder = settings[BUDMAN_FOLDER]
        budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
        budman_store_abs_path = budman_folder_abs_path / budman_store_value
        return budman_store_abs_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion BUDMAN_STORE path methods
# ---------------------------------------------------------------------------- +
# def bsm_BDM_URL_save(bm : "BudgetModel") -> None:
#     """Save the BudgetModel store to a .jsonc file."""
#     try:
#         if bm is None or not isinstance(bm, BudgetModel):
#             raise ValueError("BudgetModel is None or not a BudgetModel.")
#         logger.info("Saving BudgetModel to file.")
#         if not bm.bm_initialized:
#             raise ValueError("BudgetModel is not initialized.")
#         bm.bm_last_modified_by = getpass.getuser()
#         bm.bm_last_modified_date = p3u.now_iso_date_string()
#         # Get the budget_model store abs_path. Trust the setting in the
#         # BudgetModel instance.
#         file_path = bm.bsm_BDM_URL_abs_path()
#         # Only persist the properties in BM_PERSISTED_PROPERTIES.
#         filtered_bsm = {k: v for k, v in bm.__dict__.items() if k in BSM_PERSISTED_PROPERTIES}
#         jsonc_content = json5.encode(filtered_bsm)
#         with open(file_path, "w") as f:
#             f.write(jsonc_content)
#         logger.info(f"Saved BDM_URL to file: {file_path}")
#         return None
#     except json5.Json5UnstringifiableType as e:
#         logger.error(p3u.exc_err_msg(e))
#         logger.error(f"Unstringifiable type: {type(e.unstringifiable).__name__} value: '{str(e.unstringifiable)}'")
#         raise
#     except json5.Json5DecoderException as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
# ---------------------------------------------------------------------------- +
# def bsm_BDM_URL_load(bm : "BudgetModel") -> Dict:
#     """Load BDM_URL from a .jsonc file, return as a Dict object."""
#     try:
#         if bm is None or not isinstance(bm, BudgetModel):
#             raise ValueError("BudgetModel is None or not a BudgetModel.")
#         logger.info("loading BDM_URL from a file.")
#         store_abs_path = bm.bsm_BDM_URL_abs_path()
#         if not store_abs_path.exists():
#             raise FileNotFoundError(f"BDM_URL path does not exist: {store_abs_path}")
#         if not store_abs_path.is_file():
#             raise ValueError(f"BDM_URL path is not a file: {store_abs_path}")
#         if not store_abs_path.suffix == ".jsonc":
#             raise ValueError(f"BDM_URL path is not a .jsonc file: {store_abs_path}")
#         with open(store_abs_path, "r") as f:
#             jsonc_content = json5.decode(f.read())
#         if (jsonc_content is None or 
#             not isinstance(jsonc_content, dict) or 
#             len(jsonc_content) == 0):
#             raise ValueError(f"BDM_URL content is None, not a Dict or empty.")
#         logger.info(f"loaded BDM_URL content from file: {store_abs_path}")
#         return jsonc_content
#     except json5.Json5DecoderException as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
# ---------------------------------------------------------------------------- +
def bsm_BDM_URL_abs_path(bm_folder : str = BM_DEFAULT_BUDGET_FOLDER) -> Path:
    """Construct the default store path."""
    try:
        bm_folder_path = Path(bm_folder).expanduser()
        bm_folder_abs_path = bm_folder_path.resolve()
        bdm_url_abs_path = bm_folder_abs_path / BSM_DEFAULT_BUDGET_MODEL_FILE_NAME
        return bdm_url_abs_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
# ---------------------------------------------------------------------------- +
