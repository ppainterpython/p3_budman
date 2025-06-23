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
    "THIS_APP_NAME",
    "APP_NAME",
    "SHORT_APP_NAME"
]

