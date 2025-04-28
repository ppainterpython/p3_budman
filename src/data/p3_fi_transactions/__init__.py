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
    budget_model,
    init_budget_model,
    check_budget_model,
    validate_budget_model,
    load_fi_transactions, 
    save_fi_transactions,
    fi_if_workbook_keys,
)
from .budget_categorization import (
    check_budget_category,
    map_budget_category,
    process_incoming_categorization
)

from .category_mapping import (
    map_category,
    category_map_count,
)

__all__ = [
    "budget_model",
    "init_budget_model",
    "check_budget_model",
    "validate_budget_model",
    "save_fi_transactions",
    "fi_if_workbook_keys",
    "check_budget_category",
    "map_budget_category",
    "process_incoming_categorization",
    "map_category",
    "category_map_count",
]