# ---------------------------------------------------------------------------- +
#region p3_execl_budget.p3_banking_transactions transaction_files.py module
""" Support for reading and writing excel files for FI transactions.

    Assumptions:
    - The FI transactions are in a folder specified in the budget_config.
    - Banking transaction files are typical excel spreadsheets. 
    - Data content starts in cell A1.
    - Row 1 contains column headers. All subsequent rows are data.
"""
#endregion p3_execl_budget.p3_banking_transactions transaction_files.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from .budget_model_constants import *
from budget_model_template import _BudgetModelTemplate
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Model (MVVM sense of Model)
# ---------------------------------------------------------------------------- +
class SingletonMeta(type):
    """Metaclass for implementing the Singleton pattern for subclasses."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
# ---------------------------------------------------------------------------- +
class BudgetModel(metaclass=SingletonMeta):
    """BudgetModel class implementing Singleton pattern.
    
        A singleton class to manage the budget model for the application.
        This class is used to store and manage the budget data, including
        the budget folder, institutions, and options. Uses only dict-friendly
        items.

        Properties:
        -----------
        - budget_folder_path_str: A pathname to a parent budget folder, 
            e.g., ~/OneDrive/budget.
        - budget_folder_abs_path: A Path object representing the absolute path
            to the budget folder.
        - institutions: A dictionary to store the financial institutions.
        - options: A dictionary to store the options for the budget model.
        - budget_data: A dictionary to store non-persistent the budget data.
    """
    # ------------------------------------------------------------------------ +
    #region BudgetModel class constructor __init__()
    def __init__(self) -> None:
        # Private attributes initialization, basic stuff only.
        # for serialization ease, always persist dates as str type.
        logger.debug("Start: BudgetModelTemplate() Initialization...")
        setattr(self, BM_INITIALIZED, False)
        setattr(self, BM_BF, None)  # budget folder path
        setattr(self, BM_FI, {})  # financial institutions
        setattr(self, BM_STORE_URI, None)  # uri for budget model store
        setattr(self, BM_OPTIONS, {})  # budget model options
        setattr(self, BM_CREATED_DATE, p3u.now_iso_date_string()) 
        setattr(self, BM_LAST_MODIFIED_DATE, self._created_date)
        setattr(self, BM_LAST_MODIFIED_BY, getpass.getuser())
        setattr(self, BM_WORKING_DATA, {})  # wd - budget model working data
    #endregion BudgetModel class constructor __init__()
    # ------------------------------------------------------------------------ +
    #region BudgetModel internal class properties
    def to_dict(self):
        '''Return BudgetModelTemplate dictionary object. Used for serialization.'''
        ret = {
            BM_INITIALIZED: self.bm_initialized,
            BM_BF: self.bm_bf,
            BM_FI: self.bm_fi,
            BM_STORE_URI: self.bm_store_uri,
            BM_OPTIONS: self.bm_options,
            BM_CREATED_DATE: self.bm_created_date,
            BM_LAST_MODIFIED_DATE: self.bm_last_modified_date,
            BM_LAST_MODIFIED_BY: self.bm_last_modified_by,
            BM_WORKING_DATA: self.bm_working_data
        }
        return ret
    def __repr__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"{{ "
        ret += f"'{BM_INITIALIZED}': {self.bm_initialized}, "
        ret += f"'{BM_BF}': '{self.bm_bf}', "
        ret += f"'{BM_FI}': '{self.bm_fi}', "
        ret += f"'{BM_STORE_URI}': '{self.bm_store_uri}', "
        ret += f"'{BM_OPTIONS}': '{self.bm_options}', "
        ret += f"'{BM_CREATED_DATE}': '{self.bm_created_date}', "
        ret += f"'{BM_LAST_MODIFIED_DATE}': '{self.bm_last_modified_date}', "
        ret += f"'{BM_LAST_MODIFIED_BY}': '{self.bm_last_modified_by}', "
        ret += f"'{BM_WORKING_DATA}': '{self.bm_working_data}' }} "
        return ret
    def __str__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"BudgetModlelTemplate({str(self.bm_bf)}): "
        ret += f"{BM_INITIALIZED} = {str(self.bm_initialized)}, "
        ret += f"{BM_BF} = '{str(self.bm_bf)}', "
        ret += f"{BM_FI} = [{', '.join([repr(fi_key) for fi_key in self.bm_fi.keys()])}], "
        ret += f"{BM_STORE_URI} = '{self.bm_store_uri}' "
        ret += f"{BM_OPTIONS} = '{self.bm_options}' "
        ret += f"{BM_CREATED_DATE} = '{self.bm_created_date}', "
        ret += f"{BM_LAST_MODIFIED_DATE} = '{self.bm_last_modified_date}', "
        ret += f"{BM_LAST_MODIFIED_BY} = '{self.bm_last_modified_by}', "
        ret += f"{BM_WORKING_DATA} = {self.bm_working_data}"
        return ret
    #endregion BudgetModel internal class properties
    # ------------------------------------------------------------------------ +
    #region BudgetModel public class properties
    @property
    def bm_initialized(self) -> bool:
        """The initialized value."""
        return self._initialized
    
    @bm_initialized.setter
    def bm_initialized(self, value )-> None:
        """Set the initialized value."""
        self._initialized = value

    @property
    def bm_bf(self) -> str:
        """The budget folder path is a string, e.g., '~/OneDrive/."""
        return self._budget_folder

    @bm_bf.setter
    def bm_bf(self, value: str) -> None:
        """Set the budget folder path."""
        self._budget_folder = value

    @property
    def bm_store_uri(self) -> str:
        """The budget model store URI."""
        return self._budget_model_store_uri
    
    @bm_store_uri.setter
    def bm_store_uri(self, value: str) -> None:
        """Set the budget model store URI."""
        self._budget_model_store_uri = value

    @property
    def bm_fi(self) -> dict:
        """The financial institutions dictionary."""
        return self._financial_institutions
    
    @bm_fi.setter
    def bm_fi(self, value: dict) -> None:
        """Set the financial institutions dictionary."""
        self._financial_institutions = value

    @property
    def bm_options(self) -> dict:
        """The budget model options dictionary."""
        return self._options
    
    @bm_options.setter
    def bm_options(self, value: dict) -> None:
        """Set the budget model options dictionary."""
        self._options = value

    @property
    def bm_created_date(self) -> str:
        """The created date."""
        return self._created_date
    
    @bm_created_date.setter
    def bm_created_date(self, value: str) -> None:  
        """Set the created date."""
        self._created_date = value

    @property
    def bm_last_modified_date(self) -> str:
        """The last modified date."""
        return self._last_modified_date
    
    @bm_last_modified_date.setter
    def bm_last_modified_date(self, value: str) -> None:
        """Set the last modified date."""
        self._last_modified_date = value

    @property
    def bm_last_modified_by(self) -> str:
        """The last modified by."""
        return self._last_modified_by
    
    @bm_last_modified_by.setter
    def bm_last_modified_by(self, value: str) -> None:
        """Set the last modified by."""
        self._last_modified_by = value
    
    @property
    def bm_working_data(self) -> dict:
        """The budget model working data."""
        return self._wd
    
    @bm_working_data.setter
    def bm_working_data(self, value: dict) -> None:
        """Set the budget model working data."""
        self._wd = value

    #endregion BudgetModel public class properties
    # ------------------------------------------------------------------------ +
    #region BudgetModel public methods
    # ------------------------------------------------------------------------ +
    #region BudgetModel.initialize(self, budget_node : dict = None) public 
    def inititailize(self, 
                 bm_src:dict=None,  # Use as config, or use template if None 
                 create_missing_folders : bool = True,
                 raise_errors : bool = True
                 ) -> None:
        """Initialize budget_model from bm_src as config, or use the 
         builtin BudgetModelTemplate by default.

        Args:
            bm_src (dict): A BudgetModelStore object to configure from. If
                None, use the BudgetModelTemplate internally.
            create_missing_folders (bool): Create missing folders if True.
            raise_errors (bool): Raise errors if True.
        """
        me = self.inititailize
        bmconfig : dict = None
        logger.debug(f"Start: BudgetModel.initialize()...")
        try:
            if bm_src is None:
                # Use the BudgetModelTemplate as the config source
                bmconfig = _BudgetModelTemplate(
                    create_missing_folders=create_missing_folders,
                    raise_errors=raise_errors)
            else:   
                bmconfig = bm_src
            # Apply the configuration to the budget model (self)
            self.bm_initialized = bmconfig.bm_initialized
            self.bm_bf = bmconfig.bm_bf
            self.bm_fi = bmconfig.bm_fi.copy()
            self.bm_store_uri = bmconfig.bm_store_uri
            self.bm_options = bmconfig.bm_options.copy()
            self.bm_created_date = bmconfig.bm_created_date
            self.bm_last_modified_date = bmconfig.bm_last_modified_date
            self.bm_last_modified_by = bmconfig.bm_last_modified_by
            self.bm_working_data = bmconfig.bm_working_data.copy()
            logger.debug(f"Complete: BudgetModel.initialize()...")
        except Exception as e:
            m = p3u.exc_msg(me, e)
            logger.error(m)
            raise
    #endregion BudgetModel.initialize(self, budget_node : dict = None) public 
    # ------------------------------------------------------------------------ +
    #region bf_ Budget Folder methods
    def bf_path(self) -> str:
        return Path(getattr(self,BM_BF)).expanduser()
    def bf_abs_path(self) -> str:
        return self.bf_path().resolve()
    #endregion bf_ Budget Folder methods
    # ------------------------------------------------------------------------ +
    #region fi_ Financial Institution methods
    def fi_path(self, inst_key: str) -> str:
        """Calculate the path of a Financial Institution folder in the
        Budget Storage Model.
        
        Each FI key, or inst_key, maps to a file folder in the budget folder.
        """
        bfp = self.bf_path().expanduser()
        bfip = bfp / inst_key # bank folder institution path
        return bfip
    def fi_abs_path(self, inst_key: str) -> str:
        return self.fi_path(inst_key).resolve()
    #endregion fi_ Financial Institution methods
    # ------------------------------------------------------------------------ +
    #region budget_model_working_data methods
    # budget_model_working_data is a dictionary to store dynamic, non-property data.
    def set_budget_model_working_data(self, key, value):
        self.budget_model_working_data[key] = value

    def get_budget_model_working_data(self, key):
        return self.budget_model_working_data.get(key, 0)
    #endregion budget_model_data methods
    # ------------------------------------------------------------------------ +
    #region fi_if_workbook_keys() function
    def fi_if_workbook_keys(self, inst_key:str=None,bm:dict=None) -> dict:
        """Get the list of workbooks in Incoming Folder (if) for the 
        specified financial nstitution (fi) key.

        Args:
            inst_key (str): The key of the institution to get the workbooks for.

        Returns:
            dict: A dictionary of workbooks with the file name as the key.
        """
        me = self.fi_if_workbook_keys
        try:

            if inst_key is None or inst_key not in self.bm_fi:
                m = f"Invalid institution key: '{inst_key}'"
                logger.error(m)
                raise ValueError(m)
            inst = self.bm_fi[inst_key]
            workbooks = inst[FI_IF_WORKBOOKS].keys()
            return workbooks
        except Exception as e:
            logger.exception(p3u.exc_msg(me, e))
            raise
    #endregion fi_if_workbook_keys() function
    # ------------------------------------------------------------------------ +
    #region load_fi_transactions() function
    def load_fi_transactions(self, inst_key:str, process_folder: str, 
                             trans_file : str = None) -> Workbook:
        """Get FI transactions from an excel file into an openpyxl.Workbook.
        
        Transactions downloaded from an FI are in a folder. 
        The file is assumed to be in the folder specified in the budget_config. 
        A folder is specified in the budget_config.json file. That folder is scanned 
        for transactions in excel files if a particular file is not specified.

        TODO: If trans_file is not specified, then scan the folder for files. 
        Return a dictionary of workbooks with the file name as the key.

        Args:
            trans_file (str): The name of the transaction file to load.

        Returns:
            Workbook: The workbook containing the FI transactions.

        """
        me = self.load_fi_transactions
        st = time.time()
        try:
            trans_path = self.fi_abs_path / trans_file
            logger.info("Loading FI transactions...")
            wb = load_workbook(filename=trans_path)
            logger.info(f"Loaded FI transactions from {str(trans_path)}")
            delta = f"{time.time() - st():.3f} seconds."
            logger.info(f"Complete: {delta}")
            return wb
        except Exception as e:
            logger.error(p3u.exc_msg(me, e))
            raise    
    #endregion load_fi_transactions() function
    # ------------------------------------------------------------------------ +
    #endregion BudgetModel public methods
# ---------------------------------------------------------------------------- +
#region check_budget_model() -> bool
def check_budget_model() -> bool:   
    """Quick check of the budget model schema is valid.

    Returns:
        bool: True if the budget model schema is valid, raise otherwise.
    """
    me = check_budget_model
    global budget_config, budget_model, budget_config_expected_keys
    global institution_expected_keys, options_expected_keys
    try:
        if (budget_model is None or 
            not isinstance(budget_model, dict) or
            len(budget_model) == 0):
            logger.warning("Budget model is not initialized.")
            return False
        # Check if the budget model contains expected keys
        for key in budget_config_expected_keys:
            if key not in budget_model:
                m = f"Budget model missing key: '{key}'"
                logger.error(m)
                raise ValueError(m)
        # Check if the institutions are valid
        for institution_key in BudgetModel.valid_institutions_keys:
            if institution_key not in budget_config["institutions"].keys():
                m = f"Budget model has invalid institution key: '{institution_key}'"
                logger.error(m)
                raise ValueError(m)
            for key in institution_expected_keys:
                if key not in budget_model["institutions"][institution_key]:
                    m = f"Budget model institution[{institution_key}] missing key: '{key}'"
                    logger.error(m)
                    raise ValueError(m)
        for key in options_expected_keys:
            if key not in budget_model["options"]:
                m = f"Budget model missing options key: '{key}'"
                logger.error(m)
                raise ValueError(m)
        return True
    except Exception as e:
        logger.error(p3u.exc_msg(me, e))
        return False
#endregion check_budget_model() -> bool
# ---------------------------------------------------------------------------- +
#region validate_budget_model() -> None
def validate_budget_model(bm:dict=None) -> None:  
    """Validate budget_model is not None and initialized."""
    try:
        bm = get_budget_model() if bm is None else bm
        if bm is None or not bm[BM_INITIALIZED]:
            # Budget model is not initialized, raise an error.
            m = "Budget model is not initialized."
            logger.error(m)
            raise RuntimeError(m)
    except Exception as e:
        m = p3u.exc_msg(validate_budget_model, e)
        logger.error(m)
        raise
#endregion validate_budget_model() -> None
# ---------------------------------------------------------------------------- +
#endregion Budget Model (MVVM sense of Model)
# ---------------------------------------------------------------------------- +
#region save_fi_transactions() function
def save_fi_transactions(workbook : Workbook = None, trans_file:str=None) -> None:
    """Save the FI transactions workbook to the filesystem.
    
    The file is assumed to be in the folder specified in the budget_config. 
    Use the folder specified in the budget_config.json file. 
    the budget_config may have an output_prefix specified which will be
    prepended to the trans_file name.

    TODO: If trans_file is not specified, then scan the folder for files. 
    Return a dictionary of workbooks with the file name as the key.

    Args:
        trans_file (str): The path of the transaction file to save.

    Returns:
        Workbook: The workbook containing the FI transactions.

    """
    me = save_fi_transactions
    st = time.time()
    try:
        # TODO: add logic to for workbook open in excel, work around.
        if (budget_config["output_prefix"] is not None and 
            isinstance(budget_config["output_prefix"], str) and
            len(budget_config["output_prefix"]) > 0):
            file_path = budget_config["output_prefix"] + trans_file
        else:
            file_path = trans_file
        trans_path = Path(budget_config["bank_transactions_folder"]) / file_path
        logger.info("Saving FI transactions...")
        workbook.save(filename=trans_path)
        logger.info(f"Saved FI transactions to '{str(trans_path)}'")
        return
    except Exception as e:
        logger.error(p3u.exc_msg(load_fi_transactions, e))
        raise    
#endregion save_fi_transactions() function
# ---------------------------------------------------------------------------- +
# ---------------------------------------------------------------------------- +
#region fi_if_workbook_abs_paths() function
def fi_if_workbook_abs_path(inst_key:str, wb_key : str) -> Path:
    """Get abs path of Incoming Folder workbook from an inst_key and wb_key.

    For a Finacial Institution (FI) designated by inst_key, get the absolute path
    of the workbook designated by wb_key. The workbook is assumed to be in the
    incoming folder (if) for the institution.

    Args:
        inst_key (str): The key of the institution to get the workbooks for.
        wb_key (str): The key of the workbook to get the absolute path for.

    Returns:
        Path: An abs path to the workbook with the wb_key as file name.
    """
    try:
        # bm = get_budget_model() if bm is None else bm
        validate_budget_model(bm)
        if inst_key is None or inst_key not in budget_model["institutions"]:
            m = f"Invalid institution key: '{inst_key}'"
            logger.error(m)
            raise ValueError(m)
        institution = budget_model[BM_FI][inst_key]
        workbooks = institution[FI_IF].values()
        return workbooks
    except Exception as e:
        m = p3u.exc_msg(fi_if_workbook_abs_path, e)
        logger.error(m)
        raise
#endregion fi_if_workbook_abs_paths() function
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        # this_app_name = os.path.basename(__file__)
        # Configure logging
        logger_name = THIS_APP_NAME
        log_config = "budget_model_logging_config.jsonc"
        # Set the log filename for this application.
        # filenames = {"file": "logs/p3ExcelBudget.log"}
        _ = p3l.setup_logging(
            logger_name = logger_name,
            config_file = log_config
        )
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"+ Running {THIS_APP_NAME} ...")
        logger.info("+ ----------------------------------------------------- +")
        logger.debug(f"Start: {THIS_APP_NAME}...")

        bm = BudgetModel()
        bm.inititailize()
        bms = str(bm)
        bmr = repr(bm)
        bmd = bm.to_dict()

        logger.debug(f"Budget Model: str() = '{bms}'")
        logger.debug(f"Budget Model: repr() = '{bmr}'")
        logger.debug(f"Budget Model: to_dict() = '{bmd}'")
        logger.info(f"Budget Model: {str(bm)}")
        _ = "pause"
    except Exception as e:
        m = p3u.exc_msg("__main__", e)
        logger.error(m)
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
