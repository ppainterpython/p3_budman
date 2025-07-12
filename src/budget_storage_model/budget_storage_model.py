# ---------------------------------------------------------------------------- +
#region    budget_storage_model.py module
""" Implements Budget Domain Storage Model (BSM).

    Need to update: filetypes and wb_types

    In the BDM, the basic unit of storage is the BDM_WORKBOOK, which is a
    data file in a storage system, contained in folders (directories). The
    BSM translates the Domain Model view of BDM_WORKBOOKS to the underlying
    storage service specifications. The local file system and various cloud 
    storage services are where the mapping will go. BSM depends on the 
    BDMWorkbook class, from the design language namespace. BDMWorkbook
    holds metadata about the workbook. It has a wb_url attribute that links it
    to the storage service.

    A BDM_WORKBOOK has a wb_type, wb_filename and wb_filetype, which influences
    the implementation to load/save its content from/to storage.
    There are no dependencies to other application functional layers. However,
     it does include the design language namespace module for constants and 
    type definitions, as a convenience for the application developer.

    BSM presents a layered interface. 
    
    First, there is access to workbook storage via the BDM_WORKBOOK itself, 
    which contains the wb_url, wb_type etc. From that information, the secondary
    layers are used to route the request. This first layer has a method naming
    convention like: BDM_WORKBOOK_content_load() and BDM_WORKBOOK_content_save().
    A critical design constraint for layer one is that the caller bears the
    responsibility to ensure the BDM_WORKBOOK is valid and accounted for in the
    higher layers of the application.

    Second, there is a wb_url get/put layer which uses the actual content data
    in conjunction with the wb_type as arguments to route the request. This
    second layer has a method naming convention like:
    BDM_WORKBOOK_content_url_get() and BDM_WORKBOOK_content_url_put().

    Third, there is the layer to support a given storage service. Presently, 
    the BSM is supporting the local file system only. So absolute pathnames are
    used to read/write files. This third layer has a method naming convention
    like: excel_WORKBOOK_file_load() and excel_WORKBOOK_file_save().

    June 15, 2025 - Happy Father's Day!
    
    # TODO: move back to std lib json module, jsonc
"""
#endregion budget_storage_model.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time, toml
from pathlib import Path
from urllib.parse import urlparse, urlunparse, urlsplit, ParseResult
from typing import Dict, List, Any, Union

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
import pyjson5 as json5, json
import openpyxl
from openpyxl import Workbook, load_workbook
# local modules and packages
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budget_storage_model.csv_data_collection import (
    csv_DATA_LIST_url_get, csv_DATA_LIST_url_put,
    csv_DATA_LIST_file_load, csv_DATA_LIST_file_save
    )
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#                                                                              +
#region Layer 1 - BDM_WORKBOOK storage functions                               +
#                                                                              +
# ---------------------------------------------------------------------------- +
#region BSM Layer 1 Design Notes
"""
    Layer 1 - BDM_WORKBOOK storage functions - The BDM_WORKBOOK attributes must
    contain wb_url, wb_type, wb_filename, and wb_filetype. That information is
    used to map the load or save request to the appropriate Level 2 request. 
"""
#endregion BSM Layer 1 Design Notes
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_WORKBOOK_load() 
def bsm_BDM_WORKBOOK_load(bdm_wb:BDMWorkbook) -> bdm.WORKBOOK_CONTENT:
    """Load the BDM_WORKBOOK content from its storage service.

    A BDMWorkbook has content, stored elsewhere, and metadata kept in the
    BDM_STORE.

    Args:
        bdm_wb (BDMWorkbook): The workbook object to load content for.

    Returns:
        Any: The loaded workbook content object.
    """
    try:
        st: float = p3u.start_timer()
        logger.debug(f"Start:")
        p3u.is_not_obj_of_type("bdm_wb", bdm_wb, BDMWorkbook, raise_error=True)
        logger.debug(f"Loading BDM_WORKBOOK content for WB_ID('{bdm_wb.wb_id}') ")
        bdm_wb.wb_content = bsm_WORKBOOK_CONTENT_url_get(bdm_wb.wb_url, bdm_wb.wb_type)
        bdm_wb.wb_loaded = True
        logger.debug(f"Complete: {p3u.stop_timer(st)}")
        return bdm_wb.wb_content
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_WORKBOOK_load()
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_WORKBOOK_save()
def bsm_BDM_WORKBOOK_save(bdm_wb:BDMWorkbook) -> None:
    """
    Save the BDM_WORKBOOK content to its storage service.
    
    """
    try:
        st: float = p3u.start_timer()
        logger.debug(f"Start:")
        p3u.is_not_obj_of_type("bdm_wb", bdm_wb, BDMWorkbook, raise_error=True)
        logger.debug(f"Saving BDM_WORKBOOK content for WB_ID('{bdm_wb.wb_id}') ")
        bsm_WORKBOOK_CONTENT_url_put(bdm_wb.wb_content,bdm_wb.wb_url, bdm_wb.wb_type)
        bdm_wb.wb_loaded = True
        logger.debug(f"Complete: {p3u.stop_timer(st)}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_WORKBOOK_save()
# ---------------------------------------------------------------------------- +
#                                                                              +
#endregion Layer 1 - BDM_WORKBOOK storage functions
#                                                                              +
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#                                                                              +
#region Layer 2 - WB_URL, WB_TYPE storage functions                                       +
#                                                                              +
# ---------------------------------------------------------------------------- +
#region BSM Layer 2 Design Notes
"""
    Layer 2 - WB_URL, WB_TYPE storage functions - The WB_URL and WB_TYPE
    parameters must be present in the request to properly process the
    requests to the appropriate storage functions.
"""
#endregion BSM Layer 2  Design Notes
# ---------------------------------------------------------------------------- +
#region    bsm_WORKBOOK_CONTENT_url_get() function
def bsm_WORKBOOK_CONTENT_url_get(wb_content_url: str, 
                                     wb_type: str) -> bdm.WORKBOOK_CONTENT:
    """BSM: Load a WORKBOOK_OBJECT from storage by URL.

    Layer 2 point getting wb_content from a storage service. Parse the URL to 
    decide how to route the request to an appropriate storage service.

    Args:
        wb_content_url (str): The URL to the WORKBOOK_CONTENT object to GET.
        wb_type (str): The type of the workbook to load.

    Returns:
        Any: The loaded workbook content object. Will be a type associated
        with the given wb_type.
    """
    try:
        st: float = p3u.start_timer()
        logger.debug(f"Start:")
        # Validate the URL and wb_type. Raises error if not valid.
        bsm_WB_URL_TYPE_validate(wb_content_url, wb_type)
        # All is good, wb_type compatible with wb_content_url.
        # Since right now we only support file:// URLs, proceed on that basis.
        wb_content_abs_path: Path = bsm_WB_URL_verify_file_scheme(wb_content_url, 
                                                                  test=True)
        logger.debug(f"Loading WORKBOOK_CONTENT from path: "
                     f"'{wb_content_abs_path}' for URL: '{wb_content_url}'")
        wb_content: bdm.WORKBOOK_CONTENT = None
        wb_content = bsm_WORKBOOK_CONTENT_file_load(wb_content_abs_path, 
                                                    wb_type,
                                                    pre_validated=True)
        logger.debug(f"Complete: {p3u.stop_timer(st)}")
        return wb_content
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WORKBOOK_CONTENT_url_get() function
# ---------------------------------------------------------------------------- +
#region bsm_WORKBOOK_CONTENT_url_put() function
def bsm_WORKBOOK_CONTENT_url_put(wb_content: bdm.WORKBOOK_CONTENT, 
                                   wb_content_url: str, 
                                   wb_type: str) -> None:
    """BSM: Save a WORKBOOK_OBJECT to storage by URL.

    Layer 2 point putting wb_content to a storage service. Parse the URL to 
    decide how to route the request to an appropriate storage service.

    Args:
        wb_content (WORKBOOK_OBJECT): The workbook content object to PUT.
        wb_content_url (str): The URL to the WORKBOOK_CONTENT object to PUT.
        wb_type (str): The type of the workbook to save.

    Returns:
        None
    """
    try:
        st: float = p3u.start_timer()
        logger.debug(f"Start:")
        # Validate the URL and wb_type. Raises error if not valid.
        bsm_WB_URL_TYPE_validate(wb_content_url, wb_type)
        # All is good, wb_type compatible with wb_content_url.
        # Since right now we only support file:// URLs, proceed on that basis.
        wb_content_abs_path: Path = bsm_WB_URL_verify_file_scheme(wb_content_url,
                                                                  test=False)
        logger.debug(f"Saving WORKBOOK_CONTENT to path: "
                     f"'{wb_content_abs_path}' for URL: '{wb_content_url}'")
        bsm_WORKBOOK_CONTENT_file_save(wb_content, wb_content_abs_path, wb_type,
                                       pre_validated=True)
        logger.debug(f"Complete: {p3u.stop_timer(st)}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WORKBOOK_CONTENT_url_put() function
# ---------------------------------------------------------------------------- +
#endregion Layer 2 - WB_URL, WB_TYPE storage functions
#                                                                              +
# ---------------------------------------------------------------------------- +


# ---------------------------------------------------------------------------- +
#                                                                              +
#region Layer 3 - abs_path filesystem storage functions                                       +
#                                                                              +
# ---------------------------------------------------------------------------- +
#region BSM Layer 3 Design Notes
"""
    Layer 3 - abs_path filesystem storage functions - The wb_content_abs_path
    must be a valid file path on the local filesystem. The wb_type must be
    a valid workbook type.
"""
#endregion BSM Layer 3 Design Notes
#region    bsm_WORKBOOK_CONTENT_file_load(wb_abs_path : str = None) -> Any
def bsm_WORKBOOK_CONTENT_file_load(wb_content_abs_path:Path, 
                                   wb_type: str,
                                   pre_validated:bool=False) -> bdm.WORKBOOK_CONTENT:
    """Load a wb_content file of a given wb_type.

    BSM Layer 3: This is a local file system service function, loading a 
    workbook's data content into memory.

    Args:
        wb_content_abs_path (Path): The path of the workbook file to load.
        wb_type (str): The type of the workbook to load.
        pre_validated (bool): If True, the input parameters are already validated.

    Returns:
        WORKBOOK_CONTENT: The loaded wb_content.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Start:")

        logger.debug(f"BSM Local Filesystem: Loading WORKBOOK_CONTENT file: "
                     f"'{wb_content_abs_path}'")
        if not pre_validated:
            # Validate the wb_content_abs_path is a Path object.
            p3u.is_obj_of_type("wb_content_abs_path", wb_content_abs_path, Path, 
                               raise_error=True)
            p3u.verify_file_path_for_load(wb_content_abs_path)
            ...
        # Depending on the wb_type, route the request to actual implementation
        # for the wb_type, wb_filetype.
        wb_content: bdm.WORKBOOK_CONTENT = None
        if wb_type in [bdm.WB_TYPE_BDM_STORE, bdm.WB_TYPE_BDM_CONFIG]:
            # WB_TYPE_BDM_STORE, WB_TYPE_BDM_CONFIG: Load it as a json file.
            with open(wb_content_abs_path, "r") as f:
                wb_content = json5.decode(f.read(),10)
        elif wb_type == bdm.WB_TYPE_TXN_REGISTER:
            # WB_TYPE_TXN_REGISTER: Load it as a CSV file.
            wb_content = csv_DATA_LIST_file_load(wb_content_abs_path)
        elif wb_type == bdm.WB_TYPE_EXCEL_TXNS:
            # WB_TYPE_EXCEL_TXNS: Load it as an Excel file.
            wb_content = openpyxl.load_workbook(filename=wb_content_abs_path)
        elif wb_type == bdm.WB_TYPE_CSV_TXNS:
            # WB_TYPE_CSV_TXNS: Load it as a CSV file.
            wb_content = csv_DATA_LIST_file_load(wb_content_abs_path)
        elif wb_type == bdm.WB_TYPE_TXN_CATEGORIES:
            # WB_TYPE_TXN_CATEGORIES: Load it as a JSON file.
            with open(wb_content_abs_path, "r") as f:
                wb_content = json5.decode(f.read(),10)
        elif wb_type == bdm.WB_TYPE_CATEGORY_MAP:
            # WB_TYPE_CATEGORY_MAP, load it as a TOML file.
            with open(wb_content_abs_path, "r") as f:
                wb_content = toml.load(f)
        else: 
            # wb_type == bdm.WB_TYPE_BUDGET: # or anything else unknown
            m = f"Unsupported wb_type: '{wb_type}' for file: '{wb_content_abs_path}'"
            logger.error(m)
            raise ValueError(m)
        logger.debug(f"Complete: {p3u.stop_timer(st)}")
        return wb_content
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WORKBOOK_CONTENT_file_load(wb_abs_path : str = None) -> Any
# ---------------------------------------------------------------------------- +
#region    bsm_WORKBOOK_content_file_save(wb:Workbook,wb_abs_path : str = None) -> Any
def bsm_WORKBOOK_CONTENT_file_save(wb_content:bdm.WORKBOOK_CONTENT,
                                   wb_content_abs_path:Path, 
                                   wb_type: str,
                                   pre_validated:bool=False) -> None:
    """Save a wb_content file of a given wb_type.

    BSM Layer 3: This is a local file system service function, saving a 
    workbook's data content to the local file system.

    Args:
        wb_content (bdm.WORKBOOK_CONTENT): The workbook content to save.
        wb_content_abs_path (Path): The path of the workbook file to load.
        wb_type (str): The type of the workbook to load.
        pre_validated (bool): If True, the input parameters are already validated.

    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Start:")

        logger.debug(f"BSM Local Filesystem: Saving WORKBOOK_CONTENT file: "
                     f"'{wb_content_abs_path}'")
        wbtl: str = "WB_TYPE_UNKNOWN" # wb_type label
        if not pre_validated:
            # Validate the wb_content_abs_path is a Path object.
            p3u.is_obj_of_type("wb_content_abs_path", wb_content_abs_path, Path, raise_error=True)
            ...
        # Depending on the wb_type, route the request to actual implementation
        # for the wb_type, wb_filetype.
        if wb_type in [bdm.WB_TYPE_BDM_STORE, bdm.WB_TYPE_BDM_CONFIG]:
            # WB_TYPE_BDM_STORE, WB_TYPE_BDM_CONFIG: Save it as a json file.
            bsm_BDM_STORE_file_abs_path(wb_content, wb_content_abs_path)
            wbtl = "BDM_STORE" if wb_type == bdm.WB_TYPE_BDM_STORE else "BDM_CONFIG"
        elif wb_type == bdm.WB_TYPE_TXN_REGISTER:
            # WB_TYPE_TXN_REGISTER: Save it as a CSV file.
            csv_DATA_LIST_file_save(wb_content, wb_content_abs_path)
            wbtl = "TXN_REGISTER_WORKBOOK"
        elif wb_type == bdm.WB_TYPE_EXCEL_TXNS:
            # WB_TYPE_EXCEL_TXNS: Save it as an Excel file.
            if wb_content_abs_path.exists():
                # TODO: settings for backup folder path
                p3u.copy_backup(wb_content_abs_path, "backup")
            wb_content.save(filename=wb_content_abs_path)
            wbtl = "TXN_EXCEL_WORKBOOK"
        elif wb_type == bdm.WB_TYPE_CSV_TXNS:
            # WB_TYPE_CSV_TXNS: Load it as a CSV file.
            csv_DATA_LIST_file_save(wb_content, wb_content_abs_path)
            wbtl = "TXN_CSV_WORKBOOK"
        elif wb_type == bdm.WB_TYPE_TXN_CATEGORIES:
            # WB_TYPE_TXN_CATEGORIES: Load it as a JSON file.
            json_DATA_OBJECT_file_save(wb_content, wb_content_abs_path)
            wbtl = "TXN_CATEGORIES_WORKBOOK"
        elif wb_type == bdm.WB_TYPE_CATEGORY_MAP:
            # WB_TYPE_CATEGORY_MAP, load it as a TOML file.
            with open(wb_content_abs_path, 'w', encoding='utf-8') as f:
                toml.dump(wb_content, f)
            wbtl = "CATEGORY_MAP_WORKBOOK"
        else: 
            # wb_type == bdm.WB_TYPE_BUDGET: # or anything else unknown
            m = f"Unsupported wb_type: '{wb_type}' for file: '{wb_content_abs_path}'"
            logger.error(m)
            raise ValueError(m)
        logger.info(f"BizEVENT: Saved {wbtl} to file: {wb_content_abs_path}")
        logger.debug(f"Complete: {p3u.stop_timer(st)}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise    
#endregion bsm_WORKBOOK_content_file_save(wb_abs_path : str = None) -> Any
# ---------------------------------------------------------------------------- +
#region    bsm_WORKBOOK_content_file_save1(wb:Workbook,wb_abs_path : str = None) -> Any
def bsm_WORKBOOK_content_file_save1(wb_content:Workbook,wb_path:Path) -> None:
    """Save a transaction file for a Financial Institution Workflow.

    Storage Model: This is a Model function, storing an excel workbook
    file to storage.

    Args:
        wb (Workbook): The workbook to save.
        wb_path (Path): The path of the workbook file to save.

    """
    st = time.time()
    try:
        # TODO: add logic to for workbook open in excel, work around.
        logger.info("Saving wb: ...")
        # Make a backup copy of the csv file if it exists.
        if wb_path.exists():
            p3u.copy_backup(wb_path, Path("backup"))
        wb_content.save(filename=wb_path)
        logger.info(f"BizEVENT: Saved excel workbook to '{wb_path}'")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WORKBOOK_content_file_save1(wb_abs_path : str = None) -> Any
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_file_save() function
def json_DATA_OBJECT_file_save(json_content:bdm.DATA_OBJECT, json_abs_path:Path) -> None:
    """Save a DATA_OBJECT to a json file."""
    try:
        # json_content must be a dictionary.
        p3u.is_obj_of_type("json_content", json_content, dict, raise_error=True)
        # json_abs_path must be a Path object.
        p3u.is_obj_of_type("json_abs_path", json_abs_path, Path, raise_error=True)
        logger.debug(f"Saving DATA_OBJECT to file: '{json_abs_path}'")
        json5_string = json5.encode(json_content)
        parsed_data = json.loads(json5_string) # for pretty printting
        json_content = json.dumps(parsed_data, indent=4)
        with open(json_abs_path, "w") as f:
            f.write(json_content)
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
#region    BDM_STORE functions
#region    bsm_BDM_STORE_url_get() function
def bsm_BDM_STORE_url_get(bdms_url : str = None) -> bdm.BDM_STORE:
    """BSM: Load a bdm.BDM_STORE object from a URL.
    
    Entry point for a bdm.BDM_STORE file load operation. Parse the URL and decide
    how to load the bdm.BDM_STORE object based on the URL scheme. Decode the
    json content and return it as a dictionary.

    Args:
        bdms_url (str): The URL to the bdm.BDM_STORE object to load.
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
        # If the scheme is file, load the bdm.BDM_STORE from a file.
        if parsed_url.scheme == "file":
            # Decode the URL and convert it to a Path object.
            bdms_path = Path.from_uri(bdms_url)
            logger.debug(f"Loading bdm.BDM_STORE from path: '{bdms_path}' URL: '{bdms_url}'")
            return bsm_BDM_STORE_file_load(bdms_path)
        raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_get() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_url_put() function
def bsm_BDM_STORE_url_put(bdm_store:bdm.BDM_STORE, bdms_url : str = None) -> Dict:
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
            logger.debug(f"Putting BDM_STORE to url:'{bdms_path}' "
                        f"url:'{bdms_url}'")
            return bsm_BDM_STORE_file_save(bdm_store, bdms_path)
        raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_url_put() function
# ---------------------------------------------------------------------------- +
#region    bsm_BDM_STORE_file_load() function
def bsm_BDM_STORE_file_load(bdms_path : Path = None) -> bdm.BDM_STORE:
    """Load a BDM_STORE file from the given Path value."""
    try:
        if bdms_path is None or not isinstance(bdms_path, Path):
            raise ValueError("bdms_path is None or not a Path object.")
        logger.debug(f"Loading BDM_STORE from  file: '{bdms_path}'")
        if not bdms_path.exists():
            m = f"file does not exist: {bdms_path}"
            logger.error(m)
            raise FileNotFoundError(m)
        if not bdms_path.is_file():
            m = f"bdms_path is not a file: '{bdms_path}'"
            logger.error(m)
            raise ValueError(m)
        if not bdms_path.suffix in bdm.VALID_BSM_BDM_STORE_FILETYPES:
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
        logger.info(f"BizEVENT: Loaded '{bdms_json_size}' chars of json content from file: '{bdms_path}'")
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
def bsm_BDM_STORE_file_save(bdm_store:bdm.BDM_STORE, bdms_path:Path) -> None:
    """Save the Budget Manager Store to a .jsonc file."""
    try:
        # bdm_store must be a dictionary.
        p3u.is_obj_of_type("bdm_store", bdm_store, dict, raise_error=True)
        # store_path must be a non-empty string.
        p3u.is_obj_of_type("bdms_path", bdms_path, Path, raise_error=True)
        logger.debug(f"Saving BDM_STORE to file: '{bdms_path}'")
        # Only persist the properties in BDM_PERSISTED_PROPERTIES.
        filtered_bsm = {k: v for k, v in bdm_store.items() if k in bdm.BSM_PERSISTED_PROPERTIES}
        jsonc_content = json5.encode(filtered_bsm)
        with open(bdms_path, "w") as f:
            f.write(jsonc_content)
        logger.info(f"BizEVENT: Saved BDM_STORE to file: {bdms_path}")
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
#endregion BDM_STORE functions
# ---------------------------------------------------------------------------- +
#region    bsm_WB_TYPE(wb_url : str = None) -> Any
def bsm_WB_TYPE(wb_url : str, wb_filetype:str) -> Any:
    """Determine the type of a WORKBOOK from its url

    Args:
        wb_url (str): The URL to the workbook to load.
    
    Returns:
        str: The calculated WB_TYPE constant, will be a member of
             VALID_WB_TYPE_VALUES.
    """
    try:
        p3u.is_non_empty_str("wb_url", wb_url, raise_error=True)
        # The best approach is to have the wb_type embedded in the url
        # to the immediate left of the wb_filetype, like 
        # "file:///path/to/wb_filename.wb_type_wb_name.wb_filetype".
        for wb_type in bdm.VALID_WB_TYPE_VALUES:
            if wb_type.lower() + wb_filetype.lower()  in wb_url.lower():
                return wb_type
        wb_abs_path = bsm_WB_URL_verify_file_scheme(wb_url, test=True)
        wb_filetype = wb_abs_path.suffix.lower()
        # Suss it out based on filetype.
        if wb_filetype not in [bdm.WB_FILETYPE_XLSX, bdm.WB_FILETYPE_CSV, 
                               bdm.WB_FILETYPE_JSON, bdm.WB_FILETYPE_TOML]:
            # If the filetype is not supported, raise an error.
            m = f"Unknown workbook filetype: {wb_filetype} in file: {wb_abs_path}"
            logger.error(m)
            return bdm.WB_TYPE_UNKNOWN
        elif wb_filetype == bdm.WB_FILETYPE_CSV:
            return bdm.WB_TYPE_TXN_REGISTER
        elif wb_filetype == bdm.WB_FILETYPE_XLSX:
            return bdm.WB_TYPE_EXCEL_TXNS
        elif wb_filetype == bdm.WB_FILETYPE_JSON:
            return bdm.WB_TYPE_TXN_CATEGORIES
        elif wb_filetype == bdm.WB_FILETYPE_TOML:
            return bdm.WB_TYPE_CATEGORY_MAP
        else:
            m = f"Unknown workbook filetype: {wb_filetype} in file: {wb_abs_path}"
            logger.error(m)
            return bdm.WB_TYPE_UNKNOWN
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WB_TYPE(wb_url : str = None) -> Any
# ---------------------------------------------------------------------------- +
#endregion Layer 3 - abs_path filesystem storage functions
#                                                                              +
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#                                                                              +
#region    Common functions
#                                                                              +
# ---------------------------------------------------------------------------- +
#region    bsm_WB_URL_verify(wb_url: str) function 
def bsm_WB_URL_verify(wb_url: str,test:bool=True) -> Any:
    """Verify wb_url is valid for the BSM.
    
    At present, only file scheme is supported."""
    try:
        p3u.is_non_empty_str("wb_url", wb_url, raise_error=True)
        return bsm_WB_URL_verify_file_scheme(wb_url, test=test)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WB_URL_verify(url: str) function
# ---------------------------------------------------------------------------- +
#region    bsm_WB_URL_validate(url: str) function 
def bsm_WB_URL_validate(wb_content_url: str,result:bool=False) -> Union[ParseResult, None]:
    """Validate wb_url is a valid for support storage service requirements.
    
    Args:
        wb_url (str): The URL to validate.
    Returns: None, means url is valid.
    Raises:
        ValueError: If the URL is not valid.        
    """
    try:
        p3u.is_non_empty_str("wb_content_url", wb_content_url, raise_error=True)
        parsed_url: ParseResult = urlparse(wb_content_url)
        split_url = urlsplit(wb_content_url)
        if not parsed_url:
            raise ValueError(f"Invalid wb_content_url: {wb_content_url}")
        if not parsed_url.scheme:
            raise ValueError(f"Invalid URL has no scheme: {wb_content_url}")
        if not parsed_url.path:
            raise ValueError(f"Invalid URL has no path: {wb_content_url}")
        if parsed_url.scheme not in bdm.BSM_SUPPORTED_URL_SCHEMES:
            raise ValueError(f"URL scheme is not supported: {parsed_url.scheme}")
        return parsed_url if result else None
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WB_URL_verify_file_scheme(url: str) function
# ---------------------------------------------------------------------------- +
#region    bsm_WB_TYPE_validate() function 
def bsm_WB_URL_TYPE_validate(wb_content_url: str, wb_type: str,
                         result:bool=False) -> Union[None, ParseResult]:
    """Validate wb_type is a valid for supported storage service requirements.

    Verify the wb_type is compatible with the wb_url, that the url is for
    a workbook of the given type, and that the url is valid.
    Args:
        wb_type (str): The type of the workbook to validate.
        wb_url (str): The URL to validate.
    Returns: None, means url is valid.
    Raises:
        ValueError: If the URL is not valid.        
    """
    try:
        p3u.is_non_empty_str("wb_type", wb_type, raise_error=True)
        p3u.is_non_empty_str("wb_content_url", wb_content_url, raise_error=True)
        if (wb_type == bdm.WB_TYPE_UNKNOWN or
            wb_type not in bdm.VALID_WB_TYPE_VALUES):
            m = f"Invalid workbook type: {str(wb_type)}."
            logger.error(m)
            raise ValueError(m)
        wb_filetype:str = bdm.WB_FILETYPE_MAP.get(wb_type, None)
        if not wb_filetype:
            m = f"wb_type '{wb_type}' is not supported, " \
                f"no filetype mapping found."
            logger.error(m)
            raise ValueError(m)
        # wb_type is valid, how about the wb_url?
        parsed_url: ParseResult = bsm_WB_URL_validate(wb_content_url,result=True)
        # wb_url is valid, but can it be supported for the wb_type?
        wb_abs_path: Path = bsm_WB_URL_verify_file_scheme(parsed_url, test=False)
        if wb_filetype not in wb_abs_path.suffix.lower():
            m = f"wb_content_url filetype '{wb_abs_path.suffix}' does not match " \
                f"wb_type '{wb_type}' filetype '{wb_filetype}'."
            logger.error(m)
            raise ValueError(m)
        return parsed_url if parsed_url else None
    except Exception as e:
        raise
#endregion bsm_WB_TYPE_validate() function
# ---------------------------------------------------------------------------- +
#region    bsm_WB_URL_verify_file_scheme(url: str) function 
def bsm_WB_URL_verify_file_scheme(wb_url: Union[str,ParseResult], test:bool=True) -> Path:
    """Verify wb_url is a valid file url and path, return it as a Path object."""
    try:
        if (not p3u.is_non_empty_str("wb_url", wb_url) and 
            not isinstance(wb_url, (str, ParseResult))):
            raise TypeError(f"wb_url must be a non-empty str or ParseResult, "
                            f"got: {type(wb_url).__name__}")
        parsed_url: ParseResult = wb_url if isinstance(wb_url, ParseResult) else urlparse(wb_url)
        if not isinstance(parsed_url, ParseResult) or parsed_url.scheme != "file":
            raise ValueError(f"Only URL scheme: 'file' supported, "
                             f"but got: {parsed_url.scheme}")
        orig_url: str = urlunparse(parsed_url)
        file_path: Path = Path().from_uri(orig_url)
        if test and not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        return file_path
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_WB_URL_verify_file_scheme(url: str) function
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
                logger.info(f"BizEVENT: Creating folder: '{str(ap)}'")
                ap.mkdir(parents=True, exist_ok=True)
                return True
            else:
                raise ValueError(m)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
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
        for filetype in bdm.VALID_WB_FILETYPES:
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
#endregion Common functions
#                                                                              +
# ---------------------------------------------------------------------------- +