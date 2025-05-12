from typing import Dict, List, Tuple


THIS_APP_NAME = "p3_budget_model"

# Prefix namespace
# BDM - Budget Model Domain
# BM - Budget Model
# BF - Budget Folder, contains FI folders with data files
# FI - Financial Institution
# FI_F - Financial Institution Folder
# FI_WF - Financial Institution Workflow Folder
# FI_IF -  Financial Institution Incoming Folder
# FI_CF - Financial Institution Categorized Folder
# FI_FF - Financial Institution Finalized Folder
# BMO - for Budget Model Options
# BSM - Budget Model Storage Sub-Domain

# Budget Model Filesystem Path Constants 
BSM_DEFAULT_BUDGET_MODEL_FILE_NAME = "budget_model.jsonc"
BM_DEFAULT_BUDGET_FOLDER = "~/OneDrive/budget"
PATH = "_path"
ABS_PATH = "_abs_" + PATH
WORKBOOKS = "_workbooks"

# Budget Model Domain Constants
# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# BudgetModel (BM) class attribute name Constants
BM_INITIALIZED = "_initialized"
BM_FOLDER = "_budget_folder"
BM_STORE = "_budget_model_store"
BM_FI_COLLECTION = "_financial_institutions"
BM_WF_COLLECTION = "_workflows"
BM_OPTIONS = "_options"
BM_CREATED_DATE = "_created_date"
BM_LAST_MODIFIED_DATE = "_last_modified_date"
BM_LAST_MODIFIED_BY = "_last_modified_by"
BM_WORKING_DATA = "_wd"
BM_VALID_PROPERTIES = (BM_INITIALIZED, BM_FOLDER, BM_STORE, 
                    BM_FI_COLLECTION, BM_WF_COLLECTION,  BM_OPTIONS,
                    BM_CREATED_DATE, BM_LAST_MODIFIED_DATE, 
                    BM_LAST_MODIFIED_BY, BM_WORKING_DATA)

# BM_OPTIONS Budget Model Options (BMO)Constants
BMO_LOG_CONFIG = "log_config"
BMO_LOG_LEVEL = "log_level"
BMO_LOG_FILE = "log_file"
BMO_JSON_LOG_FILE = "json_log_file_name"
BMO_EXPECTED_KEYS = (BMO_LOG_CONFIG, BMO_LOG_LEVEL, BMO_LOG_FILE,
                    BMO_JSON_LOG_FILE)

# FI_OBJECT financial institution pseudo-Object (Dictionary key names)
FI_KEY = "fi_key" 
FI_NAME = "fi_name"
FI_TYPE = "fi_type"
FI_FOLDER = "fi_folder" 
FI_WORKFLOW_DATA = "fi_workflow_data" 
# Additional FI_OBJECT-related constants
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
WF_OBJECT_VALID_KEYS = (WF_KEY, WF_NAME, 
                        WF_FOLDER_IN, WF_FOLDER_OUT,
                        WF_PREFIX_IN, WF_PREFIX_OUT, WF_WORKBOOK_MAP)
WF_FOLDER_PATH_ELEMENTS = (WF_FOLDER_IN, WF_FOLDER_OUT)

# Some data values are used in conjunction with Path objects,
# as elements of a pathname, such as folders and file names.
# All Path-related data values are treated as pseudo-Objects and have
# methods to construct, manipulate, and resolve Path objects and handle
# the various string representations of the Path objects.
BM_VALID_PATH_ELEMENTS = (BM_FOLDER, BM_STORE,
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
WORKBOOK_LIST = List # pseudo-type of object
WORKBOOK_ITEM = Tuple # pseudo-type of object

# Key values used for transient working_data
BDWD_INITIALIZED = "bdwd_initialized"
#    Key Name: BDWD_INITIIALIZED
#   Key Value: bool True | False
# Description: Indicates if the BDWB has been initialized.
BDWD_LOADED_WORKBOOKS = "bdwd_loaded_workbooks"
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


# Miscellaneous Convenience Constants
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
