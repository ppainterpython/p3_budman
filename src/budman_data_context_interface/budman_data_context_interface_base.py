# ---------------------------------------------------------------------------- +
#region budman_data_context_base_interface.py module
""" BudManDataContextBaseInterface: Abstract Base Class interface.

    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers. A DC is an abstraction for data used by ViewModels
    and Models and even directly by a View.

    The properties and methods reflect the application design language, in terms
    of the domain model objects, command processing, etc. 

    A Data Context is not a Model, nor a View Model, it is a bridge between
    the two. It provides a way to access and manipulate data without exposing
    the underlying implementation details.

    Each property and method herein documents its purpose. 
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
#endregion Imports
# ---------------------------------------------------------------------------- +
class BudManDataContextBaseInterface(ABC):
    """Abstract Base Class Interface for Budget Manager Data Context."""

    #region Abstract Properties
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
    def dc_WB_TYPE(self) -> str:
        """Return the current WB_TYPE (workbook type) .
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
        """Return the list of workbooks in the DC."""
        pass
    @dc_WORKBOOKS.setter
    @abstractmethod
    def dc_WORKBOOKS(self, value: bdmns.WORKBOOK_LIST) -> None:
        """Set the list of workbooks in the DC."""
        pass

    @property
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self) -> bdmns.LOADED_WORKBOOK_LIST:
        """Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        pass
    @dc_LOADED_WORKBOOKS.setter
    @abstractmethod
    def dc_LOADED_WORKBOOKS(self, value: bdmns.LOADED_WORKBOOK_LIST) -> None:
        """Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        pass
    #endregion Abstract Properties
    # ------------------------------------------------------------------------ +
    #region Abstract Methods
    @abstractmethod
    def dc_initialize(self) -> None:
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
    def dc_WORKBOOK_loaded(self, wb_name: str) -> bool:
        """Indicates whether the named workbook is loaded."""
        pass

    @abstractmethod
    def dc_WORKBOOK_load(self, wb_name: str) -> Workbook:
        """Load the specified workbook by name."""
        pass

    @abstractmethod
    def dc_WORKBOOK_save(self, wb_name: str, wb: Workbook) -> None:
        """Save the specified workbook by name."""
        pass

    @abstractmethod
    def dc_WORKBOOK_remove(self, wb_name: str) -> None:
        """Remove the specified workbook by name."""
        pass

    @abstractmethod
    def dc_WORKBOOK_add(self, wb_name: str, wb: Workbook) -> None:
        """Add a new workbook to the data context."""
        pass

    @abstractmethod
    def dc_BUDMAN_STORE_load(self, file_path: str) -> None:
        """Load the BUDMAN_STORE from the specified file path. NotImplementedError.
        The design presumes that the BUDMAN_STORE is managed by the downstream
        Model implementation, that the budget_domain_model uses it to 
        initialize the state of the BDM. This implementation has no BDM.
        """
        pass

    @abstractmethod
    def dc_BUDMAN_STORE_save(self, file_path: str) -> None:
        """Save the BUDMAN_STORE to the specified file path."""
        pass

    #endregion Abstract Methods
    # ------------------------------------------------------------------------ +
