# ---------------------------------------------------------------------------- +
#region data_context_base_ABC.py module
""" DataContext_Base: Abstract Base Class interface.

    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers, providing an abstraction for data used by ViewModels, 
    Models and a View.

    A Data Context is not a Model, nor a View Model, it is a bridge between
    the two. It provides a way to access and manipulate data without exposing
    the underlying implementation details. It provides the application context
    at any moment in time, so the values change.

    This ABC defines the interface which is applied by concrete implementations.
"""
#endregion budman_data_context_base_ABC.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABC, abstractmethod
from typing import Tuple, Any, Union, Dict, Optional
# third-party modules and packages
# local modules and packages
#endregion Imports
# ---------------------------------------------------------------------------- +
class DataContext_Base(ABC):
    """Abstract Base Class Interface for mvvm Data Context."""
    # ------------------------------------------------------------------------ +
    #region DataContext_Base Properties (abstract) 
    @property
    @abstractmethod
    def dc_id(self) -> str:
        """Identify the data context implementation."""
        pass
    @dc_id.setter
    @abstractmethod
    def dc_id(self, value: str) -> None:
        """Set the identifier for the data context implementation."""
        pass

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

    #endregion DataContext_Base Properties (abstract)
    # ------------------------------------------------------------------------ +
    #region DataContext_Base Methods (abstract)
    @abstractmethod
    def dc_initialize(self) -> Dict[str, Any]:
        """Initialize the data context."""
        pass
    #endregion DataContext_Base Methods (abstract)
    # ------------------------------------------------------------------------ +
