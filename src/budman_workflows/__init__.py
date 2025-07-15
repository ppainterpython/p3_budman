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

from .budget_intake import (
    process_txn_intake
)
from .workflow_utils import (
    extract_category_tree, 
    output_category_tree,
    category_tree_to_csv,
    category_map_count, 
    clear_category_map,
    categorize_transaction,
    extract_bdm_tree,
    output_bdm_tree
)
from .budget_categorization import (
    check_sheet_columns, 
    check_sheet_schema, 
    ORIGINAL_DESCRIPTION_COL_NAME, 
    process_budget_category,
    apply_check_register
)
from .txn_category import (
    BDMTXNCategory,
    BDMTXNCategoryManager,
    TXNCategoryCatalog
)
from .budget_category_mapping import (
    check_register_map, 
    compile_category_map,
    category_map, 
    compiled_category_map,
    clear_category_map,
    get_category_map,
    set_category_map,
    clear_compiled_category_map,
    get_compiled_category_map,
    set_compiled_category_map,
    clear_check_register_map,
    get_check_register_map,
    set_check_register_map,
    CategoryCounter,
    category_histogram,
    get_category_histogram,
    clear_category_histogram
)

# symbols for "from budman_model import *"
__all__ = [
    # txn_category.py module
    "BDMTXNCategory",
    "TXNCategoryCatalog",
    "BDMTXNCategoryManager",
    # workflow_utils.py module
    "category_map_count",
    "extract_category_tree",
    "output_category_tree",
    "category_tree_to_csv",
    "category_map_count",
    "clear_category_map",
    "categorize_transaction",
    "extract_bdm_tree",
    "output_bdm_tree",
    # budget_categorization.py module
    "check_sheet_columns",
    "check_sheet_schema",
    "ORIGINAL_DESCRIPTION_COL_NAME",
    "process_budget_category",
    "apply_check_register",
    # budget_category_mapping.py module
    "check_register_map",
    "compile_category_map",
    "category_map",
    "compiled_category_map",
    "clear_category_map",
    "get_category_map",
    "set_category_map",
    "clear_compiled_category_map",
    "get_compiled_category_map",
    "set_compiled_category_map",
    "clear_check_register_map",
    "get_check_register_map",
    "set_check_register_map",
    "category_histogram",
    "clear_category_histogram",
    "get_category_histogram",
]