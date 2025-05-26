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
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budget_manager_domain_model import design_language_namespace as bdmns
from budman_data_context_interface import BudManDataContextBaseInterface
import p3_utils as p3u
# from .budget_model_constants import  *
# from .budget_category_mapping import (
#     map_category, category_map_count)
# from .budget_domain_model import BudgetDomainModel
# from data.p3_fi_transactions.budget_model import BudgetModel
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
    def INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        return self.DC.INITIALIZED
    @INITIALIZED.setter
    def INITIALIZED(self, value: bool) -> None:
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
    def dc_WB_TYPE(self) -> str:
        """Return the WB_TYPE workbook type."""
        return self.DC.dc_WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the WB_TYPE workbook type."""
        self.DC.dc_WB_TYPE = value

    @property
    def dc_WB_NAME(self) -> str:
        """Return the WB_NAME workbook name."""
        return self.DC.dc_WB_NAME
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
        """Set the WB_NAME workbook name."""
        self.DC.dc_WB_NAME = value

    @property
    def dc_BUDMAN_STORE(self) -> str:
        """Return the BUDMAN_STORE jsonc definition."""
        return self.DC.dc_BUDMAN_STORE
    @dc_BUDMAN_STORE.setter
    def dc_BUDMAN_STORE(self, value: str) -> None:
        """Set the BUDMAN_STORE jsonc definition."""
        self.DC.dc_BUDMAN_STORE = value

    @property
    def dc_WORKBOOKS(self) -> bdmns.WORKBOOK_LIST:
        """Return the list of workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its absolute path.
        """
        return self.DC.dc_WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: bdmns.WORKBOOK_LIST) -> None:
        """Set the list of workbooks in the DC."""
        self.DC.dc_WORKBOOKS = value

    @property
    def dc_LOADED_WORKBOOKS(self) -> bdmns.LOADED_WORKBOOK_LIST:
        """Return the list of loaded workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its Workbook object.
        """
        return self.DC.dc_LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: bdmns.LOADED_WORKBOOK_LIST) -> None:
        """Set the list of loaded workbooks in the DC."""
        self.DC.dc_LOADED_WORKBOOKS = value
    #endregion BudManDataContextClientInterface Properties
    # ------------------------------------------------------------------------ +
    #region BudManDataContextClientInterface Methods
    def initialize(self) -> None:
        """Initialize the data context."""
        super().initialize()
        return self

    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return self.DC.dc_FI_KEY_validate(fi_key)

    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """Validate the provided WF_KEY."""
        return self.DC.dc_WF_KEY_validate(wf_key)

    def dc_WB_TYPE_validate(self, wb_type: str) -> bool:
        """Validate the provided WB_TYPE."""
        return self.DC.dc_WB_TYPE_validate(wb_type)

    def dc_WB_NAME_validate(self, wb_name: str) -> bool:
        """Validate the provided WB_NAME."""
        return self.DC.dc_WB_NAME_validate(wb_name)

    def dc_WB_REF_validate(self, wb_ref: str) -> bool:
        """Validate the provided workbook reference."""
        return self.DC.dc_WB_REF_validate(wb_ref)

    def WORKBOOK_loaded(self, wb_name: str) -> Workbook:
        """Indicates whether the named workbook is loaded."""
        return self.DC.WORKBOOK_loaded(wb_name)

    def WORKBOOK_load(self, wb_name: str) -> Workbook:
        """Load the specified workbook by name."""
        return self.DC.WORKBOOK_load(wb_name)

    def WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """Save the specified workbook by name."""
        return self.DC.WORKBOOK_save(wb_name, wb)

    def WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        return self.DC.WORKBOOK_remove(wb_name)

    def WORKBOOK_add(self, wb_name: str, wb: Workbook) -> None:
        """Add a new workbook to the data context."""
        return self.DC.WORKBOOK_add(wb_name, wb)

    def BUDMAN_STORE_load(self, file_path: str) -> None:
        """Load the BUDMAN_STORE from the specified file path."""
        return self.DC.BUDMAN_STORE_load(file_path)

    def BUDMAN_STORE_save(self, file_path: str) -> None:
        """Save the BUDMAN_STORE to the specified file path."""
        return self.DC.BUDMAN_STORE_save(file_path)

    #endregion BudManDataContextClientInterface Methods
    # ------------------------------------------------------------------------ +
