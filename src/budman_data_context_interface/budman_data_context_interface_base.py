# ---------------------------------------------------------------------------- +
#region budman_data_context_base_interface.py module
""" BudManDataContextBaseInterface: interface for a Budget Manager Data Context.

    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers. A DC is an abstraction for data used by ViewModels
    and Models and even directly by a View.

    The properties and methods reflect the application design language, in terms
    of the domain model objects, command processing, etc. 
"""
#endregion budman_data_context_base_interface.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budget_manager_domain_model import design_language_namespace as bdmns
# from .budget_model_constants import  *
# from .budget_category_mapping import (
#     map_category, category_map_count)
# from .budget_domain_model import BudgetDomainModel
# from data.p3_fi_transactions.budget_model import BudgetModel
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManDataContextBaseInterface(ABC):
    """BudManDataContextBaseInterface: Interface for a Budget Manager Data Context."""
    # ------------------------------------------------------------------------ +
    #region Abstract Properties
    @property
    @abstractmethod
    def INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        pass
    @INITIALIZED.setter
    @abstractmethod
    def INITIALIZED(self, value: bool) -> None:
        """Set the initialized state of the data context."""
        pass

    @property
    @abstractmethod
    def dc_FI_KEY(self) -> str:
        """Return the FI_KEY for the financial institution."""
        pass
    @dc_FI_KEY.setter
    @abstractmethod
    def dc_FI_KEY(self, value: str) -> None:
        """Set the FI_KEY for the financial institution."""
        pass

    @property
    @abstractmethod
    def dc_WF_KEY(self) -> str:
        """Return the WF_KEY for the workflow."""
        pass
    @dc_WF_KEY.setter
    @abstractmethod
    def dc_WF_KEY(self, value: str) -> None:
        """Set the WF_KEY for the workflow."""
        pass

    @property
    @abstractmethod
    def dc_WB_TYPE(self) -> str:
        """Return the WB_TYPE workbook type."""
        pass
    @dc_WB_TYPE.setter
    @abstractmethod
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the WB_TYPE workbook type."""
        pass

    @property
    @abstractmethod
    def dc_WB_NAME(self) -> str:
        """Return the WB_NAME workbook name."""
        pass
    @dc_WB_NAME.setter
    @abstractmethod
    def dc_WB_NAME(self, value: str) -> None:
        """Set the WB_NAME workbook name."""
        pass

    @property
    @abstractmethod
    def dc_BUDMAN_STORE(self) -> str:
        """Return the BUDMAN_STORE jsonc definition."""
        pass
    @dc_BUDMAN_STORE.setter
    @abstractmethod
    def dc_BUDMAN_STORE(self, value: str) -> None:
        """Set the BUDMAN_STORE jsonc definition."""
        pass

    @property
    @abstractmethod
    def dc_WORKBOOKS(self) -> bdmns.WORKBOOK_LIST:
        """Return the list of workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its absolute path.
        """
        pass
    @dc_WORKBOOKS.setter
    @abstractmethod
    def dc_WORKBOOKS(self, value: bdmns.WORKBOOK_LIST) -> None:
        """Set the list of workbooks in the DC."""
        pass

    @property
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self) -> bdmns.LOADED_WORKBOOK_LIST:
        """Return the list of loaded workbooks in the DC.
        This is a List of tuples, where each tuple contains the workbook name
        and its Workbook object.
        """
        pass
    @dc_LOADED_WORKBOOKS.setter
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self, value: bdmns.LOADED_WORKBOOK_LIST) -> None:
        """Set the list of loaded workbooks in the DC."""
        pass
    #endregion Abstract Properties
    # ------------------------------------------------------------------------ +
    #region Abstract Methods
    @abstractmethod
    def initialize(self) -> None:
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
    def WORKBOOK_loaded(self, wb_name: str) -> bool:
        """Indicates whether the named workbook is loaded."""
        pass

    @abstractmethod
    def WORKBOOK_load(self, wb_name: str) -> Workbook:
        """Load the specified workbook by name."""
        pass

    @abstractmethod
    def WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """Save the specified workbook by name."""
        pass

    @abstractmethod
    def WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        pass

    @abstractmethod
    def WORKBOOK_add(self, wb_name: str, wb: Workbook) -> None:
        """Add a new workbook to the data context."""
        pass

    @abstractmethod
    def BUDMAN_STORE_load(self, file_path: str) -> None:
        """Load the BUDMAN_STORE from the specified file path."""
        pass

    @abstractmethod
    def BUDMAN_STORE_save(self, file_path: str) -> None:
        """Save the BUDMAN_STORE to the specified file path."""
        pass

    #endregion Abstract Methods
    # ------------------------------------------------------------------------ +
