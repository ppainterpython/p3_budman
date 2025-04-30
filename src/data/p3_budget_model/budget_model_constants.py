THIS_APP_NAME = "p3_budget_model"

# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# Budget Model Constants                           # BM prefix
BM_DEFAULT_BUDGET_MODEL_FILE_NAME = "budget_model.json" # BM prefix
BM_DEFAULT_BUDGET_FOLDER = "~/OneDrive/budget"     # BM prefix
ABS_PATH = "_abs_path"                             # suffix Path absolute path value
ABS_PATH_STR = ABS_PATH + "_str"                   # suffix Path absolute path str repr
WORKBOOKS = "_workbooks"                           # suffix Workbooks

# Prefix namespace
# BM prefix for Budget Model
# BF prefix for Budget Folder
# FI prefix for Financial Institution
# FI_IF prefix for Financial Institution Incoming Folder
# FI_CF prefix for Financial Institution Categorized Folder
# FI_PF prefix for Financial Institution Processed Folder
# BMO prefix for Budget Model Options

# Budget Model (BM) class attribute name Constants
BM_INITIALIZED = "_initialized"                     # BM prefix
BM_BF = "_budget_folder"                            # BM_BF prefix
BM_STORE_URI = "_budget_model_store_uri"            # BM prefix
BM_FI = "_financial_institutions"                   # FI prefix
BM_OPTIONS = "_options"                             # BM prefix
BM_CREATED_DATE = "_created_date"                   # BM prefix         
BM_LAST_MODIFIED_DATE = "_last_modified_date"       # BM prefix
BM_LAST_MODIFIED_BY = "_last_modified_by"           # BM prefix
BM_WORKING_DATA = "_wd"                             # BM prefix

# Information in each financial institution (FI) dictionary object.
FI_NAME = "name"                                   # FI prefix
FI_TYPE = "type"                                   # FI prefix
FI_FOLDER = "fi_folder"                            # FI prefix

# sub-folder names for each financial institution (FI).
FI_IF = "incoming_folder"                          # FI_IF prefix
FI_IF_WORKBOOKS = FI_IF + WORKBOOKS                # FI_IF prefix

FI_CF = "categorized_folder"                       # FI_CF prefix
FI_CF_WORKBOOKS = FI_CF + WORKBOOKS                # FI_CF prefix0

FI_PF = "processed_folder"                         # FI_PF prefix
FI_PF_WORKBOOKS = FI_PF + WORKBOOKS                # FI_PF prefix

# Budget Model Options Constants
BMO_FI_IF_PREFIX = "incoming_prefix"               # BMO prefix
BMO_FI_CF_PREFIX = "categorized_prefix"
BMO_FI_PF_PREFIX = "processed_prefix"
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
