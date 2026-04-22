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

    # TODO: move back to std lib json module, jsonc
"""
#endregion budget_storage_model.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import csv, logging, os, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import List, Dict, Any

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
import budman_namespace.design_language_namespace as bdm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region    csv_DATA_LIST_get_url() function
def csv_DATA_LIST_url_get(csv_url : str = None) -> bdm.DATA_LIST_TYPE:
    """Get a DATA_LIST object from a URL to a csv file in storage.

    A csv DATA_LIST is read in from the csv_url. Parse the URL and decide
    how to load the DATA_LIST object based on the URL scheme. 

    Args:
        csv_url (str): The URL to the DATA_LIST object to load.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Get DATA_LIST from  url: '{csv_url}'")
        # only support file:// scheme for now.
        csv_path = p3u.verify_url_file_path(csv_url, test=True)
        result = csv_DATA_LIST_file_load(csv_path)
        logger.debug(f"Complete csv_path: {csv_path} {p3u.stop_timer(st)}")
        return result
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_get_url() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_LIST_url_put() function
def csv_DATA_LIST_url_put(csv_list: list, csv_url: str = None) -> None:
    """Put a DATA_LIST object to a URL in storage.

    A csv list is stored to the csv_url. Parse the URL and decide
    how to load the DATA_LIST object based on the URL scheme. 

    Args:
        csv_list (list): The DATA_LIST object to save.
        csv_url (str): The URL to the DATA_LIST object to load.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Get DATA_LIST from  url: '{csv_url}'")
        # only support file:// scheme for now.
        csv_path = p3u.verify_url_file_path(csv_url, test=True)
        csv_DATA_LIST_file_save(csv_list, csv_path)
        logger.debug(f"Complete csv_path: {csv_path} {p3u.stop_timer(st)}")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_url_put() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_LIST_file_load() function
def csv_DATA_LIST_file_load(csv_path : Path) -> bdm.DATA_LIST_TYPE:
    """Load a DATA_LIST from a csv file at the given Path.
    
    A csv file is read in from the csv_path. The csv file is expected to
    have a header row with the fieldnames that map to the DATA_LIST dict
    item keys.

    Args:
        csv_path (Path): The path to the csv file to load.
        fieldnames (List[str] | None): The expected fieldnames for the csv file.

    Returns:
        bdm.DATA_LIST_TYPE: The loaded DATA_LIST object.

    Raises:
        ValueError: If the csv file does not have the expected fieldnames.
    """
    try:        
        st = p3u.start_timer()
        logger.debug(f"BSM: Start: Loading DATA_LIST from csv file: '{csv_path}'")
        # Verify the csv_path is a valid file path for loading.
        # If the file does not exist, raise an error. 
        _ = p3u.is_valid_path("csv_path", csv_path)  
        p3u.verify_file_path_for_load(csv_path)
        has_header: bool = False
        # Only handle csv files here.
        if csv_path.suffix != bdm.WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        with open(csv_path, "r",newline="",encoding='utf-8-sig') as f:
            # File has no header, use provided fieldnames
            reader = csv.DictReader(f, skipinitialspace=True)
            data_list: bdm.DATA_LIST_TYPE = list(reader)
        logger.info(f"BizEVENT: BSM: Loaded DATA_LIST from csv file: '{csv_path}'")
        logger.debug(f"BSM: Complete {p3u.stop_timer(st)}")
        return data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_load() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_LIST_file_save() function
def csv_DATA_LIST_file_save(csv_content: bdm.DATA_LIST_TYPE, csv_path : Path = None) -> None:
    """Save a DATA_LIST to a csv file at the given Path."""
    try:
        st = p3u.start_timer()
        logger.debug(f"Saving DATA_LIST to file: '{csv_path}'")
        p3u.verify_file_path_for_save(csv_path)
        # Only hand csv files here.
        if csv_path.suffix != bdm.WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        # Extract the fieldnames from the first row of the cvs_content.
        try:
            first_record = csv_content[0]
        except IndexError:
            m = "The cvs_content is empty, cannot determine fieldnames."
            logger.error(m)
            raise ValueError(m)
        fieldnames = list(first_record.keys())

        # Make a backup copy of the csv file if it exists.
        if csv_path.exists():
            p3u.copy_backup(csv_path, Path("backup"))
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for row in csv_content:
                writer.writerow(row)
        logger.info(f"BizEVENT: Save DATA_LIST to csv  file: '{csv_path}'")
        logger.debug(f"Complete {p3u.stop_timer(st)}")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_save() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_has_header_row() function
def csv_DATA_LIST_has_header_row(csv_content: bdm.DATA_LIST_TYPE, fieldnames  : List[str]) -> bool:
    """Check if a csv data list has a header row."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot check header row."
            logger.error(m)
            raise ValueError(m)
        # check if data_list[0] is equale to fieldnames case insensitive
        if csv_content and set(k.lower() for k in csv_content[0].keys()) == set(k.lower() for k in fieldnames):
            return True
        return False
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_has_header_row() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_add_header_row() function
def csv_DATA_LIST_add_header_row(csv_content: bdm.DATA_LIST_TYPE, fieldnames  : List[str]) -> bdm.DATA_LIST_TYPE:
    """Add a header row to a csv data list if it does not already have one."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot add header row."
            logger.error(m)
            raise ValueError(m)
        # Check if the first row of the csv_data_list has the fieldnames as keys.
        first_row = csv_content[0]
        if all(field in first_row for field in fieldnames):
            logger.debug("The csv_data_list already has a header row.")
            return csv_content
        # If not, add a header row with the fieldnames as keys and empty values.
        header_row = {field: "" for field in fieldnames}
        new_csv_data_list = [header_row] + csv_content
        logger.debug(f"Added header row to csv_data_list: {fieldnames}")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_add_header_row() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_remove_column() function
def csv_DATA_LIST_remove_columns(csv_content: bdm.DATA_LIST_TYPE, 
                                 column_name: str | List[str]) -> bdm.DATA_LIST_TYPE:
    """Remove a column from a csv data list."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot remove column."
            logger.error(m)
            raise ValueError(m)
        new_csv_data_list = []
        for row in csv_content:
            if isinstance(column_name, list):
                for col in column_name:
                    if col in row:
                        del row[col]
            else:
                if column_name in row:
                    del row[column_name]
            new_csv_data_list.append(row)
        logger.debug(f"Removed column '{column_name}' from csv_data_list.")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_remove_column() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_add_columns() function
def csv_DATA_LIST_add_columns(cvs_content: bdm.DATA_LIST_TYPE, 
                              columns: Dict[str, Any]) -> bdm.DATA_LIST_TYPE:
    """Add columns with default values to a csv data list."""
    try:
        if not cvs_content:
            m = "The csv_data_list is empty, cannot add columns."
            logger.error(m)
            raise ValueError(m)
        
        # Track which columns are actually added vs already exist
        added_columns = set()
        existing_columns = set()
        
        new_csv_data_list = []
        for row in cvs_content:
            for col_name, default_value in columns.items():
                if col_name not in row:
                    # Column doesn't exist, add it with default value
                    row[col_name] = default_value
                    added_columns.add(col_name)
                else:
                    # Column already exists, leave it undisturbed
                    existing_columns.add(col_name)
            new_csv_data_list.append(row)
        
        # Log what happened
        if added_columns:
            logger.debug(f"Added new columns '{list(added_columns)}' to csv_data_list.")
        if existing_columns:
            logger.debug(f"Left existing columns '{list(existing_columns)}' undisturbed in csv_data_list.")
            
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_remove_extra_columns() function
def csv_DATA_LIST_remove_extra_columns(cvs_content: bdm.DATA_LIST_TYPE,
                                     expected_columns: List[str]) -> bdm.DATA_LIST_TYPE:
    """Remove columns that are not in the expected_columns list from a csv data list."""
    try:
        if not cvs_content:
            m = "The csv_data_list is empty, cannot remove extra columns."
            logger.error(m)
            raise ValueError(m)
        
        new_csv_data_list = []
        for row in cvs_content:
            new_row = {col: val for col, val in row.items() if col in expected_columns}
            new_csv_data_list.append(new_row)
        
        logger.debug(f"Removed extra columns not in '{expected_columns}' from csv_data_list.")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_remove_extra_columns() function
