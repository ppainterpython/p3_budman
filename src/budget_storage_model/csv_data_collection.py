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
def csv_DATA_LIST_file_load(csv_path : Path, 
                            return_type: type = bdm.DATA_ROW_DICT_TYPE) -> bdm.DATA_ROW_DICT_TYPE | bdm.DATA_ROW_LIST_TYPE:
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
        # Only handle csv files here.
        if csv_path.suffix != bdm.WB_FILETYPE_CSV:
            m = f"csv_path filetype is not supported: {csv_path.suffix}"
            logger.error(m)
            raise ValueError(m)
        if  return_type not in [bdm.DATA_ROW_DICT_TYPE, bdm.DATA_ROW_LIST_TYPE]:
            m = f"return_type is not supported: {str(return_type)}"
            logger.error(m)
            raise ValueError(m)
        data_list: bdm.DATA_ROW_LIST_TYPE = []
        data_dict: bdm.DATA_ROW_DICT_TYPE = []
        with open(csv_path, "r",newline="",encoding='utf-8-sig') as f:
            if return_type == bdm.DATA_ROW_DICT_TYPE:
                # File has no header, use provided fieldnames
                reader = csv.DictReader(f, skipinitialspace=True)
                data_dict = list(reader)
                logger.info(f"BizEVENT: BSM: Loaded DATA_ROW_DICT_TYPE from csv file: '{csv_path}'")
                logger.debug(f"BSM: Complete {p3u.stop_timer(st)}")
                return data_dict
            else:
                reader = csv.reader(f, skipinitialspace=True)
                data_list = list(reader)
                logger.info(f"BizEVENT: BSM: Loaded DATA_ROW_LIST_TYPE from csv file: '{csv_path}'")
                logger.debug(f"BSM: Complete {p3u.stop_timer(st)}")
                return data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_load() function
# ---------------------------------------------------------------------------- +
#region    csv_DATA_LIST_file_save() function
def csv_DATA_LIST_file_save(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                            csv_path : Path = None) -> None:
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
        logger.info(f"BizEVENT: Save DATA_LIST to csv file: '{csv_path}'")
        logger.debug(f"Complete {p3u.stop_timer(st)}")
        return
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_file_save() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_has_header_row() function
def csv_DATA_LIST_has_header_row(csv_content: bdm.DATA_OBJECT_LIST_TYPE | bdm.DATA_ROW_LIST_TYPE, 
                                fieldnames: List[str]) -> bool:
    """Check if a csv data list has a header row.
    
    Handles both DATA_OBJECT_LIST_TYPE (List[Dict]) and DATA_ROW_LIST_TYPE (List[List[str]]).
    
    Args:
        csv_content: The csv data content in either format
        fieldnames: The expected fieldnames to check for
    
    Returns:
        True if header row matches expected fieldnames, False otherwise
    """
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot check header row."
            logger.error(m)
            raise ValueError(m)
        
        # Detect the data type
        if csv_is_DATA_OBJECT_LIST_TYPE(csv_content):
            # Handle Dictionary format (List[Dict])
            return _has_header_row_dict_format(csv_content, fieldnames)
        elif csv_is_DATA_ROW_LIST_TYPE(csv_content):
            # Handle List format (List[List[str]])
            return _has_header_row_list_format(csv_content, fieldnames)
        else:
            m = f"Unsupported csv_content type: {type(csv_content)}"
            logger.error(m)
            raise ValueError(m)
            
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise

def _has_header_row_dict_format(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                                fieldnames: List[str]) -> bool:
    """Check if dictionary format csv data has the expected fieldnames as keys."""
    if not csv_content:
        return False
    
    # Check if the keys of the first dictionary match the expected fieldnames (case insensitive)
    first_row_keys = set(k.lower() for k in csv_content[0].keys())
    expected_keys = set(k.lower() for k in fieldnames)
    
    return first_row_keys == expected_keys

def _has_header_row_list_format(csv_content: bdm.DATA_ROW_LIST_TYPE, 
                               fieldnames: List[str]) -> bool:
    """Check if list format csv data has the expected fieldnames in first row."""
    if not csv_content:
        return False
    
    # Check if first row matches fieldnames (case insensitive)
    first_row_values = set(k.lower() for k in csv_content[0])
    expected_values = set(k.lower() for k in fieldnames)
    
    return first_row_values == expected_values
#endregion csv_DATA_LIST_has_header_row() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_add_header_row() function
def csv_DATA_LIST_add_header_row(csv_content: bdm.DATA_ROW_LIST_TYPE, fieldnames  : List[str]) -> bdm.DATA_OBJECT_LIST_TYPE:
    """Add a header row to a csv data list if it does not already have one."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot add header row."
            logger.error(m)
            raise ValueError(m)
        if not csv_is_DATA_ROW_LIST_TYPE(csv_content):
            m = "The csv_data_list is not of type DATA_ROW_LIST_TYPE, cannot add header row."
            logger.error(m)
            raise ValueError(m)
        if not isinstance(fieldnames, list) or not all(isinstance(f, str) for f in fieldnames):
            m = "The fieldnames must be a list of strings to add header row."
            logger.error(m)
            raise ValueError(m)
        # Check if the first row of the csv_data_list has the fieldnames as keys.
        first_row = csv_content[0]
        if all(field in first_row for field in fieldnames):
            logger.debug("The csv_data_list already has a header row.")
            return csv_content
        # If not, add a header row with the fieldnames
        new_csv_data_list = [fieldnames] + csv_content
        logger.debug(f"Added header row to csv_data_list: {fieldnames}")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_add_header_row() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_remove_column() function
def csv_DATA_LIST_remove_columns(
        csv_content: bdm.DATA_OBJECT_LIST_TYPE | bdm.DATA_ROW_LIST_TYPE, 
        column_name: str | List[str]) -> bdm.DATA_OBJECT_LIST_TYPE | bdm.DATA_ROW_LIST_TYPE:
    """Remove a column from a csv data list."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot remove column."
            logger.error(m)
            raise ValueError(m)
        new_csv_data_list = []
        if isinstance(column_name, str):
            column_name = [column_name]
        if csv_is_DATA_ROW_DICT_TYPE(csv_content):
            for row in csv_content:
                for col in column_name:
                    if col in row:
                        del row[col]
            new_csv_data_list.append(row)
            return new_csv_data_list
        elif csv_is_DATA_ROW_LIST_TYPE(csv_content):
            new_csv_data_list = csv_DATA_ROW_LIST_remove_columns_by_name(csv_content, column_name)
        logger.debug(f"Removed column '{column_name}' from csv_data_list.")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_LIST_remove_column() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_add_columns() function
def csv_DATA_LIST_add_columns(csv_content: bdm.DATA_OBJECT_LIST_TYPE | bdm.DATA_ROW_LIST_TYPE, 
                              columns_and_defaults: Dict[str, Any],
                              has_header: bool = True) -> bdm.DATA_OBJECT_LIST_TYPE | bdm.DATA_ROW_LIST_TYPE:
    """Add columns with default values to a csv data list.
    
    Handles both DATA_OBJECT_LIST_TYPE (List[Dict]) and DATA_ROW_LIST_TYPE (List[List[str]]).
    
    Args:
        csv_content: The csv data content in either format
        columns_and_defaults: Dict mapping column names to default values
        has_header: Whether the first row is a header (only relevant for DATA_ROW_LIST_TYPE)
    
    Returns:
        The modified csv data in the same format as input
    """
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot add columns."
            logger.error(m)
            raise ValueError(m)
        
        # Detect the data type
        if csv_is_DATA_OBJECT_LIST_TYPE(csv_content):
            # Handle Dictionary format (List[Dict])
            return _add_columns_to_dict_format(csv_content, columns_and_defaults)
        elif csv_is_DATA_ROW_LIST_TYPE(csv_content):
            # Handle List format (List[List[str]])
            return _add_columns_to_list_format(csv_content, columns_and_defaults, has_header)
        else:
            m = f"Unsupported csv_content type: {type(csv_content)}"
            logger.error(m)
            raise ValueError(m)
            
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise

def _add_columns_to_dict_format(csv_content: bdm.DATA_OBJECT_LIST_TYPE, 
                                columns_and_defaults: Dict[str, Any]) -> bdm.DATA_OBJECT_LIST_TYPE:
    """Add columns to dictionary format csv data."""
    # Track which columns are actually added vs already exist
    added_columns = set()
    existing_columns = set()
    
    new_csv_data_list = []
    for row in csv_content[1:]:  # Skip header row as requested
        for col_name, default_value in columns_and_defaults.items():
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

def _add_columns_to_list_format(csv_content: bdm.DATA_ROW_LIST_TYPE, 
                                columns_and_defaults: Dict[str, Any],
                                has_header: bool) -> bdm.DATA_ROW_LIST_TYPE:
    """Add columns to list format csv data."""
    new_csv_data_list = []
    column_names = list(columns_and_defaults.keys())
    default_values = [str(columns_and_defaults[col]) for col in column_names]
    
    for i, row in enumerate(csv_content):
        new_row = row.copy()
        
        if i == 0 and has_header:
            # Add column names to header row
            new_row.extend(column_names)
        else:
            # Add default values to data rows
            new_row.extend(default_values)
        
        new_csv_data_list.append(new_row)
    
    logger.debug(f"Added columns '{column_names}' to list format csv_data_list.")
    return new_csv_data_list
#endregion csv_DATA_LIST_add_columns() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_LIST_remove_extra_columns() function
def csv_DATA_LIST_remove_extra_columns(cvs_content: bdm.DATA_OBJECT_LIST_TYPE,
                                     expected_columns: List[str]) -> bdm.DATA_OBJECT_LIST_TYPE:
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
# ---------------------------------------------------------------------------- +
#region csv_is_DATA_ROW_LIST_TYPE() function
def csv_is_DATA_ROW_LIST_TYPE(csv_content: bdm.DATA_OBJECT_LIST_TYPE) -> bool:
    """Check if a csv data list is of type DATA_ROW_LIST_TYPE."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot check type."
            logger.error(m)
            raise ValueError(m)
        return isinstance(csv_content, list) and all(isinstance(row, list) for row in csv_content)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_is_DATA_ROW_LIST_TYPE() function
# ---------------------------------------------------------------------------- +
#region csv_is_DATA_OBJECT_LIST_TYPE() function
def csv_is_DATA_OBJECT_LIST_TYPE(csv_content: bdm.DATA_OBJECT_LIST_TYPE) -> bool:
    """Check if a csv data list is of type DATA_OBJECT_LIST_TYPE."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot check type."
            logger.error(m)
            raise ValueError(m)
        return isinstance(csv_content, list) and all(isinstance(row, dict) for row in csv_content)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_is_DATA_ROW_LIST_TYPE() function
# ---------------------------------------------------------------------------- +
#region csv_is_DATA_ROW_DICT_TYPE() function
def csv_is_DATA_ROW_DICT_TYPE(csv_content: bdm.DATA_ROW_DICT_TYPE) -> bool:
    """Check if a csv data list is of type DATA_ROW_DICT_TYPE."""
    return csv_is_DATA_OBJECT_LIST_TYPE(csv_content)
#endregion csv_is_DATA_ROW_DICT_TYPE() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_ROW_LIST_remove_columns_by_index() function
def csv_DATA_ROW_LIST_remove_columns_by_index(csv_content: bdm.DATA_ROW_LIST_TYPE, 
                                         column_indices: int | List[int]) -> bdm.DATA_ROW_LIST_TYPE:
    """Remove columns by index from a csv data list (List[List[str]] format)."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot remove columns."
            logger.error(m)
            raise ValueError(m)
        if not csv_is_DATA_ROW_LIST_TYPE(csv_content):
            m = "The csv_data_list is not of type DATA_ROW_LIST_TYPE, cannot add header row."
            logger.error(m)
            raise ValueError(m)
        
        # Ensure column_indices is a list
        if isinstance(column_indices, int):
            indices_to_remove = [column_indices]
        else:
            indices_to_remove = list(column_indices)
        
        # Sort indices in descending order to avoid index shifting issues
        indices_to_remove.sort(reverse=True)
        
        new_csv_data_list = []
        for row in csv_content:
            new_row = row.copy()  # Create a copy to avoid modifying original
            # Remove columns from right to left (highest index first)
            for col_index in indices_to_remove:
                if 0 <= col_index < len(new_row):
                    del new_row[col_index]
            new_csv_data_list.append(new_row)
        
        logger.debug(f"Removed column indices '{column_indices}' from csv_data_list.")
        return new_csv_data_list
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_ROW_LIST_remove_columns_by_index() function
# ---------------------------------------------------------------------------- +
#region csv_DATA_ROW_LIST_remove_columns_by_name() function
def csv_DATA_ROW_LIST_remove_columns_by_name(csv_content: bdm.DATA_ROW_LIST_TYPE, 
                                        column_names: str | List[str]) -> bdm.DATA_ROW_LIST_TYPE:
    """Remove columns by name from a csv data list (List[List[str]] format with header row)."""
    try:
        if not csv_content:
            m = "The csv_data_list is empty, cannot remove columns."
            logger.error(m)
            raise ValueError(m)
        if not csv_is_DATA_ROW_LIST_TYPE(csv_content):
            m = "The csv_data_list is not of type DATA_ROW_LIST_TYPE, cannot add header row."
            logger.error(m)
            raise ValueError(m)
        
        if not csv_DATA_LIST_has_header_row(csv_content, column_names):
            raise ValueError("Cannot remove columns by name without header row.")
        
        # Ensure column_names is a list
        if isinstance(column_names, str):
            names_to_remove = [column_names]
        else:
            names_to_remove = list(column_names)
        
        # Get header row and find indices of columns to remove
        header_row = csv_content[0]
        indices_to_remove = []
        
        for name in names_to_remove:
            try:
                index = header_row.index(name)
                indices_to_remove.append(index)
            except ValueError:
                logger.warning(f"Column '{name}' not found in header row.")
        
        if not indices_to_remove:
            logger.debug("No valid column names found to remove.")
            return csv_content
        
        # Use the index-based function
        return csv_DATA_ROW_LIST_remove_columns_by_index(csv_content, indices_to_remove)
        
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion csv_DATA_ROW_LIST_remove_columns_by_name() function
# ---------------------------------------------------------------------------- +
