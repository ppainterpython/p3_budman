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
from typing import Any, Optional, Union, List
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook
# local modules and packages
from budman_namespace import (
    WB_TYPE_BUDGET, WB_TYPE_TRANSACTIONS,DC_CHECK_REGISTERS,
    VALID_WB_TYPE_VALUES, WB_FILETYPE_MAP, P2, P4, P6,
    WB_REF, WB_NAME, WB_TYPE, WF_PURPOSE, WF_KEY, FI_KEY,
    WORKBOOK_DATA_COLLECTION
)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
ID_SEPARATOR = "|"
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
    wb_type : str = field(default=WB_TYPE_TRANSACTIONS)
    wb_url : str = None
    fi_key: str = None
    wf_key: str = None
    wf_purpose: str = None
    wf_folder_id: str = None
    wf_folder: str = None
    wb_loaded : bool = False
    #endregion dataclass object attributes
    # ------------------------------------------------------------------------ +
    #region    BDMWorkbook __post_init__ method
    def __post_init__(self) -> None:
        """BDMWorkbook.__post_init__() method."""
        # Validate the wb_type.
        if not self.wb_type or self.wb_type == "not_set":
            self.wb_type = WB_TYPE_TRANSACTIONS
    #endregion BDMWorkbook __post_init__ method
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
    def wb_id(self) -> Any:
        """ combine wf_folder ID_SEPARATOR wb_name. """
        return f"{self.wf_folder}{ID_SEPARATOR}{self.wb_name}"
    @wb_id.setter
    def wb_id(self, value: Any) -> None:
        """ set the wb_name. """
        raise NotImplementedError("BDMWorkbook.wb_id is a read-only property, "
                                  "it is derived from wf_folder and wb_name.")
    @property
    def name(self) -> Any:
        """ name property returns the wb_name. """
        return self.wb_name
    @name.setter
    def name(self, value: Any) -> None:
        """ set the wb_name. """
        self.wb_name = value
    #endregion BDMWorkbook properties
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region BDMWorkbook instance methods
    # ------------------------------------------------------------------------ +
    #region wdc_update(wdc)
    def wdc_update(self, wdc : WORKBOOK_DATA_COLLECTION) -> bool:
        """ Add or replace self to the WORKBOOK_DATA_COLLECTION."""
        try:
            if not isinstance(wdc, dict):
                raise TypeError(f"wdc WORKBOOK_DATA_COLLECTION must be a dict,"
                                f"not a type: '{type(wdc).__name__}'")
            # First, is self in the wdc already.
            i = BDMWorkbook.wb_index(self.wb_id, wdc)
            if i == -1:
                # Not in the wdc, so add self.
                wdc[self.wb_id] = self
                logger.debug(f"Added {self.wb_id} to WORKBOOK_DATA_COLLECTION.")
                return True
            elif i < len(wdc):
                # Already in the wdc, so replace it.
                wdc[self.wb_id] = self
                logger.debug(f"Replaced {self.wb_id} in WORKBOOK_DATA_COLLECTION.")
                return True
            else:
                logger.error(f"Invalid index {i} for WORKBOOK_DATA_COLLECTION.")
                raise IndexError(f"Invalid index {i} for WORKBOOK_DATA_COLLECTION.")
        except Exception as e:
            logger.error(f"Error updating WORKBOOK_DATA_COLLECTION: {p3u.exc_err_msg(e)}")
            raise
    #endregion wdc_update(wdc)
    # ------------------------------------------------------------------------ +
    #region display_str
    def display_str(self, wb_index:int=-1) -> str:
        """ Return a string representation of the BDMWorkbook object. """
        s = f"{P4}{str(wb_index):>4}{P4}{str(self.wb_type):15}{P2}"
        s += f"{str(self.wb_name):35}{P2}{str(self.wf_key):15}{P2}"
        s += f"{str(self.wf_purpose):10}{P2}{str(self.wf_folder_id):20}{P2}"
        s += f"{str(self.wf_folder):18}" #{P2}{str(self.wb_url):150}"
        return s
    #endregion display_str
    # ------------------------------------------------------------------------ +
    #region display_brief_str
    def display_brief_str(self, wb_index:int=-1) -> str:
        """ Return a string representation of the BDMWorkbook object. """
        s = f"{P4}{str(wb_index):^6}{P2}{str(self.wb_type):15}{P2}"
        s += f"{str(self.wb_name):35}"
        return s
    #endregion display_brief_str
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbook instance methods
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region    BDMWorkbook Class methods
    # ------------------------------------------------------------------------ +
    #region    wb_index(wb_id: str, wdc: WORKBOOK_DATA_COLLECTION) -> Optional[int]
    @classmethod
    def by_index(cls, index: str|int, wdc: WORKBOOK_DATA_COLLECTION) -> Optional["BDMWorkbook"]:
        """Return the BDMWorkbook by index from the WORKBOOK_DATA_COLLECTION."""
        if not isinstance(wdc, dict):
            raise TypeError(f"wdc WORKBOOK_DATA_COLLECTION must be a dict,"
                            f"not a type: '{type(wdc).__name__}'")
        for i, wb in enumerate(wdc.values()):
            if i == int(index):
                return wb
        return None
    #endregion wb_index(wb_id: str, wdc: WORKBOOK_DATA_COLLECTION) -> Optional[int]
    # ------------------------------------------------------------------------ +
    #region    wb_index(wb_id: str, wdc: WORKBOOK_DATA_COLLECTION) -> Optional[int]
    @classmethod
    def wb_index(cls, wb_id: str, wdc: WORKBOOK_DATA_COLLECTION) -> int:
        """Return the index of the BDMWorkbook in the WORKBOOK_DATA_COLLECTION."""
        if not isinstance(wdc, dict):
            raise TypeError(f"wdc WORKBOOK_DATA_COLLECTION must be a dict,"
                            f"not a type: '{type(wdc).__name__}'")
        for index, wb in enumerate(wdc.values()):
            if wb.wb_id == wb_id:
                return index
        return -1
    #endregion wb_index(wb_id: str, wdc: WORKBOOK_DATA_COLLECTION) -> Optional[int]
    # ------------------------------------------------------------------------ +
    #region    wb_index_find(wdc: WORKBOOK_DATA_COLLECTION, attr_name, attr_value) -> Optional[int]
    @classmethod
    def wb_index_find(cls, wdc: WORKBOOK_DATA_COLLECTION, 
                      attr_name:str,attr_value:str) -> Union[int, List[int]]:
        """Return the index(es) of the BDMWorkbook(s) with attr_name: attr_value.
        
        returns:
            int: index of a single match, or -1 if not found.
            List[int]: list of indices if multiple matches found.
        """
        if not isinstance(wdc, dict):
            raise TypeError(f"wdc WORKBOOK_DATA_COLLECTION must be a dict,"
                            f"not a type: '{type(wdc).__name__}'")
        results : list = [i for i, (_,v) in enumerate(wdc.items()) 
                            if (hasattr(v, attr_name) and 
                                getattr(v, attr_name) == attr_value)] 
        if len(results) == 0:
            return -1
        if len(results) == 1:
            return results[0]
        return results
    #endregion wb_index_find(wb_id: str, wdc: WORKBOOK_DATA_COLLECTION) -> Optional[int]
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbook Class methods
    # ------------------------------------------------------------------------ +
