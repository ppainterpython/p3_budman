# ---------------------------------------------------------------------------- +
#region test_budman_data_context.py
"""DC-Only: BudManDataContext: A concrete implementation BudManDataContext_Base 
    for the Budget Manager application. 
    
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
    
    This class provides a minimalist implementation of the interface, 
    which can be extended by subclasses to provide more specific functionality. 
    Here there is no reference to outside data objects, such as a Model or 
    ViewModel. Subclasses may override or extend the default DC behavior.
"""
#endregion test_budman_data_context.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Tuple, Any, Union, Dict, Optional
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
from budman_namespace.design_language_namespace import (
    FI_OBJECT, BDM_FI_COLLECTION, BDM_WF_COLLECTION,
    VALID_WF_PURPOSE_VALUES, VALID_WB_TYPE_VALUES,
    DATA_CONTEXT, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION, WORKBOOK_OBJECT,
    BDM_STORE, DATA_COLLECTION, ALL_KEY, FI_KEY, WF_KEY, WB_ID, WB_NAME,
    WB_TYPE, WF_PURPOSE, WB_INDEX, WB_URL, BUDMAN_RESULT, WORKBOOK_CONTENT,
    BDM_DATA_CONTEXT, DC_FI_KEY, DC_WF_KEY, DC_WF_PURPOSE, DC_WB_TYPE
    )
from budman_data_context.budman_data_context_base_ABC import BudManDataContext_Base
from budget_storage_model.csv_data_collection import (csv_DATA_LIST_url_get)
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class BudManDataContext(BudManDataContext_Base):
    """Concrete, non-MVVM-Aware implementation of BudManDataContext_Base."""
    # ------------------------------------------------------------------------ +
    #region BudManDataContext__init__()
    def __init__(self, *args, dc_id : str = None) -> None:
        """DC-Only: Constructor Initialize the BudManDataContext."""
        self._initialization_in_progress = True
        self._dc_id :str = dc_id if dc_id else self.__class__.__name__
        self._dc_initialized = False 
        self._dc_FI_OBJECT : Optional[FI_OBJECT] = None 
        self._dc_FI_KEY : Optional[str] = None       
        self._dc_WF_KEY : Optional[str] = None       
        self._dc_WF_PURPOSE : Optional[str] = None
        self._dc_WB_ID : Optional[str] = None
        self._dc_WB_TYPE : Optional[str] = None      
        self._dc_WB_NAME : Optional[str] = None     
        self._dc_WB_INDEX : int = -1
        self._dc_ALL_WBS : bool = False
        self._dc_BDM_STORE : BDM_STORE = None
        self._dc_WORKBOOK : Optional[WORKBOOK_OBJECT] = None
        self._dc_WORKBOOK_DATA_COLLECTION : WORKBOOK_DATA_COLLECTION = dict()
        self._dc_LOADED_WORKBOOKS : LOADED_WORKBOOK_COLLECTION = dict()
        self._dc_DataContext : DATA_CONTEXT = dict()
    #endregion BudManDataContext__init__()
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Properties (concrete) 
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
    def dc_VALID(self) -> bool:
        """DC-Only: Indicates whether the data context is valid."""
        success, reason = self.dc_is_valid()
        return success
    
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
    def dc_id(self) -> str:
        """DC-Only: Return the id of the data context implementation."""
        return self._dc_id
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """DC-Only: Set the id of the data context implementation."""
        if not isinstance(value, str):
            raise TypeError("dc_id must be a string.")
        self._dc_id = value

    #region    dc_FI_OBJECT
    @property
    def dc_FI_OBJECT(self) -> str:
        """DC-Only: Return the FI_OBJECT of the current Financial Institution. """
        return self._dc_FI_OBJECT if self.dc_VALID else None
    @dc_FI_OBJECT.setter
    def dc_FI_OBJECT(self, value: str) -> None:
        """DC-Only: Set the FI_OBJECT of the current Financial Institution."""
        if not self.dc_VALID: return None
        self._dc_FI_OBJECT = value
    #endregion dc_FI_OBJECT

    @property
    def dc_FI_KEY(self) -> str:
        """DC-Only: Return the FI_KEY of the current Financial Institution.
        Depends on the value of dc_BDM_STORE.
        Current means that the other data in the DC is for this FI.
        """
        if self.dc_BDM_STORE is None and not self._initialization_in_progress:
            m = "dc_BDM_STORE is None. Cannot get fi_key."
            logger.warning(m)
            return None
        return self._dc_FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """DC-Only: Set the FI_KEY of the current Financial Institution.
        Depends on the value of dc_BDM_STORE.
        """
        if self.dc_BDM_STORE is None and not self._initialization_in_progress:
            m = "dc_BDM_STORE is None. Cannot set fi_key."
            logger.warning(m)
            return None
        self._dc_FI_KEY = value

    @property
    def dc_WF_KEY(self) -> str:
        """DC-Only: Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        return self._dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """DC-Only: Set the WF_KEY for the workflow."""
        self._dc_WF_KEY = value

    @property
    def dc_WF_PURPOSE(self) -> str:
        """DC-Only: Return the current WF_PURPOSE (workbook type) .
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self._dc_WF_PURPOSE
    @dc_WF_PURPOSE.setter
    def dc_WF_PURPOSE(self, value: str) -> None:
        """DC-Only: Set the WF_PURPOSE workbook type."""
        self._dc_WF_PURPOSE = value

    @property
    def dc_WB_ID(self) -> str:
        """DC-Only: Return the current WB_ID workbook reference.
        
        Current means the wb_id for the last operation on a named or referenced
        workbook. The other data in the DC is updated in a similar fashion.
        After an operation on 'all' workbooks, the dc_WB_ID is set to 'all'.
        """
        return self._dc_WB_ID
    @dc_WB_ID.setter
    def dc_WB_ID(self, value: str) -> None:
        """DC-Only: Set the WB_ID workbook reference."""
        self._dc_WB_ID = value

    @property
    def dc_WB_TYPE(self) -> str:
        """DC-Only: Return the current WB_TYPE (workbook type) .
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self._dc_WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """DC-Only: Set the WB_TYPE workbook type."""
        self._dc_WB_TYPE = value

    @property
    def dc_WB_NAME(self) -> str:
        """DC-Only: Return the current WB_NAME workbook name.
        
        Current means that the other data in the DC is for this workbook, and 
        that a user has specified this workbook specifically by name.
        This indicates the name of the workbook being processed, e.g., 'budget.xlsx',
        """
        return self._dc_WB_NAME
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
        """DC-Only: Set the WB_NAME workbook name."""
        self._dc_WB_NAME = value

    @property
    def dc_WB_INDEX(self) -> int:
        """DC-Only: Return the current WB_INDEX workbook index.
        
        Current means that the other data in the DC is for this workbook, and 
        that a user has specified this workbook specifically by index.
        The index is based on the order of workbooks in the dc_WORKBOOK_DATA_COLLECTION.
        """
        return self._dc_WB_INDEX
    @dc_WB_INDEX.setter
    def dc_WB_INDEX(self, value: int) -> None:
        """DC-Only: Set the WB_INDEX workbook index."""
        if not isinstance(value, int):
            raise TypeError(f"dc_WB_INDEX must be an int, not {type(value).__name__}")
        self._dc_WB_INDEX = value

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
    def dc_BDM_STORE(self) -> str:
        """DC-Only: Return the BDM_STORE jsonc definition."""
        return self._dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: str) -> None:
        """DC-Only: Set the BDM_STORE jsonc definition."""
        self._dc_BDM_STORE = value

    @property
    def dc_WORKBOOK(self) -> WORKBOOK_OBJECT:
        """Return the current workbook in focus in the DC."""
        if not self.dc_VALID: return None
        return self._dc_WORKBOOK
    @dc_WORKBOOK.setter
    def dc_WORKBOOK(self, value: WORKBOOK_OBJECT) -> None:
        """Set the current workbook in focus in the DC."""
        if not self.dc_VALID: return None
        if not self.dc_WORKBOOK_validate(value):
            raise TypeError(f"dc_WORKBOOK must be a valid WORKBOOK_OBJECT, "
                            f"not a type: '{type(value).__name__}'")
        self._dc_WORKBOOK = value
        self.dc_WB_INDEX = self.dc_WORKBOOK_index(value.wb_id)
        self.dc_WB_NAME = value.wb_name  # Set the wb_name in the DC.
        self.dc_WB_ID = value.wb_id

    @property
    def dc_WORKBOOK_DATA_COLLECTION(self) -> WORKBOOK_DATA_COLLECTION:
        """DC-Only: Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key. The WORKBOOK_DATA_COLLECTION
        is sorted by the key, wb_id, the wb_index is based on the sorted order."""
        if not self.dc_VALID: return None
        return self._dc_WORKBOOK_DATA_COLLECTION
    @dc_WORKBOOK_DATA_COLLECTION.setter
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_COLLECTION) -> None:
        """DC-Only: Set the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.
        The WORKBOOK_DATA_COLLECTION should be sorted by the key,
        wb_id as it is updated. The wb_index should be based on the 
        sorted order of the WORKBOOK_DATA_COLLECTION.
        """
        if not self.dc_VALID: return None
        if not isinstance(value, dict):
            raise TypeError(f"dc_WORKBOOK_DATA_COLLECTION must be a dict, "
                            f"not a type: '{type(value).__name__}'")
        self._dc_WORKBOOK_DATA_COLLECTION = dict(sorted(value.items()))

    @property
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """DC-Only: Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        return self._dc_LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """DC-Only: Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        self._dc_LOADED_WORKBOOKS = value
    #endregion BudManDataContext_Base Properties (concrete)
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Methods (concrete)
    def dc_initialize(self) -> None:
        """DC-Only: Runtime Initialize the data context."""
        try:
            # For best outcome, the subclass should set dc_BDM_STORE ahead of time.
            self.dc_BDM_STORE = dict() if self.dc_BDM_STORE is None else self.dc_BDM_STORE
            # Update DC values saved in BDM_STORE.BDM_DATA_CONTEXT.
            bdms = self.dc_BDM_STORE
            bdm_store_dc = bdms.get(BDM_DATA_CONTEXT, {})
            self.dc_FI_KEY = bdm_store_dc.get(DC_FI_KEY, None)
            self.dc_WF_KEY = bdm_store_dc.get(DC_WF_KEY, None)
            self.dc_WF_PURPOSE = bdm_store_dc.get(DC_WF_PURPOSE, None)
            self.dc_WB_TYPE = bdm_store_dc.get(DC_WB_TYPE, None)
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
        return fi_key in self.dc_BDM_STORE[BDM_FI_COLLECTION] or fi_key == ALL_KEY

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

    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """DC-Only: Validate the provided workbook reference."""
        try:
            wb_all, wb_index, wb = self.dc_WB_REF_resolve(wb_ref)
            if wb_all or int(wb_index) >= 0 or wb is not None:
                # If wb_all is True, or we have a valid index and wb.
                return True
            return False
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    
    def dc_WB_REF_resolve(self, wb_ref:str|int) -> Tuple[bool,int, str]:
        """DC-Only: Resolve a wb_ref to valid wb_index, wb_name, or ALL_KEY.

        Args:
            wb_ref (str|int): The wb_ref to validate and resolve. Expecting
            an int, str with a digit, a str with ALL_KEY, or a str with 
            wb_id, wb_name or wb_url.

        Returns:
            Tuple[wb_all:bool, wb_index:int, WORKBOOK_OBJECT: wb]: 
                (True, -1, None) if wb_ref is ALL_KEY. 
                (False, wb_index, wb) for a valid index and its workbook.
                (False, wb_index, wb) matched wb_id, wb_name or wb_url.
                (False, -1, None) if wb_ref is invalid match.
        
        Raises:
            TypeError: if wb_ref is not a str or int.
        """
        try:
            # Resolve the wb_ref to a valid index and name. Without knowing
            # the type of the workbook in reference.
            # Returns: Tuple[wb_all:bool, wb_index:int, wb_name:str]:
            if wb_ref is None:
                logger.error("wb_ref is None. Cannot resolve.")
                return False, -1, None
            # wb_ref is intended to be flexible for the user. It can be:
            # - an integer value representing a workbook index
            # - a string of digits convertible to int workbook index
            # - a string 'all' representing all workbooks
            # - a string representing a workbook id, name, or url

            # Process integer wb_index
            wi_int = self.dc_WB_INDEX_validate_int(wb_ref)
            success : bool = False
            result : Optional[WORKBOOK_OBJECT] | Optional[str] = None
            all_wbs : bool = False
            if wi_int >= 0:
                # BUDMAN_RETURN??
                wb = self.dc_WORKBOOK_by_index(wi_int)
                if wb is not None:
                    return all_wbs, wi_int, wb 
                return False, -1, None
            # Match ALL_KEY
            if isinstance(wb_ref, str) and wb_ref.strip() == ALL_KEY:
                return True, -1, None
            # If not a str, then invalid from this point.
            if not isinstance(wb_ref, str):
                return True, -1, None
            # Check for wb_id
            if wb_ref in self.dc_WORKBOOK_DATA_COLLECTION:
                wb = self.dc_WORKBOOK_DATA_COLLECTION[wb_ref]
                wb_index = self.dc_WORKBOOK_index(wb_ref)
                return False, wb_index, wb
            # Check for wb_name
            wb = self.dc_WORKBOOK_find(WB_NAME, wb_ref)
            if wb is not None:
                wb_index = self.dc_WORKBOOK_index(wb_ref)
                return False, wb_index, wb
            # Check for wb_url
            wb = self.dc_WORKBOOK_find(WB_URL, wb_ref)
            if wb is not None:
                wb_index = self.dc_WORKBOOK_index(wb_ref)
                return False, wb_index, wb
            return False, -1, None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    
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

    def dc_WORKBOOK_validate(self, wb : WORKBOOK_OBJECT) -> bool:
        """DC-Only: Validate the type of WORKBOOK_OBJECT.
        Abstract: sub-class hook to test specialized WORKBOOK_OBJECT types.
        DC-ONLY: check builtin type: 'object'.
        Model-Aware subclasses should override to validate a specific type.
        """
        if not self.dc_VALID: return False
        return isinstance(wb, object)

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
            # Note: transitioning to dc_WORKBOOK_COLLECTION from dc_WORKBOOKS
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
            # Note: transitioning to dc_WORKBOOK_COLLECTION from dc_WORKBOOKS
            wdc = self.dc_WORKBOOK_DATA_COLLECTION
            i = -1
            if wb_id is None or not isinstance(wb_id, str) or len(wb_id) == 0:
                logger.error(f" TypeError(wb_id must be a string, got {type(wb_id)})")
                return -1
            wdc_key_list = list(wdc.keys())
            if wb_id in wdc_key_list:
                # If the wb_id is in the keys, return its index.
                return wdc_key_list.index(wb_id)
            return -1
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    
    def dc_WORKBOOK_by_index(self, wb_index: int) -> Optional[WORKBOOK_OBJECT]:
        """DC-Only: Return obj or None."""
        try:
            if self.dc_WB_INDEX_validate(wb_index):
                return list(self.dc_WORKBOOK_DATA_COLLECTION.values())[wb_index]
            return None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Error retrieving workbook by index '{wb_index}': {e}")

    def dc_WORKBOOK_find(self, find_key: str, value: str) -> WORKBOOK_OBJECT:
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
        success, result = self.dc_is_valid()
        try:
            success, result = self.dc_is_valid()
            if not success: return False, result
            if wb is None :
                logger.error("dc_WORKBOOK_content_get requires a valid WORKBOOK_OBJECT.")
                return False, None
            if wb.wb_id in self.dc_LOADED_WORKBOOKS:
                # If the workbook is loaded, return its content.
                return True, self.dc_LOADED_WORKBOOKS[wb.wb_id]           
            return False, None
        except Exception as e:
            m = p3u.exc_err_msg(e)  
            logger.error(m)
            return False, m
    
    def dc_WORKBOOK_content_put(self, wb_content:WORKBOOK_CONTENT, wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """DC-Only: Put the workbook's content into dc_LOADED_WORKBOOKS property.
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
        try:
            success, result = self.dc_is_valid()
            if not success: return False, result
            if wb is None :
                logger.error("dc_WORKBOOK_content_get requires a valid WORKBOOK_OBJECT.")
                return None
            self.dc_LOADED_WORKBOOKS[wb.wb_id] = wb_content
            return True, None 
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
        
    def dc_WORKBOOK_content_load(self, wb_content:WORKBOOK_CONTENT, wb: WORKBOOK_OBJECT) -> BUDMAN_RESULT:
        """DC-Only: Load the specified workbook content by returning it from 
           dc_LOADED_WORKBOOKS property if present.
           Returns:
                BUDMAN_RESULT: a Tuple[success: bool, result: Any].
                success = True, result is a message about the loaded workbook
                indicating the workbook is available in the 
                dc_LOADED_WORKBOOKS collection.
                success = False, result is a string describing the error.
        """
        try:
            # DC-Only World
            success : bool = False
            result : Any = None
            success, result = self.dc_is_valid()
            if not success: return False, result
            # self.dc_WORKBOOK_OBJECT
            if not self.dc_WORKBOOK_validate(wb):
                raise TypeError(f"wb must be an object, got {type(wb).__name__}")
            # Check if the workbook is already loaded. But need something to 
            # look for, maybe wb_id, wb_name, or name?
            wb_id = str(getattr(wb, WB_ID, None))
            wb_name = str(getattr(wb, WB_NAME, None))
            name = str(getattr(wb, 'name', None))
            if wb_id and wb_id not in self.dc_LOADED_WORKBOOKS:
                return False, f"Workbook with id '{wb_id}' is not loaded."
            # Add settings in DC for the workbook. 
            wb_name = str(getattr(wb, WB_NAME, None))
            self.dc_WB_ID = str(self.dc_WORKBOOK_index(wb_id))
            self._dc_WB_NAME = wb_name  
            self.dc_LOADED_WORKBOOKS[wb_id] 
            return True, None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Error loading workbook id: '{wb!r}': {e}")

    def dc_WORKBOOK_content_save(self, wb_index: str, wb: Workbook) -> BUDMAN_RESULT:
        """DC-Only: Save the specified workbook content by name."""
        wb_path = Path(wb_index)
        try:
            wb.save(wb_path)
        except Exception as e:
            logger.error(f"Failed to save workbook '{wb_index}': {e}")
            raise
        return None
    #endregion WORKBOOK_CONTENT storage-related methods

    def dc_WORKBOOK_remove(self, wb_index: str) -> WORKBOOK_OBJECT:
        """DC-Only: Remove the specified workbook by index."""
        try:
            bdm_wb = self.dc_WORKBOOK_by_index(wb_index)
            if bdm_wb is None:
                logger.error(f"Workbook with index '{wb_index}' not found.")
                return None
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
        for the budget_domain_model. This implementation has no BDM.
        """
        logger.error("BDM_STORE_load method is not implemented in this interface.")
        return None

    def dc_BDM_STORE_save(self, file_path: str) -> None:
        """Save the BDM_STORE to the specified file path."""
        logger.error("BDM_STORE_save method is not implemented in this interface.")
        return None

    #endregion BudManDataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
    #region    Helper methods
    # ------------------------------------------------------------------------ +
    #region dc_is_valid()
    def dc_is_valid(self) -> BUDMAN_RESULT:
        """DC-Only: Check if the data context is valid and usable.
        Returns:
            BUDMAN_RESULT: A tuple of (success: bool, reason: str).0
            bool: True if the data context is valid, False otherwise.   
            str: A 'reason' message indicating the reason for invalidity.
        """
        # If initialization in progress, then act like it is valid, during the
        # initialization process.
        if self._initialization_in_progress:
            m = "Data context initialization in progress."
            logger.debug(m)
            return True, m
        if not isinstance(self, BudManDataContext_Base):
            m = "Data context must be an instance of BudManDataContext_Base"
            logger.error(m)
            return False, m
        if not self.dc_INITIALIZED:
            m = "Data context is not initialized."
            logger.error(m)
            return False, m
        if self.dc_BDM_STORE is None:
            m = "Data context BDM_STORE is not set."
            logger.error(m)
            return False, m
        return True, "It's all good, the data context is valid."
    #endregion dc_is_valid()
    # ------------------------------------------------------------------------ +
    #endregion Helper methods
    # ------------------------------------------------------------------------ +
