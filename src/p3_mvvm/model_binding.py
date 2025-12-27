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
from .model_base_ABC import Model_Base
#endregion imports
# ---------------------------------------------------------------------------- +
class Model_Binding(Model_Base):
    """
    A Model Binding in the MVVM pattern identifies the host class as being
    bound to a concrete instance of a Model Object. In this abstract MVVM
    framework, the 'model' property is implemented by the host class so that
    at DI time, the concrete model can be set. Host class methods then access
    the Model interface methods via self.model.
    """
    # ------------------------------------------------------------------------ +
    #region Model_Binding __init__() method
    def __init__(self) -> None:
        """Model_Binding: Simple instantiation-time initialization. 
        Binding happens at initialization-time."""
        # super().__init__()
        self._model: Model_Base = None
    #endregion Model_Binding __init__() method
    # ------------------------------------------------------------------------ +
    #region    Model_Binding Properties

    @property
    def model(self) -> object:
        """Return model object binding."""
        return self._model
    @model.setter
    def model(self, mo: object) -> None:
        """Set the model object binding."""
        self._model = mo

    @property
    def model_id(self) -> str:
        """Return the model ID."""
        return self.model.model_id

    #endregion Model_Binding Properties