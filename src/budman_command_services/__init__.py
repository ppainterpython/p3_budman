"""
budman_command_services - the Command Services Module. Provides functions
invoked for CP command execution.
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_command_services"
__description__ = "Services for BudMan CP command execution."
__license__ = "MIT"

from .budman_cp_namespace import *
from .budman_command_services import (
    # BUDMAN_CMD execution functions
    BUDMAN_CMD_router,
    BUDMAN_CMD_list_workbooks,
    BUDMAN_CMD_list_bdm_store_json,
    BUDMAN_CMD_list_files,
    BUDMAN_CMD_show_DATA_CONTEXT,
    BUDMAN_CMD_app_sync,
    BUDMAN_CMD_app_log,
    BUDMAN_CMD_app_refresh,
    BUDMAN_CMD_app_reload,
    BUDMAN_CMD_app_delete,
    # BudMan Command File Services
    BUDMAN_CMD_FILE_SERVICE_get_BSMFile,
    BUDMAN_CMD_FILE_SERVICE_get_full_filename,
    process_selected_workbook_input,
    BUDMAN_CMD_TASK_validate_model_binding,    # Helper functions
    verify_cmd_key,
    verify_subcmd_key,
    validate_cmd_arguments
)
from .workflow_command_services import (
    WORKFLOW_CMD_router,
    WORKFLOW_CMD_process
)
from .budget_intake import (
    INTAKE_SBCMD_router
)
# target for 'from budman_app import *'
__all__ = [
    "BudManApp",
    "BUDMAN_CMD_router",
    "BUDMAN_CMD_list_workbooks",
    "BUDMAN_CMD_list_bdm_store_json",
    "BUDMAN_CMD_list_files",
    "BUDMAN_CMD_show_DATA_CONTEXT",
    "BUDMAN_CMD_app_sync",
    "BUDMAN_CMD_app_log",
    "BUDMAN_CMD_app_refresh",
    "BUDMAN_CMD_app_reload",
    "BUDMAN_CMD_app_delete",
    # budman_command_services.py
    "BUDMAN_CMD_FILE_SERVICE_get_BSMFile",
    "BUDMAN_CMD_FILE_SERVICE_get_full_filename",
    "process_selected_workbook_input",
    "BUDMAN_CMD_TASK_validate_model_binding",
    "verify_cmd_key",
    "verify_subcmd_key",
    "validate_cmd_arguments",
    # workflow_commands.py module
    "WORKFLOW_CMD_router",
    "WORKFLOW_CMD_process",
    # budget_intake",
    "INTAKE_SBCMD_router",
]

