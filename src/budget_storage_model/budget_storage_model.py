# ---------------------------------------------------------------------------- +
#region    budget_storage_model.py module\
""" Implements data storage for Budget Domain Model.

    Keep it simple, use a JSONC file to load/save the budget domain model 
    DATA_OBJECTs from/to storage. The BDM_STORE object is a dictionary in 
    memory and a json file in storage. Use a URL to reference it from other 
    layers of application. Initially, the file scheme is supported for 
    local files, but later it may be extended to support other storage services.

    BSM only depends on the dict to json mapping, not detailed content structure
    is used beyond that for validation. BSM is not BDM-aware.

    No dependencies to other application layers. However, it does include
    the budman_namespace module for constants and type definitions, as a
    convenience for the application developer.

    June 15, 2025 - Happy Father's Day!
    
    # TODO: switch verbs to put/get from save/load, consistent with URL usage.
    # TODO: move back to std lib json module, jsonc
"""
#endregion budget_storage_model.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict, List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
import pyjson5 as json5 
# local modules and packages
from budman_namespace import (
    BSM_PERSISTED_PROPERTIES, BDM_STORE, VALID_BSM_BDM_STORE_FILETYPES,
    VALID_WB_FILETYPES)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_url_load() function
def bsm_BDM_STORE_url_load(bdms_url : str = None) -> BDM_STORE:
    """BSM: Load a BDM_STORE object from a URL.
    
    Entry point for a BDM_STORE file load operation. Parse the URL and decide
    how to load the BDM_STORE object based on the URL scheme. Decode the
    json content and return it as a dictionary.

    Args:
        bdms_url (str): The URL to the BDM_STORE object to load.
    """
    try:
        # bdms_url must be a non-empty string.
        p3u.is_non_empty_str("bdms_url", bdms_url, raise_error=True)
        # bdms_url must be a valid URL.
        parsed_url = urlparse(bdms_url)
        if not parsed_url.scheme:
            raise ValueError(f"Invalid URL has no scheme: {bdms_url}")
        if not parsed_url.path:
            raise ValueError(f"Invalid URL has no path: {bdms_url}")
        if parsed_url.scheme not in ["file", "http", "https"]:
            raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
        # If the scheme is file, load the BDM_STORE from a file.
        if parsed_url.scheme == "file":
            # Decode the URL and convert it to a Path object.
            bdms_path = Path.from_uri(bdms_url)
            logger.info(f"Loading BDM_STORE from path: '{bdms_path}' URL: '{bdms_url}'")
            return bsm_BDM_STORE_file_load(bdms_path)
        raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_load() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_url_save() function
def bsm_BDM_STORE_url_save(bdm_store:BDM_STORE, bdms_url : str = None) -> Dict:
    """BSM: Save the BDM_STORE object to storage at the url.
    
    Store the BDM_STORE dictionary with a storage service based on the url.

    Args:
        bdms_url (str): The URL to the BDM_STORE object to store.
    """
    try:
        # bdm_store must be a dictionary.
        p3u.is_obj_of_type("bdm_store", bdm_store, dict, raise_error=True)
        # store_url must be a non-empty string.
        p3u.is_non_empty_str("store_url", bdms_url, raise_error=True)
        # store_url must be a valid URL.
        try:
            parsed_url = urlparse(bdms_url)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise ValueError(f"Invalid URL: {bdms_url}")
        if not parsed_url.scheme:
            raise ValueError(f"store_url has no scheme: {bdms_url}")
        if parsed_url.scheme not in ["file", "http", "https"]:
            raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
        # If the scheme is file, load the BDM_STORE from a file.
        if parsed_url.scheme == "file":
            # Decode the URL into a Path object.
            bdms_path = Path.from_uri(bdms_url)
            logger.info(f"Loading BDM_STORE from path:'{bdms_path}' "
                        f"url:'{bdms_url}'")
            return bsm_BDM_STORE_file_save(bdm_store, bdms_path)
        raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_save() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_file_load() function
def bsm_BDM_STORE_file_load(bdms_path : Path = None) -> BDM_STORE:
    """Load a BDM_STORE file from the given Path value."""
    try:
        if bdms_path is None or not isinstance(bdms_path, Path):
            raise ValueError("bdms_path is None or not a Path object.")
        logger.info(f"Loading BDM_STORE from  file: '{bdms_path}'")
        if not bdms_path.exists():
            m = f"file does not exist: {bdms_path}"
            logger.error(m)
            raise FileNotFoundError(m)
        if not bdms_path.is_file():
            m = f"bdms_path is not a file: '{bdms_path}'"
            logger.error(m)
            raise ValueError(m)
        if not bdms_path.suffix in VALID_BSM_BDM_STORE_FILETYPES:
            m = f"bdms_path filetype is not supported: {bdms_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        if bdms_path.stat().st_size == 0:
            m = f"file is empty: {bdms_path}"
            logger.error(m)
            raise ValueError(m)
        with open(bdms_path, "r") as f:
            bdms_json : str = f.read()
            bdms_json_size = len(bdms_json)
            bdm_store_content = json5.decode(bdms_json,10)
        logger.info(f"Loaded '{bdms_json_size}' chars of json content from file: '{bdms_path}'")
        return bdm_store_content
    except json5.Json5DecoderException as e:
        logger.error(p3u.exc_err_msg(e))
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_file_load() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_file_save() function
def bsm_BDM_STORE_file_save(bdm_store:BDM_STORE, bdms_path:Path) -> None:
    """Save the Budget Manager Store to a .jsonc file."""
    try:
        # bdm_store must be a dictionary.
        p3u.is_obj_of_type("bdm_store", bdm_store, dict, raise_error=True)
        # store_path must be a non-empty string.
        p3u.is_obj_of_type("bdms_path", bdms_path, Path, raise_error=True)
        logger.info("Saving Budget Manager Store to file: '{bdms_path}'")
        # Only persist the properties in BDM_PERSISTED_PROPERTIES.
        filtered_bsm = {k: v for k, v in bdm_store.items() if k in BSM_PERSISTED_PROPERTIES}
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
#region    bsm_verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
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
#endregion bsm_verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
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
#region    bsm_get_workbook_names()
def bsm_get_workbook_names(abs_folder : Path) -> List[Path]:
    """Return list of workbook Paths from absolute folder path."""
    try:
        p3u.is_obj_of_type("wb_folder", abs_folder, Path, raise_error=True)
        # Get a list of Path objects for all .xlsx files in the folder.
        wb_paths = list(abs_folder.glob("*.xlsx"))
        if not wb_paths:
            logger.warning(f"No workbook files found in folder: {abs_folder}")
            return []
        filtered_wb_paths = bsm_filter_workbook_names(wb_paths)
        return filtered_wb_paths
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_get_workbook_names()
# ---------------------------------------------------------------------------- +
#region    bsm_get_workbook_names()
def bsm_get_workbook_names2(abs_folder : Path) -> List[Path]:
    """Return list of workbook Paths from absolute folder path."""
    try:
        p3u.is_obj_of_type("wb_folder", abs_folder, Path, raise_error=True)
        # Get a list of Path objects for all .xlsx files in the folder.
        wb_paths = []
        for filetype in VALID_WB_FILETYPES:
            my_glob = f"*{filetype}"
            filetype_paths = list(abs_folder.glob(my_glob))
            if not filetype_paths:
                logger.debug(f"No '{filetype}' files found in folder: {abs_folder}")
                continue
            wb_paths.extend(filetype_paths)
        filtered_wb_paths = bsm_filter_workbook_names(wb_paths)
        return filtered_wb_paths
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_get_workbook_names()
# ---------------------------------------------------------------------------- +
#region    bsm_filter_workbook_names()
def bsm_filter_workbook_names(wb_paths : List[Path]) -> List[Path]:
    """Filter out paths for invalid workbooks."""
    try:
        p3u.is_obj_of_type("wb_name_list", wb_paths, list, raise_error=True)
        if len(wb_paths) == 0:
            return []
        ret_list : List[Path] = []
        ret_list = [f for f in wb_paths if not f.name.startswith("~$")]
        return ret_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_filter_workbook_names()
# ---------------------------------------------------------------------------- +
