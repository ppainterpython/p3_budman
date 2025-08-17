# ---------------------------------------------------------------------------- +
#region data_context_binding_ABC.py module
"""DC_Binding: DI binding to DataContext_Base_ABC.

    This class defines an Binding interface to a concrete provider of the
    DataContext_Base_ABC interface. Binding is a reference to the Dependency
    Injection (DI) design pattern, where the client class is bound to an
    implementation of the DataContext_Base_ABC interface at runtime. When 
    instantiated, it is given a reference to an object implementing the 
    interface. From the client side, the interface is used to interact with 
    the concrete data context without needing to know the details of the 
    implementation, as a client sdk pattern.

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
class DataContext_Binding(DataContext_Base):
    """DC_Binding: Interface for a Data Context clients.
    
    This interface is used by clients to interact with a Data Context (DC)
    without needing to know the details of the implementation. The design
    pattern is to bind a provider object as the data_context at creation time.
    """
    # ------------------------------------------------------------------------ +
    #region Class Methods
    @classmethod
    def _valid_DC_Binding(cls, dc_binding: object) -> DataContext_Base:
        """DC_Binding: Return dc_value if valid, else raise exception."""
        if dc_binding is None:
            raise ValueError("DC_Binding cannot be None")
        if not isinstance(dc_binding, DataContext_Base):
            raise TypeError("DC_Binding must be subclass of DataContext_Base")
        return dc_binding
    #endregion Class Methods
    # ------------------------------------------------------------------------ +
    #region DataContext_Binding __init__() method
    def __init__(self) -> None:
        """DC_Binding: Simple instantiation-time initialization. 
        Binding happens at initialization-time."""
        # super().__init__()
        self._data_context: DataContext_Base = None
    #endregion DataContext_Binding __init__() method
    # ------------------------------------------------------------------------ +
    #region DataContext_Binding Properties
    @property
    def data_context(self) -> DataContext_Base:
        """DC_Binding: Return the data context object."""
        return self._data_context
    @data_context.setter
    def data_context(self, dc_value: DataContext_Base) -> None:
        """DC_Binding: Set the data context object."""
        self._data_context = dc_value

    @property
    def DC(self) -> DataContext_Base:
        """DC_Binding: Return the data context.
        This is DC_Binding behavior. If the binding is not valid, an exception 
        is raised. The DC property is a reference to the data context object.
        """
        return self._data_context
        # return DataContext_Binding._valid_DC_Binding(self).data_context
    @DC.setter
    def DC(self, value: DataContext_Base) -> None:
        """DC_Binding: Set the name of the data context.
        This is DC_Binding behavior. If the binding is not valid, an exception 
        is raised. The DC property is a reference to the data context object.
        """        
        self.data_context = DataContext_Binding._valid_DC_Binding(value)
    #endregion DataContext_Binding Properties
    # ------------------------------------------------------------------------ +
    #region DataContext_Base Properties (concrete)
    @property
    def dc_id(self) -> str:
        """DC_Binding: Return the identifier for the data context implementation."""
        return self.DC.dc_id
    @dc_id.setter
    def dc_id(self, value: str) -> None:
        """DC_Binding: Set the identifier for the data context implementation."""
        self.DC.dc_id = value

    @property
    def dc_INITIALIZED(self) -> bool:
        """DC_Binding: Indicates whether the data context has been initialized."""
        return self.DC.dc_INITIALIZED
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """DC_Binding: Set the initialized state of the data context."""
        self.DC.dc_INITIALIZED = value

    @property
    def dc_VALID(self) -> bool:   
        """DC-Only: Indicates whether the data context is valid."""
        return self.DC.dc_VALID

    #endregion DataContext_Base Properties (concrete)
    # ------------------------------------------------------------------------ +
    #region DataContext_Base Methods (concrete)
    def dc_initialize(self) -> None:
        """DC_Binding: Initialize the data context."""
        # super().dc_initialize()
        self.DC.dc_initialize()
        return self
    #endregion DataContext_Base Methods (concrete)
    # ------------------------------------------------------------------------ +
