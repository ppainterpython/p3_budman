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
    "WORKBOOK_LIST",
    "WORKBOOK_ITEM",
    "LOADED_WORKBOOK_LIST",
    "DATA_CONTEXT",
    "BDM_WORKING_DATA_OBJECT",
    "BDM_STORE",
    "BDM_CONFIG",
    # "MODEL_OBJECT",
    "DATA_OBJECT",
    "BMO_COLLECTION",
    "DATA_COLLECTION",
    "DATA_LIST",
    "BMO_COLLECTION",
    "FI_OBJECT",
    "FI_COLLECTION",
    "FI_DATA_OBJECT",
    "FI_DATA_COLLECTION",
    "WF_OBJECT",
    "WF_COLLECTION",
    "WF_DATA_COLLECTION",
    "WF_DATA_OBJECT",
    "BDM_WORKING_DATA_OBJECT",
    # Budget Model Filesystem Path default constants
    "PATH",
    "ABS_PATH",
    "WORKBOOKS",
    # Attribute key name constants
    "FI_KEY",
    "WF_KEY",
    "WB_TYPE",
    "WB_NAME",
    "WB_REF",
    "WB_INFO",
    # Attribute value constants
    "WB_INFO_LEVEL_INFO",
    "WB_INFO_LEVEL_VERBOSE",
    "WB_INFO_VALID_LEVELS",
    "RELOAD_TARGET",
    "CATEGORY_MAP",
    "ALL_KEY",
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
    "BDM_VALID_PROPERTIES",
    "BSM_PERSISTED_PROPERTIES",
    "BSM_VALID_BDM_STORE_FILETYPES",
    # Well-known column names for banking transactions workbooks.
    "BUDGET_CATEGORY_COL",
    # BDM_OPTIONS Budget Model Options (BMO)Constants
    "BMO_LOG_CONFIG",
    "BMO_LOG_LEVEL",
    "BMO_LOG_FILE",
    "BMO_JSON_LOG_FILE",
    "BMO_EXPECTED_KEYS",
    # FI_OBJECT financial institution pseudo-Object (Dictionary key names)
    "FI_KEY",
    "FI_NAME",
    "FI_TYPE",
    "FI_FOLDER",
    "FI_DATA_COLLECTION",
    # Additional FI_DATA-related constants
    "FI_OBJECT_VALID_ATTR_KEYS",
    "VALID_FI_KEYS",
    "VALID_FI_TYPES",
    "BDM_FI_NAMES",
    # Supported BM Workflow Names
    "BDM_WF_INTAKE",
    "BDM_WF_CATEGORIZATION",
    "BDM_WF_FINALIZATION",
    "BDM_VALID_WORKFLOWS",
    # WF_OBJECT workflow definition object (Dictionary key names)
    "WF_KEY",
    "WF_NAME",
    "WF_INPUT_FOLDER",
    "WF_WORKING_FOLDER",
    "WF_OUTPUT_FOLDER",
    "WF_PREFIX_IN",
    "WF_PREFIX_OUT",
    "WF_TYPE_MAP",
    "WF_OBJECT_VALID_ATTR_KEYS",
    "WF_FOLDER_PATH_ELEMENTS",
    "BDM_VALID_PATH_ELEMENTS",
    # WF_DATA_OBJECT is a subclass of DATA_OBJECT
    "WF_INPUT",
    "WF_WORKING",
    "WF_OUTPUT",
    "WF_WORKBOOK_TYPES",
    "WF_DATA_OBJECT_VALID_ATTR_KEYS",
    # BDM_WORKING_DATA
    "BDMWD_INITIALIZED",
    "BDMWD_FI_KEY",
    "BDMWD_WF_KEY",
    "BDMWD_WB_TYPE",
    "BDMWD_WB_NAME",
    "BDMWD_WORKBOOKS",
    "BDMWD_LOADED_WORKBOOKS",
    "BDMWD_BDM_STORE",
    "BDM_WORKING_DATA_VALID_ATTR_KEYS",
    # DATA_CONTEXT "good guy" interface (Dictionary key names)
    "DC_INITIALIZED",
    "DC_FI_KEY",
    "DC_WF_KEY",
    "DC_WB_TYPE",
    "DC_WB_NAME",
    "DC_WORKBOOKS",
    "DC_LOADED_WORKBOOKS",
    "DC_BDM_STORE",
    "BDMWD_OBJECT_VALID_ATTR_KEYS",
    "BUDMAN_DEFAULT_WORKFLOW_VALUE",
    "BUDMAN_DEFAULT_WORKBOOK_TYPE_VALUE",
    "P2",
    "P4",
    "P6",
    "P8",
    "P10"
]
