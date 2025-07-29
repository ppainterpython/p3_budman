# ---------------------------------------------------------------------------- +
#region budman_app_data_context_client.py module
"""DC_Binding: DI binding to BudManAppDataContext_Base.

    This class defines an Binding interface to a concrete provider of the
    BudManAppDataContext_Base interface. Binding is a reference to the Dependency
    Injection (DI) design pattern, where the client class is bound to an
    implementation of the BudManAppDataContext_Base interface at runtime. When 
    instantiated, it is given a reference to an object implementing the 
    interface. From the client side, the interface is used to interact with 
    the concrete data context without needing to know the details of the 
    implementation, as a client sdk pattern.

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

    Each property and method herein documents its purpose. Most of the 
    properties and methods, if the return value is not None, return basic 
    data types, or aliases for those defined in the Design Language namespace.
    However, some of the return a BUDMAN_RESULT, which is a tuple of
    (success: bool, result: Any). This scheme is used to be forgiving when
    errors occur. The success value being True means no error and the result
    value is the output of the function. When success is False, the result
    value is a string describing the error.
"""
#endregion budman_app_ data_context_client.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
from typing import Tuple, Union, Dict, Optional
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from budman_namespace.design_language_namespace import (
    DATA_COLLECTION, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION, WORKBOOK_OBJECT, BUDMAN_RESULT, 
    WORKBOOK_CONTENT, FI_OBJECT
    )
from budman_data_context import BudManAppDataContext_Base
import p3_utils as p3u
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManAppDataContext_Binding(BudManAppDataContext_Base):
    """DC_Binding: Interface for a Data Context clients.
    
    This interface is used by clients to interact with a Data Context (DC)
    without needing to know the details of the implementation. The design
    pattern is to bind a provider object as the data_context at creation time.
    If the target data_context does not implement the required interface
    BudManAppDataContext_Base Interface, a TypeError is raised.
    """
    # ------------------------------------------------------------------------ +
    #region Class Methods
    @classmethod
    def _valid_DC_Binding(cls, dc_binding: object) -> BudManAppDataContext_Base:
        """DC_Binding: Return dc_value if valid, else raise exception."""
        if dc_binding is None:
            raise ValueError("DC_Binding cannot be None")
        if not isinstance(dc_binding, BudManAppDataContext_Base):
            raise TypeError("DC_Binding must be subclass of BudManAppDataContext_Base")
        return dc_binding
    #endregion Class Methods
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Binding __init__() method
    def __init__(self) -> None:
        """DC_Binding: Simple instantiation-time initialization. 
        Binding happens at initialization-time."""
        super().__init__()
        self._data_context: BudManAppDataContext_Base = None
    #endregion BudManAppDataContext_Binding __init__() method
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Binding Properties
    @property
    def data_context(self) -> BudManAppDataContext_Base:
        """DC_Binding: Return the data context object."""
        return self._data_context
    @data_context.setter
    def data_context(self, dc_value: BudManAppDataContext_Base) -> None:
        """DC_Binding: Set the data context object."""
        self._data_context = dc_value

    @property
    def DC(self) -> BudManAppDataContext_Base:
        """DC_Binding: Return the data context.
        This is DC_Binding behavior. If the binding is not valid, an exception 
        is raised. The DC property is a reference to the data context object.
        """
        return BudManAppDataContext_Binding._valid_DC_Binding(self).data_context
    @DC.setter
    def DC(self, value: BudManAppDataContext_Base) -> None:
        """DC_Binding: Set the name of the data context.
        This is DC_Binding behavior. If the binding is not valid, an exception 
        is raised. The DC property is a reference to the data context object.
        """        
        self.data_context = BudManAppDataContext_Binding._valid_DC_Binding(value)
    #endregion BudManAppDataContext_Binding Properties
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Base Properties (concrete)
    @property
    def dc_id(self) -> str:
        """DC_Binding: Return the identifier for the data context implementation."""
        return self.DC.dc_id
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """DC_Binding: Set the identifier for the data context implementation."""
        self.DC.dc_id = value

    @property
    def dc_VALID(self) -> str:   
        """DC-Only: Indicates whether the data context is valid."""
        return self.DC.dc_VALID

    @property
    def dc_INITIALIZED(self) -> bool:
        """DC_Binding: Indicates whether the data context has been initialized."""
        return self.DC.dc_INITIALIZED
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """DC_Binding: Set the initialized state of the data context."""
        self.DC.dc_INITIALIZED = value

    @property
    def dc_FI_OBJECT(self) -> Optional[FI_OBJECT]:
        """DC_Binding: Return the FI_OBJECT of the current Financial Institution."""
        return self.DC.dc_FI_OBJECT 
    @dc_FI_OBJECT.setter
    def dc_FI_OBJECT(self, value: Optional[FI_OBJECT]) -> None:
        """DC_Binding: Set the FI_OBJECT of the current Financial Institution."""
        self.DC.dc_FI_OBJECT = value

    @property
    def dc_FI_KEY(self) -> Optional[str]:
        """DC_Binding: Return the FI_KEY for the financial institution."""
        return self.DC.dc_FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: Optional[str]) -> None:
        """DC_Binding: Set the FI_KEY for the financial institution."""
        self.DC.dc_FI_KEY = value

    @property
    def dc_WF_KEY(self) -> Optional[str]:
        """DC_Binding: Return the WF_KEY for the workflow."""
        return self.DC.dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: Optional[str]) -> None:
        """DC_Binding: Set the WF_KEY for the workflow."""
        self.DC.dc_WF_KEY = value

    @property
    def dc_WF_PURPOSE(self) -> Optional[str]:
        """DC_Binding: Return the WF_PURPOSE workbook type."""
        return self.DC.dc_WF_PURPOSE
    @dc_WF_PURPOSE.setter
    def dc_WF_PURPOSE(self, value: Optional[str]) -> None:
        """DC_Binding: Set the WF_PURPOSE workbook type."""
        self.DC.dc_WF_PURPOSE = value

    @property
    def dc_WB_ID(self) -> Optional[str]:
        """DC_Binding: Return the current WB_REF workbook reference value."""
        return self.DC.dc_WB_ID
    @dc_WB_ID.setter
    def dc_WB_ID(self, value: Optional[str]) -> None:
        """DC_Binding: Set the WB_REF workbook reference value."""
        self.DC.dc_WB_ID = value

    @property
    def dc_WB_TYPE(self) -> Optional[str]:
        """DC_Binding: Return the current WB_TYPE (workbook type).
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self.DC.dc_WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: Optional[str]) -> None:
        """DC_Binding: Set the WB_TYPE workbook type."""
        self.DC.dc_WB_TYPE = value

    @property
    def dc_WB_NAME(self) -> Optional[str]:
        """DC_Binding: Return the WB_NAME workbook name."""
        return self.DC.dc_WB_NAME
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: Optional[str]) -> None:
        """DC_Binding: Set the WB_NAME workbook name."""
        self.DC.dc_WB_NAME = value

    @property
    def dc_WB_INDEX(self) -> int:
        """DC_Binding: Return the WB_INDEX."""
        return self.DC.dc_WB_INDEX
    @dc_WB_INDEX.setter
    def dc_WB_INDEX(self, value: int) -> None:
        """DC_Binding: Set the WB_NAME workbook name."""
        self.DC.dc_WB_INDEX = value

    @property
    def dc_ALL_WBS(self) -> bool:
        """DC-Only: Return True if the current operation is on all workbooks."""
        return self.DC.dc_ALL_WBS
    @dc_ALL_WBS.setter
    def dc_ALL_WBS(self, value: bool) -> None:
        """DC-Only: Set the flag indicating if the current operation is on all workbooks."""
        if not isinstance(value, bool):
            raise TypeError(f"dc_WB_ALL_WORKBOOKS must be a bool, not {type(value).__name__}")
        self.DC.dc_ALL_WBS = value

    @property
    def dc_BDM_STORE(self) -> str:
        """DC_Binding: Return the BDM_STORE jsonc definition."""
        return self.DC.dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: str) -> None:
        """DC_Binding: Set the BDM_STORE jsonc definition."""
        self.DC.dc_BDM_STORE = value

    @property
    def dc_BDM_STORE_changed(self) -> bool:
        """DC-Binding: BDM_STORE content has been changed."""
        return self.DC.dc_BDM_STORE_changed
    @dc_BDM_STORE_changed.setter
    def dc_BDM_STORE_changed(self, value: bool) -> None:
        """DC-Binding: Set the BDM_STORE changed status."""
        self.DC.dc_BDM_STORE_changed = value

    @property
    def dc_WORKBOOK(self) -> WORKBOOK_OBJECT:
        """Return the current workbook in focus in the DC."""
        if not self.dc_VALID: return None
        return self.DC.dc_WORKBOOK
    @dc_WORKBOOK.setter
    def dc_WORKBOOK(self, value: WORKBOOK_OBJECT) -> None:
        """Set the current workbook in focus in the DC."""
        if not self.dc_VALID: return None
        if not isinstance(value, object):
            raise TypeError(f"dc_WORKBOOK must be an object, "
                            f"not a type: '{type(value).__name__}'")
        self.DC.dc_WORKBOOK = value

    @property
    def dc_WORKBOOK_DATA_COLLECTION(self) -> WORKBOOK_DATA_COLLECTION:
        """DC_Binding: Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.
        """
        if self.DC.dc_FI_KEY is None:
            return None
        return self.DC.dc_WORKBOOK_DATA_COLLECTION
    @dc_WORKBOOK_DATA_COLLECTION.setter
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_COLLECTION) -> None:
        """DC_Binding: Set the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key."""
        if self.DC.dc_FI_KEY is None:
            return None
        self.DC.dc_WORKBOOK_DATA_COLLECTION = value

    @property
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """DC_Binding: Return the list of loaded workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its Workbook object.
        """
        return self.DC.dc_LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """DC_Binding: Set the list of loaded workbooks in the DC."""
        self.DC.dc_LOADED_WORKBOOKS = value

    @property
    def WF_CATEGORY_MANAGER(self) -> Optional[object]:
        """Return the current category manager in the DC.

        This is a property to register and share a reference to
        the WORKFLOW CATEGORY MANAGER service, which is needed
        by some workflow command processor implementations. It does not 
        impact the DC state but will reference values in the DC.
        """
        return self.DC.WF_CATEGORY_MANAGER
    @WF_CATEGORY_MANAGER.setter
    def WF_CATEGORY_MANAGER(self, value: Optional[object]) -> None:
        """Set the current category manager in the DC."""
        self.DC.WF_CATEGORY_MANAGER = value

    #endregion BudManAppDataContext_Base Properties (concrete)
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Base Methods (concrete)
    def dc_initialize(self) -> None:
        """DC_Binding: Initialize the data context."""
        super().dc_initialize()
        self.DC.dc_initialize()
        return self

    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """DC_Binding: Validate the provided FI_KEY."""
        return self.DC.dc_FI_KEY_validate(fi_key)

    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """DC_Binding: Validate the provided WF_KEY."""
        return self.DC.dc_WF_KEY_validate(wf_key)
    
    def dc_WF_PURPOSE_FOLDER_MAP(self, wf_key: str, wf_purpose:str) -> Optional[str]:
        """DC_Binding: Return the wf_folder_id from the provided WF_KEY & WF_PURPOSE.
        """
        return self.DC.dc_WF_PURPOSE_FOLDER_MAP(wf_key, wf_purpose)

    def dc_WF_PURPOSE_FOLDER_abs_path(self, wf_key: str, wf_purpose:str) -> bool:
        """DC_Binding: Return the abs_path of the folder for the provided WF_KEY & WF_PURPOSE."""
        return self.DC.dc_WF_PURPOSE_FOLDER_abs_path(wf_key, wf_purpose)

    def dc_WF_PURPOSE_validate(self, wf_purpose: str) -> bool:
        """DC_Binding: Validate the provided WF_PURPOSE."""
        return self.DC.dc_WF_PURPOSE_validate(wf_purpose)
    
    def dc_WB_ID_validate(self, wb_id):
        """Validate the provided WB_ID."""
        return self.DC.dc_WB_ID_validate(wb_id)

    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """DC_Binding: Validate the provided WB_TYPE."""
        return self.DC.dc_WB_TYPE_validate(wb_type)

    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """DC_Binding: Validate the provided WB_NAME."""
        return self.DC.dc_WB_NAME_validate(wb_name)

    def dc_WB_INDEX_validate(self, wb_index: int) -> int:
        """Validate the provided wb_index as int return int value or -1 if invalid.

        Args:
            wb_index (int): The index of the workbook to validate.

        Returns:
            int: Int value of valid wb_index, or -1.
        """
        return self.DC.dc_WB_INDEX_validate(wb_index)

    def dc_WORKBOOK_DATA_COLLECTION_validate(self) -> bool:
        """Validate the type of WORKBOOK_DATA_COLLECTION."""
        return self.DC.dc_WORKBOOK_DATA_COLLECTION_validate()
    
    def dc_WORKBOOK_validate(self, wb: WORKBOOK_OBJECT) -> bool:
        """DC-Binding: Validate the type of WORKBOOK_OBJECT.
        Abstract: sub-class hook to test specialized WORKBOOK_OBJECT types.
        DC-ONLY: check builtin type: 'object'.
        DC-Binding: pass to _Base.
        """
        return self.DC.dc_WORKBOOK_validate(wb)
    
    def dc_WORKBOOK_loaded(self, wb_id: str) -> Workbook:
        """Indicates whether the workbook with wb_id is loaded."""
        return self.DC.dc_WORKBOOK_loaded(wb_id)
    
    def dc_WORKBOOK_name(self, wb_index: int) -> str:
        """DC_Binding: Return the wb_name associated with the give wb_index."""
        return self.DC.dc_WORKBOOK_name(wb_index)
       
    def dc_WORKBOOK_index(self, wb_id: str) -> int:
        """DC_Binding: Return the wb_index of a workbook from its wb_id.
        
        Args:
            wb_name (str): The name of the workbook to find.
        Returns:
            int: The index of the workbook in the WORKBOOK_DATA_COLLECTION, or -1 if not found.
        """
        return self.DC.dc_WORKBOOK_index(wb_id)

    def dc_WORKBOOK_by_index(self, wb_index: int) -> Optional[WORKBOOK_OBJECT]:
        """DC_Binding: Return (True, BDWWorkbook on success, (False, error_msg) on failure."""
        return self.DC.dc_WORKBOOK_by_index(wb_index)

    def dc_WORKBOOK_find(self, find_key: str, value: str) -> WORKBOOK_OBJECT:
        """DC_Binding: Locate and return a workbook by the key and value."""
        return self.DC.dc_WORKBOOK_find(find_key, value)

    #region WORKBOOK_CONTENT storage-related methods
    def dc_WORKBOOK_content_get(self, wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """DC-Only: Get the workbook content from dc_LOADED_WORKBOOKS property
        if present. This class is not Model-Aware, so the application may
        use other means to arrange for content to be there with appropriate
        overrides or by putting the content directly with 
        dc_WORKBOOK_content_put. To be simple and consistent, use the 
        WORKBOOK_OBJECT to access the workbook content. In other methods, 
        a wb_ref is resolved to a WORKBOOK_OBJECT, so this method can be 
        used to get the content of a workbook by its WORKBOOK_OBJECT.

        Args:
            wb (WORKBOOK_OBJECT): The workbook object to retrieve content for.
        Returns:
            Optional[WORKBOOK_CONTENT]: The content of the workbook if available,
            otherwise None.
        """
        return self.DC.dc_WORKBOOK_content_get(wb) 

    def dc_WORKBOOK_content_put(self, wb_content:WORKBOOK_CONTENT, wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """DC-Only: Put the workbook content into dc_LOADED_WORKBOOKS property.
        This class is not Model-Aware, so the application may
        put content in for a WORKBOOK_OBJECT with this method in the blind.
        To be simple and consistent, use the WORKBOOK_OBJECT to access 
        the workbook content. In other methods, a wb_ref is resolved to a 
        WORKBOOK_OBJECT, so this method can be used to put the content of a 
        workbook by its WORKBOOK_OBJECT.
        Args:
            wb_content (WORKBOOK_CONTENT): The content to put into the 
            dc_LOADED_WORKBOOKS property.
            wb (WORKBOOK_OBJECT): The workbook object owning the content.
        """
        return self.DC.dc_WORKBOOK_content_put(wb_content, wb)

    def dc_WORKBOOK_load(self, wb_index: str) -> BUDMAN_RESULT:
        """DC_Binding: Load the specified workbook by wb_index into dc_LOADED_WORKBOOKS.
           Returns:
                BUDMAN_RESULT: a Tuple[success: bool, result: Any].
                success = True, result is a message about the loaded workbook
                indicating the workbook is available in the 
                dc_LOADED_WORKBOOKS collection.
                success = False, result is a string describing the error.
        """
        return self.DC.dc_WORKBOOK_load(wb_index)

    def dc_WORKBOOK_save(self, wb: Workbook) -> BUDMAN_RESULT:
        """DC_Binding: Save bdm_wb WORKBOOK_CONTENT to storage.
            Abstract: Save bdm_wb WORKBOOK_CONTENT to storage.
        """
        return self.DC.dc_WORKBOOK_save(wb)
    #endregion WORKBOOK_CONTENT storage-related methods

    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """DC_Binding: Remove the specified workbook by name."""
        return self.DC.dc_WORKBOOK_remove(wb_name)

    def dc_WORKBOOK_add(self, wb_name: str, wb: Union[Workbook,Dict]) -> None:
        """DC_Binding: Add a new workbook to the data context."""
        return self.DC.dc_WORKBOOK_add(wb_name, wb)

    def dc_WORKBOOK_find(self, find_key: str, value: str) -> WORKBOOK_OBJECT:
        """DC_Binding: Locate and return a workbook by the key and value."""
        return self.DC.dc_WORKBOOK_find(find_key, value)
    
    def dc_BDM_STORE_load(self, file_path: str) -> None:
        """DC_Binding: Load a BDM_STORE from bdm_url, set dc_BDM_STORE.
        All relevant DC values reference the dc_BDM_STORE.
        """
        return self.DC.dc_BDM_STORE_load(file_path)

    def dc_BDM_STORE_save(self, file_path: str) -> None:
        """DC_Binding: Save the BDM_STORE to the specified file path."""
        return self.DC.dc_BDM_STORE_save(file_path)
    
    #endregion BudManAppDataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
