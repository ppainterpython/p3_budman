# ---------------------------------------------------------------------------- +
#region test_budman_app_data_context.py
"""DC-Only: BudManAppDataContext: A concrete implementation of the interface
    defined in BudManAppDataContext_Base.
    
    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers, providing an abstraction for data used by ViewModels, 
    Models and a View.

    The properties and methods reflect the BudMan application design language, 
    in terms of the Domain Model objects, command processing, etc. So, it is
    Budget Domain Model (BDM) aware through the BDM_STORE dictionary, 
    but not bound to a particular application's implementation of the View, 
    ViewModel, or Model interface. But, the key concepts in the BDM concerning 
    Financial Institutions (FI), Workflows (WF), Workbooks (WB), and the 
    Budget Data Model (BDM_STORE) are all represented in the Data Context.

    This DC-Only implementation is designed to depend on the BDM_STORE dictionary
    as a data structure. A key binding is the FI_DATA_OBJECT property. This
    DC operates on the premise that one FI is in focus at a time, and all
    operations are performed in the context of that FI. Changing the FI_OBJECT
    value ripples through the other properties and methods, so that the
    application context is always consistent.

    A Data Context is not a Model, nor a View Model, it is a bridge between
    the two. It provides a way to access and manipulate data without exposing
    the underlying implementation details. It provides the application context
    at any moment in time, so the values change. This implementation, DC-Only,
    is a concrete implmentation of the BudManAppDataContext_Base abstract class.
    It uses the BDM_STORE dictionary as the backing store. For use with
    specific application-specific ViewModels, and Models, a different 
    concrete implementation of the BudManAppDataContext_Base may be used, or
    become a subclass of this class, to provide additional functionality through
    overrides of the properties and methods defined here.

    Each property and method herein documents its purpose. Most of the 
    properties and methods, if the return value is not None, return basic 
    data types, or aliases for those defined in the Design Language namespace.
    However, some of the return a BUDMAN_RESULT_TYPE, which is a tuple of
    (success: bool, result: Any). This scheme is used to be forgiving when
    errors occur. The success value being True means no error and the result
    value is the output of the function. When success is False, the result
    value is a string describing the error.
    
    This class provides a minimalist implementation of the interface, 
    which can be extended by subclasses to provide more specific functionality. 
    Here there is no reference to outside data objects, such as a Model or 
    ViewModel. Subclasses may override or extend the default DC behavior.

    This "DC-Only" implementation is designed to work by referencing the Data
    Context (DC) directly. The BDM_STORE dictionary is assumed to support
    the data content implied by the DC base interface. No particular 
    implementation of the Model is assumed. But the structure of the BDM_STORE
    is treated as an abstraction of the Budget Domain design langauge concepts.
"""
#endregion test_budman_app_data_context.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from ast import Not
import pytest, os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Tuple, Any, Union, Dict, Optional
# third-party modules and packages
from openpyxl import Workbook
from treelib import Tree, Node
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
from budman_namespace.design_language_namespace import (
    FI_OBJECT_TYPE, DATA_CONTEXT_TYPE, LOADED_WORKBOOK_COLLECTION_TYPE, 
    WORKBOOK_DATA_COLLECTION_TYPE, WORKBOOK_OBJECT_TYPE,
    BDM_STORE_TYPE, DATA_COLLECTION_TYPE, BUDMAN_RESULT_TYPE, WORKBOOK_CONTENT_TYPE,
    BDM_FI_COLLECTION, BDM_WF_COLLECTION, 
    FI_WORKBOOK_DATA_COLLECTION, FI_FOLDER,
    VALID_WF_PURPOSE_VALUES, VALID_WB_TYPE_VALUES,
    BDM_STORE_OBJECT, BDM_FOLDER,
    FI_KEY, WF_KEY, WB_ID, WB_NAME,
    WB_TYPE, WF_PURPOSE, WB_INDEX, WB_URL, WB_LOADED, WB_CONTENT,
    BDM_DATA_CONTEXT, DC_FI_KEY, DC_WF_KEY, DC_WF_PURPOSE, DC_WB_TYPE,
    FILE_TREE_NODE_TYPE_KEY, FILE_TREE_NODE_WF_KEY, FILE_TREE_NODE_WF_PURPOSE
    )
from budman_namespace.bdm_workbook_class import BDMWorkbook
import budget_storage_model as bsm
from budman_data_context.budman_app_data_context_base_ABC import BudManAppDataContext_Base
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class BudManAppDataContext(BudManAppDataContext_Base):
    """Concrete, non-MVVM-Aware implementation of BudManAppDataContext_Base."""
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext__init__()
    def __init__(self, *args, dc_id : str = None) -> None:
        """DC-Only: Constructor Initialize the BudManAppDataContext."""
        self._initialization_in_progress = True
        self._dc_id :str = dc_id if dc_id else self.__class__.__name__
        self._dc_initialized = False 
        self._dc_FI_OBJECT : Optional[FI_OBJECT_TYPE] = None 
        self._dc_FI_KEY : Optional[str] = None       
        self._dc_WF_KEY : Optional[str] = None       
        self._dc_WF_PURPOSE : Optional[str] = None
        self._dc_WB_ID : Optional[str] = None
        self._dc_WB_TYPE : Optional[str] = None      
        self._dc_WB_NAME : Optional[str] = None     
        self._dc_WB_INDEX : int = -1
        self._dc_ALL_WBS : bool = False
        self._dc_BDM_STORE : BDM_STORE_TYPE = None
        self._dc_BDM_STORE_changed : bool = False
        self._dc_WORKBOOK : Optional[WORKBOOK_OBJECT_TYPE] = None
        self._dc_WORKBOOK_DATA_COLLECTION : WORKBOOK_DATA_COLLECTION_TYPE = dict()
        self._dc_LOADED_WORKBOOKS : LOADED_WORKBOOK_COLLECTION_TYPE = dict()
        self._dc_DataContext : DATA_CONTEXT_TYPE = dict()
        self._dc_WORKBOOK_TREE : Optional[Tree] = None
    #endregion BudManAppDataContext__init__()
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Base Properties (concrete) 
    @property
    def dc_id(self) -> str:
        """DC-Only: Identify the data context implementation."""
        return self._dc_id
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """DC-Only: Set the identifier for the data context implementation."""
        if not isinstance(value, str):
            raise TypeError("dc_id must be a string.")
        self._dc_id = value

    @property
    def dc_INITIALIZED(self) -> bool:
        """DC-Only: Indicates whether the data context has been initialized."""
        return self._dc_initialized
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """DC-Only: Set the initialized state of the data context."""
        if value:
            # Full enable dc_VALID after upstream sets to True
            self._initialization_in_progress = False
        self._dc_initialized = value

    @property
    def dc_VALID(self) -> bool:
        """DC-Only: Indicates whether the data context is valid."""
        success, reason = self.dc_is_valid()
        return success
    
    @property
    def dc_FI_OBJECT(self) -> Optional[FI_OBJECT_TYPE]:
        """DC-Only: Return the FI_OBJECT of the current Financial Institution. """
        return self._dc_FI_OBJECT if self.dc_VALID else None
    @dc_FI_OBJECT.setter
    def dc_FI_OBJECT(self, value: Optional[FI_OBJECT_TYPE]) -> None:
        """DC-Only: Set the FI_OBJECT of the current Financial Institution."""
        if not self.dc_VALID: return None
        # The value must be a valid FI_OBJECT.
        if not isinstance(value, dict):
            raise TypeError(f"dc_FI_OBJECT must be an FI_OBJECT, "
                            f"not {type(value).__name__}.")
        # The value's FI_KEY must match dc_FI_KEY.
        if value[FI_KEY] != self.dc_FI_KEY:
            raise ValueError(f"FI_OBJECT key mismatch: "
                             f"value[{FI_KEY}]('{value[FI_KEY]}') != "
                             f"dc_FI_KEY('{self.dc_FI_KEY}')")
        # The new FI_OBJECT value must be the same object from dc_BDM_STORE.
        if value != self.dc_BDM_STORE[BDM_FI_COLLECTION].get(self.dc_FI_KEY, None):
            raise ValueError(f"dc_FI_OBJECT must be the same object from "
                             f"dc_BDM_STORE[BDM_FI_COLLECTION] for key "
                             f"dc_FI_KEY'{self.dc_FI_KEY}').")
        self._dc_FI_OBJECT = value

    @property
    def dc_FI_KEY(self) -> Optional[str]:
        """DC-Only: Return the FI_KEY of the current Financial Institution.
        Depends on the value of dc_FI_OBJECT.
        Current means that the other data in the DC is for this FI.
        """
        return self.dc_FI_OBJECT[FI_KEY] if self.dc_VALID else None
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: Optional[str]) -> None:
        """DC-Only: Set the FI_KEY of the current Financial Institution by
        setting the dc_FI_OBJECT to the FI_OBJECT associated with that FI_KEY 
        in the BDM_STORE. The dc_FI_KEY property is derived from the 
        dc_FI_OBJECT property. Depends on the value of dc_BDM_STORE.
        """
        if self.dc_VALID:
            if not self.dc_FI_KEY_validate(value):
                raise ValueError(f"Invalid FI_KEY: {value}")
        self.dc_FI_OBJECT = self.dc_BDM_STORE[BDM_FI_COLLECTION].get(value, None)

    @property
    def dc_WF_KEY(self) -> Optional[str]:
        """DC-Only: Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        return self._dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: Optional[str]) -> None:
        """DC-Only: Set the WF_KEY for the workflow."""
        self._dc_WF_KEY = value if self.dc_WF_KEY_validate(value) else None

    @property
    def dc_WF_PURPOSE(self) -> Optional[str]:
        """DC-Only: Return the current WF_PURPOSE (workbook type) .
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self._dc_WF_PURPOSE
    @dc_WF_PURPOSE.setter
    def dc_WF_PURPOSE(self, value: Optional[str]) -> None:
        """DC-Only: Set the WF_PURPOSE workbook type."""
        self._dc_WF_PURPOSE = value

    @property
    def dc_WB_ID(self) -> Optional[str]:
        """DC-Only: Return the current WB_ID workbook reference.
        
        Current means the wb_id for the current .
        """
        wb = self.dc_WORKBOOK
        if not wb: return None
        return wb[WB_ID]
    @dc_WB_ID.setter
    def dc_WB_ID(self, value: Optional[str]) -> None:
        """DC-Only: dc_WB_ID setter not supported, set the dc_WORKBOOK property."""
        raise NotImplementedError("dc_WB_ID is read-only, "
                                  "set the dc_WORKBOOK property instead.")

    @property
    def dc_WB_TYPE(self) -> Optional[str]:
        """DC-Only: Return the current WB_TYPE (workbook type) .
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        wb = self.dc_WORKBOOK
        if not wb: return ""
        if self.dc_WORKBOOK_has_property(wb,WB_TYPE):
            return wb[WB_TYPE]
        return None
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: Optional[str]) -> None:
        """DC-Only: dc_WB_TYPE setter not supported, set the dc_WORKBOOK property."""
        raise NotImplementedError("dc_WB_TYPE is read-only, "
                                  "set the dc_WORKBOOK property instead.")

    @property
    def dc_WB_NAME(self) -> Optional[str]:
        """DC-Only: Return the current WB_NAME workbook name.
        
        Current means that the other data in the DC is for this workbook, and 
        that a user has specified this workbook specifically by name.
        This indicates the name of the workbook being processed, e.g., 'budget.xlsx',
        """
        wb = self.dc_WORKBOOK
        if not wb: return None
        if self.dc_WORKBOOK_has_property(wb,WB_NAME):
            return wb[WB_NAME]
        return None
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: Optional[str]) -> None:
        """DC-Only: dc_WB_NAME setter not supported, set the dc_WORKBOOK property."""
        raise NotImplementedError("dc_WB_NAME is read-only, "
                                  "set the dc_WORKBOOK property instead.")

    @property
    def dc_WB_INDEX(self) -> int:
        """DC-Only: Return the current WB_INDEX workbook index.
        
        Current means that the other data in the DC is for this workbook, and 
        that a user has specified this workbook specifically by index.
        The wb_index is based on the order of workbooks in the dc_WORKBOOK_DATA_COLLECTION.
        """
        wb = self.dc_WORKBOOK
        if not wb: return -1
        wb_id = self.dc_WB_ID
        return self.dc_WORKBOOK_index(wb_id) if wb_id else -1
    @dc_WB_INDEX.setter
    def dc_WB_INDEX(self, value: int) -> None:
        """DC-Only: dc_WB_INDEX setter not supported, set the dc_WORKBOOK property."""
        raise NotImplementedError("dc_WB_INDEX is read-only, "
                                  "set the dc_WORKBOOK property instead.")

    @property
    def dc_ALL_WBS(self) -> bool:
        """DC-Only: Return True if the current operation is on all workbooks."""
        return self._dc_ALL_WBS
    @dc_ALL_WBS.setter
    def dc_ALL_WBS(self, value: bool) -> None:
        """DC-Only: Set the flag indicating if the current operation is on all workbooks."""
        if not isinstance(value, bool):
            raise TypeError(f"dc_WB_ALL_WORKBOOKS must be a bool, not {type(value).__name__}")
        self._dc_ALL_WBS = value

    @property
    def dc_BDM_STORE(self) -> Optional[str]:
        """DC-Only: Return the BDM_STORE jsonc definition."""
        return self._dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: Optional[str]) -> None:
        """DC-Only: Set the BDM_STORE jsonc definition."""
        self._dc_BDM_STORE = value

    @property
    def dc_BDM_STORE_changed(self) -> bool:
        """DC-Only: BDM_STORE content has been changed."""
        return self._dc_BDM_STORE_changed
    @dc_BDM_STORE_changed.setter
    def dc_BDM_STORE_changed(self, value: bool) -> None:
        """DC-Only: Set the BDM_STORE changed status."""
        self._dc_BDM_STORE_changed = value

    @property
    def dc_WORKBOOK(self) -> WORKBOOK_OBJECT_TYPE:
        """DC-Only: Return the current workbook in focus in the DC.
           This binding determines the values of related properties:
           - dc_WB_INDEX
           - dc_WB_ID
           - dc_WB_NAME
           - dc_WB_TYPE
        """
        if not self.dc_VALID: return None
        if not self.dc_WORKBOOK_validate(self._dc_WORKBOOK):
            return None
        return self._dc_WORKBOOK
    @dc_WORKBOOK.setter
    def dc_WORKBOOK(self, value: WORKBOOK_OBJECT_TYPE) -> None:
        """Set the current workbook in focus in the DC."""
        if not self.dc_VALID: return None
        if value is None:
            self._dc_WORKBOOK = None
            return
        if not self.dc_WORKBOOK_validate(value):
            return None
        self._dc_WORKBOOK = value

    @property
    def dc_WORKBOOK_DATA_COLLECTION(self) -> WORKBOOK_DATA_COLLECTION_TYPE:
        """DC-Only: Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key. The WORKBOOK_DATA_COLLECTION
        is sorted by the key, wb_id, the wb_index is based on the sorted order."""
        if not self.dc_VALID: return None
        fi_object = self.dc_FI_OBJECT
        wdc = fi_object[FI_WORKBOOK_DATA_COLLECTION]
        return wdc
    @dc_WORKBOOK_DATA_COLLECTION.setter
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_COLLECTION_TYPE) -> None:
        """DC-Only: Set the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.
        The WORKBOOK_DATA_COLLECTION should be sorted by the key,
        wb_id as it is updated. The wb_index should be based on the 
        sorted order of the dc_WORKBOOK_DATA_COLLECTION.
        """
        raise NotImplementedError("dc_WORKBOOK_DATA_COLLECTION is read-only, "
                                  "set the dc_FI_OBJECT property instead.")

    @property
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION_TYPE:
        """DC-Only: Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        return self._dc_LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION_TYPE) -> None:
        """DC-Only: Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        self._dc_LOADED_WORKBOOKS = value

    @property
    def dc_FILE_TREE(self) -> Optional[Tree]:
        """DC-Only: Requires a binding to a model or storage system.
        This backing variable can be set by a subclass override."""
        return self._dc_FILE_TREE

    @property
    def dc_WORKBOOK_TREE(self) -> Optional[Tree]:
        """DC-Only: Requires a binding to a model or storage system.
        This backing variable can be set by a subclass override."""
        return self._dc_WORKBOOK_TREE
    #endregion BudManAppDataContext_Base Properties (concrete)
    # ------------------------------------------------------------------------ +
    #region BudManAppDataContext_Base Methods (concrete)
    def dc_initialize(self) -> None:
        """DC-Only: Runtime Initialize the data context."""
        try:
            # For best outcome, the subclass should set dc_BDM_STORE ahead of time.
            self.dc_BDM_STORE = dict() if self.dc_BDM_STORE is None else self.dc_BDM_STORE
            # Update DC values saved in BDM_STORE.BDM_DATA_CONTEXT.
            bdms = self.dc_BDM_STORE
            bdm_store_dc = getattr(bdms,BDM_DATA_CONTEXT, {})
            self._dc_FI_KEY = bdm_store_dc.get(DC_FI_KEY, None)
            self._dc_WF_KEY = bdm_store_dc.get(DC_WF_KEY, None)
            self._dc_WF_PURPOSE = bdm_store_dc.get(DC_WF_PURPOSE, None)
            self._dc_WB_TYPE = bdm_store_dc.get(DC_WB_TYPE, None)
            # Further Model-Aware initialization can be done in the subclass.
            # So, don't change the values here.
            return self
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise RuntimeError(f"Failed to initialize the data context: {m}")

    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """DC-Only: Validate the provided FI_KEY.
           Is the fi_key valid in the current BDM_STORE?
        """
        if not self.dc_VALID: return False
        return fi_key in self.dc_BDM_STORE[BDM_FI_COLLECTION]

    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """DC-Only: Validate the provided WF_KEY."""
        if not self.dc_VALID: return False
        return wf_key in self.dc_BDM_STORE[BDM_WF_COLLECTION]

    def dc_WF_PURPOSE_validate(self, wf_purpose: str) -> bool:
        """DC-Only: Validate the provided WF_PURPOSE."""
        return wf_purpose in VALID_WF_PURPOSE_VALUES

    def dc_WB_ID_validate(self, wb_id: str) -> bool:
        """Validate the provided WB_ID."""
        if not self.dc_VALID: return False
        _ = p3u.is_str_or_none("wb_id", wb_id, raise_error=True)
        return True if wb_id in self.dc_WORKBOOK_DATA_COLLECTION else False

    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """DC-Only: Validate the provided WB_TYPE."""
        return wb_type in VALID_WB_TYPE_VALUES

    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """DC-Only: Validate the provided WB_NAME."""
        return isinstance(wb_name, str) and len(wb_name) > 0

    def dc_WB_INDEX_validate(self, wb_index: int) -> bool:
        """DC-Only: Validate the provided wb_index.

        Test is wb_index matches a workbook present in wdc. 

        Args:
            wb_index (int): The index of the workbook to validate.

        Returns:
            bool: True if wb_index is in range and has a workbook object.
        """
        if not self.dc_VALID: return False
        if not isinstance(wb_index, int):
            m = (f"TypeError: wb_index must be a int, got {type(wb_index)}")
            logger.error(m)
            return False
        # Check if the index is valid.
        try:
            if not self.dc_WORKBOOK_DATA_COLLECTION_validate():
                return False
            if wb_index < 0 or wb_index >= len(self.dc_WORKBOOK_DATA_COLLECTION):
                m = (f"Workbook index out of range: {wb_index}")
                logger.error(m)
                return False
            bdm_wb = list(self.dc_WORKBOOK_DATA_COLLECTION.values())[wb_index]
            if bdm_wb is None:
                m = (f"No workbook with index '{wb_index}' found in dc_WORKBOOK_DATA_COLLECTION.")
                logger.error(m)
                return False
            return True
        except ValueError:
            m = (f"ValueError: wb_index '{wb_index}' is not a valid index in the "
                    f"dc_WORKBOOK_DATA_COLLECTION.")
            logger.error(m)
            return False

    def dc_WORKBOOK_DATA_COLLECTION_validate(self) -> bool:
        """Validate the type of WORKBOOK_DATA_COLLECTION."""
        if not self.dc_VALID: return False
        if self.dc_WORKBOOK_DATA_COLLECTION is None:
            logger.error("dc_WORKBOOK_DATA_COLLECTION is None.")
            return False
        wdc = self.dc_WORKBOOK_DATA_COLLECTION
        if not isinstance(wdc, dict):
            logger.error(f"dc_WORKBOOK_DATA_COLLECTION must be a dict, "
                         f"not type: '{type(wdc).__name__}'")
            return False
        return True 

    def dc_WORKBOOK_validate(self, wb : WORKBOOK_OBJECT_TYPE=None) -> bool:
        """ DC-Only: Validate the type of WORKBOOK_OBJECT_TYPE.
            Abstract: sub-class hook to test specialized WORKBOOK_OBJECT_TYPE types.
            DC-ONLY: check builtin type: 'object'. with wb_id attribute.
            Model-Aware subclasses should override to validate a specific type.
        """
        if not self.dc_VALID: return False
        if not isinstance(wb, (dict, object)): return False
        if not p3u.has_property(wb, 'wb_id'): return False
        return True

    def dc_WORKBOOK_loaded(self, wb_id: str) -> bool:
        """DC-Only: Indicates whether the workbook with wb_id is loaded."""
        if not self.dc_VALID: return False
        if (not self.dc_INITIALIZED or not self.dc_WB_ID_validate(wb_id)):
            return False
        lwbl = self.dc_LOADED_WORKBOOKS
        if (lwbl is None or 
            not isinstance(self.dc_LOADED_WORKBOOKS, dict) or
            len(lwbl) == 0):
            return False
        return True if wb_id in lwbl else False

    def dc_WORKBOOK_name(self, wb_index: int) -> str:
        """DC-Only: Return wb_name for wb_index or None if does not exist."""
        try:
            if not isinstance(wb_index, int):
                if isinstance(wb_index, str) and wb_index.isdigit():
                    wb_index = int(wb_index)
                else:
                    raise TypeError(f"wb_index must be an int, got {type(wb_index)}")
            if wb_index < 0 or wb_index >= len(self.dc_WORKBOOK_DATA_COLLECTION):
                logger.error(f"Invalid workbook index: {wb_index}")
                return None
            # WORKBOOK_TUPLE_LIST is a list of tuples, where each 
            # tuple is (wb_name, wb_path)
            obj = self.dc_WORKBOOK_DATA_COLLECTION[wb_index] 
            if isinstance(obj, object) and hasattr(obj, 'name'):
                return obj.name
            if isinstance(obj, dict) and obj.get('name', None) :
                return obj.get('name')
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise ValueError(f"Error retrieving workbook name for index {wb_index}: {e}")
    
    def dc_WORKBOOK_index(self, wb_id: str ) -> int:
        """DC-Only: Return the wb_index of a workbook from its wb_id.
        
        Args:
            wb_name (str): The name of the workbook to find.
        Returns:
            int: The index of the workbook in the WORKBOOK_DATA_COLLECTION, or -1 if not found.
        """
        try:
            wdc = self.dc_WORKBOOK_DATA_COLLECTION
            i = -1
            if wb_id is None or not isinstance(wb_id, str) or len(wb_id) == 0:
                logger.error(f" TypeError(wb_id must be a string, got {type(wb_id)})")
                return -1
            # The wb_index is determined as the index from list(wdc.keys())
            wdc_key_list = list(wdc.keys())
            if wb_id in wdc_key_list:
                # If the wb_id is in the keys, return its index.
                return wdc_key_list.index(wb_id)
            return -1
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    
    def dc_WORKBOOK_by_index(self, wb_index: int) -> Optional[WORKBOOK_OBJECT_TYPE]:
        """DC-Only: Return obj or None."""
        try:
            if self.dc_WB_INDEX_validate(wb_index):
                return list(self.dc_WORKBOOK_DATA_COLLECTION.values())[wb_index]
            return None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Error retrieving workbook by index '{wb_index}': {e}")

    def dc_WORKBOOK_find(self, find_key: str, value: str) -> WORKBOOK_OBJECT_TYPE:
        """DC-Only: Locate and return a workbook by the key and value."""
        try:
            if not self.dc_VALID:
                logger.error("Data context is not valid.")
                return None
            # If the wb_key is WB_ID, that is the key to the collection.
            if find_key == WB_ID:
                if value in self.dc_WORKBOOK_DATA_COLLECTION:
                    return self.dc_WORKBOOK_DATA_COLLECTION[value]
                else:   
                    logger.error(f"Workbook find_key '{find_key}' not found in WORKBOOK_DATA_COLLECTION.")
                    return None
            if find_key == WB_INDEX:
                # If the find_key is WB_INDEX.
                success, wb = self.dc_WORKBOOK_by_index(value)
                if success:
                    return wb
                return None
            # Search each workbook in the collection for the find_key: value.
            for wb_id, wb in self.dc_WORKBOOK_DATA_COLLECTION.items():
                if getattr(wb, find_key, None) == value:
                    return wb
            logger.warning(f"No workbook found with {find_key} = {value}.")
            return None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Error finding workbook by {find_key} = {value}: {e}")

    #region WORKBOOK_CONTENT_TYPE storage-related methods
    def dc_WORKBOOK_content_get(self, wb: WORKBOOK_OBJECT_TYPE) -> BUDMAN_RESULT_TYPE:
        """DC-Only: Get the workbook content from dc_LOADED_WORKBOOKS property
        if present. This class is not Model-Aware, so the application may
        use other means to arrange for content to be there with appropriate
        overrides or by putting the content directly with 
        dc_WORKBOOK_content_put. To be simple and consistent, use the 
        WORKBOOK_OBJECT_TYPE to access the workbook content. In other methods, 
        a wb_ref is resolved to a WORKBOOK_OBJECT_TYPE, so this method can be 
        used to get the content of a workbook by its WORKBOOK_OBJECT_TYPE.

        Args:
            wb (WORKBOOK_OBJECT_TYPE): The workbook object to retrieve content for.
        Returns:
            Optional[WORKBOOK_CONTENT_TYPE]: The content of the workbook if available,
            otherwise None.
        """
        success, result = self.dc_is_valid()
        try:
            success, result = self.dc_is_valid()
            if not success: return False, result
            if wb is None :
                logger.error("dc_WORKBOOK_CONTENT_TYPE_get requires a valid WORKBOOK_OBJECT_TYPE.")
                return False, None
            if wb.wb_id in self.dc_LOADED_WORKBOOKS:
                # If the workbook is loaded, return its content.
                return True, self.dc_LOADED_WORKBOOKS[wb.wb_id]           
            return False, None
        except Exception as e:
            m = p3u.exc_err_msg(e)  
            logger.error(m)
            return False, m
    
    def dc_WORKBOOK_content_put(self, wb_content:WORKBOOK_CONTENT_TYPE, wb: WORKBOOK_OBJECT_TYPE) -> BUDMAN_RESULT_TYPE:
        """DC-Only: Put the workbook's content into dc_LOADED_WORKBOOKS property.
        This class is not Model-Aware, so the application may
        put content in for a WORKBOOK_OBJECT_TYPE with this method in the blind.
        To be simple and consistent, use the WORKBOOK_OBJECT_TYPE to access 
        the workbook content. In other methods, a wb_ref is resolved to a 
        WORKBOOK_OBJECT_TYPE, so this method can be used to put the content of a 
        workbook by its WORKBOOK_OBJECT_TYPE.

        Args:
            wb_content (WORKBOOK_CONTENT_TYPE): The content to put into the 
            dc_LOADED_WORKBOOKS property.
            wb (WORKBOOK_OBJECT_TYPE): The workbook object owning the content.
        """
        try:
            success, result = self.dc_is_valid()
            if not success: return False, result
            if wb is None :
                logger.error("dc_WORKBOOK_CONTENT_TYPE_get requires a valid WORKBOOK_OBJECT_TYPE.")
                return None
            self.dc_LOADED_WORKBOOKS[wb.wb_id] = wb_content
            return True, None 
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
        
    def dc_WORKBOOK_load(self, bdm_wb: WORKBOOK_OBJECT_TYPE) -> BUDMAN_RESULT_TYPE:
        """ DC-Only: Load bdm_wb WORKBOOK_CONTENT_TYPE. As DC-ONLY, there is no
            direct dependency on Model. The application must set the wb_content
            attribute outside, and set bdm_wb.wb_loaded.

            Abstract: Load bdm_wb WORKBOOK_CONTENT_TYPE from storage, set value 
            or bdm_wb.wb_content, and set bdm_wb.wb_loaded. Make this bdm_wb
            the dc_WORKBOOK, so that the application can use it.

            Returns:
                BUDMAN_RESULT_TYPE: a Tuple[success: bool, result: Any].
                    success = True, result is bdm_wb.wb_content.
                    success = False, result is a string describing the error.
        """
        try:
            # DC-Only World. Can only detect and return wb_content if it is 
            # flagged as loaded, return the bdm_wb.wb_content.
            success : bool = False
            result : Any = None
            success, result = self.dc_is_valid()
            if not success: return False, result
            if not self.dc_WORKBOOK_validate(bdm_wb):
                raise TypeError(f"Invalid BDM_WORKBOOK object, "
                                f"type: '{type(bdm_wb).__name__}")
            # Check if the workbook is already loaded by some app means
            # outside this DC-Only implementation?
            wb_id = str(getattr(bdm_wb, WB_ID, None))
            wb_loaded = getattr(bdm_wb, WB_LOADED, False)
            wb_content = getattr(bdm_wb, WB_CONTENT, None)
            if not wb_loaded:
                return False, f"BDM_WORKBOOK with id '{wb_id}' is not loaded."
            # Add settings in DC for the workbook.
            self.dc_WORKBOOK = bdm_wb
            self.dc_LOADED_WORKBOOKS[wb_id] = wb_content
            return True, wb_content
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m

    def dc_WORKBOOK_save(self, bdm_wb: Workbook) -> BUDMAN_RESULT_TYPE:
        """ DC-Only: Save bdm_wb WORKBOOK_CONTENT_TYPE to storage.
            Abstract: Save bdm_wb WORKBOOK_CONTENT_TYPE to storage.
        """
        try:
            # DC-Only World. Can only detect and return wb_content if it is 
            # flagged as loaded, return the bdm_wb.wb_content.
            success : bool = False
            result : Any = None
            success, result = self.dc_is_valid()
            if not success: return False, result
            if not self.dc_WORKBOOK_validate(bdm_wb):
                raise TypeError(f"Invalid BDM_WORKBOOK object, "
                                f"type: '{type(bdm_wb).__name__}")
            wb_id = str(getattr(bdm_wb, WB_ID, None))
            return True, f"BDM_WORKBOOK with id '{wb_id}' save request."
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
        return None
    #endregion WORKBOOK_CONTENT_TYPE storage-related methods

    def dc_WORKBOOK_remove(self, wb_index: str) -> WORKBOOK_OBJECT_TYPE:
        """DC-Only: Remove the specified workbook by index from the DC.
        This implementation works only with the in-memory DC structure.
        It is not model-aware."""
        try:
            bdm_wb: BDMWorkbook = self.dc_WORKBOOK_by_index(wb_index)
            if bdm_wb is None:
                logger.error(f"Workbook with index '{wb_index}' not found.")
                return None
            if bdm_wb.wb_content :
                del bdm_wb.wb_content
                bdm_wb.wb_content = None
                bdm_wb.wb_loaded = False
            del self.dc_WORKBOOK_DATA_COLLECTION[bdm_wb.wb_id]
            return bdm_wb
        except Exception as e:
            logger.error(f"Failed to remove workbook '{wb_index}': {e}")
            raise
        return None

    def dc_WORKBOOK_add(self, wb_name: str, wb: Union[Workbook, Dict]) -> None:
        """DC-Only: Add a new workbook to the data context."""
        # TODO: Not used yet, Handle duplicates by wb_name, need wb_id for uniqueness
        self.dc_WORKBOOK_DATA_COLLECTION[wb_name] = wb
        return None

    def dc_BDM_STORE_load(self, bdm_url: str) -> None:
        """DC-Only: Load a BDM_STORE from bdm_url, set dc_BDM_STORE.
        All relevant DC values reference the dc_BDM_STORE.
        Override this method to bind to a concrete Model implementation, 
        for the budget_domain_model. This implementation has no BDM but will
        read the BDM_STORE from a json file in storage.
        """
        try:
            bdm_store = bsm.bsm_BDM_STORE_url_get(bdm_url)
            if bdm_store is None:
                raise ValueError(f"Failed to load BDM_STORE from URL: {bdm_url}")
            self.dc_BDM_STORE = bdm_store
            self.dc_INITIALIZED = True
            return self.dc_BDM_STORE
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise RuntimeError(f"Failed to load BDM_STORE from URL '{bdm_url}': {m}")

    def dc_BDM_STORE_save(self, file_path: str) -> None:
        """Save the BDM_STORE to the specified file path."""
        logger.error("BDM_STORE_save method is not implemented in this interface.")
        return None
    
    #endregion BudManAppDataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
    #region    Helper methods
    # ------------------------------------------------------------------------ +
    #region dc_is_valid()
    def dc_is_valid(self) -> BUDMAN_RESULT_TYPE:
        """DC-Only: Check if the data context is valid and usable.
        Returns:
            BUDMAN_RESULT_TYPE: A tuple of (success: bool, reason: str).0
            bool: True if the data context is valid, False otherwise.   
            str: A 'reason' message indicating the reason for invalidity.
        """
        # If initialization in progress, then act like it is valid, during the
        # initialization process.
        if self._initialization_in_progress:
            m = "Data context initialization in progress."
            logger.debug(m)
            return True, m
        if not isinstance(self, BudManAppDataContext_Base):
            m = "Data context must be an instance of BudManAppDataContext_Base"
            logger.error(m)
            return False, m
        if not self.dc_INITIALIZED:
            m = "Data context is not initialized."
            logger.error(m)
            return False, m
        if self._dc_BDM_STORE is None:
            m = "Data context BDM_STORE is not set."
            logger.error(m)
            return False, m
        if self._dc_FI_OBJECT is None:
            m = "Data context FI_OBJECT is not set."
            logger.error(m)
            return False, m
        return True, "It's all good, the data context is valid."
    #endregion dc_is_valid()
    # ------------------------------------------------------------------------ +
    #region dc_WORKBOOK_has_property(wb: WORKBOOK_OBJECT_TYPE, prop: str) -> bool
    def dc_WORKBOOK_has_property(self, wb: WORKBOOK_OBJECT_TYPE, prop: str) -> bool:
        """DC-Only: Check if the workbook has a specific property.
        
        Args:
            wb (WORKBOOK_OBJECT_TYPE): The workbook object to check.
            prop (str): The property name to check for.
        
        Returns:
            bool: True if the workbook has the property, False otherwise.
        """
        if not self.dc_VALID:
            logger.error("Data context is not valid.")
            return False
        return p3u.has_property(wb, prop)
    #endregion dc_WORKBOOK_has_property(wb: WORKBOOK_OBJECT_TYPE, prop: str) -> bool
    # ------------------------------------------------------------------------ +
    #endregion Helper methods
    # ------------------------------------------------------------------------ +
