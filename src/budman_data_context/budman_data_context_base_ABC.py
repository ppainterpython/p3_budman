# ---------------------------------------------------------------------------- +
#region budman_data_context_base_ABC.py module
""" BudManDataContext_Base: Abstract Base Class interface.

    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers, providing an traction for data used by ViewModels, 
    Models and a View.

    The properties and methods reflect the BudMan application design language, 
    in terms of the domain model objects, command processing, etc. So, it is
    Budget Domain Model (BDM) aware, but not bound to a particular View, 
    ViewModel, or Model interface. But, the key concepts in the BDM concerning
    Financial Institutions (FI), Workflows (WF), Workbooks (WB), and the
    Budget Data Model (BDM_STORE) are all represented in the Data Context.

    A Data Context is not a Model, nor a View Model, it is a bridge between
    the two. It provides a way to access and manipulate data without exposing
    the underlying implementation details. It provides the application context
    at any moment in time, so the values change.

    This ABC defines the interface which is applied by concrete implementations.

    Each property and method herein documents its purpose. Most of the 
    properties and methods, if the return value is not None, return basic 
    data types, or aliases for those defined in the Design Language namespace.
    However, some of the return a BUDMAN_RESULT, which is a tuple of
    (success: bool, result: Any). This scheme is used to be forgiving when
    errors occur. The success value being True means no error and the result
    value is the output of the function. When success is False, the result
    value is a string describing the error.
"""
#endregion budman_data_context_base_ABC.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
from typing import Tuple, Any, Union, Dict
# third-party modules and packages
from openpyxl import Workbook
# local modules and packages
from src.budman_namespace import (
    DATA_CONTEXT, WORKBOOK_DATA_LIST, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION, WORKFLOW_DATA_COLLECTION,
    BDM_STORE, DATA_COLLECTION, WORKBOOK_OBJECT, BUDMAN_RESULT,
    WORKBOOK_CONTENT)
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManDataContext_Base(ABC):
    """Abstract Base Class Interface for Budget Manager Data Context."""
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Properties (abstract) 
    @property
    def dc_id(self) -> str:
        """Identify the data context implementation."""
        pass
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """Set the identifier for the data context implementation."""
        pass

    @property
    @abstractmethod
    def dc_VALID(self) -> bool:
        """Indicates whether the data context is valid."""
        pass
    
    @property
    @abstractmethod
    def dc_INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        pass
    @dc_INITIALIZED.setter
    @abstractmethod
    def dc_INITIALIZED(self, value: bool) -> None:
        """Set the initialized state of the data context."""
        pass

    @property
    @abstractmethod
    def dc_id(self) -> str:
        """Identify the data context implementation."""
        pass
    @dc_id.setter
    @abstractmethod
    def dc_id(self, value: str) -> None:
        """Set the identifier for the data context implementation."""
        pass

    @property
    @abstractmethod
    def dc_FI_OBJECT(self) -> str:
        """Return the FI_OBJECT of the current Financial Institution. """
        pass
    @dc_FI_OBJECT.setter
    @abstractmethod
    def dc_FI_OBJECT(self, value: str) -> None:
        """Set the FI_OBJECT of the current Financial Institution."""
        pass

    @property
    @abstractmethod
    def dc_FI_KEY(self) -> str:
        """Return the FI_KEY of the current Financial Institution.
        Current means that the other data in the DC is for this FI.
        """
        pass
    @dc_FI_KEY.setter
    @abstractmethod
    def dc_FI_KEY(self, value: str) -> None:
        """Set the FI_KEY of the current Financial Institution."""
        pass

    @property
    @abstractmethod
    def dc_WF_KEY(self) -> str:
        """Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        pass
    @dc_WF_KEY.setter
    @abstractmethod
    def dc_WF_KEY(self, value: str) -> None:
        """Set the WF_KEY for the workflow."""
        pass

    @property
    @abstractmethod
    def dc_WF_PURPOSE(self) -> str:
        """Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        pass
    @dc_WF_PURPOSE.setter
    @abstractmethod
    def dc_WF_PURPOSE(self, value: str) -> None:
        """Set the WF_KEY for the workflow."""
        pass

    @property
    @abstractmethod
    def dc_WB_TYPE(self) -> str:
        """Return the current WB_TYPE (workbook type).
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        pass
    @dc_WB_TYPE.setter
    @abstractmethod
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the WB_TYPE workbook type."""
        pass

    @property
    @abstractmethod
    def dc_WB_NAME(self) -> str:
        """Return the current WB_NAME workbook name.
        
        Current means that the other data in the DC is for this workbook, and 
        that a user has specified this workbook specifically by name.
        This indicates the name of the workbook being processed, e.g., 'budget.xlsx',
        """
        pass
    @dc_WB_NAME.setter
    @abstractmethod
    def dc_WB_NAME(self, value: str) -> None:
        """Set the WB_NAME workbook name."""
        pass

    @property
    @abstractmethod
    def dc_WB_REF(self) -> str:
        """Return the current WB_REF workbook reference.
        
        Current means the wb_ref for the last operation on a named or referenced
        workbook. The other data in the DC is updated in a similar fashion.
        After an operation on 'all' workbooks, the dc_WB_REF is set to 'all'.
        """
        pass
    @dc_WB_REF.setter
    @abstractmethod
    def dc_WB_REF(self, value: str) -> None:
        """Set the WB_REF workbook reference."""
        pass

    @property
    @abstractmethod
    def dc_BDM_STORE(self) -> str:
        """Return the BDM_STORE jsonc definition."""
        pass
    @dc_BDM_STORE.setter
    @abstractmethod
    def dc_BDM_STORE(self, value: str) -> None:
        """Set the BDM_STORE jsonc definition."""
        pass

    @property
    @abstractmethod
    def dc_WORKBOOK_DATA_COLLECTION(self) -> WORKBOOK_DATA_COLLECTION:
        """Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.The WORKBOOK_DATA_COLLECTION
        is sorted by the key, wb_id, the wb_index is based on the sorted order."""
        pass
    @dc_WORKBOOK_DATA_COLLECTION.setter
    @abstractmethod
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_LIST) -> None:
        """Set the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.
        The WORKBOOK_DATA_COLLECTION should be sorted by the key,
        wb_id as it is updated. The wb_index should be based on the 
        sorted order of the WORKBOOK_DATA_COLLECTION.
        """
        pass

    @property
    @abstractmethod
    def dc_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """Return the list of workbooks in the DC."""
        pass
    @dc_WORKBOOKS.setter
    @abstractmethod
    def dc_WORKBOOKS(self, value: WORKBOOK_DATA_LIST) -> None:
        """Set the list of workbooks in the DC."""
        pass

    @property
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        pass
    @dc_LOADED_WORKBOOKS.setter
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        pass

    @property
    @abstractmethod
    def dc_EXCEL_WORKBOOKS(self) -> DATA_COLLECTION:
        """Return the collection of workbooks currently open in Excel."""
        pass
    @dc_EXCEL_WORKBOOKS.setter
    @abstractmethod
    def dc_EXCEL_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Set the collection of workbooks currently open in Excel."""
        pass
    #endregion BudManDataContext_Base Properties (abstract)
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Methods (abstract)
    @abstractmethod
    def dc_initialize(self) -> DATA_CONTEXT:
        """Initialize the data context."""
        pass

    @abstractmethod
    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        pass

    @abstractmethod
    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """Validate the provided WF_KEY."""
        pass

    @abstractmethod
    def dc_WF_PURPOSE_validate(self, wf_purpose: str) -> bool:
        """Validate the provided WF_PURPOSE."""
        pass

    @abstractmethod
    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """Validate the provided WB_TYPE."""
        pass

    @abstractmethod
    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """Validate the provided WB_NAME."""
        pass

    @abstractmethod
    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """Validate the provided workbook reference."""
        pass

    @abstractmethod
    def dc_WB_REF_resolve(self, wb_ref: str) -> Tuple[bool,int, str]:
        """Resolve a wb_ref to valid wb_index, wb_name, or ALL_KEY.

        Args:
            wb_ref (str|int): The wb_ref to validate and resolve. Expecting
            a str with a digit, a wb_name, or the ALL_KEY constant.

        Returns:
            Tuple[wb_all:bool, wb_index:int, wb_name:str]: 
                (True, -1, ALL_KEY) if wb_ref is ALL_KEY. 
                (False, wb_index, wb_name) for a valid index, adds wb_name match.
                (False, -1, wb_name) no valid index, found a wb_name.
                (False, -1, None) if wb_ref is invalid index or name value.
        
        Raises:
            TypeError: if wb_ref is not a str or int.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_loaded(self, wb_name: str) -> bool:
        """Indicates whether the named workbook is loaded."""
        pass

    @abstractmethod
    def dc_WORKBOOK_name(self, wb_index: int) -> str:
        """Return the wb_name associated with the give wb_index."""
        pass 
       
    @abstractmethod
    def dc_WORKBOOK_index(self, wb_name: str = None) -> int:
        """Return the index of a workbook based on wb_name.
        
        Args:
            wb_name (str): The name of the workbook to find.
        Returns:
            int: The index of the workbook in the WORKBOOK_DATA_LIST, or -1 if not found.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_by_index(self, wb_index: int) -> WORKBOOK_OBJECT:
        """Return (True, BDWWorkbook on success, (False, error_msg) on failure."""
        pass

    @abstractmethod
    def dc_WORKBOOK_find(self, find_key: str, value: str) -> WORKBOOK_OBJECT:
        """Locate and return a workbook by the key and value."""
        pass

    #region   WORKBOOK_CONTENT storage-related methods
    @abstractmethod
    def dc_WORKBOOK_url_get(self, wb_url: str) -> WORKBOOK_CONTENT:
        """Get the workbook content at wb_url."""
        pass

    @abstractmethod
    def dc_WORKBOOK_url_put(self, wb_content: WORKBOOK_CONTENT, wb_url:str) -> None:
        """Put the workbook content at wb_url."""
        pass

    @abstractmethod
    def dc_WORKBOOK_file_load(self, wb_index: str) -> BUDMAN_RESULT:
        """Load the specified workbook content by wb_index into dc_LOADED_WORKBOOKS.
           Returns:
                BUDMAN_RESULT: a Tuple[success: bool, result: Any].
                success = True, result is a message about the loaded workbook
                indicating the workbook is available in the 
                dc_LOADED_WORKBOOKS collection.
                success = False, result is a string describing the error.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_file_save(self, wb_index: str, wb_content: Workbook) -> None:
        """Save the specified workbook content by name."""
        pass
    #endregion WORKBOOK_CONTENT storage-related methods

    @abstractmethod
    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        pass

    @abstractmethod
    def dc_WORKBOOK_add(self, wb_name: str, wb: Union[Workbook, Dict]) -> None:
        """Add a new workbook to the data context."""
        pass

    @abstractmethod
    def dc_BDM_STORE_load(self, bdm_url: str) -> BDM_STORE:
        """Load a BDM_STORE from bdm_url, set dc_BDM_STORE.
        All relevant DC values reference the dc_BDM_STORE.
        """
        pass

    @abstractmethod
    def dc_BDM_STORE_save(self, bdm_store: BDM_STORE, bdm_url: str) -> None:
        """Save the BDM_STORE to the specified file path."""
        pass

    #endregion BudManDataContext_Base Methods (abstract)
    # ------------------------------------------------------------------------ +
