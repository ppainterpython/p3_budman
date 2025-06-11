"""
Budget Manager - budman_workflows package

Budget Manager (budman) follows an MVVM design pattern. Also, the application 
provides a workflow pattern to implement processes for applying transformations
on the budget data objects, e.g., excel workbooks, csv files, etc.

Workflows are named sequences of tasks, performed in a defined manner, perhaps
triggered by a detected change to data. A workflow has associated Input, 
Working, and Output folders where data objects reside. A workflow also has
associated task functions that do the actual work on the data objects.
# ---------------------------------------------------------------------------- +
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_workflows"
__description__ = "Budget Manager (BudMan) Workflow process implementation."
__license__ = "MIT"

from .budget_category_mapping import (
    map_category, category_map, category_map_count
)
from .budget_categorization import (
    check_budget_category, check_sheet_columns, map_budget_category,
    check_sheet_schema,ORIGINAL_DESCRIPTION_COL_NAME, apply_check_register
)

# symbols for "from budman_model import *"
__all__ = [
    "budget_category_mapping",  # list modules here to use importlib.reload()
    "check_budget_category",
    "check_sheet_columns",
    "check_sheet_schema",
    "ORIGINAL_DESCRIPTION_COL_NAME",
    "map_budget_category",
    "map_category",
    "category_map",
    "category_map_count",
    "apply_check_register"
]