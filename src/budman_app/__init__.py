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

from .budman_app import (
    BudManApp
)

# target for 'from budman_app import *'
__all__ = [
    "BudManApp"
]

