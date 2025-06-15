# ---------------------------------------------------------------------------- +
#region budman_data_context_client.py module
""" BudManDataContextClient: interface for a Budget Manager Data Context client object.

    This class defines an interface to bind to a concrete provider implementation 
    of the BudManDataContextBaseInterface. When instantiated, it is given a 
    reference to an object implementing the interface. From the client side,
    the interface is used to interact with the data context without needing to
    know the details of the implementation, as a client sdk pattern.

    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers. A DC is an abstraction for data used by ViewModels
    and Models and even directly by a View.

    The properties and methods reflect the application design language, in terms
    of the domain model objects, command processing, etc. 
"""
#endregion budman_data_context_client.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
from typing import Tuple
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budman_namespace import (
    DATA_COLLECTION, WORKBOOK_DATA_LIST, LOADED_WORKBOOK_COLLECTION,
    WORKBOOK_DATA_COLLECTION
    )
from budman_data_context import BudManDataContextBaseInterface
import p3_utils as p3u
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManDataContextClientInterface(BudManDataContextBaseInterface):
    """BudManDataContextClientInterface: Interface for a Data Context clients.
    
    This interface is used by clients to interact with a Data Context (DC)
    without needing to know the details of the implementation. The design
    pattern is to bind a provider object as the data_context at creation time.
    If the target data_context does not implement the required interface
    BudManDataContextBaseInterfaceIt, a TypeError is raised.
    """
    # ------------------------------------------------------------------------ +
    #region Class Methods
    @classmethod
    def _valid_data_context(cls, dc_value: object) -> None:
        """Check if the provided data context is valid raise error if not."""
        if not isinstance(dc_value, BudManDataContextBaseInterface):
            raise TypeError("dc_value must be an instance of BudManDataContextBaseInterface")
        return None
    #endregion Class Methods
    def __init__(self, dc_value: BudManDataContextBaseInterface) -> None:
        """Initialize the BudManDataContextClientInterface with a data context."""
        super().__init__()
        BudManDataContextClientInterface._valid_data_context(dc_value)
        self._data_context = dc_value

    #region BudManDataContextClientInterface Properties
    @property
    def data_context(self) -> BudManDataContextBaseInterface:
        """Return the data context object."""
        return self._data_context
    @data_context.setter
    def data_context(self, dc_value: BudManDataContextBaseInterface) -> None:
        """Set the data context object."""
        self._data_context = dc_value

    def _valid_DC(self) -> None:
        """raise exception if the DC property is invalid."""
        BudManDataContextClientInterface._valid_data_context(self._data_context)

    @property
    def DC(self) -> BudManDataContextBaseInterface:
        """Return the name of the data context."""
        self._valid_DC()
        return self.data_context
    @DC.setter
    def DC(self, value: BudManDataContextBaseInterface) -> None:
        """Set the name of the data context."""
        self._valid_DC()
        self.data_context = value

    @property
    def dc_INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        return self.DC.INITIALIZED
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """Set the initialized state of the data context."""
        self.DC.INITIALIZED = value

    @property
    def dc_FI_KEY(self) -> str:
        """Return the FI_KEY for the financial institution."""
        return self.DC.dc_FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """Set the FI_KEY for the financial institution."""
        self.DC.dc_FI_KEY = value

    @property
    def dc_WF_KEY(self) -> str:
        """Return the WF_KEY for the workflow."""
        return self.DC.dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """Set the WF_KEY for the workflow."""
        self.DC.dc_WF_KEY = value

    @property
    def dc_WF_PURPOSE(self) -> str:
        """Return the WF_PURPOSE workbook type."""
        return self.DC.dc_WF_PURPOSE
    @dc_WF_PURPOSE.setter
    def dc_WF_PURPOSE(self, value: str) -> None:
        """Set the WF_PURPOSE workbook type."""
        self.DC.dc_WF_PURPOSE = value

    @property
    def dc_WB_NAME(self) -> str:
        """Return the WB_NAME workbook name."""
        return self.DC.dc_WB_NAME
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
        """Set the WB_NAME workbook name."""
        self.DC.dc_WB_NAME = value

    @property
    def dc_WB_REF(self) -> str:
        """Return the current WB_REF workbook reference value."""
        return self.DC.dc_WB_REF
    @dc_WB_REF.setter
    def dc_WB_REF(self, value: str) -> None:
        """Set the WB_REF workbook reference value."""
        self.DC.dc_WB_REF = value

    @property
    def dc_BDM_STORE(self) -> str:
        """Return the BDM_STORE jsonc definition."""
        return self.DC.dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: str) -> None:
        """Set the BDM_STORE jsonc definition."""
        self.DC.dc_BDM_STORE = value

    @property
    def dc_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """Return the list of workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its absolute path.
        """
        return self.DC.dc_WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: WORKBOOK_DATA_LIST) -> None:
        """Set the list of workbooks in the DC."""
        self.DC.dc_WORKBOOKS = value

    @property
    def dc_WORKBOOK_DATA_COLLECTION(self) -> WORKBOOK_DATA_COLLECTION:
        """Return the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key.
        """
        if self.DC.dc_FI_KEY is None:
            return None
        return self.DC.dc_WORKBOOK_DATA_COLLECTION
    @dc_WORKBOOK_DATA_COLLECTION.setter
    def dc_WORKBOOK_DATA_COLLECTION(self, value: WORKBOOK_DATA_LIST) -> None:
        """Set the WORKBOOK_DATA_COLLECTION of workbooks in the DC.
        Depends on the value of dc_FI_KEY, returning the 
        FI_WORKBOOK_DATA_COLLECTION for that fi_key."""
        if self.DC.dc_FI_KEY is None:
            return None
        self.DC.dc_WORKBOOK_DATA_COLLECTION = value

    @property
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Return the list of loaded workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its Workbook object.
        """
        return self.DC.dc_LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Set the list of loaded workbooks in the DC."""
        self.DC.dc_LOADED_WORKBOOKS = value

    @property
    def dc_EXCEL_WORKBOOKS(self) -> DATA_COLLECTION:
        """DC-Only: Return the collection of workbooks currently open in Excel."""
        return self.DC.dc_EXCEL_WORKBOOKS
    @dc_EXCEL_WORKBOOKS.setter
    def dc_EXCEL_WORKBOOKS(self, value: DATA_COLLECTION) -> None:
        """DC-Only: Set the collection of workbooks currently open in Excel."""
        self.DC.dc_EXCEL_WORKBOOKS = value

    @property 
    def dc_CHECK_REGISTERS(self) -> DATA_COLLECTION:
        """DC-Only: Return the check register data collection."""
        return self.DC.dc_CHECK_REGISTERS
    @dc_CHECK_REGISTERS.setter
    def dc_CHECK_REGISTERS(self, value: DATA_COLLECTION) -> None:
        """DC-Only: Set the check register data collection."""
        self.DC.dc_CHECK_REGISTERS = value

    @property 
    def dc_LOADED_CHECK_REGISTERS(self) -> DATA_COLLECTION:
        """DC-Only: Return the check register data collection."""
        return self.DC.dc_CHECK_REGISTERS
    @dc_LOADED_CHECK_REGISTERS.setter
    def dc_LOADED_CHECK_REGISTERS(self, value: DATA_COLLECTION) -> None:
        """DC-Only: Set the check register data collection."""
        self.DC.dc_CHECK_REGISTERS = value



    #endregion BudManDataContextClientInterface Properties
    # ------------------------------------------------------------------------ +
    #region BudManDataContextClientInterface Methods
    def dc_initialize(self) -> None:
        """Initialize the data context."""
        super().dc_initialize()
        self.DC.dc_initialize()
        return self

    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return self.DC.dc_FI_KEY_validate(fi_key)

    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """Validate the provided WF_KEY."""
        return self.DC.dc_WF_KEY_validate(wf_key)

    def dc_WF_PURPOSE_validate(self, wf_purpose: str) -> bool:
        """Validate the provided WF_PURPOSE."""
        return self.DC.dc_WF_PURPOSE_validate(wf_purpose)

    def dc_WF_PURPOSE_validate(self, wf_purpose: str) -> bool:
        """Validate the provided WF_PURPOSE."""
        return self.DC.dc_WF_PURPOSE_validate(wf_purpose)

    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """Validate the provided WB_NAME."""
        return self.DC.dc_WB_NAME_validate(wb_name)

    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """Validate the provided workbook reference."""
        return self.DC.dc_WB_REF_validate(wb_ref)

    def dc_WF_KEY_resolve(self, wf_key : str) -> Tuple[bool, int, str]: 
        """Return True if the wf_key is valid."""
        # Bind through the DC (data_context) object.
        return self.DC.dc_WF_KEY_resolve(wf_key)

    def dc_WORKBOOKS_member(self, wb_name: str) -> bool:
        """DC-Only: Indicates whether the named workbook is a member of the DC."""
        return self.DC.dc_WORKBOOKS_member(wb_name)    

    def dc_WORKBOOK_loaded(self, wb_name: str) -> Workbook:
        """Indicates whether the named workbook is loaded."""
        return self.DC.dc_WORKBOOK_loaded(wb_name)

    def dc_WORKBOOK_load(self, wb_name: str) -> Workbook:
        """Load the specified workbook by name."""
        return self.DC.dc_WORKBOOK_load(wb_name)

    def dc_WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """Save the specified workbook by name."""
        return self.DC.dc_WORKBOOK_save(wb_name, wb)

    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        return self.DC.dc_WORKBOOK_remove(wb_name)

    def dc_WORKBOOK_add(self, wb_name: str, wb: Workbook) -> None:
        """Add a new workbook to the data context."""
        return self.DC.dc_WORKBOOK_add(wb_name, wb)

    def dc_BDM_STORE_load(self, file_path: str) -> None:
        """Load a BDM_STORE from bdm_url, set dc_BDM_STORE.
        All relevant DC values reference the dc_BDM_STORE.
        """
        return self.DC.dc_BDM_STORE_load(file_path)

    def dc_BDM_STORE_save(self, file_path: str) -> None:
        """Save the BDM_STORE to the specified file path."""
        return self.DC.dc_BDM_STORE_save(file_path)
    
    def dc_CHECK_REGISTER_name(self, wb_index: int) -> str:
        """DC-Only: Return wb_name for wb_index or None if does not exist."""
        return self.DC.dc_CHECK_REGISTER_name(wb_index)
    
    def dc_CHECK_REGISTER_index(self, wb_name: str = None) -> int:  
        """DC-Only: Return the index of a check register based on wb_name.
        
        Args:
            wb_name (str): The name of the check register to find.
        Returns:
            int: The index of the check register in the dc_CHECK_REGISTERS, or -1 if not found.
        """
        return self.DC.dc_CHECK_REGISTER_index(wb_name)
    
    def dc_CHECK_REGISTER_load(self, wb_name: str, wb_ref:str) -> DATA_COLLECTION:
        """DC-Only: Load the specified check register by name."""
        return self.DC.dc_CHECK_REGISTER_load(wb_name, wb_ref)

    def dc_CHECK_REGISTER_add(self, wb_name: str, wb_ref: str, wb: DATA_COLLECTION) -> None:
        """DC-Only: Add a new loaded workbook to the data context."""
        return self.DC.dc_CHECK_REGISTER_add(wb_name, wb_ref, wb)    

    #endregion BudManDataContextClientInterface Methods
    # ------------------------------------------------------------------------ +
