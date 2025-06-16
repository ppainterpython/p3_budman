# ---------------------------------------------------------------------------- +
#region test_budman_data_context.py
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
#endregion test_budman_data_context.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Tuple, Any
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
from budman_namespace import (
    FI_OBJECT, BDM_FI_COLLECTION, BDM_WF_COLLECTION,
    VALID_WF_PURPOSE_VALUES,
    VALID_WB_TYPE_VALUES,
    DATA_CONTEXT, WORKBOOK_DATA_LIST, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION, WORKFLOW_DATA_COLLECTION,
    BDM_STORE, DATA_COLLECTION, ALL_KEY, FI_KEY, WF_KEY, WB_REF, WB_NAME,
    WB_TYPE, WF_PURPOSE)
from budman_data_context import BudManDataContext_Base
from budget_storage_model.csv_data_collection import (csv_DATA_COLLECTION_get)
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class BudManDataContext(BudManDataContext_Base):
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
    #region BudManDataContext__init__()
    def __init__(self, *args, dc_id : str = None) -> None:
        self._initialization_in_progress = True
        self._dc_id :str = dc_id if dc_id else self.__class__.__name__
        self._dc_initialized = False 
        self._dc_FI_OBJECT : FI_OBJECT = None 
        self._dc_FI_KEY = None       
        self._dc_WF_KEY = None       
        self._dc_WF_PURPOSE = None
        self._dc_WB_TYPE = None      
        self._dc_WB_NAME = None     
        self._dc_WB_REF = None
        self._dc_BDM_STORE : BDM_STORE = None 
        self._dc_WORKBOOKS : WORKBOOK_DATA_LIST = None # deprecated, use dc_WORKBOOK_DATA_COLLECTION
        self._dc_WORKBOOK_DATA_COLLECTION : WORKBOOK_DATA_COLLECTION = None 
        self._dc_LOADED_WORKBOOKS : LOADED_WORKBOOK_COLLECTION = None
        self._dc_EXCEL_WORKBOOKS : DATA_COLLECTION = None
        self._dc_DataContext : DATA_CONTEXT = None 
        self._dc_CHECK_REGISTERS : DATA_COLLECTION = None 
        self._dc_LOADED_CHECK_REGISTERS : DATA_COLLECTION = None 
    #endregion BudManDataContext__init__()
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Properties (concrete) 
    @property
    def dc_VALID(self) -> bool:
        """DC-Only: Indicates whether the data context is valid."""
        return self.dc_is_valid()
    
    @property
    def dc_INITIALIZED(self) -> bool:
        """DC-Only: Indicates whether the data context has been initialized."""
        return self._dc_initialized
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """DC-Only: Set the initialized state of the data context."""
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
        if self.dc_BDM_STORE is None:
            m = "dc_BDM_STORE is None. Cannot get fi_key."
            logger.warning(m)
            return None
        return self._dc_FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """DC-Only: Set the FI_KEY of the current Financial Institution.
        Depends on the value of dc_BDM_STORE.
        """
        if self.dc_BDM_STORE is None:
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
    def dc_WB_REF(self) -> str:
        """DC-Only: Return the current WB_REF workbook reference.
        
        Current means the wb_ref for the last operation on a named or referenced
        workbook. The other data in the DC is updated in a similar fashion.
        After an operation on 'all' workbooks, the dc_WB_REF is set to 'all'.
        """
        return self._dc_WB_REF
    @dc_WB_REF.setter
    def dc_WB_REF(self, value: str) -> None:
        """DC-Only: Set the WB_REF workbook reference."""
        self._dc_WB_REF = value

    @property
    def dc_BDM_STORE(self) -> str:
        """DC-Only: Return the BDM_STORE jsonc definition."""
        return self._dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: str) -> None:
        """DC-Only: Set the BDM_STORE jsonc definition."""
        self._dc_BDM_STORE = value

    @property
    def dc_WORKBOOK_DATA_COLLECTION(self) -> DATA_COLLECTION:
        """DC-Only: Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key."""
        if not self.dc_VALID: return None
        return self._dc_WORKBOOK_DATA_COLLECTION
    @dc_WORKBOOK_DATA_COLLECTION.setter
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_LIST) -> None:
        """DC-Only: Set the list of workbooks in the DC."""
        if not self.dc_VALID: return None
        self._dc_WORKBOOK_DATA_COLLECTION = value

    @property
    def dc_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """DC-Only: Return the list of workbooks in the DC."""
        return self._dc_WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: WORKBOOK_DATA_LIST) -> None:
        """DC-Only: Set the list of workbooks in the DC."""
        self._dc_WORKBOOKS = value

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

    @property
    def dc_EXCEL_WORKBOOKS(self) -> DATA_COLLECTION:
        """DC-Only: Return the collection of workbooks currently open in Excel."""
        return self._dc_EXCEL_WORKBOOKS
    @dc_EXCEL_WORKBOOKS.setter
    def dc_EXCEL_WORKBOOKS(self, value: DATA_COLLECTION) -> None:
        """DC-Only: Set the collection of workbooks currently open in Excel."""
        self._dc_EXCEL_WORKBOOKS = value

    @property 
    def dc_CHECK_REGISTERS(self) -> DATA_COLLECTION:
        """DC-Only: Return the check register data collection."""
        return self._dc_CHECK_REGISTERS
    @dc_CHECK_REGISTERS.setter
    def dc_CHECK_REGISTERS(self, value: DATA_COLLECTION) -> None:
        """DC-Only: Set the check register data collection."""
        self._dc_CHECK_REGISTERS = value

    @property 
    def dc_LOADED_CHECK_REGISTERS(self) -> DATA_COLLECTION:
        """DC-Only: Return the check register data collection."""
        return self._dc_LOADED_CHECK_REGISTERS
    @dc_LOADED_CHECK_REGISTERS.setter
    def dc_LOADED_CHECK_REGISTERS(self, value: DATA_COLLECTION) -> None:
        """DC-Only: Set the check register data collection."""
        self._dc_LOADED_CHECK_REGISTERS = value

    #endregion BudManDataContext_Base Properties (concrete)
    # ------------------------------------------------------------------------ +
    #region BudManDataContext_Base Methods (concrete)
    def dc_id(self) -> str:
        """DC-Only: Identify the data context implementation."""
        return self._dc_id

    def dc_initialize(self) -> None:
        """DC-Only: Initialize the data context."""
        self.dc_FI_OBJECT = None 
        self.dc_FI_KEY = None
        self.dc_WF_KEY = None
        self.dc_WF_PURPOSE = None
        self.dc_WB_TYPE = None
        self.dc_WB_NAME = None
        self.dc_WB_REF = None
        self.dc_BDM_STORE = dict()
        self.dc_WORKBOOKS = []
        self.dc_WORKBOOK_DATA_COLLECTION = dict()
        self.dc_LOADED_WORKBOOKS = dict()
        self.dc_EXCEL_WORKBOOKS = dict()
        self.dc_DataContext = dict()
        self.dc_CHECK_REGISTERS = dict()
        self.dc_LOADED_CHECK_REGISTERS = dict()
        self.dc_INITIALIZED = True
        self._initialization_in_progress = False
        return self

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

    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """DC-Only: Validate the provided WB_TYPE."""
        return wb_type in VALID_WB_TYPE_VALUES

    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """DC-Only: Validate the provided WB_NAME."""
        return isinstance(wb_name, str) and len(wb_name) > 0

    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """DC-Only: Validate the provided workbook reference."""
        try:
            wb_all, wb_index, wb_name = self.dc_WB_REF_resolve(wb_ref)
            if wb_all or int(wb_index) >= 0 or wb_name is not None:
                # If wb_all is True, or we have a valid index and name.
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
        try:
            # Resolve the wb_ref to a valid index and name. Without knowing
            # the type of the workbook in reference.
            # Returns: Tuple[wb_all:bool, wb_index:int, wb_name:str]:
            if wb_ref is None:
                logger.error("wb_ref is None. Cannot resolve.")
                return False, -1, None
            if isinstance(wb_ref, str):
                if wb_ref == ALL_KEY:
                    return True, -1, ALL_KEY
                if wb_ref.isdigit() or isinstance(wb_ref, int):
                    # If the wb_ref is a digit, treat it as an index.
                    wb_index = wb_ref
                    obj = self.dc_WORKBOOK_DATA_COLLECTION[wb_index]
                    if obj :
                        wb_name = getattr(obj, WB_NAME)
                        return False, wb_index, wb_name
                    if wb_index < 0 or wb_index >= len(self.dc_WORKBOOKS):
                        m = f"Invalid wb_index: {wb_index} for wb_ref: '{wb_ref}'"
                        logger.error(m)
                        return False, -1, None
                    wb_name = self.dc_WORKBOOK_name(wb_index)
                    if wb_name is None:
                        return False, -1, None
                    return False, wb_index, wb_name
                else :
                    # Could be a wb_name or a wb_url
                    wb_url_path = p3u.verify_url_file_path(wb_ref, test=False)
                    wb_name = wb_ref.strip() # TODO: flesh this out
                    if wb_url_path is not None :
                        wb_name = wb_url_path.name # TODO: flesh this out
                        wb_index = self.dc_CHECK_REGISTER_index(wb_name)
                    return False, -1, wb_name
            elif isinstance(wb_ref, int):
                # If the wb_ref is an int, treat it as an index.
                wb_index = wb_ref
                if wb_index < 0 or wb_index >= len(self.dc_WORKBOOKS):
                    m = f"Invalid wb_index: {wb_index} for wb_ref: '{wb_ref}'"
                    logger.error(m)
                    return False, -1, None
                wb_name = self.dc_WORKBOOK_name(wb_index)
                if wb_name is None:
                    return False, -1, None
                return False, wb_index, wb_name
            return False, -1, None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def dc_WORKBOOKS_member(self, wb_name: str) -> bool:
        """DC-Only: Indicates whether the named workbook is a member of the DC."""
        _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
        # Reference the DC.WORKBOOKS property.
        if (not self.dc_INITIALIZED or 
                self.dc_WORKBOOKS is None or 
                not isinstance(self.dc_WORKBOOKS, list)):
            return False
        wbl = self.dc_WORKBOOKS
        return True if wb_name in [wb[0] for wb in wbl] else False
    
    def dc_WORKBOOK_loaded(self, wb_name: str) -> bool:
        """DC-Only: Indicates whether the named workbook is loaded."""
        _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
        # Reference the DC.LOADED_WORKBOOKS property.
        if not self.dc_VALID: return False
        if (not self.dc_INITIALIZED or 
                self.dc_LOADED_WORKBOOKS is None or 
                not isinstance(self.dc_LOADED_WORKBOOKS, dict)):
            return False
        lwbl = self.dc_LOADED_WORKBOOKS
        return True if wb_name in lwbl else False

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
    
    def dc_WORKBOOK_index(self, wb_name: str = None) -> int:
        """DC-Only: Return the index of a workbook based on wb_name.
        
        Args:
            wb_name (str): The name of the workbook to find.
        Returns:
            int: The index of the workbook in the WORKBOOK_DATA_LIST, or -1 if not found.
        """
        try:
            # Note: transitioning to dc_WORKBOOK_COLLECTION from dc_WORKBOOKS
            wbc = self.dc_WORKBOOK_DATA_COLLECTION
            i = -1
            for i, (key, obj) in enumerate(wbc):
                if isinstance(obj, object) and hasattr(obj, 'name'):
                    return KeyError
                if isinstance(obj, dict) and obj.get('name', None) == wb_name:
                    return key
            return -1
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def dc_WORKBOOK_get(self, wb_url: str) -> Any:
        """DC-Only: Get the workbook at wb_url."""
        logger.warning("dc_WORKBOOK_get must be overridden.")
        return None 

    def dc_WORKBOOK_load(self, wb_index: str) -> Any:
        """DC-Only: Load the workbook indicated by wb_index."""
        try:
            if not self.dc_VALID:
                logger.error("Data context is not valid.")
                return None
            if not isinstance(wb_index, str):
                raise TypeError(f"wb_index must be a string, got {type(wb_index)}")
            wb_obj = self.dc_WORKBOOK_DATA_COLLECTION.get(wb_index, None)
            if wb_obj is None:
                m = f"dc_WORKBOOK_DATA_COLLECTION does not have a workbook with index '{wb_index}'."
                logger.error(m)
                return False, m
            return True, wb_obj
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Error loading workbook with index '{wb_index}': {e}")

    def dc_WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """DC-Only: Save the specified workbook by name."""
        wb_path = Path(wb_name)
        try:
            wb.save(wb_path)
        except Exception as e:
            logger.error(f"Failed to save workbook '{wb_name}': {e}")
            raise
        return None

    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """DC-Only: Remove the specified workbook by name."""
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
        """DC-Only: Add a new workbook to the data context."""
        self.dc_LOADED_WORKBOOKS[wb_name] = wb
        return None

    def dc_WORKBOOK_find(self, wb_key: str, value: str) -> None:
        """DC-Only: Locate and return a workbook by the key and value."""
        try:
            if not self.dc_VALID:
                logger.error("Data context is not valid.")
                return None
            if wb_key not in self.dc_WORKBOOK_DATA_COLLECTION:
                logger.error(f"Workbook key '{wb_key}' not found in WORKBOOK_DATA_COLLECTION.")
                return None
            for wb_name, wb in self.dc_WORKBOOK_DATA_COLLECTION.items():
                if getattr(wb, wb_key, None) == value:
                    return wb
            logger.warning(f"No workbook found with {wb_key} = {value}.")
            return None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Error finding workbook by {wb_key} = {value}: {e}")

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

    def dc_CHECK_REGISTER_name(self, wb_index: int) -> str:
        """DC-Only: Return wb_name for wb_index or None if does not exist."""
        try:
            if wb_index < 0 or wb_index >= len(self.dc_CHECK_REGISTERS):
                logger.error(f"Invalid workbook index: {wb_index}")
                return None
            # DATA_COLLECTION is a dict {wb_name: wb_ref} 
            wb_name, _ = self.dc_WORKBOOKS[wb_index] 
            return wb_name
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise ValueError(f"Error retrieving workbook name for index {wb_index}: {e}")
    
    def dc_CHECK_REGISTER_index(self, wb_name: str = None) -> int:
        """DC-Only: Return the index of a check_register based on wb_name.
        
        Args:
            wb_name (str): The name of the workbook to find.
        Returns:
            int: The index in the CHECK_REGISTERS DATA_COLLECTION, 
            or -1 if not found.
        """
        try:
            crl = self.dc_CHECK_REGISTERS
            for i, cr_name_in_list in enumerate(crl):
                if cr_name_in_list == wb_name:
                    return i
            return -1
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def dc_CHECK_REGISTER_load(self, wb_name, wb_ref: str) -> DATA_COLLECTION:
        """DC-Only: Load the specified workbook by wb_ref."""
        try:
            wb = csv_DATA_COLLECTION_get(wb_ref)
            self.dc_WB_NAME = wb_name
            self.dc_CHECK_REGISTERS[wb_name] = wb_ref
            self.dc_LOADED_CHECK_REGISTERS[wb_name] = wb
            return wb 
        except Exception as e:
            logger.error(f"Failed to load check register '{wb_name}': {e}")
            raise

    def dc_CHECK_REGISTER_add(self, wb_name: str, wb_ref: str, wb: DATA_COLLECTION) -> None:
        """DC-Only: Add a new loaded workbook to the data context."""
        self.dc_CHECK_REGISTERS[wb_name] = wb_ref
        self.dc_LOADED_WORKBOOKS[wb_name] = wb
        return None

    #endregion BudManDataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
    #region    Helper methods
    # ------------------------------------------------------------------------ +
    #region dc_is_valid()
    def dc_is_valid(self) -> bool:
        """DC-Only: Check if the data context is valid and initialized."""
        if not isinstance(self, BudManDataContext_Base):
            logger.error("Data context must be an instance of BudManDataContext_Base")
        if not self.dc_INITIALIZED:
            # If initialization in progress, then act like it is valid, during the
            # initialization process.
            if self._initialization_in_progress:
                logger.debug("Data context initialization in progress.")
                return True
            logger.debug("Data context is not initialized.")
            return False
        if self.dc_BDM_STORE is None:
            logger.error("Data context BDM_STORE is not set.")
            return False
        # if self.dc_FI_KEY is None:
        #     logger.error("Data context FI_KEY is not set.")
        #     return False
        return True
    #endregion dc_is_valid()
    # ------------------------------------------------------------------------ +
    #endregion Helper methods
    # ------------------------------------------------------------------------ +
