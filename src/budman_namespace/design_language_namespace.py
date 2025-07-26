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
DATA_OBJECT = Dict[str, Any] 
DATA_TUPLE = Tuple[str, DATA_OBJECT]  # A tuple of (key, value) for data objects
DATA_COLLECTION = Dict[str, DATA_OBJECT] 
DATA_LIST = List[DATA_OBJECT] 
type DATA_MAP = Dict[str, str]
# BUDMAN data type constants
type WORKBOOK_ID = str
type BUDMAN_RESULT = tuple[bool, Any]  # A tuple of (success, message or data)
type WORKBOOK_OBJECT = Union[object, Dict]
type WORKBOOK_CONTENT = Any
WORKBOOK_DATA_COLLECTION = Dict[str, WORKBOOK_OBJECT]
WORKBOOK_ITEM = DATA_TUPLE
LOADED_WORKBOOK_COLLECTION = dict[WORKBOOK_ID, WORKBOOK_CONTENT]
LOADED_WORKBOOK_ITEM = DATA_OBJECT
DATA_CONTEXT = DATA_OBJECT
BDM_STORE = DATA_OBJECT
BDM_CONFIG = DATA_OBJECT
BDM_CHECK_REGISTER = DATA_OBJECT
# WORKBOOK type related types
type CATEGORY_MAP_WORKBOOK = DATA_MAP # a mapping dict
type TXN_CATEGORIES_WORKBOOK = DATA_OBJECT
type TXN_REGISTER_WORKBOOK = DATA_OBJECT
type EXCEL_TXNS_WORKBOOK = openpyxl.Workbook
type EXCEL_TXNS_WORKSHEET = openpyxl.worksheet.worksheet.Worksheet
type CATEGORY_COLLECTION = DATA_COLLECTION
type COMPLIED_CATEGORY_MAP = Dict[re.Pattern, str]

# MODEL_OBJECT : Type[object] = object()
BDMO_OBJECT = DATA_OBJECT
FI_OBJECT = DATA_OBJECT  # Financial Institution object
FI_COLLECTION = DATA_COLLECTION
FI_DATA_OBJECT = DATA_OBJECT
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
# Budget Storage Model (BSM) constants
BSM_SUPPORTED_URL_SCHEMES = ("file") #, "http", "https")
VALID_BSM_BDM_STORE_FILETYPES = (".json", ".jsonc")
BSM_DATA_COLLECTION_CSV_STORE_FILETYPES = (".csv",".txt")
PATH = "_path"
ABS_PATH = "_abs" + PATH
WORKBOOKS = "_workbooks"
# ---------------------------------------------------------------------------- +
# DC and BDMWorkbook Attribute key name constants
WB_INDEX = "wb_index" 
WB_ID = "wb_id"
WB_NAME = "wb_name"
WB_FILENAME = "wb_filename"
WB_FILETYPE = "wb_filetype"
WB_TYPE = "wb_type"
WB_URL = "wb_url" 
FI_KEY = "fi_key"
WF_KEY = "wf_key"
WF_PURPOSE = "wf_purpose" 
WF_FOLDER_ID = "wf_folder_id" 
WF_FOLDER = "wf_folder"
WB_LOADED = "wb_loaded" 
WB_CONTENT = "wb_content" 
WB_CATEGORY_COLLECTION = "wb_category_collection"
WB_CATEGORY_COUNT = "wb_category_count"
WB_CATEGORY_MAP_URL = "wb_category_map_url"  # URL to the category map workbook
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
    BDM_URL, BDM_FI_COLLECTION, BDM_WF_COLLECTION,  
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
FI_TRANSACTION_DESCRIPTION_COLUMN = "fi_transaction_description_column"
FI_WORKBOOK_DATA_COLLECTION = "fi_workbook_data_collection" 
# Additional FI_DATA-related constants
VALID_FI_OBJECT_ATTR_KEYS = (FI_KEY, FI_NAME, FI_TYPE, FI_FOLDER, 
                             FI_WORKBOOK_DATA_COLLECTION)
VALID_FI_KEYS = ("boa", "merrill")
VALID_FI_TYPES = ("bank", "brokerage", "organization", "person")
BDM_FI_NAMES = ("Bank of America", "Merrill Lynch", "CitiBANK")
# ---------------------------------------------------------------------------- +
#
# Supported BM Workflow Names
#
BDM_WF_INTAKE = "intake"
BDM_WF_CATEGORIZATION = "categorize_transactions"
BDM_WF_FINALIZATION = "budget"
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
WF_FOLDER = "wf_folder"
WF_FOLDER_ID = "wf_folder_id"
# ---------------------------------------------------------------------------- +
# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
VALID_BDM_PATH_ELEMENTS = (BDM_FOLDER, BDM_URL, FI_FOLDER, 
                           WF_INPUT_FOLDER, WF_WORKING_FOLDER, WF_OUTPUT_FOLDER)
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
WB_USER_CONTENT = ".user_content"
WB_TYPE_UNKNOWN = ".unknown_type"
VALID_WB_TYPE_VALUES = (
    WB_TYPE_BDM_STORE, WB_TYPE_BDM_CONFIG,
    WB_TYPE_TXN_REGISTER, WB_TYPE_EXCEL_TXNS,
    WB_TYPE_CSV_TXNS, WB_TYPE_BUDGET, 
    WB_TYPE_TXN_CATEGORIES,
    WB_TYPE_CATEGORY_MAP,
    WB_USER_CONTENT
    # WB_TYPE_UNKNOWN
    )
WB_URL = "wb_url"  
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
#region CLIView command output type constants
# CMD_RESULT dictionary key constants
CMD_RESULT_TYPE ="cmd_result_type"
CMD_RESULT_CONTENT = "cmd_result_content"
# CMD_RESULT_TYPE values
CLIVIEW_OUTPUT_STRING = "cliview_output_string"
CLIVIEW_WORKBOOK_INFO_TABLE = "cliview_workbook_info_table"
CLIVIEW_WORKBOOK_TREE_VIEW = "cliview_workbook_tree_view"
#endregion CLIView command output type constants
# ---------------------------------------------------------------------------- +
#
# Last ditch BudMan application default settings
#
BUDMAN_DEFAULT_WORKFLOW_VALUE = BDM_WF_CATEGORIZATION
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
