# ---------------------------------------------------------------------------- +
#region budman_app_data_context_base_ABC.py module
""" BudManAppDataContext_Base: Abstract Base Class interface.

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
#endregion budman_app_data_context_base_ABC.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
from typing import Tuple, Any, Union, Dict, Optional
# third-party modules and packages
from openpyxl import Workbook
# local modules and packages
from budman_namespace.design_language_namespace import (
    DATA_CONTEXT, FI_OBJECT, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION,
    BDM_STORE, DATA_COLLECTION, WORKBOOK_OBJECT, BUDMAN_RESULT,
    WORKBOOK_CONTENT)
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManAppDataContext_Base(ABC):
    """Abstract Base Class Interface for Budget Manager Data Context."""
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Base Properties (abstract) 
    @property
    def dc_id(self) -> str:
        """Abstract: Identify the data context implementation."""
        pass
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """Abstract: Set the identifier for the data context implementation."""
        pass

    @property
    @abstractmethod
    def dc_VALID(self) -> bool:
        """Abstract: Indicates whether the data context is valid."""
        pass
    
    @property
    @abstractmethod
    def dc_INITIALIZED(self) -> bool:
        """Abstract: Indicates whether the data context has been initialized."""
        pass
    @dc_INITIALIZED.setter
    @abstractmethod
    def dc_INITIALIZED(self, value: bool) -> None:
        """Abstract: Set the initialized state of the data context."""
        pass

    @property
    @abstractmethod
    def dc_FI_OBJECT(self) -> Optional[FI_OBJECT]:
        """Abstract: Return the FI_OBJECT of the current Financial Institution. """
        pass
    @dc_FI_OBJECT.setter
    @abstractmethod
    def dc_FI_OBJECT(self, value: Optional[FI_OBJECT]) -> None:
        """Abstract: Set the FI_OBJECT of the current Financial Institution."""
        pass

    @property
    @abstractmethod
    def dc_FI_KEY(self) -> Optional[str]:
        """Abstract: Return the FI_KEY of the current Financial Institution.
        Current means that the other data in the DC is for this FI.
        """
        pass
    @dc_FI_KEY.setter
    @abstractmethod
    def dc_FI_KEY(self, value: Optional[str]) -> None:
        """Abstract: Set the FI_KEY of the current Financial Institution."""
        pass

    @property
    @abstractmethod
    def dc_WF_KEY(self) -> Optional[str]:
        """Abstract: Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        pass
    @dc_WF_KEY.setter
    @abstractmethod
    def dc_WF_KEY(self, value: Optional[str]) -> None:
        """Abstract: Set the WF_KEY for the workflow."""
        pass

    @property
    @abstractmethod
    def dc_WF_PURPOSE(self) -> Optional[str]:
        """Abstract: Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        pass
    @dc_WF_PURPOSE.setter
    @abstractmethod
    def dc_WF_PURPOSE(self, value: Optional[str]) -> None:
        """Abstract: Set the WF_KEY for the workflow."""
        pass

    @property
    @abstractmethod
    def dc_WB_ID(self) -> Optional[str]:
        """Abstract: Return the current WB_REF workbook reference.

        Current means the wb_ref for the last operation on a named or referenced
        workbook. The other data in the DC is updated in a similar fashion.
        After an operation on 'all' workbooks, the dc_WB_REF is set to 'all'.
        """
        pass
    @dc_WB_ID.setter
    @abstractmethod
    def dc_WB_ID(self, value: Optional[str]) -> None:
        """Set the WB_REF workbook reference."""
        pass

    @property
    @abstractmethod
    def dc_WB_TYPE(self) -> Optional[str]:
        """Abstract: Return the current WB_TYPE (workbook type).
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        pass
    @dc_WB_TYPE.setter
    @abstractmethod
    def dc_WB_TYPE(self, value: str) -> None:
        """Abstract: Set the WB_TYPE workbook type."""
        pass

    @property
    @abstractmethod
    def dc_WB_NAME(self) -> Optional[str]:
        """Abstract: Return the current WB_NAME workbook name.

        Current means that the other data in the DC is for this workbook, and
        that a user has specified this workbook specifically by name.
        This indicates the name of the workbook being processed, e.g., 'budget.xlsx',
        """
        pass
    @dc_WB_NAME.setter
    @abstractmethod
    def dc_WB_NAME(self, value: Optional[str]) -> None:
        """Abstract: Set the WB_NAME workbook name."""
        pass

    @property
    @abstractmethod
    def dc_WB_INDEX(self) -> int:
        """Abstract: Return the current WB_INDEX.

        Current means that the other data in the DC is for this workbook, and
        that a user has specified this workbook specifically by index.
        This index is the 0-based index order of the dc_WORKBOOK_DATA_COLLECTION.
        """
        pass
    @dc_WB_INDEX.setter
    @abstractmethod
    def dc_WB_INDEX(self, value: int) -> None:
        """Abstract: Set the WB_INDEX workbook index."""
        pass

    @property
    @abstractmethod
    def dc_ALL_WBS(self) -> bool:
        """Abstract: True indicates all workbooks in the DC are selected.
        False indicate that ALL selection is not in effect.
        """
        pass
    @dc_ALL_WBS.setter
    @abstractmethod
    def dc_ALL_WBS(self, value: bool) -> None:
        """Abstract: Set the ALL_WBS selection status."""
        pass

    @property
    @abstractmethod
    def dc_BDM_STORE(self) -> Optional[str]:
        """Abstract: Return the BDM_STORE jsonc definition."""
        pass
    @dc_BDM_STORE.setter
    @abstractmethod
    def dc_BDM_STORE(self, value: Optional[str]) -> None:
        """Abstract: Set the BDM_STORE jsonc definition."""
        pass

    @property
    @abstractmethod
    def dc_BDM_STORE_changed(self) -> bool:
        """Abstract: BDM_STORE content has been changed."""
        pass
    @dc_BDM_STORE_changed.setter
    @abstractmethod
    def dc_BDM_STORE_changed(self, value: bool) -> None:
        """Abstract: Set the BDM_STORE changed status."""
        pass

    @property
    @abstractmethod
    def dc_WORKBOOK(self) -> WORKBOOK_OBJECT:
        """Abstract: Return the current workbook in focus in the DC."""
        pass
    @dc_WORKBOOK.setter
    @abstractmethod
    def dc_WORKBOOK(self, value: WORKBOOK_OBJECT) -> None:
        """Abstract: Set the current workbook in focus in the DC."""
        pass

    @property
    @abstractmethod
    def dc_WORKBOOK_DATA_COLLECTION(self) -> WORKBOOK_DATA_COLLECTION:
        """Abstract: Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.The WORKBOOK_DATA_COLLECTION
        is sorted by the key, wb_id, the wb_index is based on the sorted order."""
        pass
    @dc_WORKBOOK_DATA_COLLECTION.setter
    @abstractmethod
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_COLLECTION) -> None:
        """Abstract: Set the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.
        The WORKBOOK_DATA_COLLECTION should be sorted by the key,
        wb_id as it is updated. The wb_index should be based on the 
        sorted order of the WORKBOOK_DATA_COLLECTION.
        """
        pass

    @property
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Abstract: Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        pass
    @dc_LOADED_WORKBOOKS.setter
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Abstract: Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        pass
    #endregion BudManAppDataContext_Base Properties (abstract)
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Base Methods (abstract)
    @abstractmethod
    def dc_initialize(self) -> DATA_CONTEXT:
        """Abstract: Initialize the data context."""
        pass

    @abstractmethod
    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Abstract: Validate the provided FI_KEY."""
        pass

    @abstractmethod
    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """Abstract: Validate the provided WF_KEY."""
        pass

    @abstractmethod
    def dc_WF_PURPOSE_FOLDER_MAP(self, wf_key: str, wf_purpose:str) -> Optional[str]:
        """Abstract: Return the wf_folder_id from the provided WF_KEY & WF_PURPOSE."""
        pass

    @abstractmethod
    def dc_WF_PURPOSE_FOLDER_abs_path(self, wf_key: str, wf_purpose:str) -> bool:
        """Abstract: Return the abs_path of the folder for the provided WF_KEY & WF_PURPOSE."""
        pass

    @abstractmethod
    def dc_WB_ID_validate(self, wb_id: str) -> bool:
        """Abstract: Validate the provided WB_ID."""
        pass

    @abstractmethod
    def dc_WF_PURPOSE_validate(self, wf_purpose: str) -> bool:
        """Validate the provided WF_PURPOSE."""
        pass

    @abstractmethod
    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """Abstract: Validate the provided WB_TYPE."""
        pass

    @abstractmethod
    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """Abstract: Validate the provided WB_NAME."""
        pass

    @abstractmethod
    def dc_WB_INDEX_validate(self, wb_index: int) -> bool:
        """Abstract: Validate the provided WB_INDEX."""
        pass

    @abstractmethod
    def dc_WORKBOOK_DATA_COLLECTION_validate(self, wdc : WORKBOOK_DATA_COLLECTION) -> bool:
        """Abstract: Validate the type of WORKBOOK_DATA_COLLECTION."""
        pass

    @abstractmethod
    def dc_WORKBOOK_validate(self, wb : WORKBOOK_OBJECT) -> bool:
        """Abstract: Validate the type of WORKBOOK_OBJECT.
        Abstract: sub-class hook to test specialized WORKBOOK_OBJECT types.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_loaded(self, wb_id: str) -> bool:
        """Abstract: Indicates whether the workbook with wb_id is loaded."""
        pass

    @abstractmethod
    def dc_WORKBOOK_name(self, wb_index: int) -> str:
        """Abstract: Return the wb_name associated with the give wb_index."""
        pass 
       
    @abstractmethod
    def dc_WORKBOOK_index(self, wb_id: str = None) -> int:
        """Abstract: Return the index of a workbook based on wb_id.
        
        Args:
            wb_id (str): The wb_id of the workbook to index.
        Returns:
            int: The index of the workbook in the WORKBOOK_DATA_COLLECTION, or -1 if not found.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_by_index(self, wb_index: int) -> Optional[WORKBOOK_OBJECT]:
        """Abstract: Return (True, BDWWorkbook on success, (False, error_msg) on failure."""
        pass

    @abstractmethod
    def dc_WORKBOOK_find(self, find_key: str, value: str) -> WORKBOOK_OBJECT:
        """Abstract: Locate and return a workbook by the key and value."""
        pass

    #region   WORKBOOK_CONTENT storage-related methods
    @abstractmethod
    def dc_WORKBOOK_content_get(self, wb: WORKBOOK_OBJECT, load:bool=True) -> BUDMAN_RESULT:
        """Abstract: Get the workbook content from dc_LOADED_WORKBOOKS property,
        if present, and return as result. This abstract class is not 
        Model-Aware, so the application may use other means to arrange for 
        content to be there with appropriate overrides or by putting the 
        content directly with dc_WORKBOOK_content_put. To be simple and 
        consistent, use the WORKBOOK_OBJECT to access the workbook metadata.

        Args:
            wb (WORKBOOK_OBJECT): The workbook object to retrieve content for.
            load (bool): If True, load the content from storage if not 
                already loaded.
        Returns:
            Optional[WORKBOOK_CONTENT]: The content of the workbook if available,
            otherwise None.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_content_put(self, wb_content:WORKBOOK_CONTENT, wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """Abstract: Put the workbook's content to storage.
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
        Returns:
            BUDMAN_RESULT: a Tuple[success: bool, result: Any].
                success = True, result is a message about the loaded 
                workbook indicating the workbook is available in the 
                dc_LOADED_WORKBOOKS collection.
                success = False, result is a string describing the error.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_load(self, bdm_wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """ Abstract: Load bdm_wb WORKBOOK_CONTENT from storage, set value 
            or bdm_wb.wb_content, and set bdm_wb.wb_loaded. Make this bdm_wb
            the dc_WORKBOOK, so that the application can use it.

            Returns:
                BUDMAN_RESULT: a Tuple[success: bool, result: Any].
                    success = True, result is bdm_wb.wb_content.
                    success = False, result is a string describing the error.
        """
        pass

    @abstractmethod
    def dc_WORKBOOK_save(self,bdm_wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """Abstract: Save bdm_wb WORKBOOK_CONTENT to storage."""
        pass
    #endregion WORKBOOK_CONTENT storage-related methods

    @abstractmethod
    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """Abstract: Remove the specified workbook by name."""
        pass

    @abstractmethod
    def dc_WORKBOOK_add(self, wb_name: str, wb: Union[Workbook, Dict]) -> None:
        """Add a new workbook to the data context."""
        pass

    @abstractmethod
    def dc_BDM_STORE_load(self, bdm_url: str) -> BDM_STORE:
        """Abstract: Load a BDM_STORE from bdm_url, set dc_BDM_STORE.
        All relevant DC values reference the dc_BDM_STORE.
        """
        pass

    @abstractmethod
    def dc_BDM_STORE_save(self, bdm_store: BDM_STORE, bdm_url: str) -> None:
        """Abstract: Save the BDM_STORE to the specified file path."""
        pass

    #endregion BudManAppDataContext_Base Methods (abstract)
    # ------------------------------------------------------------------------ +
