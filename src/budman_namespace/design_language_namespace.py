# ---------------------------------------------------------------------------- +
#region budman_design_language_namespace.py module
""" BudgetManagerDesignLanguage: a design language for Budget Management.

"""
#endregion budman_design_language_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages

# third-party modules and packages
import re
from typing import Dict, List, Tuple, Any, Type, TYPE_CHECKING, Union
import openpyxl
from openpyxl import Workbook
import openpyxl.worksheet.worksheet
from openpyxl.worksheet.worksheet import Worksheet #as Worksheet
# local modules and packages

#endregion Imports
# ---------------------------------------------------------------------------- +
# Type Alias Constants
# Base Types - not model-aware
DATA_OBJECT_TYPE = Dict[str, Any] 
DATA_TUPLE_TYPE = Tuple[str, DATA_OBJECT_TYPE]  # A tuple of (key, value) for data objects
DATA_COLLECTION_TYPE = Dict[str, DATA_OBJECT_TYPE] 
DATA_LIST_TYPE = List[DATA_OBJECT_TYPE] 
type DATA_MAP_TYPE = Dict[str, str]
# BUDMAN data type constants
type WORKBOOK_ID_TYPE = str
type BUDMAN_RESULT_TYPE = tuple[bool, Any]  # A tuple of (success, message or data)
type WORKBOOK_OBJECT_TYPE = Union[object, Dict]
type WORKBOOK_CONTENT_TYPE = Any
WORKBOOK_DATA_COLLECTION_TYPE = Dict[str, WORKBOOK_OBJECT_TYPE]
WORKBOOK_ITEM_TYPE = DATA_TUPLE_TYPE
LOADED_WORKBOOK_COLLECTION_TYPE = dict[WORKBOOK_ID_TYPE, WORKBOOK_CONTENT_TYPE]
LOADED_WORKBOOK_ITEM_TYPE = DATA_OBJECT_TYPE
DATA_CONTEXT_TYPE = DATA_OBJECT_TYPE
BDM_STORE_TYPE = DATA_OBJECT_TYPE
BDM_CONFIG_TYPE = DATA_OBJECT_TYPE
BDM_CHECK_REGISTER_TYPE = DATA_OBJECT_TYPE
# WORKBOOK type related types
type CATEGORY_MAP_WORKBOOK_TYPE = DATA_MAP_TYPE # a mapping dict
type TXN_CATEGORIES_WORKBOOK_TYPE = DATA_OBJECT_TYPE
type TXN_REGISTER_WORKBOOK_TYPE = DATA_OBJECT_TYPE
type EXCEL_TXNS_WORKBOOK_TYPE = openpyxl.Workbook
type EXCEL_TXNS_WORKSHEET_TYPE = openpyxl.worksheet.worksheet.Worksheet
type CATEGORY_COLLECTION_TYPE = DATA_COLLECTION_TYPE
type COMPLIED_CATEGORY_MAP_TYPE = Dict[re.Pattern, str]

# MODEL_OBJECT-related types
type BDM_OPTIONS_TYPE = DATA_OBJECT_TYPE
type FI_OBJECT_TYPE = DATA_OBJECT_TYPE  # Financial Institution object
type FI_COLLECTION_TYPE = DATA_COLLECTION_TYPE
type WF_OBJECT_TYPE = DATA_OBJECT_TYPE  # Workflow object
type WF_COLLECTION_TYPE = DATA_COLLECTION_TYPE 
type WF_FOLDER_CONFIG_TYPE = DATA_OBJECT_TYPE
type WF_FOLDER_CONFIG_LIST_TYPE = List[WF_FOLDER_CONFIG_TYPE]
type FI_WF_FOLDER_CONFIG_COLLECTION_TYPE = Dict[str, WF_FOLDER_CONFIG_LIST_TYPE]
# ---------------------------------------------------------------------------- +
# Budget Storage Model (BSM) constants
BSM_SUPPORTED_URL_SCHEMES = ("file") #, "http", "https")
VALID_BSM_BDM_STORE_FILETYPES = (".json", ".jsonc")
BSM_DATA_COLLECTION_CSV_STORE_FILETYPES = (".csv",".txt")
PATH = "_path"
ABS_PATH = "_abs" + PATH
WORKBOOKS = "_workbooks"
# ---------------------------------------------------------------------------- +
# Common dictionary attribute key name constants
FI_KEY = "fi_key"
WF_KEY = "wf_key"
WF_FOLDER = "wf_folder"
WF_PURPOSE = "wf_purpose"
WF_PREFIX = "wf_prefix"  
WF_FOLDER_URL = "wf_folder_url" 
WB_INDEX = "wb_index" 
WB_ID = "wb_id"
WB_NAME = "wb_name"
WB_FILENAME = "wb_filename"
WB_FILETYPE = "wb_filetype"
WB_TYPE = "wb_type"
WB_URL = "wb_url" 
WB_URL = "wb_url"  
WB_LOADED = "wb_loaded" 
WB_CONTENT = "wb_content" 
WB_CATEGORY_COLLECTION = "wb_category_collection"
WB_CATEGORY_COUNT = "wb_category_count"
WB_CATEGORY_MAP_URL = "wb_category_map_url"  # URL to the category map workbook
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
BDM_DATA_CONTEXT = "_data_context"             # Type: DATA_CONTEXT
BSM_FILE_TREE = "_bsm_file_tree"               # Type: BSMFileTree, not persisted
BDM_VALID_PREFIXES = "_valid_prefixes"          # Type: List[str]
BDM_VALID_WB_TYPES = "_valid_wb_types"          # Type: List[str
# BDMConfig class Property name Constants (same as BudgetDomainModel)
# but with BDM_CONFIG_OBJECT instead of BDM_STORE_OBJECT.
BDM_CONFIG_OBJECT = "_bdm_config_object"       # Type: BDM_CONFIG
# Validation list constants
VALID_BDM_PROPERTIES = (
    BDM_ID, BDM_STORE_OBJECT, BDM_CONFIG_OBJECT, BDM_INITIALIZED, 
    BDM_FILENAME, BDM_FILETYPE, BDM_FOLDER, 
    BDM_URL, BDM_FI_COLLECTION, BDM_WF_COLLECTION, BDM_OPTIONS,
    BDM_CREATED_DATE, BDM_LAST_MODIFIED_DATE, 
    BDM_LAST_MODIFIED_BY, BDM_DATA_CONTEXT, BSM_FILE_TREE)
BSM_PERSISTED_PROPERTIES = (
    BDM_ID, BDM_FILENAME, BDM_FILETYPE, BDM_FOLDER, 
    BDM_URL, BDM_FI_COLLECTION, BDM_WF_COLLECTION,  
    BDM_OPTIONS, BDM_CREATED_DATE, BDM_LAST_MODIFIED_DATE, BDM_LAST_MODIFIED_BY,
    BDM_DATA_CONTEXT)
# ---------------------------------------------------------------------------- +
VALID_BSM_BDM_STORE_FILETYPES = (".json", ".jsonc")
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
FI_KEY = FI_KEY # common
FI_NAME = "fi_name"
FI_TYPE = "fi_type"
FI_FOLDER = "fi_folder" 
FI_TRANSACTION_DESCRIPTION_COLUMN = "fi_transaction_description_column"
FI_TRANSACTION_BUDGET_CATEGORY_COLUMN = "fi_transaction_budget_category_column"
FI_TRANSACTION_WORKSHEET_NAME = "fi_transaction_worksheet_name"
FI_WF_FOLDER_CONFIG_COLLECTION = "fi_wf_folder_config_collection" 
FI_WORKBOOK_DATA_COLLECTION = "fi_workbook_data_collection" 
VALID_FI_OBJECT_ATTR_KEYS = (FI_KEY, FI_NAME, FI_TYPE, FI_FOLDER, 
                             FI_WF_FOLDER_CONFIG_COLLECTION, 
                             FI_TRANSACTION_WORKSHEET_NAME,
                             FI_WORKBOOK_DATA_COLLECTION)
# Other FI-related constants
VALID_FI_KEYS = ("boa", "merrill")
VALID_FI_TYPES = ("bank", "brokerage", "organization", "person")
BDM_FI_NAMES = ("Bank of America", "Merrill Lynch", "CitiBANK")
# ---------------------------------------------------------------------------- +
#
# Example Workflow Names
#
EXAMPLE_BDM_WF_INTAKE = "intake"
EXAMPLE_BDM_WF_CATEGORIZATION = "categorize_transactions"
EXAMPLE_BDM_WF_BUDGET = "budget"
VALID_BDM_WORKFLOWS = (EXAMPLE_BDM_WF_INTAKE, EXAMPLE_BDM_WF_CATEGORIZATION, EXAMPLE_BDM_WF_BUDGET)
# ---------------------------------------------------------------------------- +
#
# WF_OBJECT_TYPE workflow definition object (Dictionary key names)
#
WF_KEY = WF_KEY #common
WF_NAME = "wf_name"  
WF_FOLDER_CONFIG_LIST = "wf_folder_config_list" 
VALID_WF_OBJECT_ATTR_KEYS = (WF_KEY, WF_NAME, WF_FOLDER_CONFIG_LIST)
# WF_FOLDER_CONFIG_TYPE workflow folder definition object (Dictionary key names)
WF_FOLDER = WF_FOLDER # common
WF_PURPOSE = WF_PURPOSE # common
WF_PREFIX = WF_PREFIX # common  
WF_FOLDER_URL = WF_FOLDER_URL # common 
# Additional WF_OBJECT-related constants
VALID_WF_FOLDER_CONFIG_OBJECT_ATTR_KEYS = (WF_FOLDER, WF_PURPOSE,
                                           WF_PREFIX, WF_FOLDER_URL)
# ---------------------------------------------------------------------------- +
# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
VALID_BDM_PATH_ELEMENTS = (BDM_FOLDER, BDM_URL, FI_FOLDER)
# ---------------------------------------------------------------------------- +
# Workflow-related (WF_) data associated with a specific FI is BSM territory.
# The primary data object now is the WORKBOOK (excel workbook, .csv file, .json etc.). 
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
VALID_WF_PURPOSE_CHOICES = ["input", "working", "output"]
VALID_WF_PURPOSE_MAP = dict(zip(VALID_WF_PURPOSE_CHOICES, VALID_WF_PURPOSE_VALUES))

# NEW Workbook Type Constants. These define the types of workbooks that
# might be stored in a storage system, such as a file system or a database.
# These symbols navigate the transition from the BDM to the BSM.
WB_TYPE_BDM_STORE = ".bdm_store"
WB_TYPE_BDM_CONFIG = ".bdm_config"
WB_TYPE_TXN_REGISTER = ".txn_register"
WB_TYPE_EXCEL_TXNS = ".excel_txns"
WB_TYPE_CSV_TXNS = ".csv_txns"
WB_TYPE_TXN_CATEGORIES = ".txn_categories"
WB_TYPE_CATEGORY_MAP = "_category_map"
WB_TYPE_BUDGET = ".budget"
VALID_WB_TYPE_VALUES = [
    WB_TYPE_BDM_STORE, WB_TYPE_BDM_CONFIG,
    WB_TYPE_TXN_REGISTER, WB_TYPE_EXCEL_TXNS,
    WB_TYPE_CSV_TXNS, WB_TYPE_BUDGET, 
    WB_TYPE_TXN_CATEGORIES,
    WB_TYPE_CATEGORY_MAP,
]
WB_TYPE_UNKNOWN = ".unknown_type"
# Workbook Filetype Constants
WB_FILETYPE_CSV = ".csv"
WB_FILETYPE_XLSX = ".xlsx"
WB_FILETYPE_JSON = ".json"
WB_FILETYPE_JSONC = ".jsonc"
WB_FILETYPE_TEXT = ".txt"
WB_FILETYPE_TOML = ".toml"
WB_FILETYPE_PY = ".py"
# Valid filetypes for workbook types
WB_FILETYPE_MAP = {
    WB_TYPE_BDM_STORE: WB_FILETYPE_JSONC,
    WB_TYPE_BDM_CONFIG: WB_FILETYPE_JSONC,
    WB_TYPE_TXN_REGISTER: WB_FILETYPE_CSV,
    WB_TYPE_EXCEL_TXNS: WB_FILETYPE_XLSX,
    WB_TYPE_CSV_TXNS: WB_FILETYPE_CSV,
    WB_TYPE_BUDGET: WB_FILETYPE_XLSX,
    WB_TYPE_TXN_CATEGORIES: WB_FILETYPE_JSON,
    WB_TYPE_CATEGORY_MAP: WB_FILETYPE_PY
}
VALID_WB_FILETYPES = (
    WB_FILETYPE_CSV, WB_FILETYPE_XLSX,
    WB_FILETYPE_JSON, WB_FILETYPE_JSONC, WB_FILETYPE_TEXT,
    WB_FILETYPE_TOML, WB_FILETYPE_PY
)
# ---------------------------------------------------------------------------- +
# DATA_CONTEXT "good guy" interface (Dictionary key names)
DC_INITIALIZED = "dc_initialized"
DC_FI_KEY = FI_KEY
DC_WF_KEY = WF_KEY
DC_WF_PURPOSE = WF_PURPOSE
DC_WB_TYPE = WB_TYPE
DC_WB_NAME = WB_NAME
DC_LOADED_WORKBOOKS = "dc_loaded_workbooks"  # key name
DC_BDM_STORE = "dc_bdm_store"
VALID_DATA_CONTEXT_ATTR_KEYS = (
    DC_INITIALIZED,
    DC_FI_KEY,
    DC_WF_KEY,
    DC_WB_NAME,
    DC_WB_TYPE,
    DC_LOADED_WORKBOOKS,
    DC_BDM_STORE
)
# ---------------------------------------------------------------------------- +
#
# Last ditch BudMan application default settings
#
BUDMAN_DEFAULT_WORKFLOW_VALUE = EXAMPLE_BDM_WF_CATEGORIZATION
BUDMAN_DEFAULT_WORKBOOK_TYPE_VALUE = WF_WORKING
# ---------------------------------------------------------------------------- +
# Miscellaneous Convenience Constants
BUDMAN_WIDTH = 250
P1 = " "  # 1 space padding
P2 = "  "  # 2 space padding
P3 = "   "  # 3 space padding
P4 = "    "  # 4 space padding
P5 = "     "  # 5 space padding
P6 = "      "  # 6 space padding
P7 = "       "  # 7 space padding
P8 = "        "  # 8 space padding
P9 = "         "  # 9 space padding
P10 = "          "  # 10 space padding
