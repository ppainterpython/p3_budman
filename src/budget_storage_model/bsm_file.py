#region    bdm_file.py module
""" Implements BSMFile Class.

    The BDM uses a "file tree" as a shortcut to locate files in the budget
    domain model. BDM assumes that files are stored in folders in a storage 
    system, which might be a cloud storage system, a local file system, or
    a hybrid of both. The Budget Storage Model handles actual binding to a
    a particular storage system.

    For CLI and other simple user interfaces, a file tree is a tree structure
    based on the Treelib module. This module provides a simple API to create 
    and update a file tree for a specified budget domain model based on a url.

    Once initialized, the file_tree is saved in a .json file in the root of the
    bdm_store folder. Other functions are used to look up information from the
    file_tree about folders and files using an int file_index or dir_index. The 
    index values are unique to the entire tree. 
"""
#endregion bsm_file.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

# third-party modules and packages
import p3_utils as p3u, p3logging as p3l

# local modules and packages
from budget_storage_model import (bsm_URL_verify_file_scheme,)

#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

#region    BSMFile Class
class BSMFile:
    BSM_FILE = "file"
    BSM_FOLDER = "folder"
    def __init__(self, 
                 type:str=BSM_FILE, 
                 dir_index:int=-1, 
                 file_index:int=-1, 
                 file_url:Optional[str]=None,
                 valid_prefixes:List[str]=[],
                 valid_wb_types:List[str]=[]) -> None:
        self.type: str = type
        self.dir_index: int = dir_index
        self.file_index: int = file_index
        self.file_url: Optional[str] = file_url
        self._valid_prefixes: List[str] = valid_prefixes if valid_prefixes else []
        self._valid_wb_types: List[str] = valid_wb_types if valid_wb_types else []
        self._path: Path = None
        self._full_filename: Optional[str] = None
        self._filename: Optional[str] = None
        self._extension: Optional[str] = None
        self._prefix: Optional[str] = None
        self._wb_type: Optional[str] = None
        self._in_bdm: bool = False
        self.update()

    def __str__(self) -> str:
        return self.full_filename

    @property
    def full_filename(self) -> Optional[str]:
        """Return the full filename (with extension) of the file."""
        return self._full_filename
    @property
    def filename(self) -> Optional[str]:
        """Return the filename (without extension)."""
        return self._filename
    @property
    def extension(self) -> Optional[str]:
        """Return the file extension."""
        return self._extension
    @property
    def abs_path(self) -> Optional[Path]:
        """Return the absolute file path."""
        return self._path
    @property
    def prefix(self) -> Optional[str]:
        """Return the workflow prefix from the filename."""
        return self._prefix
    @property
    def wb_type(self) -> Optional[str]:
        """Return the workbook type from the filename."""
        return self._wb_type
    @property
    def in_bdm(self) -> bool:
        """Return True if the file is in the BDM_STORE."""
        return self._in_bdm
    @in_bdm.setter
    def in_bdm(self, value: bool) -> None:
        """Set the in_bdm property."""
        if not isinstance(value, bool):
            raise ValueError("in_bdm must be a boolean value.")
        self._in_bdm = value
    def verify_url(self) -> Optional[Path]:
        """Verify the file URL."""
        try:
            return bsm_URL_verify_file_scheme(self.file_url)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            return False
    def update(self) -> None:
        """Update the prefix and wb_type properties based on the filename."""
        if not self.file_url:
            return
        self._path = Path.from_uri(self.file_url)
        self._full_filename = self._path.name
        self._filename = self._path.stem
        self._extension = self._path.suffix
        filename_sans_prefix: str = self._filename
        for prefix in self._valid_prefixes:
            # prefix must be at the start of the filename
            if self._filename.startswith(prefix):
                self._prefix = prefix
                self._filename = self._filename[len(prefix):]
                break

        for wb_type in self._valid_wb_types:
            # wb_type must be at the end of the filename_sans_prefix
            if self._filename.endswith(wb_type):
                self._wb_type = wb_type
                self._filename = self._filename[:-len(wb_type)]
                break

#endregion BSMFile Class
# ---------------------------------------------------------------------------- +
