# ---------------------------------------------------------------------------- +
#region workbook_object.py module
""" workbook_object.py implements the WorkbookObject class 

"""
#endregion budget_domain_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from dataclasses import dataclass, asdict, field
import logging
from pathlib import Path
from typing import Any, Optional
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook
# local modules and packages
from budman_namespace import (
    WB_TYPE_BUDGET, WB_TYPE_TRANSACTIONS,DC_CHECK_REGISTERS,
    VALID_WB_TYPE_VALUES, WB_FILETYPE_MAP, P2, P4, P6,
    WB_REF, WB_NAME, WB_TYPE, WF_PURPOSE, WF_KEY, FI_KEY,
)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
@dataclass
class BDMWorkbook:
    """ BDMWorkbook is basic wrapper around file-based data objects. It 
    holds the metadata attributes for a particular workbook. BDMWorkbook objects
    are serialized for storage. A url is used to identify the workbook, and
    the workbook is loaded from the storage system when needed.
    """
    # region dataclass object attributes
    wb_name : str = None
    wb_filename : str = None
    wb_filetype : str = None #Optional[str] = "not_set"
    wb_type : str = None
    wb_url : str = None
    fi_key: str = None
    wf_key: str = None
    wf_purpose: str = None
    wf_folder_id: str = None
    wf_folder: str = None
    loaded : bool = False
    wb_index : Optional[int] = -1
    _content : Any = field(init=False,default=None) # Not included in todict() serialization
    #endregion dataclass object attributes
    # ------------------------------------------------------------------------ +
    #region BDMWorkbook properties
    @property
    def content(self) -> Any:
        """ content property returns the workbook content. """
        return self._content
    @content.setter
    def content(self, value: Any) -> None:
        """ content property setter sets the workbook content. """
        self._content = value
    @property
    def name(self) -> Any:
        """ wb_name property returns the workbook content. """
        return self.wb_name
    @name.setter
    def name(self, value: Any) -> None:
        """ wb_name property setter sets the workbook content. """
        self.wb_name = value
    #endregion BDMWorkbook properties
    # ------------------------------------------------------------------------ +
    #region BDMWorkbook methods
    # ------------------------------------------------------------------------ +
    #region soft_merge
    def soft_merge(self, source : "BDMWorkbook") -> bool:
        """ Return True is source is the same workbook, merge new information. """
        if not isinstance(source, BDMWorkbook):
            raise TypeError("source must be a BDMWorkbook instance")
        # First, evaluate if the two are the same workbook. Files can move
        # around in storage.
        if self.wb_name != source.wb_name or self.wb_url != source.wb_url:
            logger.debug(f"Rejected based on wb_name, or wb_url differences.")
            return None
        # For now, just update the wb_type if self.wb_type is None or empty.
        if not self.wb_type or self.wb_type == "not_set":
            self.wb_type = source.wb_type
        return False
    #endregion display_str
    # ------------------------------------------------------------------------ +
    #region display_str
    def display_str(self) -> str:
        """ Return a string representation of the BDMWorkbook object. """
        s = f"{P4}{str(self.wb_index):^6}{P2}{str(self.wb_type):15}{P2}"
        s += f"{str(self.wb_name):35}{P2}{str(self.wf_key):15}{P2}"
        s += f"{str(self.wf_purpose):10}{P2}{str(self.wf_folder_id):20}{P2}"
        s += f"{str(self.wf_folder):18}" #{P2}{str(self.wb_url):150}"
        return s
    #endregion display_str
    # ------------------------------------------------------------------------ +
    #region display_brief_str
    def display_brief_str(self) -> str:
        """ Return a string representation of the BDMWorkbook object. """
        s = f"{P4}{str(self.wb_index):^6}{P2}{str(self.wb_type):15}{P2}"
        s += f"{str(self.wb_name):35}"
        return s
    #endregion display_brief_str
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbook methods
    # ------------------------------------------------------------------------ +
    # ------------------------------------------------------------------------ +
    # ------------------------------------------------------------------------ +
