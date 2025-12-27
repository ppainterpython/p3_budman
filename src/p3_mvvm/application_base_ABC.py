# ---------------------------------------------------------------------------- +
#region application_base_ABC.py
"""Application_Base: Abstract Base Class - defines the basic attributes of a
p3_mvvm application."""
#endregion application_base_ABC.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from abc import ABC, abstractmethod
# third-party modules and packages
# local modules and packages
from .command_processor_Binding import CommandProcessor_Binding
from .data_context_binding import DataContext_Binding
from .model_binding import Model_Binding

#endregion imports
# ---------------------------------------------------------------------------- +
class Application_Base(CommandProcessor_Binding, DataContext_Binding, Model_Binding, ABC):
    """Abstract Base Class for p3_mvvm application pattern.
    Any application class providing a concrete Model implementation as a subclass  
    should provide the properties and relationships defined herein.

    Each application has a Model, a View, a View Model, a Command Processor (CP)
    and a Data Context (DC).
    """
    
    @property
    @abstractmethod
    def view(self) -> str:
        """Return view object's class name to identify it."""
        pass

    @property
    @abstractmethod
    def view_model(self) -> str:
        """Return view model object's class name to identify it."""
        pass

