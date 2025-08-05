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
from budman_namespace.bdm_singleton_meta import BDMSingletonMeta
from budman_namespace.design_language_namespace import *
from budget_storage_model import *
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
class BDMConfig(metaclass=BDMSingletonMeta):
    """Provides a BDMConfig either from BDM_STORE file or template.
    
    Creates a BDMConfig object pre-populated with values from BDM_STORE file
    or a template using reasonable default values.
    """
    # ------------------------------------------------------------------------ +
    #region BDMConfig template dictionary

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
        BDM_FI_COLLECTION: { # EXAMPLE FI_COLLECTION Dict[FI_KEY: FI_OBJECT]
            "boa": # FI_KEY
            {      # FI_OBJECT
                FI_KEY: "boa",
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                FI_WF_FOLDER_CONFIG_COLLECTION: { 
                    "intake": 
                    [ # WF_FOLDER_CONFIG_LIST_TYPE
                        { # WF_FOLDER_CONFIG_TYPE Object
                            WF_FOLDER: "raw_data", 
                            WF_PURPOSE: "wf_input",
                            WF_PREFIX: None,
                            WF_FOLDER_URL: None
                        },
                        { # WF_FOLDER_CONFIG_TYPE Object
                            WF_FOLDER: "new", 
                            WF_PURPOSE: "wf_working",
                            WF_PREFIX: None,
                            WF_FOLDER_URL: None
                        }
                    ],
                    "categorize_transactions": 
                    [ # WF_FOLDER_CONFIG_LIST_TYPE
                        { # WF_FOLDER_CONFIG_TYPE Object
                            WF_FOLDER: "categorized", 
                            WF_PURPOSE: "wf_working",
                            WF_PREFIX: "categorized_",
                            WF_FOLDER_URL: None
                        }
                    ]
                },
                FI_WORKBOOK_DATA_COLLECTION: 
                    {  # FI_WORKBOOK_DATA_COLLECTION: Dict[WB_ID: WORKBOOK_OBJECT]
                        "some_wb_id": {}
                },
            },
            "merrill": # FI_KEY
            {          # FI_DATA
                FI_KEY: "merrill",
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                FI_WF_FOLDER_CONFIG_COLLECTION: { 
                    "intake": 
                    [ # WF_FOLDER_CONFIG_LIST_TYPE
                        { # WF_FOLDER_CONFIG_TYPE Object
                            WF_FOLDER: "raw_data", 
                            WF_PURPOSE: "wf_input",
                            WF_PREFIX: None,
                            WF_FOLDER_URL: None
                        },
                        { # WF_FOLDER_CONFIG_TYPE Object
                            WF_FOLDER: "new", 
                            WF_PURPOSE: "wf_working",
                            WF_PREFIX: None,
                            WF_FOLDER_URL: None
                        }
                    ],
                    "categorize_transactions": 
                    [ # WF_FOLDER_CONFIG_LIST_TYPE
                        { # WF_FOLDER_CONFIG_TYPE Object
                            WF_FOLDER: "categorized", 
                            WF_PURPOSE: "wf_working",
                            WF_PREFIX: "categorized_",
                            WF_FOLDER_URL: None
                        }
                    ]
                },
                FI_WORKBOOK_DATA_COLLECTION: 
                    {  # FI_WORKBOOK_DATA_COLLECTION: Dict[WB_ID: WORKBOOK_OBJECT]
                        "some_wb_id": {}
                },
            },
        },
        # Example workflow collection
        BDM_WF_COLLECTION: {
            EXAMPLE_BDM_WF_INTAKE: { # WF Object 
                WF_KEY: EXAMPLE_BDM_WF_INTAKE,
                WF_NAME: EXAMPLE_BDM_WF_INTAKE,
                WF_FOLDER_CONFIG_LIST: [ # WF_FOLDER_CONFIG_LIST_TYPE
                    { # WF_FOLDER_CONFIG_TYPE Object
                        WF_FOLDER: "raw_data", WF_PURPOSE: "wf_input", 
                        WF_PREFIX: None, WF_FOLDER_URL: None
                    },
                    { # WF_FOLDER_CONFIG_TYPE Object
                        WF_FOLDER: "new", WF_PURPOSE: "wf_working", 
                        WF_PREFIX: None, WF_FOLDER_URL: None
                    }
                ]
            },
            EXAMPLE_BDM_WF_CATEGORIZATION: { # WF Object
                WF_KEY: EXAMPLE_BDM_WF_CATEGORIZATION,
                WF_NAME: EXAMPLE_BDM_WF_CATEGORIZATION,
                WF_FOLDER_CONFIG_LIST: [ # WF_FOLDER_CONFIG_LIST_TYPE
                    { # WF_FOLDER_CONFIG_TYPE Object
                        WF_FOLDER: "categorized", WF_PURPOSE: "wf_working", 
                        WF_PREFIX: "categorized_", WF_FOLDER_URL: None
                    }
                ]
            },
            EXAMPLE_BDM_WF_BUDGET: { # WF Object
                WF_KEY: EXAMPLE_BDM_WF_BUDGET,
                WF_NAME: EXAMPLE_BDM_WF_BUDGET,
                WF_FOLDER_CONFIG_LIST: [ # WF_FOLDER_CONFIG_LIST_TYPE
                    { # WF_FOLDER_CONFIG_TYPE Object
                        WF_FOLDER: "budget", WF_PURPOSE: "wf_working", 
                        WF_PREFIX: "budget_", WF_FOLDER_URL: None
                    }
                ]
            }
        },
    # "_workflows": {
    #     "intake": {
    #         "wf_key": "intake",
    #         "wf_name": "intake",
    #         "wf_folders": [
    #             {"wf_folder": "raw_data", "wf_purpose": "wf_input", "wf_prefix": null},
    #             {"wf_folder": "new", "wf_purpose": "wf_working", "wf_prefix": null}
    #         ],
    #     },
    #     "categorize_transactions": {
    #         "wf_key": "categorize_transactions",
    #         "wf_name": "categorize_transactions",
    #         "wf_folders": [
    #             {"wf_folder": "categorized", "wf_purpose": "wf_working", "wf_prefix": "categorized_"}
    #         ]
    #     },
    #     "budget": {
    #         "wf_key": "budget",
    #         "wf_name": "budget",
    #         "wf_folders": [
    #             {"wf_folder": "budget", "wf_purpose": "wf_working", "wf_prefix": "budget_"}
    #         ]
    #     }
    # },
        BDM_OPTIONS: {
            BDMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BDMO_LOG_LEVEL: "DEBUG",
            BDMO_LOG_FILE: "logs/p3BudgetModel.log",
            BDMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        },
        BDM_CREATED_DATE: None,
        BDM_LAST_MODIFIED_DATE: None,
        BDM_LAST_MODIFIED_BY: None,
        # BDM_WORKING_DATA: {},
        BDM_DATA_CONTEXT: {
            DC_FI_KEY: "boa",  # Financial Institution Key
            DC_WF_KEY: EXAMPLE_BDM_WF_CATEGORIZATION,  # Workflow Key
            DC_WF_PURPOSE: WF_WORKING,
            DC_WB_TYPE: WF_WORKING
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
        # BDM_WORKING_DATA: {},
        BDM_DATA_CONTEXT: bdm_store_config[BDM_DATA_CONTEXT]
    }
    #endregion BDMConfig dictionary
    # ------------------------------------------------------------------------ +
    #region BDM_CONFIG_default() classmethod
    @classmethod
    def BDM_CONFIG_default(cls, default : bool = False) -> BDM_CONFIG_TYPE:
        """Get a pristine version of a BDMConfig object."""
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
            # Create an instance of BDMConfig configured from bmt
            bdm_config = BDMConfig(bdm_config = bmt)            
            logger.debug(f"Complete:")   
            return bdm_config
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_CONFIG_default() classmethod
    # ------------------------------------------------------------------------ +
    #region BDM_CONFIG_validate_attributes() created BDMConfig from a loaded BDM_STORE url.
    @classmethod
    def BDM_CONFIG_validate_attributes(cls, bdm_config : dict) -> None:
        """Verify a BDMConfig object has all required attributes.

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
    #region BDM_STORE_dehydrate() remove non-serializable objects.
    # @classmethod
    # def BDM_STORE_dehydrate(cls, model : BudgetDomainModel) -> None:
    #     """Create a BDM_STORE dict from a BudgetDomainModel instance.
    #     Remove non-serializable objects from the resulting BDM_STORE."""
    #     try:
    #         logger.debug("Start:  ...")

    #         _ = p3u.is_not_obj_of_type("model", model, BudgetDomainModel, 
    #                                    raise_error=True)    
    #         bdm_store: BDM_STORE_TYPE = model.to_dict()
    #         # Traverse the BDM_STORE and remove non-serializable objects.
    #         # Replace objects with known non-serializable attributes with a
    #         # dict copy with the non-serializable attributes set to None.
    #         if (BDM_FI_COLLECTION in bdm_store and
    #             bdm_store[BDM_FI_COLLECTION] is not None and
    #             isinstance(bdm_store[BDM_FI_COLLECTION], dict) and 
    #             len(bdm_store[BDM_FI_COLLECTION]) > 0):
    #             for fi_key, fi_object in bdm_store[BDM_FI_COLLECTION].items():
    #                 if not isinstance(fi_object, dict):
    #                     continue
    #                 if (FI_WORKBOOK_DATA_COLLECTION not in fi_object or
    #                     fi_object[FI_WORKBOOK_DATA_COLLECTION] is None or
    #                     not isinstance(fi_object[FI_WORKBOOK_DATA_COLLECTION], dict) or
    #                     len(fi_object[FI_WORKBOOK_DATA_COLLECTION]) == 0):
    #                     continue
    #                 for wb_id, bdm_wb in fi_object[FI_WORKBOOK_DATA_COLLECTION].items():
    #                     if isinstance(bdm_wb, BDMWorkbook):
    #                         # Convert the BDMWorkbook object to a dict.
    #                         # Don't modify the BDMWorkbook objects
    #                         bdm_wb_dict = bdm_wb.to_dict()
    #                     elif isinstance(bdm_wb, dict):
    #                         bdm_wb_dict = bdm_wb
    #                     else:
    #                         continue
    #                     # A bdm_wb dict may have an object for wb_content
    #                     if bdm_wb_dict[WB_CONTENT] is not None:
    #                         # Never serialize the wb_content, so set it to None.
    #                         wbc_type = type(bdm_wb_dict[WB_CONTENT]).__name__
    #                         logger.debug(f" Dehydrating BDMWorkbook({wb_id}): "
    #                                      f"wb_content type: '{wbc_type}'")
    #                         bdm_wb_dict[WB_CONTENT] = None
    #                         bdm_wb_dict[WB_LOADED] = False 
    #                         # Replace the bdm_wb in fi_object[FI_WORKBOOK_DATA_COLLECTION]
    #                         fi_object[FI_WORKBOOK_DATA_COLLECTION][wb_id] = bdm_wb_dict
    #         logger.debug(f"Complete:")   
    #         return bdm_store
    #     except Exception as e:
    #         m = p3u.exc_err_msg(e)
    #         logger.error(m)
    #         raise
    #endregion BDM_STORE_dehydrate() created BDMConfig from a loaded BDM_STORE url.
    # ------------------------------------------------------------------------ +
    #region BDM_STORE_url_get() create BDM_CONFIG from a loaded BDM_STORE url.
    @classmethod
    def BDM_STORE_url_get(cls, bdm_url : str) -> BDM_CONFIG_TYPE:
        """Load the BDM_STORE json file from storage via the bdm_url, 
        validate the BDM_STORE attributes, create a BDMConfig object from 
        the BDM_STORE content and return it."""
        try:
            logger.debug("Start:  ...")
            bdm_store = bsm_BDM_STORE_url_get(bdm_url)
            # Update the URL used to load is set in the bdm_store structure.
            bdm_store[BDM_URL] = bdm_url  
            # Validate the loaded BDM_STORE config. Raises error if not happy
            cls.BDM_CONFIG_validate_attributes(bdm_store)
            # Create an instance of BDMConfig configured from bdm_store
            bdm_config = BDMConfig(bdm_config = bdm_store)            
            logger.debug(f"Complete:")
            # BDMConfig is now ready for use, populated from BDM_STORE with
            # scalar value and dictionaries retrieved from bdm_store.
            return bdm_config
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_STORE_url_get() created BDM_CONFIG from a loaded BDM_STORE url.
    # ------------------------------------------------------------------------ +
    #region BDMConfig class constructor __init__()
    def __init__(self, bdm_config : Dict) -> None:
        """Construct a BDMConfig object used for configuration.
        
        The BDMConfig class provides initialization values for initializing a
        new BudgetDomainModel instance.
        It is for internal use only. There are two means to apply it when
        constructing a new BudgetDomainModel object: 
            1. Load a BDM_STORE file from storage, or 
            2. Marshall up a pristine BDMConfig object with initial values.
        
        BDMConfig has a property BDM_CONFIG_OBJECT which has the dictionary 
        used for initialization. 

        No outside config or settings are used to keep this stand-alone and
        uncoupled from other layers of an application.
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
            setattr(self, BDM_DATA_CONTEXT, bdm_config[BDM_DATA_CONTEXT])
            # Complete the BDMConfig instance initialization.
            self.bdm_initialized = True
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    def __getitem__(self, key: str) -> Any:
        """Get an attribute by key."""
        return getattr(self, key)   
    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute by key."""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Key '{key}' not found in BDMConfig.")
    #endregion BDMConfig class constructor __init__()
    # ------------------------------------------------------------------------ +
    #region    Mimic the BudgetDomainModel (BDM) properties
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
    def bdm_config_object(self) -> BDM_CONFIG_TYPE:
        """The budget model configuration object."""
        return getattr(self, BDM_CONFIG_OBJECT)
    @bdm_config_object.setter
    def bdm_config_object(self, value: BDM_CONFIG_TYPE) -> None:
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
    def bdm_options(self) -> BDM_OPTIONS_TYPE:
        """The budget model options dictionary."""
        return self._options
    @bdm_options.setter
    def bdm_options(self, value: BDM_OPTIONS_TYPE) -> None:
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
    def data_context(self) -> DATA_CONTEXT_TYPE:
        """The saved data context values for the budget model."""
        return self._data_context 
    @data_context.setter
    def data_context(self, value: DATA_CONTEXT_TYPE) -> None:
        """Set the saved data context valuesfor the budget model."""
        self._data_context = value

    #endregion BudgetDomainModel (BDM) compatible properties
    # ------------------------------------------------------------------------ +
