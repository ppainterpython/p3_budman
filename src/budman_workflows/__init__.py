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

from .workflow_utils import (
    generate_hash_key, 
    split_budget_category, 
    extract_category_tree, 
    output_category_tree,
    category_tree_to_csv,
    category_map_count, 
    map_category, 
    categorize_transaction
)
from .budget_categorization import (
    check_sheet_columns, 
    check_sheet_schema, 
    check_budget_category, 
    ORIGINAL_DESCRIPTION_COL_NAME, 
    process_budget_category,
    apply_check_register
)
from .budget_category_mapping import (
    category_map, 
    compiled_category_map,
    check_register_map, 
    category_histogram,
    clear_category_histogram,
    get_category_histogram,
    BDMTXNCategory
)

# symbols for "from budman_model import *"
__all__ = [
    # workflow_utils.py module
    "generate_hash_key",
    "split_budget_category",
    "category_map_count",
    "extract_category_tree",
    "output_category_tree",
    "category_tree_to_csv",
    "category_map_count",
    "map_category",
    "categorize_transaction",
    # budget_categorization.py module
    "check_sheet_columns",
    "check_sheet_schema",
    "check_budget_category",
    "ORIGINAL_DESCRIPTION_COL_NAME",
    "process_budget_category",
    "apply_check_register",
    # budget_category_mapping.py module
    "category_map",
    "compiled_category_map",
    "check_register_map",
    "category_histogram",
    "clear_category_histogram",
    "get_category_histogram",
    "BDMTXNCategory"
]