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
__name__ = "budman_app"
__description__ = "Budget Manager (BudMan) a p3 application."
__license__ = "MIT"

from .budman_app_constants import * #(
#     BUDMAN_SETTINGS,
#     BUDMAN_FOLDER,
#     BUDMAN_STORE,
#     BUDMAN_STORE_FILETYPE,
#     BUDMAN_DEFAULT_FI,
#     BUDMAN_DEFAULT_WORKFLOW,
#     BUDMAN_DEFAULT_WORKBOOK_TYPE,
#     APP_NAME,
#     SHORT_APP_NAME
# )
from .budman_app import (
    BudManApp,
    BudManApp_settings,
    configure_logging,
    configure_settings
)

# target for 'from budman_app import *'
__all__ = [
    "BudManApp",
    "BudManApp_settings",
    "BUDMAN_SETTINGS",
    "BUDMAN_FOLDER",
    "BUDMAN_STORE",
    "BUDMAN_STORE_FILETYPE",
    "BUDMAN_DEFAULT_FI",
    "BUDMAN_DEFAULT_WORKFLOW",
    "BUDMAN_DEFAULT_WORKBOOK_TYPE",
    "APP_NAME",
    "SHORT_APP_NAME"
]

