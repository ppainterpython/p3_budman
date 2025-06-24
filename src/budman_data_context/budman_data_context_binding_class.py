# ---------------------------------------------------------------------------- +
#region budman_data_context_client.py module
"""DC_Binding: DI binding to BudManDataContext_Base.

    This class defines an Binding interface to a concrete provider of the
    BudManDataContext_Base interface. Binding is a reference to the Dependency
    Injection (DI) design pattern, where the client class is bound to an
    implementation of the BudManDataContext_Base interface at runtime. When 
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
#endregion budman_data_context_client.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
from typing import Tuple, Union, Dict, Optional
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budman_namespace.design_language_namespace import (
    DATA_COLLECTION, WORKBOOK_DATA_LIST, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION, WORKBOOK_OBJECT, BUDMAN_RESULT, 
    WORKBOOK_CONTENT
    )
from budman_data_context import BudManDataContext_Base
import p3_utils as p3u
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManDataContext_Binding(BudManDataContext_Base):
    """DC_Binding: Interface for a Data Context clients.
    
    This interface is used by clients to interact with a Data Context (DC)
    without needing to know the details of the implementation. The design
    pattern is to bind a provider object as the data_context at creation time.
    If the target data_context does not implement the required interface
    BudManDataContextBaseInterfaceIt, a TypeError is raised.
    """
    # ------------------------------------------------------------------------ +
    #region Class Methods
    @classmethod
    def _valid_DC_Binding(cls, dc_binding: object) -> BudManDataContext_Base:
        """DC_Binding: Return dc_value if valid, else raise exception."""
        if dc_binding is None:
            raise ValueError("DC_Binding cannot be None")
        if not isinstance(dc_binding, BudManDataContext_Base):
            raise TypeError("DC_Binding must be subclass of BudManDataContext_Base")
        return dc_binding
    #endregion Class Methods
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Binding __init__() method
    def __init__(self) -> None:
        """DC_Binding: Simple instantiation-time initialization. 
        Binding happens at initialization-time."""
        super().__init__()
        self._data_context: BudManDataContext_Base = None
    #endregion BudManDataContext_Binding __init__() method
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Binding Properties
    @property
    def data_context(self) -> BudManDataContext_Base:
        """DC_Binding: Return the data context object."""
        return self._data_context
    @data_context.setter
    def data_context(self, dc_value: BudManDataContext_Base) -> None:
        """DC_Binding: Set the data context object."""
        self._data_context = dc_value

    @property
    def DC(self) -> BudManDataContext_Base:
        """DC_Binding: Return the data context.
        This is DC_Binding behavior. If the binding is not valid, an exception 
        is raised. The DC property is a reference to the data context object.
        """
        return BudManDataContext_Binding._valid_DC_Binding(self).data_context
    @DC.setter
    def DC(self, value: BudManDataContext_Base) -> None:
        """DC_Binding: Set the name of the data context.
        This is DC_Binding behavior. If the binding is not valid, an exception 
        is raised. The DC property is a reference to the data context object.
        """        
        self.data_context = BudManDataContext_Binding._valid_DC_Binding(value)
    #endregion BudManDataContext_Binding Properties
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Binding Methods
    # def _valid_DC(self) -> None:
    #     """DC_Binding: raise exception if the DC property is invalid."""
    #     BudManDataContext_Binding._valid_DC_Binding(self._data_context)
    #endregion BudManDataContext_Binding Methods
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Properties (concrete)
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
    def dc_FI_OBJECT(self) -> str:
        """DC_Binding: Return the FI_OBJECT of the current Financial Institution."""
        return self.DC.dc_FI_OBJECT 
    @dc_FI_OBJECT.setter
    def dc_FI_OBJECT(self, value: str) -> None:
        """DC_Binding: Set the FI_OBJECT of the current Financial Institution."""
        self.DC.dc_FI_OBJECT = value

    @property
    def dc_FI_KEY(self) -> str:
        """DC_Binding: Return the FI_KEY for the financial institution."""
        return self.DC.dc_FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """DC_Binding: Set the FI_KEY for the financial institution."""
        self.DC.dc_FI_KEY = value

    @property
    def dc_WF_KEY(self) -> str:
        """DC_Binding: Return the WF_KEY for the workflow."""
        return self.DC.dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """DC_Binding: Set the WF_KEY for the workflow."""
        self.DC.dc_WF_KEY = value

    @property
    def dc_WF_PURPOSE(self) -> str:
        """DC_Binding: Return the WF_PURPOSE workbook type."""
        return self.DC.dc_WF_PURPOSE
    @dc_WF_PURPOSE.setter
    def dc_WF_PURPOSE(self, value: str) -> None:
        """DC_Binding: Set the WF_PURPOSE workbook type."""
        self.DC.dc_WF_PURPOSE = value

    @property
    def dc_WB_TYPE(self) -> str:
        """DC_Binding: Return the current WB_TYPE (workbook type).
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self.DC.dc_WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """DC_Binding: Set the WB_TYPE workbook type."""
        self.DC.dc_WB_TYPE = value

    @property
    def dc_WB_NAME(self) -> str:
        """DC_Binding: Return the WB_NAME workbook name."""
        return self.DC.dc_WB_NAME
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
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
    def dc_WB_REF(self) -> str:
        """DC_Binding: Return the current WB_REF workbook reference value."""
        return self.DC.dc_WB_REF
    @dc_WB_REF.setter
    def dc_WB_REF(self, value: str) -> None:
        """DC_Binding: Set the WB_REF workbook reference value."""
        self.DC.dc_WB_REF = value

    @property
    def dc_WB_ALL_WORKBOOKS(self) -> bool:
        """DC-Only: Return True if the current operation is on all workbooks."""
        return self.DC.dc_WB_ALL_WORKBOOKS
    @dc_WB_ALL_WORKBOOKS.setter
    def dc_WB_ALL_WORKBOOKS(self, value: bool) -> None:
        """DC-Only: Set the flag indicating if the current operation is on all workbooks."""
        if not isinstance(value, bool):
            raise TypeError(f"dc_WB_ALL_WORKBOOKS must be a bool, not {type(value).__name__}")
        self.DC.dc_WB_ALL_WORKBOOKS = value

    @property
    def dc_BDM_STORE(self) -> str:
        """DC_Binding: Return the BDM_STORE jsonc definition."""
        return self.DC.dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: str) -> None:
        """DC_Binding: Set the BDM_STORE jsonc definition."""
        self.DC.dc_BDM_STORE = value

    @property
    def dc_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """DC_Binding: Return the list of workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its absolute path.
        """
        return self.DC.dc_WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: WORKBOOK_DATA_LIST) -> None:
        """DC_Binding: Set the list of workbooks in the DC."""
        self.DC.dc_WORKBOOKS = value

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
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_LIST) -> None:
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
    def dc_EXCEL_WORKBOOKS(self) -> DATA_COLLECTION:
        """DC_Binding: Return the collection of workbooks currently open in Excel."""
        return self.DC.dc_EXCEL_WORKBOOKS
    @dc_EXCEL_WORKBOOKS.setter
    def dc_EXCEL_WORKBOOKS(self, value: DATA_COLLECTION) -> None:
        """DC_Binding: Set the collection of workbooks currently open in Excel."""
        self.DC.dc_EXCEL_WORKBOOKS = value

    @property 
    def dc_CHECK_REGISTERS(self) -> DATA_COLLECTION:
        """DC_Binding: Return the check register data collection."""
        return self.DC.dc_CHECK_REGISTERS
    @dc_CHECK_REGISTERS.setter
    def dc_CHECK_REGISTERS(self, value: DATA_COLLECTION) -> None:
        """DC_Binding: Set the check register data collection."""
        self.DC.dc_CHECK_REGISTERS = value

    @property 
    def dc_LOADED_CHECK_REGISTERS(self) -> DATA_COLLECTION:
        """DC_Binding: Return the check register data collection."""
        return self.DC.dc_CHECK_REGISTERS
    @dc_LOADED_CHECK_REGISTERS.setter
    def dc_LOADED_CHECK_REGISTERS(self, value: DATA_COLLECTION) -> None:
        """DC_Binding: Set the check register data collection."""
        self.DC.dc_CHECK_REGISTERS = value
    #endregion BudManDataContext_Base Properties (concrete)
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Methods (concrete)
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

    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """DC_Binding: Validate the provided workbook reference."""
        return self.DC.dc_WB_REF_validate(wb_ref)

    def dc_WB_REF_resolve(self, wf_key : str) -> Tuple[bool, int, str]: 
        """DC_Binding: Return True if the wf_key is valid."""
        # Bind through the DC (data_context) object.
        return self.DC.dc_WB_REF_resolve(wf_key)

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
            int: The index of the workbook in the WORKBOOK_DATA_LIST, or -1 if not found.
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

    def dc_WORKBOOK_save(self, wb_name: str, wb: Workbook) -> BUDMAN_RESULT:
        """DC_Binding: Save the specified workbook by name."""
        return self.DC.dc_WORKBOOK_save(wb_name, wb)
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
    
    def dc_CHECK_REGISTER_name(self, wb_index: int) -> str:
        """DC_Binding: Return wb_name for wb_index or None if does not exist."""
        return self.DC.dc_CHECK_REGISTER_name(wb_index)
    
    def dc_CHECK_REGISTER_index(self, wb_name: str = None) -> int:  
        """DC_Binding: Return the index of a check register based on wb_name.
        
        Args:
            wb_name (str): The name of the check register to find.
        Returns:
            int: The index of the check register in the dc_CHECK_REGISTERS, or -1 if not found.
        """
        return self.DC.dc_CHECK_REGISTER_index(wb_name)
    
    def dc_CHECK_REGISTER_load(self, wb_name: str, wb_ref:str) -> DATA_COLLECTION:
        """DC_Binding: Load the specified check register by name."""
        return self.DC.dc_CHECK_REGISTER_load(wb_name, wb_ref)

    def dc_CHECK_REGISTER_add(self, wb_name: str, wb_ref: str, wb: DATA_COLLECTION) -> None:
        """DC_Binding: Add a new loaded workbook to the data context."""
        return self.DC.dc_CHECK_REGISTER_add(wb_name, wb_ref, wb)    

    #endregion BudManDataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
