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
from .budget_domain_model import BudgetModel
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
def bsm_save(bm : BudgetModel) -> None:
    """Save the BudgetModel store to a .jsonc file."""
    try:
        if bm is None or not isinstance(bm, BudgetModel):
            raise ValueError("BudgetModel is None or not a BudgetModel.")
        logger.info("Saving BudgetModel to file.")
        if not bm.bm_initialized:
            raise ValueError("BudgetModel is not initialized.")
        bm.bm_last_modified_by = getpass.getuser()
        bm.bm_last_modified_date = p3u.now_iso_date_string()
        # Get the budget_model store path
        file_path = bm.bm_store
        if file_path is None:
            raise ValueError("BudgetModel store path is None.")
        jsonc_content = json5.dumps(bm, indent=4)
        with open(file_path, "w") as f:
            f.write(jsonc_content)
        logger.info(f"Saved BudgetModel to file: {file_path}")
        return None
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_msg(bsm_save, e))
        raise
    except Exception as e:
        logger.error(p3u.exc_msg(bsm_save, e))
        raise
# ---------------------------------------------------------------------------- +
def bsm_load(store_abs_path : Path) -> Dict:
    """Load the BudgetModel store from a .jsonc file."""
    try:
        logger.info("loading BudgetModel store from a file.")
        if store_abs_path is None or not isinstance(store_abs_path, Path):
            store_abs_path = bsm_bm_store_abs_path()
        if store_abs_path is None or not isinstance(store_abs_path, Path):
            raise ValueError("BudgetModel store path is None or not a Path.")
        if not store_abs_path.exists():
            raise ValueError(f"BudgetModel store path does not exist: {store_abs_path}")
        if not store_abs_path.is_file():
            raise ValueError(f"BudgetModel store path is not a file: {store_abs_path}")
        if not store_abs_path.suffix == ".jsonc":
            raise ValueError(f"BudgetModel store path is not a .jsonc file: {store_abs_path}")
        with open(store_abs_path, "r") as f:
            jsonc_content = json5.decode(f)
        logger.info(f"loaded BudgetModel store from file: {store_abs_path}")
        return jsonc_content
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
# ---------------------------------------------------------------------------- +
def bsm_bm_store_abs_path(bm_folder : str = BM_DEFAULT_BUDGET_FOLDER) -> Path:
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
