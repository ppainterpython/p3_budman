"""
Budget Manager - budget_categorization package

Budget Manager (budman) follows an MVVM design pattern. Also, the application 
provides a workflow pattern to implement processes for applying transformations
on the budget data objects, e.g., excel workbooks, csv files, etc.

Workflows are named sequences of tasks, performed in a defined manner, perhaps
triggered by a detected change to data. A workflow has associated Input, 
Working, and Output folders where data objects reside. A workflow also has
associated task functions that do the actual work on the data objects.

The budget_categorization package provides functions and classes and functions
to implement tasks associated with budget categorization workflows.
# ---------------------------------------------------------------------------- +
"""
__version__ = "0.4.0"
__author__ = "Paul Painter"
__copyright__ = "2025, 2026 Paul Painter"
__name__ = "budman_workflow_services"
__description__ = "Budget Manager (BudMan) Workflow process implementation."
__license__ = "MIT"

from .budman_wf_namespace import *
from .workflow_intake_services import (
    INTAKE_TASK_convert_csv_txns_schema
)
from .budget_categorization import (
    WORKFLOW_TASK_check_sheet_columns, 
    check_sheet_schema, 
    TRANSACTION_DESCRIPTION_COL_NAME, 
    validate_budget_categories,
    WORKFLOW_TASK_process_budget_category,
    WORKFLOW_TASK_categorize_transaction
)
from .txn_category import (
    BDMTXNCategory,
    BDMTXNCategoryManager,
    TXNCategoryMap
)

# symbols for "from budman_model import *"
__all__ = [
    # module names
    # workflow_intake_services module
    # "INTAKE_SBCMD_router",
    "INTAKE_TASK_convert_csv_txns_schema",
    # txn_category.py module
    "BDMTXNCategory",
    "TXNCategoryMap",
    "BDMTXNCategoryManager",
    # budget_categorization.py module
    "WORKFLOW_TASK_check_sheet_columns",
    "check_sheet_schema",
    "TRANSACTION_DESCRIPTION_COL_NAME",
    "validate_budget_categories",
    "WORKFLOW_TASK_process_budget_category",
    "WORKFLOW_TASK_categorize_transaction"
]
