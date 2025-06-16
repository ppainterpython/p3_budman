# ---------------------------------------------------------------------------- +
#region model_base_ABC.py
"""Model_Base: Abstract Base Class - identifies a concrete Model object."""
#endregion model_base_ABC.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from abc import ABC, abstractmethod
# third-party modules and packages
# local modules and packages
#endregion imports
# ---------------------------------------------------------------------------- +
class Model_Base(ABC):
    """Abstract Base Class for concrete Model Object.
    Any class providing a concrete Model implementation as a subclass  
    should provide the model_id property.
    A Model in the MVVM pattern has a specific role, that is 
    application-specific. 
    An application's Domain Model may be implemented in a variety of
    designs. Dependency Injection (DI) and Inversion of Control (IoC) design
    patterns are useful to enable lazy, dynamic binding to Models suitable
    to the use case circumstances. These interfaces are lightweight and provide
    a simple contract for classes that identify as a Model object.
    """
    
    @property
    @abstractmethod
    def model_id(self) -> str:
        """Return model object's class name to identify it."""
        pass
