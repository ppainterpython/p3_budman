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
import logging, os, getpass
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_excel_budget_constants import *
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
#region Budget Model Template Constants
# TBM_BF = "_" + BM_BF
# TBM_INITIALIZED = "_" + BM_INITIALIZED
# TBM_FI = "_" + BM_FI
# TBM_STORE_URI = "_" + BM_STORE_URI
# TFI_FOLDER = "_" + FI_FOLDER
# TBM_OPTIONS = "_" + BM_OPTIONS
#endregion Budget Model Template Constants
# ---------------------------------------------------------------------------- +
class _BudgetModelTemplate:
    """Default BbudgetModelTemplate class, contains default, example values.
    
    Defines the BudgetModel structure with two example Financial Institutions.
    Convenient for developer.
    """
    # ------------------------------------------------------------------------ +
    #region Budget Model Configuration Template
    # Budget configuration covers the file structure where user data is stored as 
    # settings for options and preferences. Keep it simple.
    # There is both an object model used in the application (in memory) and a
    # file system structure used to store the data. In addition, the idea is that 
    # users are placing new FI transactions in an "incoming" folder folder 
    # for processing through stages to arrive in updating the budget. Long-view is 
    # anticipate more than one bank or financial institution sourcing regular 
    # statements in spreadsheet format. So, the "budget" will cover multiple "banks"
    # information for a given user.
    budget_config_expected_keys = (BM_INITIALIZED,BM_BF, BM_FI, 
                                BM_OPTIONS)
    valid_institutions_keys = ("boa", "merrill")
    institution_expected_keys = (
        FI_NAME, 
        FI_TYPE, 
        FI_FOLDER, 
        FI_IF,
        FI_IF_WORKBOOKS,
        FI_CF,
        FI_CF_WORKBOOKS,
        FI_PF,
        FI_PF_WORKBOOKS
        )
    options_expected_keys = (
        BMO_FI_IF_PREFIX, 
        BMO_FI_CF_PREFIX,
        BMO_FI_PF_PREFIX,
        BMO_LOG_CONFIG,
        BMO_LOG_LEVEL,
        BMO_LOG_FILE,
        BMO_JSON_LOG_FILE
        )
    budget_model_template = {  # _abs_path is not serialized, only _abs_path_str is serialized
        BM_INITIALIZED: False,
        BM_BF: BM_DEFAULT_BUDGET_FOLDER,
        BM_STORE_URI: None,
        BM_FI: {
            "boa": {
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                # Incoming folder name and list of workbook names,
                # e.g. ["new_boa-1391-2024-04-28.xlsx"]
                FI_IF: "data/new",
                FI_IF_WORKBOOKS: {}, # key = file name, value = absolute path
                # Categorized folder name and list of workbook names,
                # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
                FI_CF: "data/categorized",
                FI_CF_WORKBOOKS: {}, # key = file name, value = absolute path
                # Processed folder name and list of workbook names,
                # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
                FI_PF: "data/processed",
                FI_PF_WORKBOOKS: {} # key = file name, value = absolute path
            },
            "merrill": {
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                # Incoming folder name and list of workbook names,
                # e.g. ["new_boa-1391-2024-04-28.xlsx"]
                FI_IF: "data/new",
                FI_IF_WORKBOOKS: {}, # key = file name, value = absolute path
                # Categorized folder name and list of workbook names,
                # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
                FI_CF: "data/categorized",
                FI_CF_WORKBOOKS: {}, # key = file name, value = absolute path
                # Processed folder name and list of workbook names,
                # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
                FI_PF: "data/processed",
                FI_PF_WORKBOOKS: {} # key = file name, value = absolute path
            },
        },
        BM_OPTIONS: {
            BMO_FI_IF_PREFIX: "new_",
            BMO_FI_CF_PREFIX: "categorized_",
            BMO_FI_CF_PREFIX: "processed_",
            BMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BMO_LOG_LEVEL: logging.DEBUG,
            BMO_LOG_FILE: "logs/p3BudgetModel.log",
            BMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        }
    }
    # Template-only versions of structure attributes.
    # ------------------------------------------------------------------------ +
    # __init__() method for the BudgetModelTemplate class
    def __init__(self, create_missing_folders : bool = True,
                 raise_errors : bool = True) -> None:
        """Construct a BudgetModelTemplate object used to initialize the budget model.
        
        The template class is largely a dictionary populated with default values
        and some example values. The idea is to use this template to create a new
        budget model or to initialize a new budget model from the template. 
        It is for internal use only.
        """
        try:
            # Basic attribute atomic value inits. 
            # logger = logging.getLogger(THIS_APP_NAME)
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
            # Set attribute defaults for the budget model
            logger.debug(f"{P2}BM_INITIALIZED('{BM_INITIALIZED}'): "
                         f"{getattr(self,BM_INITIALIZED)}")
            setattr(self, BM_BF, BM_DEFAULT_BUDGET_FOLDER) 
            bf = getattr(self, BM_BF)  # budget folder setting, a str
            bfp = Path(bf).expanduser() # budget folder path
            bmc = bfp / BM_DEFAULT_BUDGET_MODEL_FILE_NAME # bmc: BM config file
            bfp_exists = "exists." if bfp.exists() else "does not exist!"
            bmc_exists = "exists." if bmc.exists() else "does not exist!"
            bmc_uri = p3u.path_to_file_uri(bmc) # uri for budget model config
            setattr(self, BM_STORE_URI, bmc_uri)
            logger.debug(f"{P2}BM_BF('{BM_BF}'): '{getattr(self,BM_BF)}' {bfp_exists}")
            logger.debug(
                f"{P4}_bf_path(): '{self._bf_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P4}_bf_abs_path(): '{self._bf_abs_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P2}BM_STORE_URI('{BM_STORE_URI}): '{getattr(self,BM_STORE_URI)}' "
                f"{bmc_exists}")

            # Financial Institutions (FI) as a template        # Institution folders
            bmt = _BudgetModelTemplate.budget_model_template
            fic = len(bmt[BM_FI])  # financial institutions count
            logger.debug(f"{P2}BM_FI('{BM_FI}')({fic})")
            for inst_key, inst in bmt[BM_FI].items():
                inst_folder_path = bfp / inst_key
                inst_folder_abs_path = inst_folder_path.resolve()
                ifap_exists = "exists." if inst_folder_abs_path.exists() else "does not exist!"
                logger.debug(f"{P4}Inst('{inst_key}') folder: '{inst_folder_path}'")
                if not inst_folder_abs_path.exists():
                    # If create_missing_folders is True, create the folder
                    if create_missing_folders:
                        logger.debug(f"{P4}Creating folder: '{inst_folder_abs_path}'")
                        inst_folder_abs_path.mkdir(parents=True, exist_ok=True)
                    else:
                        m = (f"{P4}Budget institution({inst_key}) " 
                            f"folder does not exist: '{str(inst_folder_abs_path)}'")
                        logger.error(m)
                        raise FileNotFoundError(m) if raise_errors else None
                getattr(self,BM_FI)[inst_key] = inst.copy()  # Copy the template values
                logger.debug(f"{P6}'{inst_key}' {str(inst)}")
                ifp = self._fi_path(inst_key)
                ifp_exists = "exists." if ifp.exists() else "does not exist!"
                logger.debug(f"{P6}_fi_path(): '{ifp}' "
                             f"{ifp_exists}")
                ifap = self._fi_abs_path(inst_key)
                logger.debug(f"{P6}_fi_abs_path(): '{ifap}'"
                             f"{ifap_exists}")

            # Initialize Budget Model Options as a template
            bmoc = len(bmt[BM_OPTIONS])
            logger.debug(f"{P2}BM_OPTION('{BM_OPTIONS}')({bmoc})")
            for opt_key, opt in bmt[BM_OPTIONS].items():
                logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

            # And the rest
            logger.debug(f"{P2}BM_CREATED_DATE({BM_CREATED_DATE}'): "
                         f"{getattr(self,BM_CREATED_DATE)}")
            logger.debug(f"{P2}BM_LAST_MODIFIED_DATE({BM_LAST_MODIFIED_DATE}'): "
                            f"{getattr(self,BM_LAST_MODIFIED_DATE)}")
            logger.debug(f"{P2}BM_LAST_MODIFIED_BY({BM_LAST_MODIFIED_BY}'): "
                            f"{getattr(self,BM_LAST_MODIFIED_BY)}")
            logger.debug(f"{P2}BM_WORKING_DATA({BM_WORKING_DATA}'): "
                            f"{getattr(self,BM_WORKING_DATA)}")
            # BudgetModelTemplate initialization is complete.
            setattr(self, BM_INITIALIZED, True)
            logger.debug(f"{P2}{BM_INITIALIZED}: {getattr(self,BM_INITIALIZED)}")
            logger.debug(f"Complete: BudgetModelTemplate() Initialization...")
        except Exception as e:
            m = p3u.exc_msg(self.__init__, e)
            logger.error(m)
            raise

    def to_dict(self):
        '''Return BudgetModel object as a dictionary. Used for serialization.'''
        ret = {
            BM_INITIALIZED: self._initialized,
            BM_BF: self._budget_folder,
            BM_FI: self._institutions,
            BM_OPTIONS: self._options,
            "budget_model_store_uri": self._budget_model_store_uri,
            "created_date": self._created_date,
            "last_modified_date": self._last_modified_date,
            "modified_by": self._modified_by
        }
        return ret
    def __repr__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"BudgetModlel({str(self._budget_folder)}) "
        ret += "'initialized' " if self._initialized else "'not initialized' "
        ret += f"Fin.Insts=[{', '.join([repr(fi_key) for fi_key in self._institutions.keys()])}], "
        ret += f"budget_model_store_uri='{self._budget_model_store_uri}' "
        ret += f"created_date='{self._created_date}', "
        ret += f"last_modified_date='{self._last_modified_date}', "
        ret += f"modified_by='{self._modified_by}', "
        return ret
    def __str__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"BudgetModlel({str(self._budget_folder)}) "
        ret += "'initialized' " if self._initialized else "'not initialized' "
        ret += f"Fin.Insts=[{', '.join([repr(fi_key) for fi_key in self._institutions.keys()])}], "
        ret += f"budget_model_store_uri='{self._budget_model_store_uri}' "
        ret += f"created_date='{self._created_date}', "
        ret += f"last_modified_date='{self._last_modified_date}', "
        ret += f"modified_by='{self._modified_by}', "
        return ret

    # Simplet getters for template values that are computed
    def _bf_path(self) -> str:
        return Path(getattr(self,BM_BF)).expanduser()
    def _bf_abs_path(self) -> str:
        return self._bf_path().resolve()

    def _fi_path(self, inst_key: str) -> str:
        """Calculate the path of a Financial Institution folder in the
        Budget Storage Model.
        
        Each FI key, or inst_key, maps to a file folder in the budget folder.
        """
        bfp = self._bf_path().expanduser()
        bfip = bfp / inst_key # bank folder institution path
        return bfip
    def _fi_abs_path(self, inst_key: str) -> str:
        return self._fi_path(inst_key).resolve()
        

    #endregion Budget Model Configuration
    # ---------------------------------------------------------------------------- +
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
    #region BudgetModel class constructor __init__() method
    def __init__(self) -> None:
        # Private attributes initialization, basic stuff only.
        # for serialization ease, always persist dates as str type.
        self._initialized : bool = False  # BM_INITIALIZED
        self._budget_folder : Path = None # BM_BF
        self._institutions : dict = {}    # BM_FI # dict {key(FINAME): value(BugdetModelFinancialInstitution)} class?
        self._options = {}                # BM_OPTIONS
        self._created_date : str= p3u.now_iso_date_string()  # store dates as str
        self._last_modified_date : str = self._created_date
        self._modified_by : str = self._last_modified_datemodified_by
        self._budget_model_store_uri : str = ""  # uri for budget model store
        self._wd = {}  # Working data, if needed
    #endregion BudgetModel class constructor
    # ------------------------------------------------------------------------ +
    #region BudgetModel internal class properties
    def to_dict(self):
        '''Return BudgetModel object as a dictionary. Used for serialization.'''
        ret = {
            BM_INITIALIZED: self._initialized,
            BM_BF: self._budget_folder,
            BM_FI: self._institutions,
            BM_OPTIONS: self._options,
            "budget_model_store_uri": self._budget_model_store_uri,
            "created_date": self._created_date,
            "last_modified_date": self._last_modified_date,
            "modified_by": self._modified_by,
        }
        return ret
    def __repr__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"BudgetModlel({str(self._budget_folder)}) "
        ret += "'initialized' " if self._initialized else "'not initialized' "
        ret += f"Fin.Insts=[{', '.join([repr(fi_key) for fi_key in self._institutions.keys()])}], "
        ret += f"budget_model_store_uri='{self._budget_model_store_uri}' "
        ret += f"created_date='{self._created_date}', "
        ret += f"last_modified_date='{self._last_modified_date}', "
        ret += f"modified_by='{self._modified_by}', "
        return ret
    def __str__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"BudgetModlel({str(self._budget_folder)}) "
        ret += "'initialized' " if self._initialized else "'not initialized' "
        ret += f"Fin.Insts=[{', '.join([repr(fi_key) for fi_key in self._institutions.keys()])}], "
        ret += f"budget_model_store_uri='{self._budget_model_store_uri}' "
        ret += f"created_date='{self._created_date}', "
        ret += f"last_modified_date='{self._last_modified_date}', "
        ret += f"modified_by='{self._modified_by}', "
        return ret
    #endregion BudgetModel internal class properties
    # ------------------------------------------------------------------------ +
    #region BudgetModel public class properties
    @property
    def initialized(self) -> bool:
        """The initialized value."""
        return self._initialized
    
    @initialized.setter
    def initialized(self, value: bool) -> None:
        """Set the initialized value."""
        self._initialized = value

    @property
    def bm_bf(self) -> str:
        """The budget folder path is a string, e.g., '~/OneDrive/."""
        return self._budget_folder

    #endregion BudgetModel public class properties
    # ------------------------------------------------------------------------ +
    #region BudgetModel public methods
    # ------------------------------------------------------------------------ +
    #region BudgetModel.initialize(self, budget_node : dict = None) public 
    def inititailize(self, 
                 budget_model:dict=None  # create if None, else copy 
                 ) -> dict:
        """Initialize the budget model with the given or fresh default 
        configuration.
        """
        me = self.inititailize
        try:
            if budget_model is None:
                # Create a new budget model from the default configuration
                self.budget_model_data = budget_config.copy()
            else:   
                # Create a new budget model from the provided configuration
                self.budget_model_data = budget_model.copy()
        except Exception as e:
            m = p3u.exc_msg(me, e)
            logger.error(m)
            raise
    #endregion BudgetModel.initialize(self, budget_node : dict = None) public 
    # ------------------------------------------------------------------------ +
    #region budget_model_working_data methods
    # budget_model_working_data is a dictionary to store dynamic, non-property data.
    def set_budget_model_working_data(self, key, value):
        self.budget_model_working_data[key] = value

    def get_budget_model_working_data(self, key):
        return self.budget_model_working_data.get(key, 0)
    #endregion budget_model_data methods
    # ------------------------------------------------------------------------ +
    #endregion BudgetModel public methods
# ---------------------------------------------------------------------------- +
#region get_budget_model() -> dict
def get_budget_model() -> dict:
    """Get the budget model.

    Returns:
        dict: The budget model.
    """
    global budget_model
    return budget_model
#endregion get_budget_model() -> dict
# ---------------------------------------------------------------------------- +
#region set_budget_config(model_value : dict) -> none
def set_budget_model(model_value : dict) -> None:
    """Set the budget model configuration.

    Args:
        model_value (dict): The budget model configuration.
    """
    global budget_model
    try:
        if model_value is None or not isinstance(model_value, dict):
            m = "model_value parameter is not valid."
            logger.error(m)
            raise ValueError(m)
        budget_model = model_value
        logger.debug(f"budget_model was set.")
    except Exception as e:
        logger.error(p3u.exc_msg(set_budget_model, e))
        raise   
#endregion set_budget_config(model_value : dict) -> none
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
    global budget_model
    validate_budget_model()
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
#region load_fi_transactions() function
def load_fi_transactions(trans_file:str=None) -> Workbook:
    """Get the FI transactions from configured sources into a workbook.
    
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
    global budget_model
    validate_budget_model()
    try:
        trans_path = Path.Path(budget_config["bank_transactions_folder"]) / trans_file

        logger.info("Loading FI transactions...")
        wb = load_workbook(filename=trans_path)
        logger.info(f"Loaded FI transactions from {str(trans_path)}")

        return wb
    except Exception as e:
        logger.error(p3u.exc_msg(load_fi_transactions, e))
        raise    
#endregion load_fi_transactions() function
# ---------------------------------------------------------------------------- +
#region fi_if_workbook_keys() function
def fi_if_workbook_keys(inst_key:str=None,bm:dict=None) -> dict:
    """Get the list of workbooks in the incoming folder for the specified institution.

    Args:
        inst_key (str): The key of the institution to get the workbooks for.

    Returns:
        dict: A dictionary of workbooks with the file name as the key.
    """
    try:
        bm = get_budget_model() if bm is None else bm
        validate_budget_model(bm)
        if inst_key is None or inst_key not in bm["institutions"]:
            m = f"Invalid institution key: '{inst_key}'"
            logger.error(m)
            raise ValueError(m)
        institution = bm[BM_FI][inst_key]
        workbooks = institution[FI_IF_WORKBOOKS].keys()
        return workbooks
    except Exception as e:
        logger.exception(p3u.exc_msg(fi_if_workbook_keys, e))
        raise

#endregion fi_if_workbook_keys() function
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
        bm = get_budget_model() if bm is None else bm
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
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"+ Running {THIS_APP_NAME} ...")
        logger.info("+ ----------------------------------------------------- +")
        logger.debug(f"Start: {THIS_APP_NAME}...")

        bm = _BudgetModelTemplate()
        logger.info(f"Budget Model: {str(bm)}")
        _ = "pause"
    except Exception as e:
        m = p3u.exc_msg("__main__", e)
        logger.error(m)
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
