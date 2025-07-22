# ---------------------------------------------------------------------------- +
#region budman_cp_namespace.py module
""" budman_cp_namespace.py defines symbol constants for Command Objects.
"""
#endregion budman_cp_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages

# third-party modules and packages

# local modules and packages
import budman_namespace as bdm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
#region Global Constants for ViewModelCommandProcessor
# BudMan Command Processor Argument Name Constants. Arguments are placed in
# the command dictionary as key/value pairs. The keys are used to identify
# the command line arguments but also include values placed in the cmd object
# prior to cp_execute_cmd() being called, depending on the parsing activity
# of a View interface that is constructing the cmd object. 
# argparse converts hyphens '-' to underscores '_', so we use underscores
#
# List of cmd 'key' (CK_) string constants, use like cmd[CK_NAME]
# cmd 'key' values are CV_
#
# All cmd obj required attributes
CMD_KEY_SUFFIX = "_cmd"
CK_CMD_KEY = "cmd_key"
"""A string identifier for a known cmd, used to bind to an execution function."""
CK_SUBCMD_KEY = "subcmd_key"
"""The string identifier for a known subcmd, can be used with cmd_key to bind exec func."""
CK_CMD_NAME = "cmd_name"
"""The cmd object key defining the command name."""
CK_SUBCMD_NAME = "subcmd_name"
"""The string identifier for a known subcmd, can be used with cmd_key to bind exec func."""
CK_CMD_EXEC_FUNC = "cmd_exec_func"
"""The cmd object key assigned the command execution function callable value."""

# Known CK_CMD_KEY and CK_CMD_NAME values for the BudManViewModel.
CV_INIT_CMD = "init"
CV_LOAD_CMD = "load"
CV_SAVE_CMD = "save"
CV_SHOW_CMD_NAME = "show"
CV_SHOW_CMD_KEY = CV_SHOW_CMD_NAME + CMD_KEY_SUFFIX
CV_CHANGE_CMD_NAME = "change"
CV_CHANGE_CMD_KEY = CV_CHANGE_CMD_NAME + CMD_KEY_SUFFIX
CV_WORKFLOW_CMD_NAME = "workflow"
CV_WORKFLOW_CMD_KEY = CV_WORKFLOW_CMD_NAME + CMD_KEY_SUFFIX
CV_APP_CMD_NAME = "app"
CV_APP_CMD_KEY = CV_APP_CMD_NAME + CMD_KEY_SUFFIX

# Known CK_SUBCMD_KEY and CK_SUBCMD_NAME values for the BudManViewModel.
CV_CATEGORIZATION_SUBCMD_NAME = "categorization"
CV_CATEGORIZATION_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_CATEGORIZATION_SUBCMD_NAME
CV_INTAKE_SUBCMD_NAME = "intake"
CV_INTAKE_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_INTAKE_SUBCMD_NAME
CV_CHECK_SUBCMD_NAME = "check"
CV_CHECK_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_CHECK_SUBCMD_NAME
CV_APPLY_SUBCMD_NAME = "apply"
CV_APPLY_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_APPLY_SUBCMD_NAME
CV_DELETE_SUBCMD = "delete"
CV_RELOAD_SUBCMD_NAME = "reload"
CV_RELOAD_SUBCMD_KEY = CV_APP_CMD_KEY + "_" + CV_RELOAD_SUBCMD_NAME
CV_LOG_SUBCMD = "log"
CV_BUDGET_CATEGORIES_SUBCMD = "BUDGET_CATEGORIES"
CV_TASK_SUBCMD = "task"
CV_WORKBOOKS_SUBCMD_NAME = "workbooks"
CV_CHANGE_WORKBOOKS_SUBCMD_KEY = CV_CHANGE_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME
CV_SHOW_WORKBOOKS_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME

# Argument attribute keys, for any cmd
CK_PARSE_ONLY = "parse_only"
CK_VALIDATE_ONLY = "validate_only"
CK_WHAT_IF = "what_if"
CK_LOAD_WORKBOOK = "load_workbook"
CK_FIX_SWITCH = "fix_switch"
CK_VALIDATE_CATEGORIES = "validate_categories"
CK_LOG_ALL = "log_all"

# Essential Data Context attributes, with cross-cutting scope over cmds
CK_FI_KEY = "fi_key"
CK_WF_KEY = "wf_key"
CK_WF_PURPOSE = "wf_purpose"
CK_WB_ID = "wb_id"
CK_WB_TYPE = "wb_type"
CK_WB_NAME = "wb_name"
CK_WB_INDEX = "wb_index"
CK_WB_LIST = "wb_list"
CK_ALL_WBS = "all_wbs"
CK_WB_REF = "wb_ref"
CK_WB_INFO = "wb_info"
CK_WF_TASK = "wf_task"

# subcmd_name CV_WORKBOOK_SUBCMD_NAME argument constants
CK_BDM_TREE = "bdm_tree"
# subcmd_name CV_CHANGE_CMD argument constants
CK_NEW_WB_TYPE = "new_wb_type"
CK_NEW_WF_KEY = "new_wf_key"
CK_NEW_WF_PURPOSE = "new_wf_purpose"
# subcmd_name CV_DELETE_SUBCMD argument constants
CK_DELETE_TARGET = "delete_target"
# subcmd_name BUDGET_CATEGORIES argument constants
CK_CAT_LIST = "cat_list"
CK_LEVEL = "level"
# subcmd_name CV_TASK_SUBCMD argument constants
CK_TASK_ARGS = "task_args"
CK_TASK_NAME = "task_name"
# subcmd_name CV_LOG_SUBCMD argument constants
CK_HANDLER_NAME = "handler_name"
CK_LIST_SWITCH = "list_switch" 
CK_LEVEL_VALUE = "level_value"
CK_ROLLOVER_SWITCH = "rollover_switch"
# subcmd_name CV_RELOAD_SUBCMD argument constants
CK_RELOAD_TARGET = "reload_target"
CV_CATEGORY_MAP = bdm.CATEGORY_MAP
CV_FI_WORKBOOK_DATA_COLLECTION = bdm.FI_WORKBOOK_DATA_COLLECTION
CV_WORKFLOWS_MODULE = "budman_workflows"
# deprecated
CK_CHECK_REGISTER = "check_register"

BUDMAN_VALID_CK_ATTRS = (CK_CMD_KEY, CK_CMD_NAME, CK_SUBCMD_KEY, CK_SUBCMD_NAME, 
                        CK_CMD_EXEC_FUNC,
                        CK_PARSE_ONLY, CK_VALIDATE_ONLY, CK_WHAT_IF, 
                        CK_FI_KEY, CK_WF_KEY,CK_WF_PURPOSE,
                        CK_WB_TYPE, CK_WB_NAME, CK_WB_REF,CK_WB_INFO,
                        CK_CHECK_REGISTER,CK_HANDLER_NAME,CK_LIST_SWITCH,
                        CK_LEVEL_VALUE, CK_ROLLOVER_SWITCH,CK_WB_INDEX, 
                        CK_ALL_WBS, CK_RELOAD_TARGET)

#endregion Global Constants for ViewModelCommandProcessor
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
