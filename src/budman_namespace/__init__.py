"""
Budget Manager Data Context Interface Package

"""
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budget_manager_domain_model"
__description__ = "Budget Manager Domain Model Namespace."
__license__ = "MIT"

# Data Context abstract interface
from .design_language_namespace import *
__all__ = [
    "design_language_namespace",
    "THIS_APP_NAME",
    "THIS_APP_SHORT_NAME",
    "THIS_APP_VERSION",
    "THIS_APP_AUTHOR",
    "THIS_APP_COPYRIGHT",
    "ALL_KEY",
    "FI_KEY",
    "WF_KEY",
    "WB_TYPE",
    "WB_NAME",
    "WB_REF",
    "WB_INFO_LEVEL_INFO",
    "WB_INFO_LEVEL_VERBOSE",
    "WB_INFO_VALID_LEVELS",
    "RELOAD_TARGET",
    "CATEGORY_MAP",
    "WORKBOOK_LIST",
    "WORKBOOK_ITEM",
    "LOADED_WORKBOOK_LIST",
    "BDM_WORKING_DATA_OBJECT",
    "DATA_CONTEXT",
    "MODEL_OBJECT",
    "P2",
    "P4",
    "P6",
    "P8",
    "P10",
]
