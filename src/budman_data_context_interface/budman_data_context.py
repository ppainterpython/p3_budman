# ---------------------------------------------------------------------------- +
# test_budman_data_context_interface.py
""" BudManDataContext: A concrete implementation BudManDataContextBaseInterface 
    for the Budget Manager application. 
    
    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers. A DC is an abstraction for data used by ViewModels
    and Models and even directly by a View.

    The properties and methods reflect the application design language, in terms
    of the domain model objects, command processing, etc. 

    A Data Context is not a Model, nor a View Model, it is a bridge between
    the two. It provides a way to access and manipulate data without exposing
    the underlying implementation details.

    Each property and method herein documents its purpose. This class provides 
    a minimalist implementation of the interface, which can be
    extended by subclasses to provide more specific functionality. Here there 
    is no reference to outside data objects, such as a Model or ViewModel. 
    Subclasses may override or extend the default DC behavior.

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
class BudManDataContext(BudManDataContextBaseInterface):
    """An implementation of BudManDataContextBaseInterface for Budget Manager.
    
    This class provides a basic implementation of the data context. Herein, the
    data_context interface will perform some actions locally and pass others
    to the budget domain model (BDM) for processing. Methods assumed to be
    implemented by the BDM are not implemented here, rather raise a 
    NotImplementedError exception. 

    The backing values for the properties are fully implemented for the 
    data_context interface. Overrides in a subclass should be aware and use
    super() to access the base class properties and methods appropriately.
    """
    # ------------------------------------------------------------------------ +
    def __init__(self) -> None:
        self._dc_initialized = False 
        self._FI_KEY = None       
        self._WF_KEY = None       
        self._WB_TYPE = None      
        self._WB_NAME = None      
        self._BUDMAN_STORE = None 
        self._WORKBOOKS : bdmns.WORKBOOK_LIST = None # from BudManDataContextBaseInterface
        self._LOADED_WORKBOOKS : bdmns.LOADED_WORKBOOK_LIST = None # from BudManDataContextBaseInterface

    #region Abstract Properties
    @property
    def dc_INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        return self._dc_initialized
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """Set the initialized state of the data context."""
        self._dc_initialized = value

    @property
    def dc_FI_KEY(self) -> str:
        """Return the FI_KEY of the current Financial Institution.
        Current means that the other data in the DC is for this FI.
        """
        return self._FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """Set the FI_KEY of the current Financial Institution."""
        self._FI_KEY = value

    @property
    def dc_WF_KEY(self) -> str:
        """Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        return self._WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """Set the WF_KEY for the workflow."""
        self._WF_KEY = value

    @property
    def dc_WB_TYPE(self) -> str:
        """Return the current WB_TYPE (workbook type) .
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self._WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the WB_TYPE workbook type."""
        self._WB_TYPE = value

    @property
    def dc_WB_NAME(self) -> str:
        """Return the current WB_NAME workbook name.
        
        Current means that the other data in the DC is for this workbook, and 
        that a user has specified this workbook specifically by name.
        This indicates the name of the workbook being processed, e.g., 'budget.xlsx',
        """
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
        """Return the list of workbooks in the DC."""
        return self._WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: bdmns.WORKBOOK_LIST) -> None:
        """Set the list of workbooks in the DC."""
        self._WORKBOOKS = value

    @property
    def dc_LOADED_WORKBOOKS(self) -> bdmns.LOADED_WORKBOOK_LIST:
        """Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        return self._LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: bdmns.LOADED_WORKBOOK_LIST) -> None:
        """Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        self._LOADED_WORKBOOKS = value
    #endregion Abstract Properties
    # ------------------------------------------------------------------------ +
    #region Abstract Methods
    def dc_initialize(self) -> None:
        """Initialize the data context."""
        self.dc_FI_KEY = None
        self.dc_WF_KEY = None
        self.dc_WB_TYPE = None
        self.dc_WB_NAME = None
        self.dc_BUDMAN_STORE = []
        self.dc_WORKBOOKS = []
        self.dc_LOADED_WORKBOOKS = []
        self.dc_INITIALIZED = True
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

    def dc_WORKBOOK_loaded(self, wb_name: str) -> bool:
        """Indicates whether the named workbook is loaded."""
        _ = p3u.is_str_or_none("wb_name", wb_name, raise_TypeError=True)
        # Reference the DC.LOADED_WORKBOOKS property.
        if (not self.dc_INITIALIZED or 
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

    def dc_WORKBOOK_load(self, wb_name: str) -> Workbook:
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
        self.dc_WORKBOOK_add(wb_name, wb)
        return wb 

    def dc_WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """Save the specified workbook by name."""
        wb_path = Path(wb_name)
        try:
            wb.save(wb_path)
        except Exception as e:
            logger.error(f"Failed to save workbook '{wb_name}': {e}")
            raise
        return None

    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        wb_path = Path(wb_name)
        if not wb_path.exists():
            logger.error(f"Workbook '{wb_name}' does not exist.")
            return None
        try:
            wb_path.unlink()  # Remove the file
            # Remove from loaded workbooks if it exists
            self.dc_LOADED_WORKBOOKS = [
                (name, wb) for name, wb in self.dc_LOADED_WORKBOOKS if name != wb_name
            ]
        except Exception as e:
            logger.error(f"Failed to remove workbook '{wb_name}': {e}")
            raise
        return None

    def dc_WORKBOOK_add(self, wb_name: str, wb: Workbook) -> None:
        """Add a new workbook to the data context."""
        self.dc_LOADED_WORKBOOKS.append((wb_name, wb))
        return None

    def dc_BUDMAN_STORE_load(self, file_path: str) -> None:
        """Load the BUDMAN_STORE from the specified file path. NotImplementedError.
        The design presumes that the BUDMAN_STORE is managed by the downstream
        Model implementation, that the budget_domain_model uses it to 
        initialize the state of the BDM. This implementation has no BDM.
        """
        logger.error("BUDMAN_STORE_load method is not implemented in this interface.")
        return None

    def dc_BUDMAN_STORE_save(self, file_path: str) -> None:
        """Save the BUDMAN_STORE to the specified file path."""
        logger.error("BUDMAN_STORE_save method is not implemented in this interface.")
        return None

    #endregion Abstract Methods
    # ------------------------------------------------------------------------ +
