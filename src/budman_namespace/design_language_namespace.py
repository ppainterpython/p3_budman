# ---------------------------------------------------------------------------- +
#region budman_design_language_namespace.py module
""" BudgetManagerDesignLanguage: a design language for Budget Management.

"""
#endregion budman_design_language_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages

# third-party modules and packages
from typing import Dict, List, Tuple, Any, Type, TYPE_CHECKING
from openpyxl import Workbook
# local modules and packages

#endregion Imports
# ---------------------------------------------------------------------------- +
# Type Alias Constants
# Base Types - not model-aware
DATA_OBJECT = Dict[str, Any] 
DATA_TUPLE = Tuple[str, DATA_OBJECT]  # A tuple of (key, value) for data objects
DATA_COLLECTION = Dict[str, DATA_OBJECT] 
DATA_LIST = List[DATA_OBJECT] 
DATA_TUPLE_LIST = List[DATA_TUPLE] 
# WORKBOOK_LIST - the list of workbooks for a specific folder. 
# It is a list of WORKBOOK_ITEM tuples: (workbook_name, workbook_abs_path)
WORKBOOK_LIST = DATA_TUPLE_LIST 
WORKBOOK_ITEM = DATA_TUPLE
WORKBOOK_DATA_COLLECTION = DATA_TUPLE_LIST
LOADED_WORKBOOK_COLLECTION = DATA_COLLECTION
LOADED_WORKBOOK_ITEM = DATA_OBJECT
DATA_CONTEXT = DATA_OBJECT
BDM_STORE = DATA_OBJECT
BDM_CONFIG = DATA_OBJECT
# MODEL_OBJECT : Type[object] = object()
BDMO_OBJECT = DATA_OBJECT
FI_OBJECT = DATA_OBJECT  # Financial Institution object
FI_COLLECTION = DATA_COLLECTION
FI_DATA_OBJECT = DATA_OBJECT
FI_DATA_COLLECTION = DATA_COLLECTION
WF_OBJECT = DATA_OBJECT  # Workflow object
WF_COLLECTION = DATA_COLLECTION 
# WF_DATA_COLLECTION workflow data collection (Dictionary key names)
# A dict for each FI, to hold the data for each workflow.
# { wf_key: WF_DATA_OBJECT, ... }
WF_DATA_COLLECTION = DATA_COLLECTION
# A dict for worklow to hold data for a specific FI
WF_DATA_OBJECT = DATA_OBJECT  # a DATA_OBJECT for a specific FI,WF
BDM_WORKING_DATA_OBJECT = DATA_OBJECT
# ---------------------------------------------------------------------------- +
# Valid data store file types for the Budget Storage Model (BSM).
BSM_VALID_BDM_STORE_FILETYPES = (".json", ".jsonc")
BSM_DATA_COLLECTION_CSV_STORE_FILETYPES = (".csv",".txt")
# ---------------------------------------------------------------------------- +
# Budget Model Filesystem Path default constants 
PATH = "_path"
ABS_PATH = "_abs" + PATH
WORKBOOKS = "_workbooks"
# ---------------------------------------------------------------------------- +
# Attribute key name constants
FI_KEY = "fi_key"
WF_KEY = "wf_key"
WB_TYPE = "wb_type"
WB_NAME = "wb_name"
WB_REF = "wb_ref"
WB_INFO = "wb_info"
# ---------------------------------------------------------------------------- +
# Attribute value constants
WB_INFO_LEVEL_INFO = "info"
WB_INFO_LEVEL_VERBOSE = "verbose"
WB_INFO_VALID_LEVELS = [WB_INFO_LEVEL_INFO, WB_INFO_LEVEL_VERBOSE]
RELOAD_TARGET = "reload_target"
CATEGORY_MAP = "category_map"
ALL_KEY = "all"
# ---------------------------------------------------------------------------- +
#
# Budget Domain Model Constants
#
# BudgetDomainModel (BDM) class Property name Constants
BDM_ID = "_bdm_id"                             # Type: str
BDM_STORE_OBJECT = "_bdm_store_object"         # Type: BDM_STORE
BDM_INITIALIZED = "_initialized"               # Type: bool
BDM_FILENAME = "_bdm_filename"                 # Type: str - path element
BDM_FILETYPE = "_bdm_filetype"                 # Type: str - path element
BDM_FOLDER = "_budget_folder"                  # Type: str - path element
BDM_URL = "_bdm_url"                           # Type: str
BDM_FI_COLLECTION = "_financial_institutions"  # Type: FI_COLLECTION
BDM_WF_COLLECTION = "_workflows"               # Type: WF_COLLECTION
BDM_OPTIONS = "_options"                       # Type: BDMO_OBJECT
BDM_CREATED_DATE = "_created_date"             # Type: str - ISO date string
BDM_LAST_MODIFIED_DATE = "_last_modified_date" # Type: str - ISO date string
BDM_LAST_MODIFIED_BY = "_last_modified_by"     # Type: str - user name
BDM_WORKING_DATA = "_wd"                       # Type: BDM_WORKING_DATA
BDM_DATA_CONTEXT = "_data_context"             # Type: DATA_CONTEXT
# BDMConfig class Property name Constants (same as BudgetDomainModel)
# but with BDM_CONFIG_OBJECT instead of BDM_STORE_OBJECT.
BDM_CONFIG_OBJECT = "_bdm_config_object"       # Type: BDM_CONFIG
# Validation list constants
BDM_VALID_PROPERTIES = (
    BDM_ID, BDM_STORE_OBJECT, BDM_CONFIG_OBJECT, BDM_INITIALIZED, 
    BDM_FILENAME, BDM_FILETYPE, BDM_FOLDER, 
    BDM_URL, BDM_FI_COLLECTION, BDM_WF_COLLECTION, BDM_OPTIONS,
    BDM_CREATED_DATE, BDM_LAST_MODIFIED_DATE, 
    BDM_LAST_MODIFIED_BY, BDM_WORKING_DATA, BDM_DATA_CONTEXT)
BSM_PERSISTED_PROPERTIES = (
    BDM_ID, BDM_FILENAME, BDM_FILETYPE, BDM_FOLDER, 
    BDM_FI_COLLECTION, BDM_WF_COLLECTION,  
    BDM_OPTIONS, BDM_CREATED_DATE, BDM_LAST_MODIFIED_DATE, BDM_LAST_MODIFIED_BY,
    BDM_DATA_CONTEXT)
# ---------------------------------------------------------------------------- +
BSM_VALID_BDM_STORE_FILETYPES = (".json", ".jsonc")
# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"
# ---------------------------------------------------------------------------- +
#
# BDMO_OBJECT Budget Domain Model Options pseudo-Object (Dictionary key names)
# TODO: Refactor this into BudManApplicationSettings, not Model Scope, no BDM_STORE
BDMO_LOG_CONFIG = "log_config"
BDMO_LOG_LEVEL = "log_level"
BDMO_LOG_FILE = "log_file"
BDMO_JSON_LOG_FILE = "json_log_file_name"
BDMO_EXPECTED_KEYS = (BDMO_LOG_CONFIG, BDMO_LOG_LEVEL, BDMO_LOG_FILE,
                    BDMO_JSON_LOG_FILE)
# ---------------------------------------------------------------------------- +
# FI_OBJECT financial institution pseudo-Object (Dictionary key names)
FI_KEY = FI_KEY 
FI_NAME = "fi_name"
FI_TYPE = "fi_type"
FI_FOLDER = "fi_folder" 
FI_DATA_COLLECTION = "fi_data_collection" 
# Additional FI_DATA-related constants
FI_OBJECT_VALID_ATTR_KEYS = (FI_KEY, FI_NAME, FI_TYPE, FI_FOLDER, FI_DATA_COLLECTION)
VALID_FI_KEYS = ("boa", "merrill")
VALID_FI_TYPES = ("bank", "brokerage", "organization", "person")
BDM_FI_NAMES = ("Bank of America", "Merrill Lynch", "CitiBANK")
# ---------------------------------------------------------------------------- +
#
# Supported BM Workflow Names
#
BDM_WF_INTAKE = "intake"
BDM_WF_CATEGORIZATION = "categorization"
BDM_WF_FINALIZATION = "finalization"
BDM_VALID_WORKFLOWS = (BDM_WF_INTAKE, BDM_WF_CATEGORIZATION, BDM_WF_FINALIZATION)
# ---------------------------------------------------------------------------- +
#
# WF_OBJECT workflow definition object (Dictionary key names)
#
WF_KEY = WF_KEY
WF_NAME = "wf_name"  # Also used as key in BM_FI workflows dictionary.
WF_INPUT_FOLDER = "wf_input_folder" # also used as key in FI_DATA_COLLECTION.
WF_WORKING_FOLDER = "wf_working_folder" # also used as key in FI_DATA_COLLECTION.
WF_OUTPUT_FOLDER = "wf_output_folder" # also used as key in FI_DATA_COLLECTION.
WF_PREFIX_IN = "wf_prefix_in"
WF_PREFIX_WORKING = "wf_prefix_working"
WF_PREFIX_OUT = "wf_prefix_out"
WB_TYPE_FOLDER_MAP = "wb_type_folder_map" # map of workbook names to paths
# Additional WF_OBJECT-related constants
WF_OBJECT_VALID_ATTR_KEYS = (WF_KEY, WF_NAME, 
                        WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER,
                        WF_PREFIX_IN, WF_PREFIX_OUT, WB_TYPE_FOLDER_MAP)
WF_FOLDER_PATH_ELEMENTS = (WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER)
# ---------------------------------------------------------------------------- +
# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
BDM_VALID_PATH_ELEMENTS = (BDM_FOLDER, BDM_URL, FI_FOLDER, 
                           WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER)
# ---------------------------------------------------------------------------- +
# WORKBOOK_DATA_COLLECTION is a subclass of DATA_OBJECT (Dict) used to manage
# Workflow-related (WF_) data associated with a specific FI).
# The primary data object now is the WORKBOOK (an excel workbook). There are
# stored by the BSM in files in folders in the filesystem, so there are Path 
# strings associated. In the BDM, a WORKBOOK has a unique name, and a type.
# Workbook types (WB_TYPE) indicate use of a workbook as either input data,
# working data, or output data.
# Workbook and folder Types
WB_INPUT = "wb_input" 
WB_WORKING = "wb_working" 
WB_OUTPUT ="wb_output" 
WB_WORKBOOK_TYPES = (WB_INPUT, WB_WORKING, WB_OUTPUT)
WB_DATA_OBJECT_VALID_ATTR_KEYS = (WB_INPUT, WB_WORKING, WB_OUTPUT)
# ---------------------------------------------------------------------------- +
# The BDM_WORKING_DATA (BDMWD_OBJECT) is designed to be a simple abstraction
# of the BudgetModel useful to View Models, Views, and other types of 
# upstream callers. Specifically, it is intended to serve as the 
# DATA_CONTEXT in an MVVM design pattern concept.
# DATA_CONTEXT is an abstract interface which can be bound to concrete
# implementations at runtime. 
# In BudgetManager, the BDMWD implements the DATA_CONTEXT interface.
# At the moment, this lightweight implementation is using a dictionary with
# well-known attribute key names and data types as a "good guy" interface.
# TODO: use an abstract base classes as proper interface for DATA_CONTEXT

# BDMWD_OBJECT "good guy" interface (Dictionary key names)
BDMWD_INITIALIZED = "bdmwd_initialized"
# Name: BDMWD_INITIALIZED
# Type: bool True | False
# Desc: Indicates if the BDMWD has been initialized.
BDMWD_FI_KEY = FI_KEY
# Name: BDMWD_FI_KEY
# Type: FI_KEY | "all" : str
# Desc: FI_KEY of the FI data in the DC, or "all" if all are loaded.
BDMWD_WF_KEY = WF_KEY
# Name: BDMWD_WF_KEY
# Type: WF_KEY | "all" : str
# Desc: WF_KEY of the FI Workflow data in the DC, or "all" if all are loaded.
BDMWD_WB_TYPE = WB_TYPE
# Name: BDMWD_WB_TYPE
# Type: WB_TYPE | "all" : str
# Desc: WB_TYPE of the FI Workflow data in the DC, or "all" if all are loaded.
BDMWD_WB_NAME = WB_NAME
# Name: BDMWD_WB_NAME
# Type: WB_NAME | "all" : str
# Desc: A specific WB_NAME, or "all" if all are loaded.
BDMWD_WORKBOOKS = "bdmwd_workbooks" # key name
# Name: BDMWD_WORKBOOKS
# Type: WORKBOOKS_LIST : list of tuples
# Desc: A list of tuples of wb_name, abs_path objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE.
BDMWD_LOADED_WORKBOOKS = "bdmwd_loaded_workbooks" # key name
# Name: BDMWD_LOADED_WORKBOOKS
# Type: LOADED_WORKBOOK_COLLECTION : list of tuples
# Desc: A list of tuples of wb_name, Workbook objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE and are loaded into BDMWD.
BDMWD_BDM_STORE = "budman_store"
# Name: BDMWD_LOADED_WORKBOOKS
# Type: Dict
# Desc: Values loaded from Budget Manager configuration file , or "store".
# Key validation list.
BDM_WORKING_DATA_VALID_ATTR_KEYS = (
    BDMWD_INITIALIZED, 
    BDMWD_FI_KEY, 
    BDMWD_WF_KEY, 
    BDMWD_WB_TYPE,
    BDMWD_WB_NAME, 
    BDMWD_WORKBOOKS, 
    BDMWD_LOADED_WORKBOOKS,
    BDMWD_BDM_STORE)
# ---------------------------------------------------------------------------- +
# DATA_CONTEXT "good guy" interface (Dictionary key names)
DC_INITIALIZED = BDMWD_INITIALIZED
# Name: DC_INITIALIZED
# Type: bool True | False
# Desc: Indicates if the DC has been initialized.
DC_FI_KEY = BDMWD_FI_KEY
# Name: DC_FI_KEY
# Type: FI_KEY | "all" : str
# Desc: FI_KEY of the FI data in the DC, or "all" if all are loaded.
DC_WF_KEY = BDMWD_WF_KEY
# Name: DC_WF_KEY
# Type: WF_KEY | "all" : str
# Desc: WF_KEY of the FI Workflow data in the DC, or "all" if all are loaded.
DC_WB_TYPE = BDMWD_WB_TYPE
# Name: DC_WB_TYPE
# Type: WB_TYPE | "all" : str
# Desc: WB_TYPE of the FI Workflow data in the DC, or "all" if all are loaded.
DC_WB_NAME = BDMWD_WB_NAME
# Name: DC_WB_NAME
# Type: WB_NAME | "all" : str
# Desc: A specific WB_NAME, or "all" if all are loaded.
DC_WORKBOOKS = BDMWD_WORKBOOKS
# Name: DC_WORKBOOKS
# Type: WORKBOOKS_LIST
# Desc: A list of tuples of wb_name, abs_path objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE
DC_LOADED_WORKBOOKS = BDMWD_LOADED_WORKBOOKS
# Name: DC_LOADED_WORKBOOKS
# Type: LOADED_WORKBOOK_COLLECTION
# Desc: A list of tuples of wb_name, and Workbook objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE
DC_BDM_STORE = BDMWD_BDM_STORE
# Name: DC_LOADED_WORKBOOKS
# Type: Dict
# Desc: Values loaded from Budget Manager configuration file , or "store".
DATA_CONTEXT_VALID_ATTR_KEYS = (
    DC_INITIALIZED,
    DC_FI_KEY,
    DC_WF_KEY,
    DC_WB_NAME,
    DC_WB_TYPE,
    DC_LOADED_WORKBOOKS,
    DC_WORKBOOKS,
    DC_BDM_STORE)

BDMWD_OBJECT_VALID_ATTR_KEYS = BDM_WORKING_DATA_VALID_ATTR_KEYS + DATA_CONTEXT_VALID_ATTR_KEYS
# ---------------------------------------------------------------------------- +
#
# Last ditch BudMan application default settings
#
BUDMAN_DEFAULT_WORKFLOW_VALUE = BDM_WF_CATEGORIZATION
BUDMAN_DEFAULT_WORKBOOK_TYPE_VALUE = WB_WORKING
# ---------------------------------------------------------------------------- +
# Miscellaneous Convenience Constants
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
