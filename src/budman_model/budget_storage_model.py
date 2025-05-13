# ---------------------------------------------------------------------------- +
#region budget_storage_model.py module
""" budget_storage_model.py implements file system storage for class BudgetModel.
"""
#endregion budget_storagae_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import Dict

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
import pyjson5 as json5 
# local modules and packages
from .budget_model_constants import *
from .budget_domain_model import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
def bsm_BM_STORE_save(bm : "BudgetModel") -> None:
    """Save the BudgetModel store to a .jsonc file."""
    try:
        if bm is None or not isinstance(bm, BudgetModel):
            raise ValueError("BudgetModel is None or not a BudgetModel.")
        logger.info("Saving BudgetModel to file.")
        if not bm.bm_initialized:
            raise ValueError("BudgetModel is not initialized.")
        bm.bm_last_modified_by = getpass.getuser()
        bm.bm_last_modified_date = p3u.now_iso_date_string()
        # Get the budget_model store abs_path. Trust the setting in the
        # BudgetModel instance.
        file_path = bm.bsm_BM_STORE_abs_path()
        # Only persist the properties in BM_PERSISTED_PROPERTIES.
        filtered_bsm = {k: v for k, v in bm.__dict__.items() if k in BSM_PERSISTED_PROPERTIES}
        jsonc_content = json5.encode(filtered_bsm)
        with open(file_path, "w") as f:
            f.write(jsonc_content)
        logger.info(f"Saved BM_STORE to file: {file_path}")
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
# ---------------------------------------------------------------------------- +
def bsm_BM_STORE_load(bm : "BudgetModel") -> Dict:
    """Load BM_STORE from a .jsonc file, return as a Dict object."""
    try:
        if bm is None or not isinstance(bm, BudgetModel):
            raise ValueError("BudgetModel is None or not a BudgetModel.")
        logger.info("loading BM_STORE from a file.")
        store_abs_path = bm.bsm_BM_STORE_abs_path()
        if not store_abs_path.exists():
            raise FileNotFoundError(f"BM_STORE path does not exist: {store_abs_path}")
        if not store_abs_path.is_file():
            raise ValueError(f"BM_STORE path is not a file: {store_abs_path}")
        if not store_abs_path.suffix == ".jsonc":
            raise ValueError(f"BM_STORE path is not a .jsonc file: {store_abs_path}")
        with open(store_abs_path, "r") as f:
            jsonc_content = json5.decode(f.read())
        if (jsonc_content is None or 
            not isinstance(jsonc_content, dict) or 
            len(jsonc_content) == 0):
            raise ValueError(f"BM_STORE content is None, not a Dict or empty.")
        logger.info(f"loaded BM_STORE content from file: {store_abs_path}")
        return jsonc_content
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
# ---------------------------------------------------------------------------- +
def bsm_BM_STORE_abs_path(bm_folder : str = BM_DEFAULT_BUDGET_FOLDER) -> Path:
    """Construct the default store path."""
    try:
        bm_folder_path = Path(bm_folder).expanduser()
        bm_folder_abs_path = bm_folder_path.resolve()
        bm_store_abs_path = bm_folder_abs_path / BSM_DEFAULT_BUDGET_MODEL_FILE_NAME
        return bm_store_abs_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
# ---------------------------------------------------------------------------- +
