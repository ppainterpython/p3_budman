from typing import Dict, List, Tuple, Any
from openpyxl import Workbook

THIS_APP_NAME = "p3_budget_manager"
THIS_APP_SHORT_NAME = "budman"

# Prefix namespace
# BDM - Budget Domain Model
# BSM - Budget Storage Model
# BM - Budget Model (BDM synonym)
# BF - Budget Folder, contains FI folders with data files
# FI - Financial Institution
# FI_F - Financial Institution Folder
# FI_WF - Financial Institution Workflow Folder
# FI_IF -  Financial Institution Incoming Folder
# FI_CF - Financial Institution Categorized Folder
# FI_FF - Financial Institution Finalized Folder
# BMO - for Budget Model Options

# Budget Model Filesystem Path Constants 
BSM_DEFAULT_BUDGET_MODEL_FILE_NAME = THIS_APP_NAME
BSM_DEFAULT_BUDGET_MODEL_FILE_TYPE = ".jsonc"
BM_DEFAULT_BUDGET_FOLDER = "~/OneDrive/budget"
PATH = "_path"
ABS_PATH = "_abs" + PATH
WORKBOOKS = "_workbooks"

#Budget Domain Model Type Constants
DATA_OBJECT = Dict[str, Any] 
BMO_COLLECTION = DATA_OBJECT
DATA_COLLECTION = Dict[str, DATA_OBJECT] 
DATA_LIST = List[Tuple[str, DATA_OBJECT]] 
BMO_COLLECTION = DATA_COLLECTION
FI_OBJECT = DATA_OBJECT  # Financial Institution object
FI_COLLECTION = Dict[str, FI_OBJECT]
FI_DATA_OBJECT = DATA_OBJECT
FI_DATA_COLLECTION = DATA_COLLECTION
WF_OBJECT = DATA_OBJECT  # Workflow object
WF_COLLECTION = Dict[str, WF_OBJECT] 
# WF_DATA_COLLECTION workflow data collection (Dictionary key names)
# A dict for each FI, to hold the data for each workflow.
# { wf_key: WF_DATA_OBJECT, ... }
WF_DATA_COLLECTION = DATA_COLLECTION
# A dict for worklow to hold data for a specific FI
WF_DATA_OBJECT = DATA_OBJECT  # a DATA_OBJECT for a specific FI,WF
# WORKBOOK_LIST - the list of workbooks for a specific folder. 
# It is a list of WORKBOOK_ITEM tuples: (workbook_name, workbook_abs_path)
WORKBOOK_LIST = List[Tuple[str, str]] 
WORKBOOK_ITEM = Tuple[str, str]
LOADED_WORKBOOKS_LIST = List[Tuple[str, Workbook]]
BDM_WORKING_DATA = Dict[str, Any]
DATA_CONTEXT = Dict[str, Any]


# Base data attribute key names
FI_KEY = 'fi_key'
WF_KEY = 'wf_key'
WB_NAME = 'wb_name'
WB_TYPE = 'wb_type'
ALL_KEY = 'all'

# Budget Model Domain Constants
# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# BudgetModel (BM) class attribute name Constants
BDM_ID = "_bdm_id"
BDM_CONFIG_OBJECT = "_bdm_config_object"
BM_INITIALIZED = "_initialized"
BDM_FOLDER = "_budget_folder"
BDM_URL = "_bdm_url"
BDM_FI_COLLECTION = "_financial_institutions"
BDM_WF_COLLECTION = "_workflows"
BM_OPTIONS = "_options"
BM_CREATED_DATE = "_created_date"
BM_LAST_MODIFIED_DATE = "_last_modified_date"
BM_LAST_MODIFIED_BY = "_last_modified_by"
BDM_WORKING_DATA = "_wd"
BM_VALID_PROPERTIES = (BM_INITIALIZED, BDM_FOLDER, BDM_URL, 
                    BDM_FI_COLLECTION, BDM_WF_COLLECTION,  BM_OPTIONS,
                    BM_CREATED_DATE, BM_LAST_MODIFIED_DATE, 
                    BM_LAST_MODIFIED_BY, BDM_WORKING_DATA)
BSM_PERSISTED_PROPERTIES = (BDM_ID, BDM_FOLDER, 
                            BDM_FI_COLLECTION, BDM_WF_COLLECTION,  
                            BM_OPTIONS,
                            BM_CREATED_DATE, BM_LAST_MODIFIED_DATE, 
                            BM_LAST_MODIFIED_BY)

# keys used in settings.toml configuration file
BUDMAN_SETTINGS = "settings.toml"
BUDMAN_FOLDER = "budman.budget_manager_folder" 
BUDMAN_STORE = "budman.budget_manager_store" 
BUDMAN_STORE_FILETYPE = "budman.budget_manager_store_filetype"
APP_NAME = "app_name"
SHORT_APP_NAME = "short_app_name"

# Current (or last) session values.

# BM_OPTIONS Budget Model Options (BMO)Constants
BMO_LOG_CONFIG = "log_config"
BMO_LOG_LEVEL = "log_level"
BMO_LOG_FILE = "log_file"
BMO_JSON_LOG_FILE = "json_log_file_name"
BMO_EXPECTED_KEYS = (BMO_LOG_CONFIG, BMO_LOG_LEVEL, BMO_LOG_FILE,
                    BMO_JSON_LOG_FILE)

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

# Supported BM Workflow Names
BM_WF_INTAKE = "intake"
BM_WF_CATEGORIZATION = "categorization"
BM_WF_FINALIZATION = "finalization"
BM_VALID_WORKFLOWS = (BM_WF_INTAKE, BM_WF_CATEGORIZATION, BM_WF_FINALIZATION)

# WF_OBJECT workflow pseudo-Object (Dictionary key names)
WF_KEY = WF_KEY
WF_NAME = "wf_name"  # Also used as key in BM_FI workflows dictionary.
WF_FOLDER_IN = "wf_folder_in" # also used as key in BM_FI dictionary.
WF_FOLDER_OUT = "wf_folder_out" # also used as key in BM_FI dictionary.
WF_PREFIX_IN = "wf_prefix_in"
WF_PREFIX_OUT = "wf_prefix_out"
WF_WORKBOOK_MAP = "wf_workbook_map" # map of workbook names to paths
# Additional WF_OBJECT-related constants
WF_OBJECT_VALID_ATTR_KEYS = (WF_KEY, WF_NAME, 
                        WF_FOLDER_IN, WF_FOLDER_OUT,
                        WF_PREFIX_IN, WF_PREFIX_OUT, WF_WORKBOOK_MAP)
WF_FOLDER_PATH_ELEMENTS = (WF_FOLDER_IN, WF_FOLDER_OUT)

# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
BM_VALID_PATH_ELEMENTS = (BDM_FOLDER, BDM_URL,
                          FI_FOLDER, WF_FOLDER_IN, WF_FOLDER_OUT)


# WF_DATA_OBJECT is a DATA_OBJECT (Dict) for FI_WF data.
WF_WORKBOOKS_IN = "wf_workbooks_in" # workbook list for input folder
WF_WORKBOOKS_OUT ="wf_workbooks_out" # workbook list for output folder
WF_WORKBOOK_TYPES = (WF_WORKBOOKS_IN, WF_WORKBOOKS_OUT)
# WF_DATA_OBJECT_KEYS = (WF_WORKBOOKS_IN, WF_WORKBOOKS_OUT)
WF_DATA_OBJECT_VALID_ATTR_KEYS = (WF_WORKBOOKS_IN, WF_WORKBOOKS_OUT)

# The BDM_WORKING_DATA (BDWD_OBJECT) is designed to be a simple abstraction
# of the BudgetModel useful to View Models, Views, and other types of 
# upstream callers. Specifically, it is intended to serve as the 
# DATA_CONTEXT in an MVVM design pattern.
# DATA_CONTEXT is an abstract interface which can be bound to concrete
# implementations at runtime. BDWD implements the DATA_CONTEXT interface.
# At the moment, this lightweight implementation is using a dictionary with
# well-known attribute key names and data types as a "good guy" interface.
# TODO: use an abstract base classes as proper interface for DATA_CONTEXT

# BDWD_OBJECT "good guy" interface (Dictionary key names)
BDWD_INITIALIZED = "bdwd_initialized"
# Name: BDWD_INITIALIZED
# Type: bool True | False
# Desc: Indicates if the BDWD has been initialized.
BDWD_LOADED_WORKBOOKS = "bdwd_loaded_workbooks" # key name
# Name: BDWD_LOADED_WORKBOOKS
# Type: LOADED_WORKBOOKS_LIST : list of tuples
# Desc: A list of tuples of wb_name, Workbook objects loaded into BDWD.
BDWD_FI = FI_KEY
# Name: BDWD_FI
# Type: FI_KEY | "all" : str
# Desc: FI_KEY of FI loaded, or "all" if all FIs are loaded.
BDM_WORKING_DATA_VALID_ATTR_KEYS = (BDWD_INITIALIZED,
                          BDWD_LOADED_WORKBOOKS,
                          BDWD_FI)

# DATA_CONTEXT "good guy" interface (Dictionary key names)
DC_INITIALIZED = BDWD_INITIALIZED
# Name: DC_INITIALIZED
# Type: bool True | False
# Desc: Indicates if the DC has been initialized.
DC_LOADED_WORKBOOKS = BDWD_LOADED_WORKBOOKS
# Name: DC_LOADED_WORKBOOKS
# Type: LOADED_WORKBOOKS_LIST
# Desc: A list of tuples of wb_name, Workbook objects loaded into BDWD.
DC_BUDMAN_STORE = "budman_store"
# Name: DC_LOADED_WORKBOOKS
# Type: Dict
# Desc: Values loaded from Budget Manager configuration file , or "store".

DATA_CONTEXT_VALID_ATTR_KEYS = (
    DC_INITIALIZED,
    FI_KEY,
    WF_KEY,
    WB_NAME,
    WB_TYPE,
    DC_LOADED_WORKBOOKS,
    DC_BUDMAN_STORE)

BDWD_OBJECT_VALID_ATTR_KEYS = BDM_WORKING_DATA_VALID_ATTR_KEYS + DATA_CONTEXT_VALID_ATTR_KEYS

# Miscellaneous Convenience Constants
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
