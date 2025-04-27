"""
p3_fi_transactions package

Budget Model applies mostly to transactions from financial institutions (FI). This package 
has the functionality to intake transactions from a financial institution (FI) and process them into
a budget model. The package is designed to work with Excel workbooks, specifically for budgeting.
"""

__author__ = "Paul Painter"
__version__ = "1.0.0"
__copyright__ = "2024 Paul Painter"
__name__ = "p3_excel_budget"
__description__ = "Work with Excel wookboo data for budgeting functions."
__license__ = "MIT"

from .budget_transaction_files import (
    init_budget_model,
    load_banking_transactions, 
    save_banking_transactions
)
from .budget_categorization import (
    check_budget_category,
    map_budget_category
)

__all__ = [
    "init_budget_model",
    "load_banking_transactions",
    "save_banking_transactions",
    "check_budget_category",
    "map_budget_category",
]