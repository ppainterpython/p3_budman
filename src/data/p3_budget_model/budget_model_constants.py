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
BM_FOLDER = "_budget_folder"
BM_STORE_URI = "_budget_model_store_uri"
BM_WORKFLOWS = "_workflows"
BM_FI = "_financial_institutions"
BM_OPTIONS = "_options"
BM_CREATED_DATE = "_created_date"
BM_LAST_MODIFIED_DATE = "_last_modified_date"
BM_LAST_MODIFIED_BY = "_last_modified_by"
BM_WORKING_DATA = "_wd"
BM_EXPECTED_KEYS = (BM_FOLDER, BM_STORE_URI, BM_WORKFLOWS, BM_FI, BM_OPTIONS,
                  BM_CREATED_DATE, BM_LAST_MODIFIED_DATE, BM_LAST_MODIFIED_BY,
                  BM_WORKING_DATA)

# Supported BM Workflow Name Constants
BM_WF_INTAKE = "intake"
BM_WF_CATEGORIZATION = "categorization"
BM_WF_FINALIZATION = "finalization"
BM_VALID_WORKFLOWS = (BM_WF_INTAKE, BM_WF_CATEGORIZATION, BM_WF_FINALIZATION)

# FI pseudo-Object (Dictionary key names)
FI_KEY = "fi_key" # also used as key in BM_FI dictionary.
FI_NAME = "name"
FI_TYPE = "type"
FI_FOLDER = "fi_folder" # also used as key in BM_FI dictionary.
FI_EXPECTED_KEYS = (FI_KEY, FI_NAME, FI_TYPE, FI_FOLDER)
VALID_FI_KEYS = ("boas", "merrill")

# WF psuedo-Object (Dictionary key names)
WF_KEY = "wf_key"
WF_NAME = "name"  # Also used as key in BM_FI workfloes dictionary.
WF_FOLDER_IN = "folder_in" # also used as key in BM_FI dictionary.
WF_WORKBOOKS_IN ="workbooks_in" # list of workflow dictianries
WF_IN_PREFIX = "wf_in_prefix"
WF_FOLDER_OUT = "folder_out" # also used as key in BM_FI dictionary.
WF_WORKBOOKS_OUT ="workbooks_out" # list of workflow dictianries
WF_OUT_PREFIX = "wf_out_prefix"
WF_EXPECTED_KEYS = (WF_KEY, WF_NAME, WF_FOLDER_IN, WF_WORKBOOKS_IN,
                    WF_IN_PREFIX, WF_FOLDER_OUT, WF_WORKBOOKS_OUT,
                    WF_OUT_PREFIX)

# Budget Model Options Constants
BMO_FI_IF_PREFIX = "incoming_prefix"
BMO_FI_CF_PREFIX = "categorized_prefix"
BMO_FI_FF_PREFIX = "finalized_prefix"
BMO_LOG_CONFIG = "log_config"
BMO_LOG_LEVEL = "log_level"
BMO_LOG_FILE = "log_file"
BMO_JSON_LOG_FILE = "json_log_file_name"
BMO_EXPECTED_KEYS = (BMO_FI_IF_PREFIX, BMO_FI_CF_PREFIX, BMO_FI_FF_PREFIX,
                    BMO_LOG_CONFIG, BMO_LOG_LEVEL, BMO_LOG_FILE,
                    BMO_JSON_LOG_FILE)

# Miscellaneous Convenience Constants
P2 = "  "  # 2 space padding
P4 = "    "  # 4 space padding
P6 = "      "  # 6 space padding
P8 = "        "  # 8 space padding
P10 = "          "  # 10 space padding
