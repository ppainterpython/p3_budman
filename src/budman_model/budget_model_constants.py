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

# Common Key Names
ALL_KEY = 'all'
WB_TYPE = "wb_type"
WB_NAME = "wb_name"

# Budget Model Domain Constants
# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# BudgetModel (BM) class attribute name Constants
BDM_ID = "_bdm_id"
BDM_CONFIG_OBJECT = "_bdm_config_object"
BM_INITIALIZED = "_initialized"
BM_FOLDER = "_budget_folder"
BDM_URL = "_bdm_url"
BM_FI_COLLECTION = "_financial_institutions"
BM_WF_COLLECTION = "_workflows"
BM_OPTIONS = "_options"
BM_CREATED_DATE = "_created_date"
BM_LAST_MODIFIED_DATE = "_last_modified_date"
BM_LAST_MODIFIED_BY = "_last_modified_by"
BDM_WORKING_DATA = "_wd"
BM_VALID_PROPERTIES = (BM_INITIALIZED, BM_FOLDER, BDM_URL, 
                    BM_FI_COLLECTION, BM_WF_COLLECTION,  BM_OPTIONS,
                    BM_CREATED_DATE, BM_LAST_MODIFIED_DATE, 
                    BM_LAST_MODIFIED_BY, BDM_WORKING_DATA)
BSM_PERSISTED_PROPERTIES = (BDM_ID, BM_FOLDER, 
                            BM_FI_COLLECTION, BM_WF_COLLECTION,  
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
BMO_COLLECTION = Dict
BMO_EXPECTED_KEYS = (BMO_LOG_CONFIG, BMO_LOG_LEVEL, BMO_LOG_FILE,
                    BMO_JSON_LOG_FILE)

# FI_OBJECT financial institution pseudo-Object (Dictionary key names)
FI_KEY = "fi_key" 
FI_NAME = "fi_name"
FI_TYPE = "fi_type"
FI_FOLDER = "fi_folder" 
FI_WORKFLOW_DATA = "fi_workflow_data" 
# Additional FI_OBJECT-related constants
FI_COLLECTION = Dict
FI_OBJECT = Dict #"fi_object"  # pseudo-type
FI_OBJECT_VALID_KEYS = (FI_KEY, FI_NAME, FI_TYPE, FI_FOLDER, FI_WORKFLOW_DATA)
VALID_FI_KEYS = ("boa", "merrill")
VALID_FI_TYPES = ("bank", "brokerage")
BDM_FI_NAMES = ("Bank of America", "Merrill Lynch")

# Supported BM Workflow Names
BM_WF_INTAKE = "intake"
BM_WF_CATEGORIZATION = "categorization"
BM_WF_FINALIZATION = "finalization"
BM_VALID_WORKFLOWS = (BM_WF_INTAKE, BM_WF_CATEGORIZATION, BM_WF_FINALIZATION)

# WF_OBJECT workflow psuedo-Object (Dictionary key names)
WF_KEY = "wf_key"
WF_NAME = "wf_name"  # Also used as key in BM_FI workfloes dictionary.
WF_FOLDER_IN = "wf_folder_in" # also used as key in BM_FI dictionary.
WF_FOLDER_OUT = "wf_folder_out" # also used as key in BM_FI dictionary.
WF_PREFIX_IN = "wf_prefix_in"
WF_PREFIX_OUT = "wf_prefix_out"
WF_WORKBOOK_MAP = "wf_workbook_map" # map of workbook names to paths
# Additional WF_OBJECT-related constants
WF_OBJECT = Dict  # pseudo-type
WF_COLLECTION = Dict
WF_OBJECT_VALID_KEYS = (WF_KEY, WF_NAME, 
                        WF_FOLDER_IN, WF_FOLDER_OUT,
                        WF_PREFIX_IN, WF_PREFIX_OUT, WF_WORKBOOK_MAP)
WF_FOLDER_PATH_ELEMENTS = (WF_FOLDER_IN, WF_FOLDER_OUT)

# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
BM_VALID_PATH_ELEMENTS = (BM_FOLDER, BDM_URL,
                          FI_FOLDER, WF_FOLDER_IN, WF_FOLDER_OUT)

# WF_DATA_COLLECTION workflow data collection (Dictionary key names)
# A dict for each FI, to hold the data for each workflow.
# { wf_key: WF_DATA_OBJECT, ... }
WF_DATA_COLLECTION = Dict #"wf_data_collection" # pseudo-type of object

# WF_DATA_OBJECT workflow data object (Dictionary key names)
# A dict for worflow to hold data for a specific FI
WF_DATA_OBJECT = Dict # pseudo-type of object
WF_WORKBOOKS_IN = "wf_workbooks_in" # workbook list for input folder
WF_WORKBOOKS_OUT ="wf_workbooks_out" # workbook list for output folder
WF_WORKBOOK_TYPES = (WF_WORKBOOKS_IN, WF_WORKBOOKS_OUT)
WF_DATA_OBJECT_KEYS = (WF_WORKBOOKS_IN, WF_WORKBOOKS_OUT)
WF_DATA_OBJECT_VALID_KEYS = (WF_WORKBOOKS_IN, WF_WORKBOOKS_OUT)

# WORKBOOK_LIST - the list of workbooks for a specific folder. It is a list
# of WORKBOOK_ITEM tuples: (workbook_name, workbook_abs_path)
WORKBOOK_LIST = List[Tuple[str, str]] # pseudo-type of object
WORKBOOK_ITEM = Tuple # pseudo-type of object
LOADED_WORKBOOKS_LIST = List[Tuple[str, Workbook]]

# The BDM_WORKING_DATA dictionary also serves as the
# DATA_CONTEXT for the BudgetModel. So, it has key names that are
# generic. 
# TODO: really need to use an abstract interface for DATA_CONTEXT
BDM_WORING_DATA = Dict[str, Any]
DATA_CONTEXT = Dict[str, Any]
BDWD_INITIALIZED = "bdwd_initialized"
#    Key Name: BDWD_INITIIALIZED
#   Key Value: bool True | False
# Description: Indicates if the BDWB has been initialized.
BDWD_LOADED_WORKBOOKS = "bdwd_loaded_workbooks" # key name
DC_LOADED_WORKBOOKS = BDWD_LOADED_WORKBOOKS
#    Key Name: BDWD_LOADED_WORKBOOKS
#   Key Value: list[Tuple(wb_name, Workbook object)]
# Description: A list of tuples of wb_name, Workbook objects loaded into BDWD.
BDWD_FI = "bdwd_fi"
#    Key Name: BDWD_FI
#   Key Value: fi_key | "all"
# Description: fi_key of FI loaded, or "all" if all FIs are loaded.
#              To load a single FI, use bdwd_FI_load(fi_key) method.
BDWD_WORKING_DATA_KEYS = (BDWD_INITIALIZED,
                          BDWD_LOADED_WORKBOOKS,
                          BDWD_FI)

DC_BUDMAN_STORE = "budman_store"
DATA_CONTEXT_KEYS = (
    FI_KEY,
    WF_KEY,
    WB_NAME,
    WB_TYPE,
    BDWD_LOADED_WORKBOOKS,
    DC_BUDMAN_STORE)


# Miscellaneous Convenience Constants
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
