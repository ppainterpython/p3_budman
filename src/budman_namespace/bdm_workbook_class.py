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
from pathlib import Path
from typing import Any, Optional, Union, List
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook
# local modules and packages

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
