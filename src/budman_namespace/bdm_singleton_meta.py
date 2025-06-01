# ---------------------------------------------------------------------------- +
#region bdm_singleton_meta.py module
""" BDMSingletonMeta is a meta class implementing the Singleton Pattern.

    Following a rough MVVM pattern, the BudgetDomainModel (BDM)) there is
    a need to manage data objects in memory for the host application. This
    class provides a simple Singleton pattern to continuously use one
    instance of each class that inherits from it. 
"""
#endregion bdm_singleton_meta.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABCMeta
import logging
# third-party modules and packages
from p3_utils import dscr
import p3logging as p3l
# local modules and packages
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMSingletonMeta(ABCMeta):
    """Metaclass for implementing the Singleton pattern for subclasses."""
    _instances = {}

    # As a metaclass, __call__() runs when an instance is created as an
    # override to the normal __new__ method which is called by the type() 
    # metaclass for all python classes. So, call super() to use the normal
    # class behavior in addition to what SingletonMeta is doing.
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Runs only for the first instance of the cls (class).
            # Invokes cls.__new__(), then cls.__init__(), which constructs 
            # a new cls instance. By default, the type() metaclass does this.
            _new_inst = super().__call__(*args, **kwargs)
            # Apply the singleton pattern, one instance per class.
            cls._instances[cls] = _new_inst
            # Save the cls so code knows what subclass was instantiated.
            _new_inst._subclassname = cls.__name__
            logger.debug(f"Created first {dscr(_new_inst)}")
        logger.debug(f"Return {dscr(cls._instances[cls])}")
        return cls._instances[cls]
# ---------------------------------------------------------------------------- +
