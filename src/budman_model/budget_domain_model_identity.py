# ---------------------------------------------------------------------------- +
#region budget_domain_model_id.py module
""" budget_domain_model_id.py implements the BudgetDomainModelIdentity class.

    A user's budget domain model identity is a unique identifier for the data
    set created and stored on the user's behalf. A short hash is used upon
    creation and incorporated into the file name of the budget domain model.

    For convenience, this class will provide path information based on the 
    identity and well-known locations.

    Properties:
        - uid : str : The unique identifier for the BudgetDomainModel.
        - name : str : The name of the BudgetDomainModel.

    Methods:
        - bdm_abs_path() : Path : Returns path to the BudgetDomainModel.
"""
#endregion budget_domain_model_id.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, time, uuid
from pathlib import Path
from typing import List, Dict

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l

# local modules and packages
from .budget_model_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudgetDomainModelIdentity:
    """BudgetDomainModelIdentity class implements the identity of the BudgetDomainModel.

    The identity is a unique identifier for the BudgetDomainModel instance.
    It is used to identify the instance in the budget storage model.

    In BDM, the identity of a budget domain model is closely linked with the
    file used to store the data content. There may be more than one per user.
    The uuid portion ensures uniqueness, but the location and name of the file
    is also important and considered as part of the identity.
    """
    def __init__(self, 
                 uid : str = None, 
                 filename : str = settings[APP_NAME],
                 filetype : str = settings[BUDMAN_STORE_FILETYPE]) -> None:
        """Initialize the BudgetDomainModelIdentity class.

        Args:
            uid : str to use as uniqueness.
        """
        self._uid = uuid.uuid4().hex[:8] if uid is None else uid
        self._name : str = filename if filename is not None else THIS_APP_NAME
        filetype_alt = filetype if filetype is not None else BSM_DEFAULT_BUDGET_MODEL_FILE_TYPE
        self._filename : str = f"{filename}_{self._uid}{filetype_alt}"
        self._bdm_folder : str = BM_DEFAULT_BUDGET_FOLDER
    # ------------------------------------------------------------------------ +
    #region Properties
    @property
    def uid(self) -> str:
        """Return the unique identifier for the BudgetDomainModel.

        Returns:
            str: The unique identifier for the BudgetDomainModel.
        """
        return self._uid
    @uid.setter
    def uid(self, value : str) -> None:
        """Set the unique identifier for the BudgetDomainModel.

        Args:
            value (str): The unique identifier for the BudgetDomainModel.
        """
        if not isinstance(value, str):
            raise ValueError(f"uid must be a string: {value}")
        self._uid = value
    @property
    def name(self) -> str:
        """Return the name of the BudgetDomainModel.

        Returns:
            str: The name of the BudgetDomainModel.
        """
        return self._name
    @name.setter
    def name(self, value : str) -> None:
        """Set the name of the BudgetDomainModel.

        Args:
            value (str): The name of the BudgetDomainModel.
        """
        if not isinstance(value, str):
            raise ValueError(f"name must be a string: {value}")
        self._name = value
    @property
    def filename(self) -> str:
        """Return the filename of the BudgetDomainModel.

        Returns:
            str: The filename of the BudgetDomainModel.
        """
        return self._filename
    @filename.setter
    def filename(self, value : str) -> None:
        """Set the filename of the BudgetDomainModel.

        Args:
            value (str): The filename of the BudgetDomainModel.
        """
        if not isinstance(value, str):
            raise ValueError(f"filename must be a string: {value}")
        self._filename = value
    @property
    def bdm_folder(self) -> str:
        """Return the folder of the BudgetDomainModel.

        Returns:
            str: The folder of the BudgetDomainModel.
        """
        return self._bdm_folder
    @bdm_folder.setter
    def bdm_folder(self, value : str) -> None:
        """Set the folder of the BudgetDomainModel.

        Args:
            value (str): The folder of the BudgetDomainModel.
        """
        if not isinstance(value, str):
            raise ValueError(f"bdm_folder must be a string: {value}")
        self._bdm_folder = value

    #endregion Properties
    # ------------------------------------------------------------------------ +
    #region Methods
    def bdm_store_abs_path(self, bdm_folder : str = BM_DEFAULT_BUDGET_FOLDER) -> Path:
        """Return the path to the BudgetDomainModel.

        Args:
            bdm_folder (str): The folder to use for the BudgetDomainModel.

        Returns:
            Path: The path object for the BudgetDomainModel.
        """
        try:
            bdm_folder = Path(bdm_folder).expanduser().resolve()
            bdm_ap = bdm_folder / self._filename
            return bdm_ap
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def bdm_store_abs_path_resolve(self) -> Path:
        """Resolve the abs_path of this BDM, returning the path if file exists.

        If the file is not accessible, an exception is raised.

        Args:
            bdm_folder (str): The folder to use for the BudgetDomainModel.

        Returns:
            Path: The path object for the BudgetDomainModel.
        
        Raises: 
            FileNotFoundError: If the file or folder does not exist.
            NotADirectoryError: If the folder path is not a directory.
            IsADirectoryError: If the path is not a file.
            ValueError: If the path is not an absolute path.
        """
        try:
            bdmi_folder = Path(self.bdm_folder).expanduser().resolve()
            if not bdmi_folder.exists():
                raise FileNotFoundError(f"Budget folder does not exist: {bdmi_folder}")
            if not bdmi_folder.is_dir():
                raise NotADirectoryError(f"Budget folder is not a directory: {bdmi_folder}")
            bdm_ap = bdmi_folder / self._filename
            if not bdm_ap.exists():
                raise FileNotFoundError(f"Budget file does not exist: {bdm_ap}")
            if not bdm_ap.is_file():
                raise IsADirectoryError(f"Budget file is not a file: {bdm_ap}")
            if not bdm_ap.is_absolute():
                raise ValueError(f"Budget file is not an absolute path: {bdm_ap}")  
            return bdm_ap
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def _new_hash():
        """Generate a new short uuid BudgetDomainModelIdentity uniqueness.

        Returns:
            str: The new uuid.
        """
        return uuid.uuid4().hex[:8]
    #endregion Methods
# ---------------------------------------------------------------------------- +