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
    VALID_WB_TYPE_VALUES, WB_FILETYPE_MAP
)
from budget_storage_model import (bsm_verify_folder, bsm_get_workbook_names)
                                  
from .model_base_interface import BDMBaseInterface
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
    loaded : bool = False
    wb_index : Optional[int] = None
    _content : Any = field(init=False) # Not included in todict() serialization

    @property
    def content(self) -> Any:
        """ content property returns the workbook content. """
        return self._content
    @content.setter
    def content(self, value: Any) -> None:
        """ content property setter sets the workbook content. """
        self._content = value