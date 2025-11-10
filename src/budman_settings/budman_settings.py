# ---------------------------------------------------------------------------- +
#region budman_settings.py
""" Application settings support fo the Budget Manager (BudMan) app."""
#endregion budman_settings.py
# ---------------------------------------------------------------------------- +
#region Imports
# python standard libraries packages and modules 
import os, logging
from pathlib import Path
# third-party  packages and module libraries
from dynaconf import Dynaconf
from p3_utils import exc_err_msg, dscr
# local packages and module libraries
from budman_namespace.bdm_singleton_meta import BDMSingletonMeta
from budman_namespace.design_language_namespace import (BUDMAN_SETTINGS_FILES_ENV_VAR, BUDMAN_FOLDER_ENV_VAR)
from .budman_settings_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
class BudManSettings(Dynaconf,metaclass=BDMSingletonMeta):
    """
    BudManSettings is a singleton settings object for the BudMan app.
    By default, it uses two env variables to locate the settings files:
    - `SETTINGS_FILE_FOR_BUDMAN`: Array with at least one settings file name.
       The default is "budman_settings.toml".
    - `ROOT_PATH_FOR_BUDMAN_FOLDER`: The root path for the BudMan folder.
       The dfault is "~/budget". 
    It extends the Dynaconf settings object to provide application-specific
    functions and methods.

    To override the environment variables, supply arguments to the contstructor.
    """
    def __init__(self, settings_files: str = None, root_path: str = None) -> None:
        """Initialize the BudManSettings instance."""
        try:
            print(f"Entry: settings_files='{settings_files}', root_path='{root_path}'")
            if settings_files is None:
                settings_files = os.getenv(BUDMAN_SETTINGS_FILES_ENV_VAR, BUDMAN_SETTINGS)
            if root_path is None:
                root_path = os.getenv(BUDMAN_FOLDER_ENV_VAR, str(Path.home() / "budget"))
            logger.debug(f"After Env: settings_files='{settings_files}', root_path='{root_path}'")
            super().__init__(settings_files=settings_files, root_path=root_path)
            logger.debug(f"Initialized BudManSettings: {self.to_dict()}")
        except Exception as e:
            logger.error(f"Failed to initialize BudManSettings: {exc_err_msg(e)}")
            raise

    # def __repr__(self) -> str:
    #     return f"<BudManSettings: {self.to_dict()}>"
    # ------------------------------------------------------------------------ +
    #region    BDM_STORE_abs_path()
    def BDM_STORE_abs_path(self) -> Path:
        """Return the absolute path to the BDM_STORE file."""
        try:
            budman_store_filename_value = self[BDM_STORE_FILENAME]
            budman_store_filetype_value = self[BDM_STORE_FILETYPE]
            budman_store_full_filename = f"{budman_store_filename_value}{budman_store_filetype_value}"
            budman_folder = self[BDM_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_full_filename
            return budman_store_abs_path
        except Exception as e:
            logger.error(exc_err_msg(e))
            raise
    #endregion BDM_STORE_abs_path()
    # ------------------------------------------------------------------------ +
    #region    BUDMAN_FOLDER_abs_path()
    def BUDMAN_FOLDER_abs_path(self) -> Path:
        """Return the absolute path to the BUDMAN_FOLDER file."""
        try:
            budman_folder = self[BDM_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            return budman_folder_abs_path
        except Exception as e:
            logger.error(exc_err_msg(e))
            raise
    #endregion BUDMAN_FOLDER_abs_path()
    # ------------------------------------------------------------------------ +
    #region    FI_FOLDER_abs_path()
    def FI_FOLDER_abs_path(self, fi_key:str) -> Path:
        """Return the absolute path to the FI_FOLDER."""
        try:
            budman_folder = self[BDM_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            fi_folder = budman_folder_abs_path / fi_key
            fi_folder_abs_path = Path(fi_folder).resolve()
            return fi_folder_abs_path
        except Exception as e:
            logger.error(exc_err_msg(e))
            raise
    #endregion FI_FOLDER_abs_path()
    # ------------------------------------------------------------------------ +
