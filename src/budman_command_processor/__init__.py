"""
Budget Manager - p3_budman package

budman_command_processor - the Command Processor pattern for p3_budman.
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_command_processor"
__description__ = "Command Processor pattern implementation for BudMan."
__license__ = "MIT"

from .budman_cp_namespace import *
from .budman_command_services import (
    # BUDMAN_CMD_TASK functions
    BUDMAN_CMD_TASK_process,
    BUDMAN_CMD_TASK_get_file_tree,
    # Helper functions
    get_filename_from_file_tree,
    verify_cmd_key
)

# target for 'from budman_app import *'
__all__ = [
    "BudManApp",
    "BUDMAN_CMD_TASK_process",
    "BUDMAN_CMD_TASK_get_file_tree",
    "get_filename_from_file_tree",
    "verify_cmd_key"
]

