# ---------------------------------------------------------------------------- +
#region budman_settings.py
""" Application settings support fo the Budget Manager (BudMan) app."""
#endregion budman_settings.py
# ---------------------------------------------------------------------------- +
#region Imports
# python standard libraries packages and modules 
import logging
# third-party  packages and module libraries
from dynaconf import Dynaconf
from p3_utils import exc_err_msg, dscr
# local packages and module libraries
from .budman_settings_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
logger = logging.getLogger(__name__)
class SingletonSettingsMeta(type):
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
class BudManSettings(metaclass=SingletonSettingsMeta):
    """A manage a singleton settings object for the BudMan app."""
    def __init__(self) -> None:
        """Initialize the BudManSettings instance."""
        self._settings = BudManApp_settings = Dynaconf(
                envvar_prefix="DYNACONF",
                settings_files=[BUDMAN_SETTINGS, '.secrets.toml'],
            )

    def __repr__(self) -> str:
        return f"<BudManSettings: {self.settings.to_dict()}>"
    @property
    def settings(self) -> Dynaconf:
        """Return the settings object."""
        return self._settings
    
#region configure_settings() function
def configure_settings(self) -> None:
    """Setup the application settings."""
    try:
        # Configure settings

        self._settings = BudManApp_settings = Dynaconf(
                envvar_prefix="DYNACONF",
                settings_files=[BUDMAN_SETTINGS, '.secrets.toml'],
            )
        return self
    except Exception as e:
        print(exc_err_msg(e))
        raise
#endregion configure_settings() function
# ------------------------------------------------------------------------ +
