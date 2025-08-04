"""
Budget Manager Namespace Package

"""
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_namespace"
__description__ = "Budget Manager Domain Model Namespace."
__license__ = "MIT"

# Data Context abstract interface
from .bdm_singleton_meta import BDMSingletonMeta
from .design_language_namespace import *

__all__ = [
    # Metaclass for Singleton Pattern
    "BDMSingletonMeta",
    # Type Alias Constants
    "DATA_OBJECT_TYPE",
    "DATA_TUPLE_TYPE",
    "DATA_COLLECTION_TYPE",
    "DATA_LIST_TYPE",
    # Base Types - not model-aware
    "BUDMAN_RESULT_TYPE",  
    "WORKBOOK_DATA_COLLECTION_TYPE",
    "WORKBOOK_ITEM_TYPE",
    "WORKBOOK_OBJECT_TYPE", 
    "WORKBOOK_CONTENT_TYPE",  
    "LOADED_WORKBOOK_COLLECTION_TYPE",
    "LOADED_WORKBOOK_ITEM_TYPE",
    "DATA_CONTEXT_TYPE",
    "BDM_STORE_TYPE",
    "BDM_CONFIG_TYPE",
    "BDM_CHECK_REGISTER_TYPE",
    "EXCEL_TXNS_WORKBOOK_TYPE",
    "EXCEL_TXNS_WORKSHEET_TYPE",
    # MODEL_OBJECT-related types,
    "BDM_OPTIONS_TYPE",
    "FI_OBJECT_TYPE",
    "FI_COLLECTION_TYPE",
    "WF_OBJECT_TYPE",
    "WF_COLLECTION_TYPE",
    "WF_FOLDER_CONFIG_TYPE",
    "WF_FOLDER_CONFIG_LIST_TYPE",
    "FI_WF_FOLDER_CONFIG_COLLECTION_TYPE",
    # Valid data store file types for the Budget Storage Model (BSM).
    "BSM_DATA_COLLECTION_CSV_STORE_FILETYPES",
    # Budget Model Filesystem Path default constants
    "PATH",
    "ABS_PATH",
    "WORKBOOKS",
    # Attribute key name constants
    "FI_KEY",
    "WF_KEY",
    "WF_PURPOSE", 
    "WB_TYPE",
    "WB_NAME",
    "WB_URL",
    "WB_ID",
    "WB_CONTENT",
    "WB_CATEGORY_COLLECTION",
    "WB_CATEGORY_COUNT",
    #Budget Domain Model Class Property Name constants
    "BDM_ID",
    "BDM_STORE_OBJECT",
    "BDM_CONFIG_OBJECT",
    "BDM_INITIALIZED",
    "BDM_FOLDER",
    "BDM_FILENAME",
    "BDM_FILETYPE",
    "BDM_URL",
    "BDM_FI_COLLECTION",
    "BDM_WF_COLLECTION",
    "BDM_OPTIONS",
    "BDM_CREATED_DATE",
    "BDM_LAST_MODIFIED_DATE",
    "BDM_LAST_MODIFIED_BY",
    "BDM_WORKING_DATA",
    "BDM_DATA_CONTEXT",
    "VALID_BDM_PROPERTIES",
    "BSM_PERSISTED_PROPERTIES",
    "VALID_BSM_BDM_STORE_FILETYPES",
    # Well-known column names for banking transactions workbooks.
    "BUDGET_CATEGORY_COL",
    # BDM_OPTIONS Budget Model Options (BMO)Constants
    "BDMO_LOG_CONFIG",
    "BDMO_LOG_LEVEL",
    "BDMO_LOG_FILE",
    "BDMO_JSON_LOG_FILE",
    "BDMO_EXPECTED_KEYS",
    # FI_OBJECT financial institution pseudo-Object (Dictionary key names)
    "FI_KEY",
    "FI_NAME",
    "FI_TYPE",
    "FI_FOLDER",
    "FI_WORKBOOK_DATA_COLLECTION", 
    # Additional FI_DATA-related constants
    "VALID_FI_OBJECT_ATTR_KEYS",
    "VALID_FI_KEYS",
    "VALID_FI_TYPES",
    "BDM_FI_NAMES",
    # Supported BM Workflow Names
    "EXAMPLE_BDM_WF_INTAKE",
    "EXAMPLE_BDM_WF_CATEGORIZATION",
    "EXAMPLE_BDM_WF_BUDGET",
    "VALID_BDM_WORKFLOWS",
    # WF_OBJECT workflow definition object (Dictionary key names)
    "WF_KEY",
    "WF_NAME",
    "WF_INPUT_FOLDER",
    "WF_WORKING_FOLDER",
    "WF_OUTPUT_FOLDER",
    "WF_PREFIX_IN",
    "WF_PREFIX_WORKING",
    "WF_PREFIX_OUT",
    "WF_PURPOSE_FOLDER_MAP",
    "VALID_WF_OBJECT_ATTR_KEYS",
    "WF_FOLDER_PATH_ELEMENTS",
    "WF_FOLDER",
    "WF_FOLDER_ID",
    "VALID_BDM_PATH_ELEMENTS",
    # Workflow Purpose 
    "WF_INPUT",
    "WF_WORKING",
    "WF_OUTPUT",
    "VALID_WF_PURPOSE_VALUES",
    # New Workbook Type constants
    "WB_TYPE_BDM_STORE",
    "WB_TYPE_BDM_CONFIG",
    "WB_TYPE_TXN_REGISTER",
    "WB_TYPE_EXCEL_TXNS",
    "WB_TYPE_BUDGET",
    "VALID_WB_TYPE_VALUES",
    "WB_URL",
    # Workbook File Type constants
    "WB_FILETYPE_CSV",
    "WB_FILETYPE_XLSX",
    "WB_FILETYPE_JSON",
    "WB_FILETYPE_JSONC",
    "WB_FILETYPE_TEXT",
    "WB_FILETYPE_MAP",
    "VALID_WB_FILETYPES",
    # DATA_CONTEXT "good guy" interface (Dictionary key names)
    "DC_INITIALIZED",
    "DC_FI_KEY",
    "DC_WF_KEY",
    "DC_WF_PURPOSE",
    "DC_WB_TYPE",
    "DC_WB_NAME",
    "DC_LOADED_WORKBOOKS",
    "DC_BDM_STORE",
    "BUDMAN_DEFAULT_WORKFLOW_VALUE",
    "BUDMAN_DEFAULT_WORKBOOK_TYPE_VALUE",
    # Miscellaneous constants
    "BUDMAN_WIDTH",
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "P6",
    "P7",
    "P8",
    "P9",
    "P10"
]
