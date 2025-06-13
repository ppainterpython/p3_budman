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
# WORKBOOK_DATA_LIST - the list of workbooks for a specific folder. 
# It is a list of WORKBOOK_ITEM tuples: (workbook_name, workbook_abs_path)
# The term WORKBOOK_DATA refers to some of the data associated with a workbook.
WORKBOOK_DATA_COLLECTION = DATA_COLLECTION
WORKBOOK_DATA_LIST = DATA_TUPLE_LIST 
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
VALID_BSM_BDM_STORE_FILETYPES = (".json", ".jsonc")
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
WF_PURPOSE = "wf_purpose" 
WB_TYPE = "wb_type"
WB_NAME = "wb_name"
WB_REF = "wb_ref"
WB_INFO = "wb_info"
# ---------------------------------------------------------------------------- +
# Attribute value constants
WB_INFO_LEVEL_INFO = "info"
WB_INFO_LEVEL_VERBOSE = "verbose"
VALID_WB_INFO_LEVELS = [WB_INFO_LEVEL_INFO, WB_INFO_LEVEL_VERBOSE]
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
VALID_BDM_PROPERTIES = (
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
VALID_BSM_BDM_STORE_FILETYPES = (".json", ".jsonc")
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
FI_WORKBOOK_COLLECTION = "fi_workbook_collection" 
# Additional FI_DATA-related constants
VALID_FI_OBJECT_ATTR_KEYS = (FI_KEY, FI_NAME, FI_TYPE, FI_FOLDER, 
                             FI_DATA_COLLECTION, FI_WORKBOOK_COLLECTION)
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
VALID_BDM_WORKFLOWS = (BDM_WF_INTAKE, BDM_WF_CATEGORIZATION, BDM_WF_FINALIZATION)
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
WF_PURPOSE_FOLDER_MAP = "wf_purpose_folder_map" # map of workbook names to paths
# Additional WF_OBJECT-related constants
VALID_WF_OBJECT_ATTR_KEYS = (WF_KEY, WF_NAME, 
                        WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER,
                        WF_PREFIX_IN, WF_PREFIX_OUT, WF_PURPOSE_FOLDER_MAP)
WF_FOLDER_PATH_ELEMENTS = (WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER)
# ---------------------------------------------------------------------------- +
# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
VALID_BDM_PATH_ELEMENTS = (BDM_FOLDER, BDM_URL, FI_FOLDER, 
                           WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER)
# ---------------------------------------------------------------------------- +
# WORKBOOK_DATA_COLLECTION is a subclass of DATA_OBJECT (Dict) used to manage
# Workflow-related (WF_) data associated with a specific FI).
# The primary data object now is the WORKBOOK (an excel workbook or a .csv file). 
# These are stored by the BSM in files in folders in a storage system, so there 
# are Path strings associated. In the BDM, a WORKBOOK has a unique name, and a 
# type, the WB_TYPE. Another key concern is that BudMan is workflow-based. So
# workbooks are processed an moved through a workflow. Each workflow is composed
# tasks performed on the workbooks. A workbook can be input to or output from a 
# workflow , or be held as working data in a workflow. So, workflows have a 
# purpose associated with the folders to designate them as input, working, or 
# output, the WF_PURPOSE.
# Workbook types (WB_TYPE) identify the nature of the file and relate to the 
# workbooks filename and filetype, which may be modified as workbooks move
# through the workflow. 
# Workflow Purpose:
WF_INPUT = "wf_input" 
WF_WORKING = "wf_working" 
WF_OUTPUT ="wf_output" 
VALID_WF_PURPOSE_VALUES = (WF_INPUT, WF_WORKING, WF_OUTPUT)

VALID_WORKBOOK_DATA_COLLECTION_ATTR_KEYS = (WF_INPUT, WF_WORKING, WF_OUTPUT)

# NEW Workbook Type Constants. These define the types of workbooks that
# might be stored in a storage system, such as a file system or a database.
WB_TYPE_BDM_STORE = "bdm_store"
WB_TYPE_BDM_CONFIG = "bdm_config"
WB_TYPE_CHECK_REGISTER = "check_register"
WB_TYPE_TRANSACTIONS = "transactions"
WB_TYPE_BUDGET = "budget"
VALID_WB_TYPE_VALUES = (
    WB_TYPE_BDM_STORE, WB_TYPE_BDM_CONFIG,
    WB_TYPE_CHECK_REGISTER, WB_TYPE_TRANSACTIONS, 
    WB_TYPE_BUDGET
    )
# Workbook Filetype Constants
WB_FILETYPE_CSV = ".csv"
WB_FILETYPE_XLSX = ".xlsx"
WB_FILETYPE_JSON = ".json"
WB_FILETYPE_JSONC = ".jsonc"
WB_FILETYPE_TEXT = ".txt"
# Valid filetypes for workbook types
WB_FILETYPE_MAP = {
    WB_TYPE_BDM_STORE: WB_FILETYPE_JSONC,
    WB_TYPE_BDM_CONFIG: WB_FILETYPE_JSONC,
    WB_TYPE_CHECK_REGISTER: WB_FILETYPE_CSV,
    WB_TYPE_TRANSACTIONS: WB_FILETYPE_XLSX,
    WB_TYPE_BUDGET: WB_FILETYPE_XLSX
}
VALID_WB_FILETYPES = (
    WB_FILETYPE_CSV, WB_FILETYPE_XLSX,
    WB_FILETYPE_JSON, WB_FILETYPE_JSONC, WB_FILETYPE_TEXT
)
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

# Name: BDMWD_INITIALIZED
# Type: bool True | False
# Desc: Indicates if the BDMWD has been initialized.
BDMWD_INITIALIZED = "bdmwd_initialized"
# Name: BDMWD_FI_KEY
# Type: FI_KEY | "all" : str
# Desc: FI_KEY of the FI data in the DC, or "all" if all are loaded.
BDMWD_FI_KEY = FI_KEY
# Name: BDMWD_WF_KEY
# Type: WF_KEY | "all" : str
# Desc: WF_KEY of the FI Workflow data in the DC, or "all" if all are loaded.
BDMWD_WF_KEY = WF_KEY
# Name: BDMWD_WF_PURPOSE
# Type: WF_PURPOSE | "all" : str
# Desc: WF_PURPOSE of the FI Workflow data in the DC, or "all" if all are loaded.
BDMWD_WF_PURPOSE = WF_PURPOSE
# Name: BDMWD_WB_TYPE
# Type: WB_TYPE | "all" : str
# Desc: WB_TYPE of workbooks in the FI Workflow data in the DC, or "all" if all are loaded.
BDMWD_WB_TYPE = WB_TYPE
# Name: BDMWD_WB_NAME
# Type: WB_NAME | "all" : str
# Desc: A specific WB_NAME, or "all" if all are loaded.
BDMWD_WB_NAME = WB_NAME
# Name: BDMWD_WORKBOOKS
# Type: WORKBOOKS_LIST : list of tuples
# Desc: A list of tuples of wb_name, abs_path objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE.
BDMWD_WORKBOOKS = "bdmwd_workbooks" # key name
# Name: BDMWD_LOADED_WORKBOOKS
# Type: LOADED_WORKBOOK_COLLECTION : list of tuples
# Desc: A list of tuples of wb_name, Workbook objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE and are loaded into BDMWD.
BDMWD_LOADED_WORKBOOKS = "bdmwd_loaded_workbooks" # key name
# Name: BDMWD_LOADED_WORKBOOKS
# Type: Dict
# Desc: Values loaded from Budget Manager configuration file , or "store".
# Key validation list.
BDMWD_BDM_STORE = "budman_store"
VALID_BDM_WORKING_DATA_ATTR_KEYS = (
    BDMWD_INITIALIZED, 
    BDMWD_FI_KEY, 
    BDMWD_WF_KEY, 
    BDMWD_WF_PURPOSE,
    BDMWD_WB_TYPE,
    BDMWD_WB_NAME, 
    BDMWD_WORKBOOKS, 
    BDMWD_LOADED_WORKBOOKS,
    BDMWD_BDM_STORE)
# ---------------------------------------------------------------------------- +
# DATA_CONTEXT "good guy" interface (Dictionary key names)

# Name: DC_INITIALIZED
# Type: bool True | False
# Desc: Indicates if the DC has been initialized.
DC_INITIALIZED = BDMWD_INITIALIZED
# Name: DC_FI_KEY
# Type: FI_KEY | "all" : str
# Desc: FI_KEY of the FI data in the DC, or "all" if all are loaded.
DC_FI_KEY = BDMWD_FI_KEY
# Name: DC_WF_KEY
# Type: WF_KEY | "all" : str
# Desc: WF_KEY of the FI Workflow data in the DC, or "all" if all are loaded.
DC_WF_KEY = BDMWD_WF_KEY
# Name: DC_WF_PURPOSE
# Type: WF_PURPOSE | "all" : str
# Desc: WF_PURPOSE of the FI Workflow data in the DC, or "all" if all are loaded.
DC_WF_PURPOSE = BDMWD_WF_PURPOSE
# Name: DC_WB_TYPE
# Type: WB_TYPE | "all" : str
# Desc: WB_TYPE of workbooks in the FI Workflow data in the DC, or "all" if all are loaded.
DC_WB_TYPE = BDMWD_WB_TYPE
# Name: DC_WB_NAME
# Type: WB_NAME | "all" : str
# Desc: A specific WB_NAME, or "all" if all are loaded.
DC_WB_NAME = BDMWD_WB_NAME
# Name: DC_WORKBOOKS
# Type: WORKBOOKS_LIST
# Desc: A list of tuples of wb_name, abs_path objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE
DC_WORKBOOKS = BDMWD_WORKBOOKS
# Name: DC_LOADED_WORKBOOKS
# Type: LOADED_WORKBOOK_COLLECTION
# Desc: A list of tuples of wb_name, and Workbook objects for workbooks associated
#       with the current FI_KEY, WF_KEY, and WB_TYPE
DC_LOADED_WORKBOOKS = BDMWD_LOADED_WORKBOOKS
# Name: DC_LOADED_WORKBOOKS
# Type: Dict
# Desc: Values loaded from Budget Manager configuration file , or "store".
DC_BDM_STORE = BDMWD_BDM_STORE
DC_CHECK_REGISTERS = "dc_check_registers"
# Name: DC_LOADED_CHECK_REGISTERS
# Type: Dict
# Desc: Values loaded from Budget Manager configuration file , or "store".
DC_LOADED_CHECK_REGISTERS = "dc_loaded_check_registers"
VALID_DATA_CONTEXT_ATTR_KEYS = (
    DC_INITIALIZED,
    DC_FI_KEY,
    DC_WF_KEY,
    DC_WB_NAME,
    DC_WB_TYPE,
    DC_LOADED_WORKBOOKS,
    DC_WORKBOOKS,
    DC_BDM_STORE,
    DC_CHECK_REGISTERS,
    DC_LOADED_CHECK_REGISTERS)

VALID_BDMWD_OBJECT_ATTR_KEYS = VALID_BDM_WORKING_DATA_ATTR_KEYS + VALID_DATA_CONTEXT_ATTR_KEYS
# ---------------------------------------------------------------------------- +
#
# Last ditch BudMan application default settings
#
BUDMAN_DEFAULT_WORKFLOW_VALUE = BDM_WF_CATEGORIZATION
BUDMAN_DEFAULT_WORKBOOK_TYPE_VALUE = WF_WORKING
# ---------------------------------------------------------------------------- +
# Miscellaneous Convenience Constants
BUDMAN_WIDTH = 200
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
