# ---------------------------------------------------------------------------- +
# test_budman_data_context_interface.py
"""BudManDataContextInterface: A concrete implementation of the 
BudManDataContextBaseInterface for the Budget Manager application. This can be
super class or used directly in a project. The bare minium functionality is provided.
It is suitable to be used as a data_context object for an instance of the
BudManDataContextClientInterface. Most applications will inherit this and
override the methods for more specific functionality.
"""
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from abc import ABC, abstractmethod
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budget_manager_domain_model import design_language_namespace as bdmns
from budman_data_context_interface import BudManDataContextBaseInterface
import budman_model as p3bm
from budman_model import P2, P4, P6, P8, P10

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(bdmns.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
class BudManDataContextInterface(BudManDataContextBaseInterface):
    """BudManDataContextInterface: A concrete implementation of the
    BudManDataContextBaseInterface for the Budget Manager application.
    
    This class provides a basic implementation of the data context. Herein, the
    data_context interface will perform some actions locally and pass others
    to the budget domain model (BDM) for processing. Methods assumed to be
    implemented by the BDM are not implemented here, rather raise a 
    NotImplementedError exception. 

    The backing values for the properties are fully implemented for the 
    data_context interface. Overrides in a subclass should be aware and use
    super() to access the base class properties and methods appropriately.
    """
    def __init__(self, bdm : p3bm.BudgetDomainModel = None) -> None:
        super().__init__()
        self._initialized = False
        self._FI_KEY = None
        self._WF_KEY = None
        self._WB_TYPE = None
        self._WB_NAME = None
        self._BUDMAN_STORE = None
        self._WORKBOOKS : bdmns.WORKBOOK_LIST = None
        self._LOADED_WORKBOOKS : bdmns.LOADED_WORKBOOK_LIST = None
        self._budget_domain_model : p3bm.BudgetDomainModel = bdm

    #region Concrete Properties
    @property
    def INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        return self._initialized
    @INITIALIZED.setter
    def INITIALIZED(self, value: bool) -> None:
        """Set the initialized state of the data context."""
        self._initialized = value

    @property
    def dc_FI_KEY(self) -> str:
        """Return the FI_KEY for the financial institution."""
        return self._FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """Set the FI_KEY for the financial institution."""
        self._FI_KEY = value
    @property
    def dc_WF_KEY(self) -> str:
        """Return the WF_KEY for the workflow."""
        return self._WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """Set the WF_KEY for the workflow."""
        self._WF_KEY = value
    @property
    def dc_WB_TYPE(self) -> str:
        """Return the WB_TYPE workbook type."""
        return self._WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the WB_TYPE workbook type."""
        self._WB_TYPE = value
    @property
    def dc_WB_NAME(self) -> str:
        """Return the WB_NAME workbook name."""
        return self._WB_NAME
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
        """Set the WB_NAME workbook name."""
        self._WB_NAME = value
    @property
    def dc_BUDMAN_STORE(self) -> str:
        """Return the BUDMAN_STORE jsonc definition."""
        return self._BUDMAN_STORE
    @dc_BUDMAN_STORE.setter
    def dc_BUDMAN_STORE(self, value: str) -> None:
        """Set the BUDMAN_STORE jsonc definition."""
        self._BUDMAN_STORE = value
    @property
    def dc_WORKBOOKS(self) -> bdmns.WORKBOOK_LIST:
        """Return the list of workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its absolute path.
        """
        return self._WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: bdmns.WORKBOOK_LIST) -> None:
        """Set the list of workbooks in the DC."""
        self._WORKBOOKS = value
    @property
    def dc_LOADED_WORKBOOKS(self) -> bdmns.LOADED_WORKBOOK_LIST:
        """Return the list of loaded workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its Workbook object.
        """
        return self._LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: bdmns.LOADED_WORKBOOK_LIST) -> None:
        """Set the list of loaded workbooks in the DC."""
        self._LOADED_WORKBOOKS = value
    #endregion Concrete Properties
    # ------------------------------------------------------------------------ +
    #region Concrete Methods
    def initialize(self) -> None:
        """Initialize the data context."""
        self.dc_FI_KEY = None
        self.dc_WF_KEY = None
        self.dc_WB_TYPE = None
        self.dc_WB_NAME = None
        self.dc_BUDMAN_STORE = []
        self.dc_WORKBOOKS = []
        self.dc_LOADED_WORKBOOKS = []
        self.INITIALIZED = True
        return self
    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return isinstance(fi_key, str) and len(fi_key) > 0
    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """Validate the provided WF_KEY."""
        return isinstance(wf_key, str) and len(wf_key) > 0
    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """Validate the provided WB_TYPE."""
        return isinstance(wb_type, str) and len(wb_type) > 0
    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """Validate the provided WB_NAME."""
        return isinstance(wb_name, str) and len(wb_name) > 0
    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """Validate the provided workbook reference."""
        return isinstance(wb_ref, str) and len(wb_ref) > 0
    def WORKBOOK_loaded(self, wb_name: str) -> bool:
        """Indicates whether the named workbook is loaded."""
        _ = p3u.is_str_or_none("wb_name", wb_name, raise_TypeError=True)
        # Reference the DC.LOADED_WORKBOOKS property.
        if (not self.INITIALIZED or 
                self.dc_LOADED_WORKBOOKS is None or 
                not isinstance(self.dc_LOADED_WORKBOOKS, list)):
            return False
        lwbl = self.dc_LOADED_WORKBOOKS
        if len(lwbl) == 0:
            return False
        for l_wb_name, _ in lwbl:
            if l_wb_name == wb_name:
                return True
        return False
    def WORKBOOK_load(self, wb_name: str) -> Workbook:
        """Load the specified workbook by name."""
        wb_path = Path(wb_name)
        if not wb_path.exists():
            wb = Workbook()
        else:
            try:
                wb = Workbook(wb_path)
            except Exception as e:
                logger.error(f"Failed to load workbook '{wb_name}': {e}")
                raise
        self.dc_WB_NAME = wb_name
        self.WORKBOOK_add(wb_name, wb)
        return wb 
    def WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """Save the specified workbook by name."""
        wb_path = Path(wb_name)
        try:
            wb.save(wb_path)
        except Exception as e:
            logger.error(f"Failed to save workbook '{wb_name}': {e}")
            raise
        return None
    def WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        raise NotImplementedError(
            "WORKBOOK_remove method is not implemented in this interface.")
    def WORKBOOK_add(self, wb_name: str, wb: Workbook) -> None:
        """Add a new workbook to the data context."""
        self.dc_LOADED_WORKBOOKS.append((wb_name, wb))
        return None
    def BUDMAN_STORE_load(self, file_path: str) -> None:
        """Load the BUDMAN_STORE from the specified file path. NotImplementedError.
        The design presumes that the BUDMAN_STORE is managed by the downstream
        Model implementation, that the budget_domain_model uses it to 
        initialize the state of the BDM. This implementation has no BDM.
        """
        raise NotImplementedError(
            "BUDMAN_STORE_load method is not implemented in this interface.")       
        return None
    def BUDMAN_STORE_save(self, file_path: str) -> None:
        """Save the BUDMAN_STORE to the specified file path."""
        raise NotImplementedError(
            "BUDMAN_STORE_save method is not implemented in this interface.")
    #endregion Concrete Methods

