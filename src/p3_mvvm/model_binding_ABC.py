# ---------------------------------------------------------------------------- +
#region model_binding_ABC.py
"""Model_Binding: Abstract Base Class - bind to a Model concrete object."""
#endregion model_binding_ABC.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from abc import ABC, abstractmethod
from typing import Any
# third-party modules and packages
# local modules and packages
#endregion imports
# ---------------------------------------------------------------------------- +
class Model_Binding(ABC):
    """
    A Model Binding in the MVVM pattern identifies the host class as being
    bound to a concrete instance of a Model Object. In this abstract MVVM
    framework, the 'model' property is implemented by the host class so that
    at DI time, the concrete model can be set. Host class methods then access
    the Model interface methods via self.model.
    """
    
    @property
    @abstractmethod
    def model(self) -> object:
        """Return model object binding."""
        pass

    @model.setter
    @abstractmethod
    def model(self, mo: object) -> None:
        """Set the model object binding."""
        pass    