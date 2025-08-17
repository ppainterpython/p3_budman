# ---------------------------------------------------------------------------- +
#region data_context.py module
"""Concrete DataContext.

    This class is a concrete provider of the DataContext_Base_ABC interface.

    A Data Context (DC) is a component of the MVVM design pattern for 
    applications. It separates concerns by Model, View Model and View object
    functional layers, providing an traction for data used by ViewModels, 
    Models and a View.

    A Data Context is not a Model, nor a View Model, it is a bridge between
    the two. It provides a way to access and manipulate data without exposing
    the underlying implementation details. It provides the application context
    at any moment in time, so the values change.

"""
#endregion budman_data_context_client.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from typing import Tuple, Union, Dict, Optional
# third-party modules and packages

# local modules and packages
from .data_context_base_ABC import DataContext_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
class DataContext(DataContext_Base):
    """Basic DataContext as base class to inherit.
    
    This class is used by providers as a subclass.
    """
    # ------------------------------------------------------------------------ +
    #region DataContext __init__() method
    def __init__(self) -> None:
        """DC_Binding: Simple instantiation-time initialization. 
        Binding happens at initialization-time."""
        super().__init__()
        self._dc_id: str = "DataContext"
    #endregion DataContext __init__() method
    # ------------------------------------------------------------------------ +
    #region DataContext_Base Properties
    @property
    def dc_id(self) -> str:
        """Return the identifier for the data context implementation."""
        return self.dc_id
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """Set the identifier for the data context implementation."""
        self.dc_id = value

    @property
    def dc_INITIALIZED(self) -> bool:
        """Indicates whether the data context has been initialized."""
        return self.dc_INITIALIZED
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """Set the initialized state of the data context."""
        self.dc_INITIALIZED = value

    @property
    def dc_VALID(self) -> bool:
        """DC-Only: Indicates whether the data context is valid."""
        if not isinstance(self, DataContext_Base):
            return False
        if not self.dc_INITIALIZED:
            return False
    
    #endregion DataContext_Base Properties
    # ------------------------------------------------------------------------ +
    #region DataContext_Base Methods (concrete)
    def dc_initialize(self) -> None:
        """DC_Binding: Initialize the data context."""
        super().dc_initialize()
        return self
    #endregion DataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
