# ---------------------------------------------------------------------------- +
#region view_base_ABC.py
"""View_Base: Abstract Base Class - identifies a concrete View object."""
#endregion view_base_ABC.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from abc import ABC, abstractmethod
# third-party modules and packages
# local modules and packages
#endregion imports
# ---------------------------------------------------------------------------- +
class View_Base(ABC):
    """Abstract Base Class for concrete View Object.
    Any class providing a concrete View implementation as a subclass  
    should provide the view_id property.
    A View in the MVVM pattern has a specific role, that is 
    application-specific. 
    An application's Domain Model may be implemented in a variety of
    designs. Dependency Injection (DI) and Inversion of Control (IoC) design
    patterns are useful to enable lazy, dynamic binding to Models suitable
    to the use case circumstances. These interfaces are lightweight and provide
    a simple contract for classes that identify as a Model object.
    """
    
    @property
    @abstractmethod
    def app_name(self) -> str:
        """Return the ViewModel object's application name."""
        pass

