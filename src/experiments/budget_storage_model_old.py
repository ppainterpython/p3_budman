# ---------------------------------------------------------------------------- +
#region    budget_storage_model.py module\
""" Implements data storage for Budget Domain Model.

    Keep it simple, use a JSONC file to store the budget domain model. Use a
    URL to reference it from other layers of application. Initially, the
    file scheme is supported for local files, but later it may be extended
    to support remote files or other storage mechanisms.

    No dependencies to other application layers.
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
from budman_namespace import BSM_PERSISTED_PROPERTIES
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_url_load() function
def bsm_BDM_STORE_url_load(bdms_url : str = None) -> Dict:
    """BSM: Load a BDM_STORE object as json from a URL.
    
    Entry point for a BDM_STORE file load operation. Parse the URL and decide
    how to load the BDM_STORE object based on the URL scheme. Parse the
    json content and return it as a dictionary.

    Args:
        bdms_url (str): The URL to the BDM_STORE object to load.
    """
    try:
        # bdms_url must be a non-empty string.
        p3u.is_non_empty_str("bdms_url", bdms_url, raise_error=True)
        # bdms_url must be a valid URL.
        try:
            parsed_url = urlparse(bdms_url)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise ValueError(f"store_url is not a valid URL: {bdms_url}")
        if not parsed_url.scheme:
            raise ValueError(f"store_url has no scheme: {bdms_url}")
        if parsed_url.scheme not in ["file", "http", "https"]:
            raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
        # If the scheme is file, load the BDM_STORE from a file.
        if parsed_url.scheme == "file":
            # Decode the URL and convert it to a Path object.
            bdms_path = Path.from_uri(bdms_url)
            logger.info(f"Loading BDM_STORE from path:'{bdms_path}' url:'{bdms_url}'")
            return bsm_BDM_STORE_file_load(bdms_path)
        raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_load() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_url_save() function
def bsm_BDM_STORE_url_save(budman_store:Dict, bdms_url : str = None) -> Dict:
    """BSM: Save the BDM_STORE object to jsonc data at the url.
    
    Convert the dictionary to json and save it to the url.

    Args:
        bdms_url (str): The URL to the BDM_STORE object to load.
    """
    try:
        # budman_store must be a dictionary.
        p3u.is_obj_of_type("budman_store", budman_store, Dict, raise_error=True)
        # store_url must be a non-empty string.
        p3u.is_non_empty_str("store_url", bdms_url, raise_error=True)
        # store_url must be a valid URL.
        try:
            parsed_url = urlparse(bdms_url)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise ValueError(f"store_url is not a valid URL: {bdms_url}")
        if not parsed_url.scheme:
            raise ValueError(f"store_url has no scheme: {bdms_url}")
        if parsed_url.scheme not in ["file", "http", "https"]:
            raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
        # If the scheme is file, load the BDM_STORE from a file.
        if parsed_url.scheme == "file":
            # Decode the URL and convert it to a Path object.
            bdms_path = Path.from_uri(bdms_url)
            logger.info(f"Loading BDM_STORE from path:'{bdms_path}' url:'{bdms_url}'")
            return bsm_BDM_STORE_file_save(bdms_path)
        raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_save() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_file_load() function
def bsm_BDM_STORE_file_load(bdms_path : Path = None) -> Dict:
    """Load a BDM_STORE file from the given Path value."""
    try:
        if bdms_path is None or not isinstance(bdms_path, Path):
            raise ValueError("bdms_path is None or not a Path object.")
        logger.info("loading BDM_STORE from a file.")
        if not bdms_path.exists():
            raise FileNotFoundError(f"BDM_URL path does not exist: {bdms_path}")
        if not bdms_path.is_file():
            raise ValueError(f"BDM_URL path is not a file: {bdms_path}")
        if not bdms_path.suffix == ".jsonc":
            raise ValueError(f"BDM_URL path is not a .jsonc file: {bdms_path}")
        with open(bdms_path, "r") as f:
            jsonc_content = json5.decode(f.read())
        if (jsonc_content is None or 
            not isinstance(jsonc_content, dict) or 
            len(jsonc_content) == 0):
            raise ValueError(f"BDM_URL content is None, not a Dict or empty.")
        logger.info(f"loaded BDM_URL content from file: {bdms_path}")
        return jsonc_content
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_load() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_file_save() function
def bsm_BDM_STORE_file_save(budman_store:Dict, bdms_path:Path) -> None:
    """Save the Budget Manager Store to a .jsonc file."""
    try:
        # budman_store must be a dictionary.
        p3u.is_obj_of_type("budman_store", budman_store, Dict, raise_error=True)
        # store_path must be a non-empty string.
        p3u.is_non_empty_str("bdms_path", bdms_path, raise_error=True)
        logger.info("Saving Budget Manager Store to file: '{bdms_path}'")
        # Only persist the properties in BDM_PERSISTED_PROPERTIES.
        filtered_bsm = {k: v for k, v in budman_store.items() if k in BSM_PERSISTED_PROPERTIES}
        jsonc_content = json5.encode(filtered_bsm)
        with open(bdms_path, "w") as f:
            f.write(jsonc_content)
        logger.info(f"Saved BDM_URL to file: {bdms_path}")
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
#endregion bsm_BDM_STORE_file_save() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_new module
def bsm_BDM_STORE_new(bdms_url : str = None) -> str:
    """Create a new budget storage model file."""
    try:
        st = p3u.start_timer()
        # bmt = BDMConfig(default=True)
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
        return None #str(bsm_store_abs_path)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_new module
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
#region    bsm_BDM_STORE_file_abs_path()
def bsm_BDM_STORE_file_abs_path(filename : str, filetype : str, folder : str  ) -> Path:
    """Construct a BDM_STORE abs_path."""
    try:
        full_filename = filename + filetype
        folder_abs_path = Path(folder).expanduser().resolve()
        full_abs_path = folder_abs_path / full_filename
        return full_abs_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_file_abs_path()
# ---------------------------------------------------------------------------- +
