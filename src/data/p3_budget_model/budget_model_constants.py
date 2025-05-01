THIS_APP_NAME = "p3_budget_model"

# Prefix namespace
# BMD - Budget Model Domain
# BM - Budget Model
# BF - Budget Folder, contains FI folders with data files
# FI - Financial Institution
# FI_F - Financial Institution Folder
# FI_WF - Financial Institution Workflow Folder
# FI_IF -  Financial Institution Incoming Folder
# FI_CF - Financial Institution Categorized Folder
# FI_FF - Financial Institution Finalized Folder
# BMO - for Budget Model Options
# BMS - Budget Model Storage Sub-Domain

# Budget Model Filesystem Path Constants 
BMS_DEFAULT_BUDGET_MODEL_FILE_NAME = "budget_model.json"
BM_DEFAULT_BUDGET_FOLDER = "~/OneDrive/budget"
PATH = "_path"
ABS_PATH = "_abs_" + PATH
WORKBOOKS = "_workbooks"

# Budget Model Domain Constants
# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# Budget Model (BM) class attribute name Constants
BM_INITIALIZED = "_initialized"
BM_BF = "_budget_folder"
BM_STORE_URI = "_budget_model_store_uri"
BM_SUPPORTED_WORKFLOWS = "_supported_workflows"
BM_FI = "_financial_institutions"
BM_OPTIONS = "_options"
BM_CREATED_DATE = "_created_date"
BM_LAST_MODIFIED_DATE = "_last_modified_date"
BM_LAST_MODIFIED_BY = "_last_modified_by"
BM_WORKING_DATA = "_wd"

# Supported BM Workflow Name Constants
BM_WF_INTAKE = "intake"
BM_WF_CATEGORIZATION = "categorization"
BM_WF_FINALIZATION = "finalization"
BM_VALID_WORKFLOWS = (BM_WF_INTAKE, BM_WF_CATEGORIZATION, BM_WF_FINALIZATION)

# FI Dictionary key names.
FI_NAME = "name"
FI_TYPE = "type"
FI_FOLDER = "fi_folder" # also used as key in BM_FI dictionary.
FI_WORKFLOWS ="workflows" # list of workflow dictianries
FI_WF_KEY_SUFFIX = "_folder"

# WF Dictionary key names.
WF_NAME = "name"  # Also used as key in BM_FI workfloes dictionary.
WF_FOLDER = "folder" # also used as key in BM_FI dictionary.
WF_WORKBOOKS ="workbooks" # list of workflow dictianries

# sub-folder names for each financial institution (FI).
FI_IF = BM_WF_INTAKE + FI_WF_KEY_SUFFIX
FI_IF_WORKBOOKS = FI_IF + WORKBOOKS

FI_CF = BM_WF_CATEGORIZATION + FI_WF_KEY_SUFFIX
FI_CF_WORKBOOKS = FI_CF + WORKBOOKS

FI_FF = BM_WF_FINALIZATION + FI_WF_KEY_SUFFIX
FI_FF_WORKBOOKS = FI_FF + WORKBOOKS

# Budget Model Options Constants
BMO_FI_IF_PREFIX = "incoming_prefix"
BMO_FI_CF_PREFIX = "categorized_prefix"
BMO_FI_FF_PREFIX = "finalized_prefix"
BMO_LOG_CONFIG = "log_config"
BMO_LOG_LEVEL = "log_level"
BMO_LOG_FILE = "log_file"
BMO_JSON_LOG_FILE = "json_log_file_name"

# Miscellaneous Convenience Constants
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
