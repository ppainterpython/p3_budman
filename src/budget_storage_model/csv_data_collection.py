# ---------------------------------------------------------------------------- +
#region    csv_data_collection.py module\
""" Provides support to load csv text into DATA_COLLECTION dictionaries.

    Keep it simple, use a csv file structure to load/save DATA_COLLECTION
    objects from/to storage. The DATA_COLLECTION object is a dictionary 
    in memory and a csv file in storage. Use a URL to reference it from 
    other layers of an application. Initially, the file scheme is supported 
    for local files, but later it may be extended to support other 
    storage services.

    Only depend on the dict to csv header row mapping, not detailed content structure
    is used beyond that for validation.

    No dependencies to other application layers.

    # TODO: switch verbs to put/get from save/load, consistent with URL usage.
    # TODO: move back to std lib json module, jsonc
"""
#endregion budget_storage_model.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import csv, logging, os, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict, Any

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
from budman_namespace import (
    DATA_COLLECTION, BDM_STORE, BSM_DATA_COLLECTION_CSV_STORE_FILETYPES,
    WB_FILETYPE_CSV)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region    csv_DATA_COLLECTION_get_url() function
def csv_DATA_COLLECTION_url_get(csv_url : str = None) -> DATA_COLLECTION:
    """Get a DATA_COLLECTION object from a URL to a csv file in storage.
    
    A csv dictionary is read in from the csv_url. Parse the URL and decide
    how to load the DATA_COLLECTION object based on the URL scheme. Decode the
    json content and return it as a dictionary.

    Args:
        csv_url (str): The URL to the DATA_COLLECTION object to load.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Get DATA_COLLECTION from  url: '{csv_url}'")
        # only support file:// scheme for now.
        # csv_path = verify_url_file_path(csv_url, test=True)
        csv_path = p3u.verify_url_file_path(csv_url, test=True)
        result = csv_DATA_COLLECTION_file_load(csv_path)
        logger.debug(f"Complete csv_path: {csv_path} {p3u.stop_timer(st)}")
        return result
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_COLLECTION_get_url() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_COLLECTION_put_url() function
def csv_DATA_COLLECTION_url_put(csv_dict:dict, csv_url : str = None) -> None:
    """Put a DATA_COLLECTION object to a URL in storage.
    
    A csv dictionary is stored to the csv_url. Parse the URL and decide
    how to load the DATA_COLLECTION object based on the URL scheme. Decode the
    json content and return it as a dictionary.

    Args:
        csv_dict (dict): The DATA_COLLECTION object to save.
        csv_url (str): The URL to the DATA_COLLECTION object to load.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Get DATA_COLLECTION from  url: '{csv_url}'")
        # only support file:// scheme for now.
        # csv_path = verify_url_file_path(csv_url, test=True)
        csv_path = p3u.verify_url_file_path(csv_url, test=True)
        csv_DATA_COLLECTION_file_save(csv_dict, csv_path)
        logger.debug(f"Complete csv_path: {csv_path} {p3u.stop_timer(st)}")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_COLLECTION_get_url() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_COLLECTION_file_load() function
def csv_DATA_COLLECTION_file_load(csv_path : Path = None) -> DATA_COLLECTION:
    """Load a DATA_COLLECTION from a csv file at the given Path."""
    try:
        st = p3u.start_timer()
        logger.debug(f"BSM: Start: Loading DATA_COLLECTION from csv file: '{csv_path}'")
        p3u.verify_file_path_for_load(csv_path)
        # Only hand csv files here.
        if csv_path.suffix != WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        with open(csv_path, "r",newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            data_collection: DATA_COLLECTION = {}
            for row in reader:
                # Use the first column as the key, rest as values.
                if row:
                    check_number = row["Number"].strip()
                    if check_number in data_collection:
                        logger.warning(f"Duplicate key found: {check_number}")
                        logger.warning(f"Skipping row: {row}")
                        continue
                    data_collection[check_number] = row
        logger.info(f"BizEVENT: BSM: Loaded DATA_COLLECTION from csv file: '{csv_path}'")
        logger.debug(f"BSM: Complete {p3u.stop_timer(st)}")
        return data_collection
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_file_load() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_COLLECTION_file_save() function
def csv_DATA_COLLECTION_file_save(cvs_dict: Dict[str, Dict[str, Any]], csv_path : Path = None) -> None:
    """Load a DATA_COLLECTION from a csv file at the given Path."""
    try:
        st = p3u.start_timer()
        logger.debug(f"Loading DATA_COLLECTION from  file: '{csv_path}'")
        p3u.verify_file_path_for_save(csv_path)
        # Only hand csv files here.
        if csv_path.suffix != WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        # Extract the fieldnames from the first row of the wb_dict.
        try:
            first_record = next(iter(cvs_dict.values()))
        except StopIteration:
            m = "The wb_dict is empty, cannot determine fieldnames."
            logger.error(m)
            raise ValueError(m)
        fieldnames = list(first_record.keys())

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for row in cvs_dict.values():
                writer.writerow(row)
        logger.info(f"BizEVENT: Save DATA_COLLECTION to csv  file: '{csv_path}'")
        logger.debug(f"Complete {p3u.stop_timer(st)}")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion bsm_BDM_STORE_file_save() function
# ---------------------------------------------------------------------------- +
#region    verify_url_file_path(url: str) function 
# def verify_url_file_path(url: str,test:bool=True) -> Path:
#     """Verify that the URL is a valid file path and return it as a Path object."""
#     try:
#         p3u.is_non_empty_str("url", url, raise_error=True)
#         parsed_url = urlparse(url)
#         if parsed_url.scheme != "file":
#             raise ValueError(f"URL scheme is not 'file': {parsed_url.scheme}")
#         file_path = Path.from_uri(url)
#         if test and not file_path.exists():
#             raise FileNotFoundError(f"File does not exist: {file_path}")
#         return file_path
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#endregion verify_url_file_path(url: str) function
# ---------------------------------------------------------------------------- +
#region    verify_file_path_for_load(url: str) function 
# def verify_file_path_for_load(file_path: Path) -> None:
#     """Verify that the file path is valid and ready to load or raise error."""
#     try:
#         p3u.is_obj_of_type("file_path", file_path, Path, raise_error=True)
#         if not file_path.exists():
#             raise FileNotFoundError(f"File does not exist: {file_path}")
#         if not file_path.exists():
#             m = f"file does not exist: {file_path}"
#             logger.error(m)
#             raise FileNotFoundError(m)
#         if not file_path.is_file():
#             m = f"csv_path is not a file: '{file_path}'"
#             logger.error(m)
#             raise ValueError(m)
#         if not file_path.suffix in BSM_DATA_COLLECTION_CSV_STORE_FILETYPES:
#             m = f"csv_path filetype is not supported: {file_path.suffix}"
#             logger.error(m)
#             raise ValueError(m)
#         if file_path.stat().st_size == 0:
#             m = f"file is empty: {file_path}"
#             logger.error(m)
#             raise ValueError(m)
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#endregion verify_file_path_for_load(url: str) function
# ---------------------------------------------------------------------------- +
