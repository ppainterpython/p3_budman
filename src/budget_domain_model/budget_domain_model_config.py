# ---------------------------------------------------------------------------- +
#region budget_domain_model_config.py module
"""BDM: class BDMConfig: Provides config object functions for the BDM.

    Thi BDMCOnfig class provides a BudgetDomainModel Storage (BDM_STORE) 
    dictionary used to configure a new instance of the BudgetDomainModel (BDM)
    class. A BDM_STORE dictionary is used for BDM data storage by json
    encoding. BDMConfig delivers a BDM_CONFIG dictionary, which is identical in 
    structure to a BDM_STORE dictionary. This is just to highlight the usage
    context being limited to BudgetDomainModel initialization.

    A BDM_CONFIG object is used to configure a new instance
    of a BudgetDomainModel (BDM) object. When a BDM_STORE file is retrieved 
    from storage by its URL, it is a BDM_STORE object. When starting up, 
    the most common function is to load a BDM_STORE file from storage, and use 
    it as the BDM_CONFIG object to initialize the BudgetDomainModel instance. 
    But, the BDMConfig class supports other methods of creating a BDM_CONFIG 
    dictionary used to initialize a BudgetDomainModel instance. The key point 
    is that however the BDM_CONFIG dictionary is created, it becomes the 
    BDM_STORE property value for the BudgetDomainModel instance. 
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
from budget_storage_model import *
from .bdm_workbook_class import BDMWorkbook 
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
class BDMConfig(metaclass=BDMSingletonMeta):
    """Provides a template Budget Domain Model BDM_STORE object.
    
    Creates a BDMConfig dictionary pre-populated with reasonable 
    default configuration values.
    """
    # ------------------------------------------------------------------------ +
    #region BDMConfig dictionary
    # The main difference between the BudgetDomainModel class and the 
    # BDMConfig class is the following 
    # budget_model_config dictionary. The BDMConfig class uses 
    # the same attribute structure and properties, as a dict, as the 
    # BDM class. Our assumption is that json is the storage format where user 
    # data is saved to storage, the BDM_STORE. Keep it simple.

    # class variable for the budget model config dictionary.
    bdm_store_config = {  
        # BDM object
        BDM_ID: "BDM_CONFIG",  # identifies the builtin BDM config object.
        BDM_STORE_OBJECT: None,
        BDM_INITIALIZED: False,
        BDM_FILENAME: "bdm_store",  # the BDM store filename, without extension
        BDM_FILETYPE: ".jsonc",  # the BDM store filetype, default is jsonc
        BDM_FOLDER: "~/OneDrive/budget", 
        BDM_URL: None,
        BDM_FI_COLLECTION: { # FI_COLLECTION Dict[FI_KEY: FI_OBJECT]
            "boa": # FI_KEY
            {      # FI_OBJECT
                FI_KEY: "boa",
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                FI_WORKFLOW_DATA_COLLECTION: 
                { # FI_WORKFLOW_DATA_COLLECTION Dict[WF_KEY: WORKFLOW_DATA_COLLECTION]
                     BDM_WF_CATEGORIZATION:  # WF_KEY: 
                     {  # WORKFLOW_DATA_COLLECTION Dict[WF_PURPOSE: WORKBOOK_DATA_LIST]
                        WF_INPUT: # WF_PURPOSE: WF_INPUT  (input data objects) 
                        [  # WORKBOOK_DATA_LIST: List[WORKBOOK_ITEMS], WORKBOOK_ITEM: Tuple[WB_NAME, WB_URL]
                            ( "input_prefix_wb_name_1", "wb_url_1" ),
                            ( "input_prefix_wb_name_2", "wb_url_2" ),
                            ( "input_prefix_wb_name_3", "wb_url_3" )
                        ], 
                        WF_WORKING: # WF_PURPOSE: WF_WORKING  (working data objects) 
                        [ # WORKBOOK_DATA_LIST: List[WORKBOOK_ITEMS], WORKBOOK_ITEM: Tuple[WB_NAME, WB_URL]
                            ( "wb_name_1", "wb_url_1" ),
                            ( "wb_name_2", "wb_url_2" ),
                            ( "wb_name_3", "wb_url_3" )
                        ], 
                        WF_OUTPUT: # WF_PURPOSE: WF_OUTPUT  (output data objects) 
                        [  # WORKBOOK_DATA_LIST: List[WORKBOOK_ITEMS], WORKBOOK_ITEM: Tuple[WB_NAME, WB_URL]
                            ( "output_prefix_wb_name_1", "wb_url_4" ),
                            ( "output_prefix_wb_name_2", "wb_url_5" ),
                            ( "output_prefix_wb_name_3", "wb_url_6" )
                        ]
                    }
                },
                FI_WORKBOOK_DATA_COLLECTION: 
                    {  # FI_WORKBOOK_DATA_COLLECTION: Dict[WB_INDEX: WORKBOOK_OBJECT]
                        0: {}
                },
            },
            "merrill": # FI_KEY
            {          # FI_DATA
                FI_KEY: "merrill",
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                FI_WORKFLOW_DATA_COLLECTION: None,
            },
        },
        BDM_WF_COLLECTION: {
            BDM_WF_INTAKE: { 
                # WF Object - TODO: add WF_KEY, verify unique
                WF_KEY: BDM_WF_INTAKE,
                WF_NAME: BDM_WF_INTAKE,
                WF_INPUT_FOLDER: None,
                WF_WORKING_FOLDER: "data/new",
                WF_OUTPUT_FOLDER: "data/categorized",
                WF_PURPOSE_FOLDER_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                },
                WF_PREFIX_IN: None,
                WF_PREFIX_WORKING: None,
                WF_PREFIX_OUT: "categorized_"
            },
            BDM_WF_CATEGORIZATION: {     
                # WF Object
                WF_KEY: BDM_WF_CATEGORIZATION,
                WF_NAME: BDM_WF_CATEGORIZATION,
                WF_INPUT_FOLDER: "data/new", 
                WF_WORKING_FOLDER: "data/categorized",
                WF_OUTPUT_FOLDER: "data/finalized",
                WF_PURPOSE_FOLDER_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                },
                WF_PREFIX_IN: None,
                WF_PREFIX_WORKING: "categorized_",
                WF_PREFIX_OUT: "finalized_"
            },
            BDM_WF_FINALIZATION: {   
                # WF Object
                WF_KEY: BDM_WF_FINALIZATION,
                WF_NAME: BDM_WF_FINALIZATION,
                WF_INPUT_FOLDER: "data/categorized",   
                WF_WORKING_FOLDER: "data/finalized",
                WF_OUTPUT_FOLDER: "data/finalized",
                WF_PURPOSE_FOLDER_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                },
                WF_PREFIX_IN: "categorized_",
                WF_PREFIX_WORKING: "final_prep_",
                WF_PREFIX_OUT: "finalized_"
            }
        },
        BDM_OPTIONS: {
            BDMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BDMO_LOG_LEVEL: "DEBUG",
            BDMO_LOG_FILE: "logs/p3BudgetModel.log",
            BDMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        },
        BDM_CREATED_DATE: None,
        BDM_LAST_MODIFIED_DATE: None,
        BDM_LAST_MODIFIED_BY: None,
        BDM_WORKING_DATA: {},
        BDM_DATA_CONTEXT: {
            DC_FI_KEY: "boa",  # Financial Institution Key
            DC_WF_KEY: BDM_WF_CATEGORIZATION,  # Workflow Key
            DC_WF_PURPOSE: WF_WORKING,
            DC_WB_TYPE: WF_WORKING,
            DC_CHECK_REGISTERS: None    # Workbook Type
        }
    }
    bdm_store_default_values = {
        BDM_ID: bdm_store_config[BDM_ID],
        BDM_STORE_OBJECT: bdm_store_config[BDM_STORE_OBJECT],
        BDM_INITIALIZED: bdm_store_config[BDM_INITIALIZED],
        BDM_FILENAME: bdm_store_config[BDM_FILENAME],
        BDM_FILETYPE: bdm_store_config[BDM_FILETYPE],
        BDM_FOLDER: bdm_store_config[BDM_FOLDER],
        BDM_URL: bdm_store_config[BDM_URL], 
        BDM_FI_COLLECTION: {},
        BDM_WF_COLLECTION: {},
        BDM_OPTIONS: copy.deepcopy(bdm_store_config[BDM_OPTIONS]),
        BDM_CREATED_DATE: bdm_store_config[BDM_CREATED_DATE],
        BDM_LAST_MODIFIED_DATE: bdm_store_config[BDM_LAST_MODIFIED_DATE],
        BDM_LAST_MODIFIED_BY: bdm_store_config[BDM_LAST_MODIFIED_BY],
        BDM_WORKING_DATA: {},
        BDM_DATA_CONTEXT: bdm_store_config[BDM_DATA_CONTEXT]
    }
    #endregion BDMConfig dictionary
    # ------------------------------------------------------------------------ +
    #region BDM_CONFIG_default() classmethod
    @classmethod
    def BDM_CONFIG_default(cls, default : bool = False) -> BDM_CONFIG:
        """Get a pristine version of a BDM_CONFIG dictionary."""
        try:
            logger.debug("Start:  ...")
            bmt = copy.deepcopy(cls.bdm_store_config)
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
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_CONFIG_default() classmethod
    # ------------------------------------------------------------------------ +
    #region BDM_CONFIG_validate_attributes() created BDMConfig from a loaded BDM_STORE url.
    @classmethod
    def BDM_CONFIG_validate_attributes(cls, bdm_config : dict) -> None:
        """Verify a BDM_CONFIG/BDM_STORE dict has all required attributes.

            Make sure the supplied dictionary has all the required
            attributes and values. If not, update it with default values.
            Does not change valued in bdm_config, just adds missing ones.
        """
        try:
            logger.debug("Start:  ...")
            bdm_config.update({k: v for k, v in BDMConfig.bdm_store_default_values.items() if k not in bdm_config})
            logger.debug(f"Complete:")   
            return bdm_config
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_CONFIG_validate_attributes() created BDMConfig from a loaded BDM_STORE url.
    # ------------------------------------------------------------------------ +
    #region BDM_STORE_rehydrate() replace selected json with objects.
    @classmethod
    def BDM_STORE_rehydrate(cls, bdm_store : dict) -> None:
        """Populate a BDM_CONFIG with objects."""
        try:
            logger.debug("Start:  ...")
            if not isinstance(bdm_store, dict):
                raise ValueError(f"bdm_store must be a dictionary: {bdm_store}")
            if len(bdm_store) == 0:
                return None
            # Populate the BDM_CONFIG with objects.
            # Populate the FI_OBJECT.
            if (BDM_FI_COLLECTION in bdm_store and
                bdm_store[BDM_FI_COLLECTION] is not None and
                isinstance(bdm_store[BDM_FI_COLLECTION], dict) and 
                len(bdm_store[BDM_FI_COLLECTION]) > 0):
                for fi_key, fi_object in bdm_store[BDM_FI_COLLECTION].items():
                    if not isinstance(fi_object, dict):
                        continue
                    if (FI_WORKBOOK_DATA_COLLECTION not in fi_object or
                        fi_object[FI_WORKBOOK_DATA_COLLECTION] is None or
                        not isinstance(fi_object[FI_WORKBOOK_DATA_COLLECTION], dict) or
                        len(fi_object[FI_WORKBOOK_DATA_COLLECTION]) == 0):
                        continue
                    for wb_index, wb_data in fi_object[FI_WORKBOOK_DATA_COLLECTION].items():
                        if not isinstance(wb_data, dict):
                            continue
                        # Convert the WORKBOOK_ITEM to a WORKBOOK_OBJECT.
                        wb_object = BDMWorkbook(**wb_data)
                        # Replace the DATA_OBJECT with the WORKBOOK_OBJECT.
                        # Use int for wb_index
                        fi_object[FI_WORKBOOK_DATA_COLLECTION][wb_index] = wb_object
            logger.debug(f"Complete:")   
            return None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_STORE_rehydrate() created BDMConfig from a loaded BDM_STORE url.
    # ------------------------------------------------------------------------ +
    #region BDM_STORE_url_load() create BDM_CONFIG from a loaded BDM_STORE url.
    @classmethod
    def BDM_STORE_url_load(cls, bdm_url : str) -> BDM_CONFIG:
        """Configure this BDMConfig object from loading a BDM_STORE url."""
        try:
            logger.debug("Start:  ...")
            bdm_store = bsm_BDM_STORE_url_load(bdm_url)
            # Ensure the URL used to load is set in the config
            bdm_store[BDM_URL] = bdm_url  
            # Validate the loaded BDM_STORE config. Raises error if not happy
            cls.BDM_CONFIG_validate_attributes(bdm_store)
            # Rehydrate any python class objects from json
            cls.BDM_STORE_rehydrate(bdm_store)
            # Get the instance of BDMConfig configured from bdms
            bdm_config = BDMConfig(bdm_config = bdm_store)            
            logger.debug(f"Complete:")   
            return bdm_config
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_STORE_url_load() created BDM_CONFIG from a loaded BDM_STORE url.
    # ------------------------------------------------------------------------ +
    #region BDMConfig class constructor __init__()
    def __init__(self, bdm_config : Dict) -> None:
        """Construct a BDMConfig object used for configuration.
        
        The BDMConfig class provides a BDM_CONFIG object useful to initialize
        new BudgetDomainModel instances.
        It is for internal use only. There are two means to apply it when
        constructing a new BudgetDomainModel object: 1. Load a BDM_STORE file 
        from storage, or 2. Marshall up a pristine BDM_CONFIG object with
        initial default values.
        
        BDMConfig has a property BDM_CONFIG which has the dictionary used for 
        initialization. BudgetDomainModel has a property BDM_STORE which is the
        dictionary used to initialize it at construction time.

        No outside config or settings are used to keep this stand-alone and
        uncoupled from other layers of an application using BDM.
        """
        st = p3u.start_timer()
        try:
           # Basic attribute atomic value inits. 
            logger.debug("Start:  ...")
            # Initialize values from the config as configuration values.
            setattr(self, BDM_ID, bdm_config.get(BDM_ID, 'Unknown'))
            setattr(self, BDM_CONFIG_OBJECT, bdm_config)
            setattr(self, BDM_INITIALIZED, bdm_config.get(BDM_INITIALIZED,False))
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
            # Complete the BDMConfig instance initialization.
            self.bdm_initialized = True
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDMConfig class constructor __init__()
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
    def bdm_config_object(self) -> BDM_CONFIG:
        """The budget model configuration object."""
        return getattr(self, BDM_CONFIG_OBJECT)
    @bdm_config_object.setter
    def bdm_config_object(self, value: BDM_CONFIG) -> None:
        """Set the budget model configuration object."""
        if not isinstance(value, dict):
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
    def bdm_options(self) -> BDMO_OBJECT:
        """The budget model options dictionary."""
        return self._options
    @bdm_options.setter
    def bdm_options(self, value: BDMO_OBJECT) -> None:
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
    def bdm_working_data(self) -> BDM_WORKING_DATA_OBJECT:
        """The budget domain model working data."""
        self._wd = {} if self._wd is None else self._wd
        return self._wd
    @bdm_working_data.setter
    def bdm_working_data(self, value: BDM_WORKING_DATA_OBJECT) -> None:
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
    def log_BDM_CONFIG_info(bmt : "BDMConfig") -> None:
        """Log the BDMConfig class information."""
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
                logger.debug(f"{P6}WF_INPUT_FOLDER: '{bmt.wf_object[WF_INPUT_FOLDER]}'")
                logger.debug(f"{P6}WF_WORKING_FOLDER: '{bmt.wf_object[WF_WORKING_FOLDER]}'")
                logger.debug(f"{P6}WF_OUTPUT_FOLDER: '{bmt.wf_object[WF_OUTPUT_FOLDER]}'")
                logger.debug(f"{P6}WF_PREFIX_IN: '{bmt.wf_object[WF_PREFIX_IN]}' "
                            f"WF_PREFIX_OUT: '{bmt.wf_object[WF_PREFIX_OUT]}'")
                logger.debug(f"{P6}WB_TYPE_FOLDER_MAP: {str(bmt.wf_object[WF_PURPOSE_FOLDER_MAP])}")
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
