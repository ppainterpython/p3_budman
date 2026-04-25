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
def csv_DATA_LIST_url_get(csv_url : str = None, 
                          return_type: type = bdm.DATA_ROW_DICT_TYPE) -> bdm.DATA_ROW_DICT_TYPE | bdm.DATA_ROW_LIST_TYPE:
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
        result = csv_DATA_LIST_file_load(csv_path, return_type=return_type)
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
def csv_DATA_LIST_file_load(csv_path: Path) -> bdm.DATA_OBJECT_LIST_TYPE:
    """Load a DATA_LIST from a csv file at the given Path.
    
    A csv file is read in from the csv_path using csv.DictReader().
    The csv file is expected to have a header row with the fieldnames.

    Args:
        csv_path (Path): The path to the csv file to load.

    Returns:
        bdm.DATA_OBJECT_LIST_TYPE: The loaded DATA_LIST object as List[Dict[str,Any]].

    Raises:
        ValueError: If the csv file cannot be loaded.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"BSM: Start: Loading DATA_LIST from csv file: '{csv_path}'")
        # Verify the csv_path is a valid file path for loading.
        _ = p3u.is_valid_path("csv_path", csv_path)  
        p3u.verify_file_path_for_load(csv_path)
        # Only handle csv files here.
        if csv_path.suffix != bdm.WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        
        with open(csv_path, "r", newline="", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            data_list: bdm.DATA_OBJECT_LIST_TYPE = list(reader)
        
        logger.info(f"BizEVENT: BSM: Loaded DATA_OBJECT_LIST_TYPE from csv file: '{csv_path}'")
        logger.debug(f"BSM: Complete {p3u.stop_timer(st)}")
        return data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_load() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_LIST_file_save() function
def csv_DATA_LIST_file_save(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                            csv_path: Path = None) -> None:
    """Save a DATA_LIST to a csv file at the given Path using csv.DictWriter()."""
    try:
        st = p3u.start_timer()
        logger.debug(f"Saving DATA_LIST to file: '{csv_path}'")
        p3u.verify_file_path_for_save(csv_path)
        # Only handle csv files here.
        if csv_path.suffix != bdm.WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        # Extract the fieldnames from the first row of the csv_content.
        try:
            first_record = csv_content[0]
        except IndexError:
            m = "The csv_content is empty, cannot determine fieldnames."
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
        logger.info(f"BizEVENT: Save DATA_LIST to csv file: '{csv_path}'")
        logger.debug(f"Complete {p3u.stop_timer(st)}")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_save() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_has_header_row() function
def csv_DATA_LIST_has_header_row(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                                fieldnames: List[str]) -> bool:
    """Check if a csv data list has the expected fieldnames as keys.
    
    Args:
        csv_content: The csv data content as List[Dict[str,Any]]
        fieldnames: The expected fieldnames to check for
    
    Returns:
        True if keys match expected fieldnames, False otherwise
    """
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot check header row."
            logger.error(m)
            raise ValueError(m)
        
        # Check if the keys of the first dictionary match the expected fieldnames (case insensitive)
        first_row_keys = set(k.lower() for k in csv_content[0].keys())
        expected_keys = set(k.lower() for k in fieldnames)
        
        return first_row_keys == expected_keys
        
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_has_header_row() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_remove_columns() function
def csv_DATA_LIST_remove_columns(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                                column_names: str | List[str]) -> bdm.DATA_OBJECT_LIST_TYPE:
    """Remove columns from a csv data list.
    
    Args:
        csv_content: The csv data content as List[Dict[str,Any]]
        column_names: Column name(s) to remove
    
    Returns:
        Modified csv data with columns removed
    """
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot remove columns."
            logger.error(m)
            raise ValueError(m)
        
        # Ensure column_names is a list
        if isinstance(column_names, str):
            columns_to_remove = [column_names]
        else:
            columns_to_remove = list(column_names)
        
        new_csv_data_list = []
        for row in csv_content:
            new_row = row.copy()
            for col in columns_to_remove:
                if col in new_row:
                    del new_row[col]
            new_csv_data_list.append(new_row)
        
        logger.debug(f"Removed columns '{column_names}' from csv_data_list.")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_remove_columns() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_add_columns() function
def csv_DATA_LIST_add_columns(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                              columns_and_defaults: Dict[str, Any]) -> bdm.DATA_OBJECT_LIST_TYPE:
    """Add columns with default values to a csv data list.
    
    Args:
        csv_content: The csv data content as List[Dict[str,Any]]
        columns_and_defaults: Dict mapping column names to default values
    
    Returns:
        Modified csv data with new columns added
    """
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot add columns."
            logger.error(m)
            raise ValueError(m)
        
        # Track which columns are actually added vs already exist
        added_columns = set()
        existing_columns = set()
        
        new_csv_data_list = []
        for row in csv_content:
            new_row = row.copy()
            for col_name, default_value in columns_and_defaults.items():
                if col_name not in new_row:
                    # Column doesn't exist, add it with default value
                    new_row[col_name] = default_value
                    added_columns.add(col_name)
                else:
                    # Column already exists, leave it undisturbed
                    existing_columns.add(col_name)
            new_csv_data_list.append(new_row)
        
        # Log what happened
        if added_columns:
            logger.debug(f"Added new columns '{list(added_columns)}' to csv_data_list.")
        if existing_columns:
            logger.debug(f"Left existing columns '{list(existing_columns)}' undisturbed in csv_data_list.")
            
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_add_columns() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_remove_extra_columns() function
def csv_DATA_LIST_remove_extra_columns(csv_content: bdm.DATA_OBJECT_LIST_TYPE,
                                     expected_columns: List[str]) -> bdm.DATA_OBJECT_LIST_TYPE:
    """Remove columns that are not in the expected_columns list from a csv data list."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot remove extra columns."
            logger.error(m)
            raise ValueError(m)
        
        new_csv_data_list = []
        for row in csv_content:
            new_row = {col: val for col, val in row.items() if col in expected_columns}
            new_csv_data_list.append(new_row)
        
        logger.debug(f"Removed extra columns not in '{expected_columns}' from csv_data_list.")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_remove_extra_columns() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_file_validate_header() function
def csv_DATA_LIST_file_validate_header(csv_path: Path, 
                                       expected_fieldnames: List[str],
                                       inplace: bool=False) -> Path:
    """Check if a CSV file has the expected header row. If missing, add it and save to a new file.
    
    Args:
        csv_path (Path): Path to the CSV file to check
        expected_fieldnames (List[str]): List of expected fieldnames for the header row
        inplace (bool): If True, modify the original file in place. If False, create a new file with "_hdr" suffix.

    Returns:
        Path: Path to the output file (original if header exists, new file with "_hdr" if header was added)
        
    Raises:
        ValueError: If the CSV file cannot be processed
    """
    try:
        logger.debug(f"Checking header in CSV file: '{csv_path}'")
        
        # Verify the csv_path is a valid file path for loading
        if not csv_path.exists():
            raise ValueError(f"CSV file does not exist: {csv_path}")
        if csv_path.suffix.lower() != '.csv':
            raise ValueError(f"File is not a CSV file: {csv_path}")
            
        # Load the CSV file using DictReader to check current structure
        with open(csv_path, "r", newline="", encoding='utf-8-sig') as f:
            # Peek at the first line to check if it looks like a header
            first_line = f.readline().strip()
            f.seek(0)  # Reset file pointer
            
            reader = csv.DictReader(f, skipinitialspace=True)
            
            # Get the actual fieldnames from DictReader (will be None, integers, or strings)
            actual_fieldnames = reader.fieldnames
            
        # Check if the current fieldnames match expected fieldnames (case insensitive)
        if actual_fieldnames:
            actual_set = set(name.lower() if isinstance(name, str) else str(name) 
                           for name in actual_fieldnames)
            expected_set = set(name.lower() for name in expected_fieldnames)
            
            if actual_set == expected_set:
                logger.debug(f"Header row already exists and matches expected fieldnames")
                return csv_path
        
        # Header is missing or doesn't match - need to add it
        logger.info(f"Adding missing header row to CSV file: {expected_fieldnames}")
        
        # Create new filename with "_hdr" appended
        stem = csv_path.stem
        suffix = csv_path.suffix
        if inplace:
            output_path = csv_path
        else:
            new_filename = f"{stem}_hdr{suffix}"
            output_path = csv_path.parent / new_filename
        
        # Read the original file as raw rows
        with open(csv_path, "r", newline="", encoding='utf-8-sig') as f:
            reader = csv.reader(f, skipinitialspace=True)
            raw_rows = list(reader)
        
        # Write new file with header row
        with open(output_path, "w", newline="", encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Write the header row first
            writer.writerow(expected_fieldnames)
            # Write all the original rows
            for row in raw_rows:
                writer.writerow(row)
        
        logger.info(f"Created CSV file with header: '{output_path}'")
        return output_path
        
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_validate_header() function
# ---------------------------------------------------------------------------- +
