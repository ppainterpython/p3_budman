THIS_APP_NAME = "p3_Budget_Model"

# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# Budget Model Constants                           # BM prefix for Budget Model
BM_DEFAULT_FILE_NAME = "budget_model.json"         # BM prefix
ABS_PATH = "_abs_path"                             # suffix Path absolute path value
ABS_PATH_STR = ABS_PATH + "_str"                   # suffix Path absolute path str repr
WORKBOOKS = "_workbooks"                           # suffix Workbooks

# Budget Model (BM) attribute name Constants
BM_INITIALIZED = "initialized"                     # BM prefix
BM_BF = "budget_folder"                            # BM_BF prefix
BM_FI = "financial_institutions"                   # FI prefix
BM_STORE_URI = "budget_store_uri"                  # BM prefix

BM_BF_ABS_PATH_STR = BM_BF   # BM prefix
BM_BF_ABS_PATH = BM_BF + ABS_PATH # BF prefix

# Information about each financial institution (FI).
FI_NAME = "name"                                   # FI prefix
FI_TYPE = "type"                                   # FI prefix
FI_FOLDER = "fi_folder"                      # FI prefix
FI_FOLDER_ABS_PATH_STR = FI_FOLDER + ABS_PATH_STR  # FI prefix
FI_FOLDER_ABS_PATH = FI_FOLDER + ABS_PATH          # FI prefix

# sub-folder names for each financial institution (FI).
FI_IF = "incoming_folder"           # FI_IF prefix
FI_IF_ABS_PATH_STR = FI_IF + ABS_PATH_STR # FI_IF prefix
FI_IF_ABS_PATH = FI_IF + ABS_PATH # FI_IF prefix
FI_IF_WORKBOOKS = FI_IF + WORKBOOKS # FI_IF prefix

FI_CF = "categorized_folder"                       # FI_CF prefix
FI_CF_ABS_PATH_STR = FI_CF + ABS_PATH_STR          # FI_CF prefix
FI_CF_ABS_PATH = FI_CF + ABS_PATH                  # FI_CF prefix
FI_CF_WORKBOOKS = FI_CF + WORKBOOKS                # FI_CF prefix0

FI_PF = "processed_folder"                         # FI_PF prefix
FI_PF_ABS_PATH_STR = FI_PF + ABS_PATH_STR          # FI_PF prefix
FI_PF_ABS_PATH = FI_PF + ABS_PATH                  # FI_PF prefix
FI_PF_WORKBOOKS = FI_PF + WORKBOOKS                # FI_PF prefix

# Budget Model Options Constants
BM_OPTIONS = "options"                             # BMO prefix
BMO_FI_IF_PREFIX = "incoming_prefix"
BMO_FI_CF_PREFIX = "categorized_prefix"
BMO_FI_PF_PREFIX = "processed_prefix"
BMO_LOG_CONFIG = "log_config"
BMO_LOG_LEVEL = "log_level"
BMO_LOG_FILE = "log_file"
BMO_JSON_LOG_FILE = "json_log_file_name"
