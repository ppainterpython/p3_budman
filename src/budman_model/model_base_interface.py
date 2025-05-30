# ---------------------------------------------------------------------------- +
#region bdm_interface.py
"""BDMInterface: Abstract Base Class for a BudgetDomainModel DI.

The Budget Domain Model (BDM) concept could be implemented in a variety of
classes. Dependency Injection (DI) and Inversion of Control (IoC) design
patterns are useful to enable lazy, dynamic binding to Models suitable
to the use case circumstances. These interfaces are lightweight and provide
a simple contract for classes that want to bind to a model object or be
bindable model objects in the Budget Domain Model (BDM).
"""
#endregion bdm_interface.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from abc import ABC, abstractmethod
# third-party modules and packages
# local modules and packages
#endregion imports
# ---------------------------------------------------------------------------- +
class BDMBaseInterface(ABC):
    """BDMBaseInterface: Abstract Base Class for BDM Dependency Injection.
    Any class providing a concrete implementation may be bound as a 
    model object. Classes approved to serve as a BDM model 
    implementation should be subclasses of BDMBaseInterface and implement
    the model_id property.
    """
    
    @property
    @abstractmethod
    def model_id(self) -> str:
        """Return model object's class name to identify it."""
        pass
