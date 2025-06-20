# ---------------------------------------------------------------------------- +
#region budman_settings.py
""" Application settings support fo the Budget Manager (BudMan) app."""
#endregion budman_settings.py
# ---------------------------------------------------------------------------- +
#region Imports
# python standard libraries packages and modules 
import logging
from pathlib import Path
# third-party  packages and module libraries
from dynaconf import Dynaconf
from p3_utils import exc_err_msg, dscr
# local packages and module libraries
from budman_namespace.bdm_singleton_meta import BDMSingletonMeta
from .budman_settings_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
class BudManSettings(metaclass=BDMSingletonMeta):
    """A manage a singleton settings object for the BudMan app."""
    # TODO: Refactor to use BudManSettings as the type rather than Dynaconf.
    # Need getter and setter for settings to ensure type safety.
    # Hide use of Dynaconf from the rest of the application.
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
    # ------------------------------------------------------------------------ +
    #region    BDM_STORE_abs_path()
    def BDM_STORE_abs_path(self) -> str:
        """Return the absolute path to the BDM_STORE file."""
        try:
            budman_store_filename_value = self.settings[BDM_STORE_FILENAME]
            budman_store_filetype_value = self.settings[BDM_STORE_FILETYPE]
            budman_store_full_filename = f"{budman_store_filename_value}{budman_store_filetype_value}"
            budman_folder = self.settings[BUDMAN_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_full_filename
            return str(budman_folder_abs_path)
        except Exception as e:
            logger.error(exc_err_msg(e))
            raise
    #endregion BDM_STORE_abs_path()
    # ------------------------------------------------------------------------ +
    #region    configure_settings() function
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
