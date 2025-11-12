#region budman_app_constants.py symbol constants for Types and Values.
""" constants used for budman_app"""
#endregion budman_app_constants.py symbol constants for Types and Values.
# ---------------------------------------------------------------------------- +
# Budget Manager (BudMan) application environment variable constants
BUDMAN_FOLDER_ENV_VAR = "ROOT_PATH_FOR_BUDMAN_FOLDER"
BUDMAN_SETTINGS_FILES_ENV_VAR = "SETTINGS_FILE_FOR_BUDMAN"
# ---------------------------------------------------------------------------- +
# Application Constants
THIS_APP_NAME = "p3_budget_manager" 
THIS_APP_SHORT_NAME = "budman" 
THIS_APP_VERSION = "0.3.0"
THIS_APP_AUTHOR = "Paul Painter"
THIS_APP_COPYRIGHT = "2025 Paul Painter"
# ---------------------------------------------------------------------------- +
# BUDMAN_SETTINGS property name constants used in settings.toml configuration file
BUDMAN_SETTINGS = "budman_settings.toml"
# Settings file keyname constants

# root level
SHORT_APP_NAME = "short_app_name"
APP_NAME = "app_name"

# [budman] Table
BDM_FOLDER = "budman.bdm_folder" 
BDM_STORE_FILENAME = "budman.store_filename" 
BDM_STORE_FILETYPE = "budman.store_filetype"
BDM_STORE_URL = "budman.store_url"  
BUDMAN_DEFAULT_FI = "budman.default_fi"
BUDMAN_DEFAULT_WORKFLOW = "budman.default_workflow"
BUDMAN_DEFAULT_WORKFLOW_PURPOSE = "budman.default_workflow_purpose"
BUDMAN_DEFAULT_WORKBOOK_TYPE = "budman.default_workbook_type"
BUDMAN_CMD_HISTORY_FILENAME = "budman.cmd_history_filename"
# [category_catalog] Table
CATEGORY_CATALOG = "category_catalog"
TXN_CATEGORIES_WORKBOOK_FULL_FILENAME = "txn_categories_workbook_full_filename"
CATEGORY_MAP_WORKBOOK_FULL_FILENAME = "category_map_workbook_full_filename"

# [logging] Table
LOGGING_DEFAULT_HANDLER = "logging.default_handler"
LOGGING_DEFAULT_LEVEL = "logging.default_level"
LOGGING_CONFIG_FILENAME = "logging.config_filename"
