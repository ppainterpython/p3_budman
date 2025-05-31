# ---------------------------------------------------------------------------- +
#region budget_domain_model_config.py module
"""BDM: class BDMConfig: Provides config object functions for the BDM.

    This module provides a BudgetDomainModel (BDM) dictionary with the identical 
    structure used for storing a BDM_STORE object with the 
    BDM Storage Model (BSM), where user data is persisted.

    When a new BDM_STORE object is created, it must be configured. This class,
    BDMConfig serves purpose. 

    BDMConfig can create a new BDM_STORE object with a default configuration.
    Or, it can load an existing BDM_STORE object to provide as config to 
    initialize the working BudgetDomainModel instance.
"""
#endregion budget_domain_model_config.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, uuid, os, getpass, copy
from pathlib import Path
from typing import List, Dict, Any
# third-party modules and packages
from openpyxl import Workbook, load_workbook
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
from budman_namespace import *
from budman_storage_model import *
# from budman_domain_model import BudgetDomainModel 
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
DEFAULT_BDM_FILENAME = "bdm_store"
DEFAULT_BDM_FILETYPE = ".jsonc"
DEFAULT_BDM_FULL_FILENAME = DEFAULT_BDM_FILENAME + DEFAULT_BDM_FILETYPE
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Model config and config support 
# ---------------------------------------------------------------------------- +
class BDMConfig():
    """Provides a template Budget Domain Model BDM_STORE object.
    
    Creates a BDMConfig dictionary pre-populated with reasonable 
    default configuration values.
    """
    # ------------------------------------------------------------------------ +
    #region BDMConfig dictionary
    # The main difference between the BudgetDomainModel class and the 
    # BudgetDomainModelConfig class is the following 
    # budget_model_config dictionary. The BudgetDomainModelConfig class uses 
    # the same attribute structure and properties, as a dict, as the 
    # BDM class. Our assumption is that json is the storage format where user 
    # data is saved to storage, the BDM_STORE. Keep it simple.

    # class variable for the budget model config dictionary.
    budget_model_config = {  
        # BDM object
        BDM_ID: "BDM_CONFIG",  # identifies the builtin BDM config object.
        BDM_CONFIG_OBJECT: None,
        BDM_INITIALIZED: False,
        BDM_FILENAME: "bdm_store",  # the BDM store filename, without extension
        BDM_FILETYPE: ".jsonc",  # the BDM store filetype, default is jsonc
        BDM_FOLDER: "~/OneDrive/budget", 
        BDM_URL: None,
        BDM_FI_COLLECTION: { # FI_COLLECTION (dict) {FI_KEY: FI_DATA}
            "boa": # FI_KEY
            {      # FI_DATA
                FI_KEY: "boa",
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                FI_DATA_COLLECTION: { # WF_DATA_COLLECTION (dict) {wf_key: WF_WORKBOOK_DATA}
                     BDM_WF_CATEGORIZATION: {  # WF_WOBKBOOK_DATA dict {key: [(),() ...]} 
                        WF_INPUT: [ # input data objects
                            ( "input_prefix_wb_name_1", "wb_abs_path_1" ),
                            ( "input_prefix_wb_name_2", "wb_abs_path_2" ),
                            ( "input_prefix_wb_name_3", "wb_abs_path_3" )
                        ], 
                        WF_WORKING: [ # working data objects, input and output
                            ( "wb_name_1", "wb_abs_path_1" ),
                            ( "wb_name_2", "wb_abs_path_2" ),
                            ( "wb_name_3", "wb_abs_path_3" )
                        ], 
                        WF_OUTPUT: [
                            ( "output_prefix_wb_name_1", "wb_abs_path_4" ),
                            ( "output_prefix_wb_name_2", "wb_abs_path_5" ),
                            ( "output_prefix_wb_name_3", "wb_abs_path_6" )
                        ]
                        }
                    },
                },
            "merrill": # FI_KEY
            {          # FI_DATA
                FI_KEY: "merrill",
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                FI_DATA_COLLECTION: None,
            },
        },
        BDM_WF_COLLECTION: {
            BDM_WF_INTAKE: {                    # bdm_fi_wf(fi_key, workflow)
                # WF Object - TODO: add WF_KEY, verify unique
                WF_KEY: BDM_WF_INTAKE,
                WF_NAME: BDM_WF_INTAKE,
                WF_INPUT_FOLDER: None,         # bsm_WF_INPUT(fi_key, workflow)
                WF_PREFIX_IN: None,
                WF_WORKING_FOLDER: "data/new",
                WF_OUTPUT_FOLDER: "data/new",
                WF_PREFIX_OUT: None,
                WF_TYPE_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                }
            },
            BDM_WF_CATEGORIZATION: {            # bdm_fi_wf(fi_key, workflow)
                # WF Object
                WF_KEY: BDM_WF_CATEGORIZATION,
                WF_NAME: BDM_WF_CATEGORIZATION,
                WF_INPUT_FOLDER: "data/new", # bsm_WF_INPUT(fi_key, workflow)
                WF_WORKING_FOLDER: "data/categorized",
                WF_OUTPUT_FOLDER: "data/categorized",
                WF_PREFIX_IN: None,
                WF_PREFIX_OUT: "categorized_",
                WF_TYPE_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                }
            },
            BDM_WF_FINALIZATION: {              # bdm_fi_wf(fi_key, workflow)
                # WF Object
                WF_KEY: BDM_WF_FINALIZATION,
                WF_NAME: BDM_WF_FINALIZATION,
                WF_INPUT_FOLDER: "data/categorized",   # bsm_WF_INPUT(fi_key, workflow)
                WF_WORKING_FOLDER: "data/finalized",
                WF_OUTPUT_FOLDER: "data/finalized",
                WF_PREFIX_IN: "categorized_",
                WF_PREFIX_OUT: "finalized_",
                WF_TYPE_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                }
            }
        },
        BDM_OPTIONS: {
            BMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BMO_LOG_LEVEL: "DEBUG",
            BMO_LOG_FILE: "logs/p3BudgetModel.log",
            BMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        },
        BDM_CREATED_DATE: None,
        BDM_LAST_MODIFIED_DATE: None,
        BDM_LAST_MODIFIED_BY: None,
        BDM_WORKING_DATA: {}
    }
    #endregion BDMConfig dictionary
    # ------------------------------------------------------------------------ +
    #region get_budget_model_config() classmethod
    @classmethod
    def get_budget_model_config(cls,default : bool = False) -> dict:
        """Get a copy of the budget domain model config dictionary."""
        try:
            logger.debug("Start:  ...")
            bmt = copy.deepcopy(cls.budget_model_config)
            if not default:
                # Freshen up some of the values for a new BDM config.
                bmt[BDM_ID] = uuid.uuid4().hex[:8]
                bmt[BDM_CREATED_DATE] = p3u.now_iso_date_string()
                bmt[BDM_LAST_MODIFIED_DATE] = p3u.now_iso_date_string()
                bmt[BDM_LAST_MODIFIED_BY] = getpass.getuser()
                path_args = (bmt[BDM_FILENAME], bmt[BDM_FILETYPE], bmt[BDM_FOLDER])
                bmt[BDM_URL] = bsm_BDM_STORE_file_abs_path(*path_args).as_uri()
            logger.debug(f"Complete:")   
            return bmt
        except Exception as e:
            m = p3u.exc_msg(cls.get_budget_model_config, e)
            logger.error(m)
            raise
    #endregion get_budget_model_config() classmethod
    # ------------------------------------------------------------------------ +
    #region BUDMAN_STORE_load() created BDMConfig from a loaded BDM_STORE url.
    @classmethod
    def BUDMAN_STORE_url_load(cls, bdms_url : str) -> dict:
        """Configure this BDMConfig object from loading BDM_STORE url."""
        try:
            logger.debug("Start:  ...")
            bdms = bsm_BDM_STORE_url_load(bdms_url)
            # Get the instance of BDMConfig configured from bdms
            bdm_config = BDMConfig(bdm_config = bdms)            
            logger.debug(f"Complete:")   
            return bdm_config
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BUDMAN_STORE_load() created BDMConfig from a loaded BDM_STORE url.
    # ------------------------------------------------------------------------ +
    #region BudgetDomainModelConfig class constructor __init__()
    def __init__(self, bdm_config : Dict) -> None:
        """Construct a BudgetDomainModelConfig object used for configuration.
        
        The BudgetDomainModelConfig class can be used to populate new 
        BudgetDomain Model objects with default and example values.
        It is for internal use only. There are two means to apply it when
        constructing a new BudgetDomainModel object:
        1. Instantiate the BudgetDomainModelConfig, which sets the 
           BudgetDomainModel._default_config_object class variable which 
           should be used when no config_object parameter is used with 
           BudgetDomainModel().
        2. Use the BudgetDomainModelConfig.budget_model_config class variable
           as the config_object parameter when instantiating BudgetDomainModel: 
           BudgetDomainModel(config_object = BudgetDomainModelConfig.budget_model_config)
        
        No outside config or settings are used to keep this stand-alone and
        uncoupled from other layers of an application using BDM.
        """
        st = p3u.start_timer()
        try:
           # Basic attribute atomic value inits. 
            logger.debug("Start:  ...")
            # Initialize values from the config as configuration values.
            # TODO: need a validate_config() method to validate the config. makes
            # sure the config has all required keys with valid values.
            setattr(self, BDM_ID, bdm_config.get(BDM_ID, 'Unknown'))
            setattr(self, BDM_CONFIG_OBJECT, bdm_config)
            setattr(self, BDM_INITIALIZED, bdm_config.get(BDM_ID,False))
            setattr(self, BDM_FILENAME, bdm_config.get(BDM_FILENAME, DEFAULT_BDM_FILENAME))
            setattr(self, BDM_FILETYPE, bdm_config.get(BDM_FILETYPE,DEFAULT_BDM_FILETYPE))
            setattr(self, BDM_FOLDER, bdm_config.get(BDM_FOLDER, "~/OneDrive/budget"))  
            setattr(self, BDM_URL, bdm_config.get(BDM_URL, None))  
            setattr(self, BDM_FI_COLLECTION, copy.deepcopy(bdm_config[BDM_FI_COLLECTION]))
            setattr(self, BDM_WF_COLLECTION, copy.deepcopy(bdm_config[BDM_WF_COLLECTION])) 
            setattr(self, BDM_OPTIONS, copy.deepcopy(bdm_config[BDM_OPTIONS]))
            setattr(self, BDM_CREATED_DATE, bdm_config[BDM_CREATED_DATE]) 
            setattr(self, BDM_LAST_MODIFIED_DATE, bdm_config[BDM_LAST_MODIFIED_DATE])
            setattr(self, BDM_LAST_MODIFIED_BY, bdm_config[BDM_LAST_MODIFIED_BY])
            setattr(self, BDM_WORKING_DATA, {})  
            # Complete the BudgetDomainModelConfig instance initialization.
            self.bdm_initialized = True
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BudgetDomainModelConfig class constructor __init__()
    # ------------------------------------------------------------------------ +
    #region    BudgetDomainModel (BDM) properties
    @property
    def bdm_id(self) -> str:
        """The budget model ID."""
        return getattr(self, BDM_ID)
    @bdm_id.setter
    def bdm_id(self, value: str) -> None:
        """Set the budget model ID."""
        if not isinstance(value, str):
            raise ValueError(f"bm_id must be a string: {value}")
        setattr(self, BDM_ID, value)

    @property
    def bdm_config_object(self) -> object:
        """The budget model configuration object."""
        return getattr(self, BDM_CONFIG_OBJECT)
    @bdm_config_object.setter
    def bdm_config_object(self, value: object) -> None:
        """Set the budget model configuration object."""
        if not isinstance(value, object):
            raise ValueError(f"bm_config_object must be an object: {value}")
        setattr(self, BDM_CONFIG_OBJECT, value)

    @property
    def bdm_initialized(self) -> bool:
        """The initialized value."""
        return self._initialized
    @bdm_initialized.setter
    def bdm_initialized(self, value )-> None:
        """Set the initialized value."""
        self._initialized = value

    @property
    def bdm_filename(self) -> str:
        """The bdm_store filename is a string, e.g., 'bdm_store"""
        return self._bdm_filename
    @bdm_filename.setter
    def bdm_filename(self, value: str) -> None:
        """Set the bdm_store filename."""
        self._bdm_filename = value

    @property
    def bdm_filetype(self) -> str:
        """The bdm_store filetype, e.g., '.jsonc"""
        return self._bdm_filetype
    @bdm_filetype.setter
    def bdm_filetype(self, value: str) -> None:
        """Set the bdm_store filetype."""
        self._bdm_filetype = value

    @property
    def bdm_folder(self) -> str:
        """The budget folder path is a string, e.g., '~/OneDrive/."""
        return self._budget_folder
    @bdm_folder.setter
    def bdm_folder(self, value: str) -> None:
        """Set the budget folder path."""
        self._budget_folder = value

    @property
    def bdm_url(self) -> str:
        """The budget manager store file url."""
        return self._bdm_url
    @bdm_url.setter
    def bdm_url(self, value: str) -> None:
        """Set the budget manager store file url."""
        self._bdm_url = value

    @property
    def bdm_fi_collection(self) -> dict:
        """The financial institutions collection."""
        return self._financial_institutions
    @bdm_fi_collection.setter
    def bdm_fi_collection(self, value: dict) -> None:
        """Set the financial institutions collection."""
        self._financial_institutions = value

    @property
    def bdm_wf_collection(self) -> dict:
        """The workflow collection."""
        return self._workflows
    @bdm_wf_collection.setter
    def bdm_wf_collection(self, value: dict) -> None:
        """Set the workflows collection."""
        self._workflows = value

    @property
    def bdm_options(self) -> dict:
        """The budget model options dictionary."""
        return self._options
    @bdm_options.setter
    def bdm_options(self, value: dict) -> None:
        """Set the budget model options dictionary."""
        self._options = value

    @property
    def bdm_created_date(self) -> str:
        """The created date."""
        return self._created_date
    @bdm_created_date.setter
    def bdm_created_date(self, value: str) -> None:  
        """Set the created date."""
        self._created_date = value

    @property
    def bdm_last_modified_date(self) -> str:
        """The last modified date."""
        return self._last_modified_date
    @bdm_last_modified_date.setter
    def bdm_last_modified_date(self, value: str) -> None:
        """Set the last modified date."""
        self._last_modified_date = value

    @property
    def bdm_last_modified_by(self) -> str:
        """The last modified by."""
        return self._last_modified_by
    @bdm_last_modified_by.setter
    def bdm_last_modified_by(self, value: str) -> None:
        """Set the last modified by."""
        self._last_modified_by = value
    
    @property
    def bdm_working_data(self) -> dict:
        """The budget domain model working data."""
        self._wd = {} if self._wd is None else self._wd
        return self._wd
    @bdm_working_data.setter
    def bdm_working_data(self, value: dict) -> None:
        """Set the budget domain model working data."""
        self._wd = {} if self._wd is None else self._wd
        self._wd = value

    @property
    def data_context(self) -> DATA_CONTEXT:
        """The data context for the budget model."""
        return self.bdm_working_data 
    @data_context.setter
    def data_context(self, value: DATA_CONTEXT) -> None:
        """Set the data context for the budget model."""
        self.bdm_working_data = value

    # budget_model_working_data is a dictionary to store dynamic, non-property data.
    def set_BDM_WORKING_DATA(self, key, value) -> None:
        self.bdm_working_data[key] = value

    def get_BDM_WORKING_DATA(self, key) -> Any:
        return self.bdm_working_data.get(key, 0)

    #endregion BudgetDomainModel (BDM) compatible properties
    # ------------------------------------------------------------------------ +
    #region log_BMT_info()
    @staticmethod
    def log_BMT_info(bmt : "BDMConfig") -> None:
        """Log the BudgetDomainModelConfig class information."""
        try:
            logger.debug("Start:  ...")
            logger.debug(f"{P2}BDM_INITIALIZED('{BDM_INITIALIZED}'): "
                         f"{bmt.bdm_initialized}")
            logger.debug(f"{P2}BDM_FOLDER('{BDM_FOLDER}'): '{bmt.bdm_url}'")
            logger.debug(f"{P2}BDM_URL('{BDM_URL}): '{bmt.bdm_url}' ")
            logger.debug(f"{P2}BDM_WORKFLOWS('{BDM_WF_COLLECTION}'): "
                         f" '{bmt.bdm_wf_collection}'")
            # Enumerate Financial Institutions (FI)
            fi_c = len(bmt.bdm_fi_collection)  # financial institutions count
            logger.debug(f"{P2}BDM_FI('{BDM_FI_COLLECTION}')({fi_c})")
            for fi_key, fi_object in bmt.bdm_fi_collection.items():
                logger.debug(f"{P4}Financial Institution: "
                         f"{fi_key}:{fi_object[FI_NAME]}:"
                         f"{fi_object[FI_TYPE]}: '{fi_object[FI_FOLDER]}'")
            # Enumerate Workflows in the budget model
            c = len(bmt.bdm_wf_collection)
            logger.debug(
                f"{P2}BDM_WF_COLLECTION['{BDM_WF_COLLECTION}']({c}): "
                f"{str(list(bmt.bdm_wf_collection.keys()))}")
            for wf_key, wf_object in bmt.bdm_wf_collection.items():
                logger.debug(f"{P4}Workflow:({wf_key}:{wf_object[WF_NAME]}: ")
                logger.debug(f"{P6}WF_INPUT: '{bmt.wf_object[WF_INPUT_FOLDER]}'")
                logger.debug(f"{P6}WF_OUTPUT_FOLDER: '{bmt.wf_object[WF_OUTPUT_FOLDER]}'")
                logger.debug(f"{P6}WF_PREFIX_IN: '{bmt.wf_object[WF_PREFIX_IN]}' "
                            f"WF_PREFIX_OUT: '{bmt.wf_object[WF_PREFIX_OUT]}'")
                logger.debug(f"{P6}WF_TYPE_MAP: {str(bmt.wf_object[WF_TYPE_MAP])}")
            # Enumerate Budget Model Options
            bmo_c = len(bmt.bdm_options)
            logger.debug(f"{P2}BDM_OPTION('{BDM_OPTIONS}')({bmo_c})")
            for opt_key, opt in bmt.bdm_options.items():
                logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

            # "And the rest. Here on Gilligan's Isle..."
            logger.debug(f"{P2}BDM_CREATED_DATE({BDM_CREATED_DATE}'): "
                         f"{bmt.bdm_created_date}")
            logger.debug(f"{P2}BDM_LAST_MODIFIED_DATE({BDM_LAST_MODIFIED_DATE}'): "
                            f"{bmt.bdm_last_modified_date}")
            logger.debug(f"{P2}BDM_LAST_MODIFIED_BY({BDM_LAST_MODIFIED_BY}'): "
                            f"{bmt.bdm_last_modified_by}")
            logger.debug(f"{P2}BDM_WORKING_DATA({BDM_WORKING_DATA}'): "
                            f"{bmt.bdm_working_data}")
            logger.debug(f"Complete:")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    #endregion log_BMT_info()
    # ------------------------------------------------------------------------ +
# ---------------------------------------------------------------------------- +
#region tryout_budget_domain_model_config() function
def tryout_budget_domain_model_config() -> None: 
    """Test the BudgetDomainModelConfig class."""
    st = p3u.start_timer()
    try:
        logger.debug("Start: ...")
        bmt = BDMConfig()
        bmt.bsm_initialize() # initialize the budget storage model 
        
        # Enumerate the financial institutions in the budget model config
        for fi_key, fi_dict in bmt.bdm_fi_collection.items():
            logger.debug(f"Financial Institution: {fi_dict[FI_FOLDER]}:"
                         f"{fi_dict[FI_TYPE]}:{fi_dict[FI_NAME]}:")
        for wf_key, wf_dict in bmt.bdm_wf_collection.items():
            logger.debug(f"{P2}Workflow('{wf_dict[WF_NAME]}'): "
                            f"{P2}WM_FOLDER_IN: '{wf_dict[WF_INPUT_FOLDER]}' "
                            f"{P2}WM_WORKBOOKS_IN: {wf_dict[WF_INPUT]}")
        # logger.debug(f"Budget Model config:     str: '{str(bmt)}'")
        # logger.debug(f"Budget Model config:    repr: '{repr(bmt)}'")
        # logger.debug(f"Budget Model config: to_dict: '{bmt.to_dict()}'")
        logger.debug(f"Complete: {p3u.stop_timer(st)}")   
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion tryout_budget_domain_model_config() function
# ---------------------------------------------------------------------------- +
