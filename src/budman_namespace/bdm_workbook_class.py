# ---------------------------------------------------------------------------- +
#region bdm_workbook_class.py module
""" bdm_workbook_class.py BDMWorkbook class implementation."""
#endregion bdm_workbook_class.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from dataclasses import dataclass, asdict, field
import logging
from urllib.parse import urlparse, unquote
from pathlib import Path
from typing import Any, Optional, Union, List, Dict
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook
# local modules and packages
import budman_namespace.design_language_namespace as bdm
from budman_namespace.design_language_namespace import (P1, P2, P3, P4, P5, P6, P7, P8, P9, P10)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
ID_SEPARATOR = "|"
BDMWORKBOOK_SCHEMA_VERSION = "1.3.0"
# Schema History:
#  1.0.0 - 06/19/2025 - Initial version with basic attributes.   
#  1.1.0 - 07/06/2025 - added wb_type, wb_content attributes.
#  1.2.0 - 07/26/2025 - added wb_last_error attribute.
#  1.3.0 - 08/04/2025 - Added wf_folder_url attribute, added wb_schema_version 
#                       and tracking schema changes.
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
@dataclass
class BDMWorkbook:
    #region    doc string
    """ BDMWorkbook is basic wrapper around file-based data objects. It 
    holds the metadata attributes for a particular workbook. BDMWorkbook objects
    are serialized for storage. A url is used to identify the workbook, and
    the workbook is loaded from the storage system when needed.

    Attributes:
        wb_id (str): Unique identifier for the workbook. It is the wf_folder 
        value appended with wb_name with '|' as a separator. 
    """
    #endregion doc string
    # ------------------------------------------------------------------------ +
    # region   dataclass object attributes
    wb_name : str = None
    wb_filename : str = None
    wb_filetype : str = None #Optional[str] = "not_set"
    wb_type : str = field(default=bdm.WB_TYPE_UNKNOWN) # added 07/06/2025
    wb_url : str = None
    fi_key: str = None
    wf_key: str = None
    wf_purpose: str = None
    # wf_folder_id: str = None # Removed 08/04/2025, added wf_folder_url at that time.
    wf_folder_url: str = None
    wf_folder: str = None
    wb_loaded : bool = False
    wb_content: bdm.WORKBOOK_CONTENT_TYPE = None  # added 07/06/2025
    wb_last_error: Optional[str] = None  # added 07/26/2025
    wb_schema_version: str = BDMWORKBOOK_SCHEMA_VERSION # added 08/04/2025
    #endregion dataclass object attributes
    # ------------------------------------------------------------------------ +
    #region __getitem__() and __setitem__() methods
    def __getitem__(self, key: str):
        # Try to get a property or attribute by name
        if (hasattr(self.__class__, key) and 
            isinstance(getattr(self.__class__, key), property)):
            return getattr(self, key)
        elif hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(f"{key} is not a valid property or attribute of BDMWorkbook")

    def __setitem__(self, key: str, value):
        # Try to set a property or attribute by name
        if hasattr(self.__class__, key) and isinstance(getattr(self.__class__, key), property):
            setattr(self, key, value)
        elif hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"{key} is not a valid property or attribute of BDMWorkbook")    
    #endregion __getitem__() and __setitem__() methods
    # ------------------------------------------------------------------------ +
    #region internal methods: __repr__
    def __repr__(self) -> str:
        """BDMWorkbook.__repr__() method."""
        return (f"<BDMWorkbook[{hex(id(self))}]: "
                f"wb_id={self.wb_id!r}, "
                f"wb_type={self.wb_type!r}, "
                f"wb_loaded={self.wb_loaded}>")
    #endregion internal methods: __repr__
    # ------------------------------------------------------------------------ +
    #region internal methods: to_dict(self)
    def to_dict(self) -> dict[str, Any]:
        """Convert the BDMWorkbook instance to a dictionary.
        Always excludes the wb_content attribute to avoid serialization issues."""
        tmp_obj: Any = self.wb_content
        self.wb_content = None
        ret_dict = asdict(self)
        self.wb_content = tmp_obj
        return ret_dict
    #endregion internal methods: to_dict(self)
    # ------------------------------------------------------------------------ +
    #region BDMWorkbook properties
    @property
    def wb_id(self) -> str:
        """ combine wf_folder ID_SEPARATOR wb_name. """
        return f"{self.wf_folder}{ID_SEPARATOR}{self.wb_name}"
    @wb_id.setter
    def wb_id(self, value: str) -> None:
        """ set the wb_name. """
        raise NotImplementedError("BDMWorkbook.wb_id is a read-only property, "
                                  "it is derived from wf_folder and wb_name.")
    @property
    def name(self) -> str:
        """ name property returns the wb_name. """
        return self.wb_name
    @name.setter
    def name(self, value: str) -> None:
        """ set the wb_name. """
        self.wb_name = value
    #endregion BDMWorkbook properties
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region BDMWorkbook class methods
    @classmethod
    def check_schema(cls, wb_data: dict[str, Any]) -> Dict[str, str]:
        """Check wb_data attributes as suitable to construct BDMWorkbook(**wb_data).
        
        As the schema evolves, this method is to help older persistent data be
        converted to recent schema versions. It checks for additions, deletions, 
        adjustments in the attributes and values of the dataclass.
        """
        p3u.is_not_obj_of_type("wb_data", wb_data, dict, raise_error=True)
        copy = wb_data.copy()
        if "wf_folder_id" in copy:
            del copy["wf_folder_id"]
        if "wb_schema_version" not in copy:
            copy["wb_schema_version"] = BDMWORKBOOK_SCHEMA_VERSION
        if "wf_folder_url" not in copy:
            copy["wf_folder_url"] = None
        return copy
    #endregion BDMWorkbook class methods
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region BDMWorkbook instance methods
    # ------------------------------------------------------------------------ +
    #region wb_index_display_str
    def wb_index_display_str(self, wb_index:int=-1) -> str:
        """ Return an indexed string representation of the BDMWorkbook object. """
        # Test output layout
        #{P2}{FI_WORKBOOK_DATA_COLLECTION}: {wdc_count}\n"
        #{P4}{WB_INDEX:8}{P2}{WB_ID:50}{P2}{WB_CONTENT:30}{P2}{WB_TYPE:15}{P2}{WB_TYPE:15}{P2}{WF_KEY:15}{P2}{WF_PURPOSE:10}{P2}\n
        #
        check = self.check_wb_url()
        wb_status: str = "found"
        if not check:
            wb_status = "not found"
        elif self.wb_loaded:
            wb_status = self.get_wb_content_repr()
        else:
            wb_status = "unloaded"
        wb_info = self.wb_info_display_str()
        s = f"{P6}{str(wb_index):>4}{P4}{str(wb_info):150}"
        return s
    #endregion wb_index_display_str
    # ------------------------------------------------------------------------ +
    #region wb_info_display_str
    def wb_info_display_str(self) -> str:
        """ Return a string representation of basic BDMWorkbook info. """
        # format: {WB_ID:50}{P2}{WB_CONTENT:30}{P2}{WB_TYPE:15}{P2}{WB_TYPE:15}{P2}{WF_KEY:15}{P2}{WF_PURPOSE:10}{P2}\n
        check = self.check_wb_url()
        wb_status: str = "found"
        if not check:
            wb_status = "not found"
        elif self.wb_loaded:
            wb_status = self.get_wb_content_repr()
        else:
            wb_status = "unloaded"
        s = f"{str(self.wb_id):50}{P2}{str(self.wb_type):15}{P2}{wb_status:30}{P2}"
        return s
    #endregion wb_info_display_str
    # ------------------------------------------------------------------------ +
    #region wb_info_show_str
    def wb_info_dict(self,wb_index:int,hdr:bool=False) -> Union[Dict, List]:
        """ Return a dictionary representation of basic BDMWorkbook info. """
        # fr += f"\n{P2}{FI_KEY:10} {WB_INDEX:6} {WB_ID:50} {WB_TYPE:15} "
        # fr += f"{WB_FILETYPE:6} {WF_KEY:20} {WF_PURPOSE:10} {WF_FOLDER:20} "
        # fr += f" {WB_CONTENT:30}"
        if hdr:
            return list(bdm.FI_KEY, bdm.WB_INDEX, bdm.WB_ID, bdm.WB_TYPE,
                       bdm.WB_FILETYPE, bdm.WF_KEY, bdm.WF_PURPOSE,
                       bdm.WF_FOLDER, bdm.WB_CONTENT)
        wb_status = self.get_wb_content_repr()
        return {
            bdm.FI_KEY: self.fi_key,
            bdm.WB_INDEX: wb_index,
            bdm.WB_ID: self.wb_id,
            bdm.WB_TYPE: self.wb_type,
            bdm.WB_FILETYPE: self.wb_filetype,
            bdm.WF_KEY: self.wf_key,
            bdm.WF_PURPOSE: self.wf_purpose,
            bdm.WF_FOLDER: self.wf_folder,
            bdm.WB_CONTENT: self.get_wb_content_repr()
        }
    #endregion wb_info_show_str
    # ------------------------------------------------------------------------ +
    #region get_wb_content_repr() method
    def get_wb_content_repr(self) -> str: 
        """Return a display string representation of the wb_content status."""
        try:
            wb_status: str = ""
            check = self.check_wb_url()
            if not check:
                wb_status = f"not found at URL:'{self.wb_url}'"
            elif self.wb_loaded and self.wb_content is not None:
                d = p3u.dscr(self.wb_content)
                if isinstance(self.wb_content, Workbook):
                    wb_status = f"{self.wb_content!r}"
                elif isinstance(self.wb_content, dict):
                    wb_status = f"{d}[{len(self.wb_content)} items]"
                else:
                    wb_status = f"{d}"
            else:
                wb_status = "unloaded"
            return wb_status
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m, None
    #endregion get_wb_content_repr() method
    # ------------------------------------------------------------------------ +
    #region display_brief_str
    def display_brief_str(self, wb_index:int=-1) -> str:
        """ Return a string representation of the BDMWorkbook object. """
        s = f"{P4}{str(wb_index):^6}{P4}{str(self.wb_name):35}{P2}"
        s += f"{str(self.wb_type):15}{P2}"
        return s
    #endregion display_brief_str
    # ------------------------------------------------------------------------ +
    #region abs_path()
    def abs_path(self) -> Optional[Path]:
        """ Return abs_path of wb_url. """
        try:
            if not self.wb_url:
                return None
            parsed_url = urlparse(self.wb_url)
            if parsed_url.scheme != "file":
                raise ValueError(f"URL scheme is not 'file': {parsed_url.scheme}")
            file_path = Path.from_uri(self.wb_url)
            return file_path
        except Exception as e:
            logger.error(f"Error checking URL '{self.wb_url}': {p3u.exc_err_msg(e)}")
            return False
    #endregion check_url
    # ------------------------------------------------------------------------ +
    #region check_wb_url()
    def check_wb_url(self) -> bool:
        """ Check if the workbook URL is valid. """
        try:
            if not self.wb_url:
                return False
            wb_path = Path().from_uri(self.wb_url)
            if not wb_path.exists():
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking URL '{self.wb_url}': {p3u.exc_err_msg(e)}")
            return False
    #endregion check_wb_url
    # ------------------------------------------------------------------------ +
    #region check_wb_url()
    def check_wb_url(self) -> bool:
        """ Check if the workbook URL is valid. """
        try:
            if not self.wb_url:
                return False
            wb_path = Path().from_uri(self.wb_url)
            if not wb_path.exists():
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking URL '{self.wb_url}': {p3u.exc_err_msg(e)}")
            return False
    #endregion check_wb_url
    # ------------------------------------------------------------------------ +
    #region determine_wb_type
    def determine_wb_type(self, wb_index:int=-1) -> str:
        """ Determine the wb_type based on the filename or set unknown. """
        abs_path: Path = self.abs_path()
        if abs_path is None:
            logger.error(f"BDMWorkbook: {self.wb_id} has no abs_path.")
            self.wb_type = bdm.WB_TYPE_UNKNOWN
            return self.wb_type
        fn = abs_path.stem
        for tn in bdm.VALID_WB_TYPE_VALUES:
            if tn in fn.lower():
                self.wb_type = tn
                return self.wb_type
        self.wb_type = bdm.WB_TYPE_UNKNOWN
        logger.warning(f"BDMWorkbook: {self.wb_id} has unknown wb_type")
        return self.wb_type
    #endregion determine_wb_type
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbook instance methods
    # ------------------------------------------------------------------------ +
