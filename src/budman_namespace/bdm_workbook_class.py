# ---------------------------------------------------------------------------- +
#region workbook_object.py module
""" workbook_object.py WorkbookObject class implementation.

"""
#endregion budget_domain_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from dataclasses import dataclass, asdict, field
import logging
from urllib.parse import urlparse, unquote
from pathlib import Path
from typing import Any, Optional, Union, List
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook
# local modules and packages
import budman_namespace.design_language_namespace as bdm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
ID_SEPARATOR = "|"
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
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
    wb_type : str = field(default="not-set")
    wb_url : str = None
    fi_key: str = None
    wf_key: str = None
    wf_purpose: str = None
    wf_folder_id: str = None
    wf_folder: str = None
    wb_loaded : bool = False
    #endregion dataclass object attributes
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
    #region BDMWorkbook instance methods
    # ------------------------------------------------------------------------ +
    #region display_str
    def display_str(self, wb_index:int=-1,wb_content:str="not loaded") -> str:
        """ Return a string representation of the BDMWorkbook object. """
        # Test output layout
        #{P2}{FI_WORKBOOK_DATA_COLLECTION}: {wdc_count}\n"
        #{P4}{WB_INDEX:8}{P2}{WB_ID:50}{P2}wb_loaded{P2}{WB_CONTENT:30}{P2}{WB_TYPE:15}{P2}{WB_TYPE:15}{P2}{WF_KEY:15}{P2}{WF_PURPOSE:10}{P2}\n
        #
        check = self.check_url()
        wb_status: str = "found"
        if not check:
            wb_status = "not found"
        elif self.wb_loaded:
            wb_status = "loaded"
        else:
            wb_status = "unloaded"
        s = f"{P6}{str(wb_index):>2}{P6}{str(self.wb_id):50}{P2}"
        s += f"{str(self.wb_type):14}{P2}{str(wb_status):^9}"
        s += f"{P2}{wb_content:30}{P2}"
        return s
    #endregion display_str
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
    #region check_url()
    def check_url(self) -> bool:
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
    #endregion check_url
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbook instance methods
    # ------------------------------------------------------------------------ +
