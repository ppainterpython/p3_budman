THIS_APP_NAME = "p3ExcelBudget"

# Well-known column names for banking transactions workbooks.
BUDGET_CATEGORY_COL = "Budget Category"

# Budget Model Constants                        # BT prefix for Budget Transactions
ABS_PATH = "_abs_path"                          # suffix Path absolute path value
ABS_PATH_STR = ABS_PATH + "_str"                # suffix Path absolute path str repr
WORKBOOKS = "_workbooks"                        # suffix Workbooks

# Parent folder for banking transactions (BT) data.
BT_BUDGET_FOLDER = "budget_folder"              # BF prefix
BT_BUDGET_FOLDER_ABS_PATH_STR = BT_BUDGET_FOLDER + ABS_PATH_STR # BF prefix
BT_BUDGET_FOLDER_ABS_PATH = BT_BUDGET_FOLDER + ABS_PATH # BF prefix

# Information about each financial institution (FI).
BT_FINANCIAL_INSTITUTIONS = "institutions"      # FI prefix Financial Institutions
FI_NAME = "name"                                # FI prefix
FI_TYPE = "type"                                # FI prefix
FI_FOLDER = "folder"                            # FI prefix
FI_FOLDER_ABS_PATH_STR = FI_FOLDER + ABS_PATH_STR  # FI prefix
FI_FOLDER_ABS_PATH = FI_FOLDER + ABS_PATH          # FI prefix

# sub-folder names for each financial institution (FI).
IF_INCOMING_FOLER = "incoming_folder"           # IF prefix
IF_INCOMING_FOLER_ABS_PATH_STR = IF_INCOMING_FOLER + ABS_PATH_STR # IF prefix
IF_INCOMING_FOLER_ABS_PATH = IF_INCOMING_FOLER + ABS_PATH # IF prefix
IF_INCOMING_FOLDER_WORKBOOKS = IF_INCOMING_FOLER + WORKBOOKS # IF prefix

CF_CATEGORAIZED_FOLDER = "categorized_folder"   # CF prefix
CF_CATEGORAIZED_FOLDER_ABS_PATH_STR = CF_CATEGORAIZED_FOLDER + ABS_PATH_STR # CF prefix
CF_CATEGORAIZED_FOLDER_ABS_PATH = CF_CATEGORAIZED_FOLDER + ABS_PATH # CF prefix
CF_CATEGORAIZED_FOLDER_WORKBOOKS = CF_CATEGORAIZED_FOLDER + WORKBOOKS # CF prefix0

PF_PROCESSED_FOLDER = "processed_folder"        # PF prefix
PF_PROCESSED_FOLDER_ABS_PATH_STR = PF_PROCESSED_FOLDER + ABS_PATH_STR # PF prefix
PF_PROCESSED_FOLDER_ABS_PATH = PF_PROCESSED_FOLDER + ABS_PATH # PF prefix
PF_PROCESSED_FOLDER_WORKBOOKS = PF_PROCESSED_FOLDER + WORKBOOKS # PF prefix

# Budget Model Options Constants
BMO_OPTIONS = "options"
BMO_INCOMING_PREFIX = "incoming_prefix"
BMO_CATEGORIZED_PREFIX = "categorized_prefix"
BMO_PROCESSED_PREFIX = "processed_prefix"
BMO_LOG_CONFIG = "log_config"
BMO_LOG_LEVEL = "log_level"
BMO_LOG_FILE = "log_file"
BMO_JSON_LOG_FILE = "json_log_file_name"
