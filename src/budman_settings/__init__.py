"""
Budget Manager - p3_budman package

Budget Manager (budman) follows a budgeting domain model based on 
transactions from financial institutions (FI). This package 
has the functionality to intake transactions from a financial institution (FI) 
and process them into a budget model. The package is designed to work with 
Excel workbooks, specifically for budgeting.
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_settings"
__description__ = "Budget Manager (BudMan) settings object support."
__license__ = "MIT"

from .budman_settings_constants import * 
from .budman_settings import BudManSettings

# target for 'from budman_app import *'
__all__ = [
    "BudManSettings",
    "BUDMAN_FOLDER_ENV_VAR",
    "BUDMAN_SETTINGS_FILES_ENV_VAR",
    "THIS_APP_NAME",
    "THIS_APP_SHORT_NAME",
    "THIS_APP_VERSION",
    "THIS_APP_AUTHOR",
    "THIS_APP_COPYRIGHT",
    "BUDMAN_SETTINGS",
    "SHORT_APP_NAME",
    "APP_NAME",
    "BDM_FOLDER",
    "BDM_STORE_FILENAME",
    "BDM_STORE_FILETYPE",
    "BDM_STORE_URL",
    "BUDMAN_DEFAULT_FI",
    "BUDMAN_DEFAULT_WORKFLOW",
    "BUDMAN_DEFAULT_WORKFLOW_PURPOSE",
    "BUDMAN_DEFAULT_WORKBOOK_TYPE",
    "BUDMAN_CMD_HISTORY_FILENAME",
    "CATEGORY_CATALOG",
    "TXN_CATEGORIES_WORKBOOK_FULL_FILENAME",
    "CATEGORY_MAP_WORKBOOK_FULL_FILENAME",
    "LOGGING_DEFAULT_HANDLER",
    "LOGGING_DEFAULT_LEVEL",
    "LOGGING_CONFIG_FILENAME"
]

