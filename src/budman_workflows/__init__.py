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

from .workflow_command_services import (
    WORKFLOW_CMD_process,
)
from .budget_intake import (
    INTAKE_TASK_process
)

# symbols for "from budman_model import *"
__all__ = [
    # workflow_commands.py module
    "WORKFLOW_CMD_process",
    # budget_intake",
    "INTAKE_TASK_process",
]