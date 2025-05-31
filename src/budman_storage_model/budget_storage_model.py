# ---------------------------------------------------------------------------- +
#region    budget_storage_model.py module\
""" budget_storage_model.py implements file system storage for class BudgetModel.
"""
#endregion budget_storage_model.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
import pyjson5 as json5 
# local modules and packages
# from .budget_domain_model_config import BudgetDomainModelConfig
# from budman_app import *
# from budman_namespace import *
# from .budget_domain_model_identity import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_url_load() function
def bsm_BDM_STORE_url_load(store_url : str = None) -> Dict:
    """BSM: Load a BDM_STORE object from a URL.
    
    Entry point for a BDM_STORE file load operation. Parse the URL and decide
    how to load the BDM_STORE object based on the URL scheme.

    Args:
        store_url (str): The URL to the BDM_STORE object to load.
    """
    try:
        # store_url must be a non-empty string.
        p3u.is_non_empty_str(store_url, "store_url",raise_error=True)
        # store_url must be a valid URL.
        try:
            parsed_url = urlparse(store_url)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise ValueError(f"store_url is not a valid URL: {store_url}")
        if not parsed_url.scheme:
            raise ValueError(f"store_url has no scheme: {store_url}")
        if parsed_url.scheme not in ["file", "http", "https"]:
            raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
        # If the scheme is file, load the BDM_STORE from a file.
        if parsed_url.scheme == "file":
            # Decode the URL and convert it to a Path object.
            file_path = unquote(parsed_url.path)
            store_path = Path(file_path).expanduser().resolve()
            logger.info(f"Loading BDM_STORE from file: {store_path}")
            return bsm_BDM_STORE_load(store_path)
        raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_load() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_load() function
def bsm_BDM_STORE_load(store_path : Path = None) -> Dict:
    """Load a BDM_STORE file from the given Path value."""
    try:
        # store_path = bsm_BDM_STORE_abs_path() if store_path is None else store_path
        if store_path is None or not isinstance(store_path, Path):
            raise ValueError("store_path is None or not a Path object.")
        logger.info("loading BDM_STORE from a file.")
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
#endregion bsm_BDM_STORE_load() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_save() function
def bsm_BDM_STORE_save(budman_store:Dict, store_path:Path) -> None:
    """Save the Budget Manager Store to a .jsonc file."""
    try:
        if budman_store is None or not isinstance(budman_store, Dict):
            raise ValueError("budman_store is None or not a Dict.")
        logger.info("Saving Budget Manager Store to file: '{store_path}'")
        # Only persist the properties in BDM_PERSISTED_PROPERTIES.
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
#endregion bsm_BDM_STORE_save() function
# ---------------------------------------------------------------------------- +
#region    budget_storage_model_new module
def budget_storage_model_new(name : str, folder : str, filetype : str) -> str:
    """Create a new budget storage model file."""
    try:
        st = p3u.start_timer()
        # bmt = BudgetDomainModelConfig(default=True)
        # filename = name or bmt.bdm_filename
        # folder = folder or bmt.bdm_folder
        # filetype = filetype or bmt.bdm_filetype
        # logger.debug("Start: ...")
        # # Create a new budget storage model file.
        # bdm = BudgetDomainModelIdentity(filename=filename, filetype=filetype)
        # bsm_folder_path = Path(folder).expanduser()
        # bsm_folder_abs_path = bsm_folder_path.resolve()
        # bsm_store_abs_path = bsm_folder_abs_path / bdm.filename
        # if not os.path.exists(bsm_store_abs_path):
        #     with open(bsm_store_abs_path, "w") as f:
        #         f.write("{}")
        #     logger.info(f"Created new budget storage model file: {bsm_store_abs_path}")
        # else:
        #     logger.warning(f"Budget storage model file already exists: {bsm_store_abs_path}")
        logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        return str(bsm_store_abs_path)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion budget_storage_model_new module
# ---------------------------------------------------------------------------- +
#region verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
def bsm_verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool:
    """Verify the folder exists, create it if it does not exist.

    Args:
        ap (Path): The absolute path to the folder to verify.
        create (bool): Create the folder if it does not exist.
        raise_errors (bool): Raise errors if True.
    """
    try:
        if not ap.is_absolute():
            m = f"Path is not absolute: '{str(ap)}'"
            logger.error(m)
            raise ValueError(m)
        if ap.exists() and ap.is_dir():
            logger.debug(f"Folder exists: '{str(ap)}'")
            return True
        if not ap.exists():
            m = f"Folder does not exist: '{str(ap)}'"
            logger.error(m)
            if create:
                logger.info(f"Creating folder: '{str(ap)}'")
                ap.mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(m)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
# ---------------------------------------------------------------------------- +
#region    BDM_STORE path methods
def bsm_BDM_STORE_abs_path() -> Path:
    """Construct the default store path."""
    try:
        # Use the BDM_STORE configured in BUDMAN_SETTINGS.
        # TODO: This is not right, not based on current user but raw default 
        bmt = BudgetDomainModelConfig(default=True)
        budman_store_value = bmt.bdm_url
        budman_folder = bmt.bdm_folder
        budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
        budman_store_abs_path = budman_folder_abs_path / budman_store_value
        return None #budman_store_abs_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion BDM_STORE path methods
# ---------------------------------------------------------------------------- +
def bsm_BDM_URL_abs_path(bm_folder : str) -> Path:
    """Construct the default store path."""
    try:
        bmt = None #BudgetDomainModelConfig(default=True)
        bm_folder = bm_folder or bmt.bdm_folder
        bm_folder_path = Path(bm_folder).expanduser()
        bm_folder_abs_path = bm_folder_path.resolve()
        full_filename = bmt.bdm_filename + bmt.bdm_filetype
        bdm_url_abs_path = bm_folder_abs_path / full_filename
        return bdm_url_abs_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
# ---------------------------------------------------------------------------- +
