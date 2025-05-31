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
import logging, uuid
from pathlib import Path
# third-party modules and packages
from p3_utils import str_empty, str_notempty, exc_err_msg
# local modules and packages
# from .budget_domain_model_identity import BudgetDomainModelIdentity
from budman_namespace import BDM_FILENAME, BDM_FILETYPE, BDM_FOLDER
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudgetDomainModelIdentity():
    """BudgetDomainModelIdentity class implements the identity of the BudgetDomainModel.

    The identity is a unique identifier for the BudgetDomainModel instance.
    It is used to identify the instance in the BDM storage model.

    In BDM, the identity of a budget domain model is closely linked with the
    file used to store the data content. There may be more than one per user.
    The uuid portion ensures uniqueness, but the location and name of the file
    is also important and considered as part of the identity.
    """
    def __init__(self, 
                 uid : str = None, 
                 filename : str = None, 
                 filetype : str = None ) -> None:
        """Initialize the BudgetDomainModelIdentity class.

        Args:
            uid : str to use as uniqueness.
        """
        # Use the default budget domain model config for default values.
        bmt = BudgetDomainModelIdentity.get_budget_model_config(default = True)
        self._uid :str = uid if str_notempty(uid) else uuid.uuid4().hex[:8] 
        self._filename : str = filename if str_notempty(filename) else bmt[BDM_FILENAME]
        self._filetype : str = filetype if str_notempty(filetype) else bmt[BDM_FILETYPE]
        self._full_filename : str = f"{filename}_{self._uid}{filetype}"
        self._bdm_folder : str = bmt[BDM_FOLDER]
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
        str_empty(value, "filename", raise_error = True)
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
        str_empty(value, "bdm_folder", raise_error = True)
        self._bdm_folder = value

    #endregion Properties
    # ------------------------------------------------------------------------ +
    #region Methods
    def bdm_store_abs_path(self) -> Path:
        """Return the path to the BudgetDomainModel.

        Args:
            bdm_folder (str): The folder to use for the BudgetDomainModel.

        Returns:
            Path: The path object for the BudgetDomainModel.
        """
        try:
            bdm_ap = Path(self.bdm_folder) / self._filename
            return bdm_ap.expanduser().resolve()
        except Exception as e:
            logger.error(exc_err_msg(e))
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
            logger.error(exc_err_msg(e))
            raise
    #endregion Methods
# ---------------------------------------------------------------------------- +