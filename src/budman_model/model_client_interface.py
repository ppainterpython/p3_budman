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
from __future__ import annotations  # For forward references in type hints
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from budget_domain_model import BDMBaseInterface
# third-party modules and packages
# local modules and packages
#endregion imports
# ---------------------------------------------------------------------------- +
class BDMClientInterface(ABC):
    """BDMClient: Abstract Base Class for BDM Dependency Injection.
    Any class needing to dynamically bind to a model object in 
    the Budget Domain Model should be a subclass. Classes approved to 
    serve as a BDM model implementation should be subclasses of 
    BDMBaseInterface. Classes wanting to bind to a model object as a 
    client should implement this interface, BDMClientInterface
    """
    
    @property
    @abstractmethod
    def model(self) -> BDMBaseInterface:
        """Return model object binding."""
        pass

    @model.setter
    @abstractmethod
    def model(self, mo: BDMBaseInterface) -> None:
        """Set the model object binding."""
        pass    