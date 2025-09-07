# ---------------------------------------------------------------------------- +
#region budman_cp_namespace.py module
""" budman_cp_namespace.py defines symbol constants for budman app Command Objects."""
#endregion budman_cp_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages

# third-party modules and packages

# local modules and packages
import p3_mvvm as p3m
import budman_namespace as bdm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# BudMan application-specific Command Processor attribute Constants.

# Known p3m.CK_CMD_KEY and p3m.CK_CMD_NAME values for BudMan app Command Objects.
CV_APP_CMD_NAME = "app"
CV_APP_CMD_KEY = CV_APP_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_CHANGE_CMD_NAME = "change"
CV_CHANGE_CMD_KEY = CV_CHANGE_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_INIT_CMD_NAME = "init"
CV_INIT_CMD_KEY = CV_INIT_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_LOAD_CMD_NAME = "load"
CV_LOAD_CMD_KEY = CV_LOAD_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_LIST_CMD_NAME = "list"
CV_LIST_CMD_KEY = CV_LIST_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_SAVE_CMD_NAME = "save"
CV_SAVE_CMD_KEY = CV_SAVE_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_SHOW_CMD_NAME = "show"
CV_SHOW_CMD_KEY = CV_SHOW_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_VAL_CMD_NAME = "val"
CV_VAL_CMD_KEY = CV_VAL_CMD_NAME + p3m.CMD_KEY_SUFFIX
CV_WORKFLOW_CMD_NAME = "workflow"
CV_WORKFLOW_CMD_KEY = CV_WORKFLOW_CMD_NAME + p3m.CMD_KEY_SUFFIX

# Supported p3m.CK_CMD_KEY, p3m.CK_SUBCMD_KEY and p3m.CK_SUBCMD_NAME values 
# for the BudMan App Command Objects.
CV_FIN_INST_SUBCMD_NAME = "FIN_INST"
CV_WORKFLOW_FIN_INST_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_FIN_INST_SUBCMD_NAME
CV_SHOW_FIN_INST_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_FIN_INST_SUBCMD_NAME
CV_WORKFLOWS_SUBCMD_NAME = "WORKFLOWS"
CV_WORKFLOWS_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_WORKFLOWS_SUBCMD_NAME
CV_SHOW_WORKFLOWS_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_WORKFLOWS_SUBCMD_NAME
CV_DATA_CONTEXT_SUBCMD_NAME = "DATA_CONTEXT"
CV_SHOW_DATA_CONTEXT_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_DATA_CONTEXT_SUBCMD_NAME
CV_BDM_STORE_SUBCMD_NAME = "BDM_STORE"
CV_LIST_BDM_STORE_SUBCMD_KEY = CV_LIST_CMD_KEY + "_" + CV_BDM_STORE_SUBCMD_NAME
CV_LOAD_BDM_STORE_SUBCMD_KEY = CV_LOAD_CMD_KEY + "_" + CV_BDM_STORE_SUBCMD_NAME
CV_SAVE_BDM_STORE_SUBCMD_KEY = CV_SAVE_CMD_KEY + "_" + CV_BDM_STORE_SUBCMD_NAME
CV_WORKBOOKS_SUBCMD_NAME = "workbooks"
CV_LIST_WORKBOOKS_SUBCMD_KEY = CV_LIST_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME
CV_LOAD_WORKBOOKS_SUBCMD_KEY = CV_LOAD_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME
CV_SAVE_WORKBOOKS_SUBCMD_KEY = CV_SAVE_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME
CV_BUDGET_CATEGORIES_SUBCMD_NAME = "BUDGET_CATEGORIES"
CV_SHOW_BUDGET_CATEGORIES_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_BUDGET_CATEGORIES_SUBCMD_NAME
CV_FILES_SUBCMD_NAME = "files"
CV_LIST_FILES_SUBCMD_KEY = CV_LIST_CMD_KEY + "_" + CV_FILES_SUBCMD_NAME
CV_SHOW_DATA_CONTEXT_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_DATA_CONTEXT_SUBCMD_NAME
CV_CATEGORIZATION_SUBCMD_NAME = "categorization"
CV_CATEGORIZATION_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_CATEGORIZATION_SUBCMD_NAME
CV_SET_SUBCMD_NAME = "set"
CV_SET_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_SET_SUBCMD_NAME
CV_LIST_SUBCMD_NAME = "list"
CV_LIST_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_LIST_SUBCMD_NAME
CV_TRANSFER_SUBCMD_NAME = "transfer"
CV_WORKFLOW_TRANSFER_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_TRANSFER_SUBCMD_NAME
CV_INTAKE_SUBCMD_NAME = "intake"
CV_WORKFLOW_INTAKE_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_INTAKE_SUBCMD_NAME
CV_CHECK_SUBCMD_NAME = "check"
CV_CHECK_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_CHECK_SUBCMD_NAME
CV_APPLY_SUBCMD_NAME = "apply"
CV_APPLY_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_APPLY_SUBCMD_NAME
CV_EXIT_SUBCMD_NAME = "exit"
CV_EXIT_SUBCMD_KEY = CV_APP_CMD_KEY + "_" + CV_EXIT_SUBCMD_NAME
CV_DELETE_SUBCMD_NAME = "delete"
CV_DELETE_SUBCMD_KEY = CV_APP_CMD_KEY + "_" + CV_DELETE_SUBCMD_NAME
CV_RELOAD_SUBCMD_NAME = "reload"
CV_RELOAD_SUBCMD_KEY = CV_APP_CMD_KEY + "_" + CV_RELOAD_SUBCMD_NAME
CV_LOG_SUBCMD_NAME = "log"
CV_LOG_SUBCMD_KEY = CV_APP_CMD_KEY + "_" + CV_LOG_SUBCMD_NAME
CV_TASK_SUBCMD_NAME = "task"
CV_TASK_SUBCMD_KEY = CV_WORKFLOW_CMD_KEY + "_" + CV_TASK_SUBCMD_NAME
CV_CHANGE_WORKBOOKS_SUBCMD_KEY = CV_CHANGE_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME
CV_SHOW_WORKBOOKS_SUBCMD_KEY = CV_SHOW_CMD_KEY + "_" + CV_WORKBOOKS_SUBCMD_NAME
CV_PARSE_ONLY_SUBCMD_NAME = "parse_only"
CV_PARSE_ONLY_SUBCMD_KEY = CV_VAL_CMD_KEY + "_" + CV_PARSE_ONLY_SUBCMD_NAME

# Common argument optional flag attribute keys, used in parsers
CK_PARSE_ONLY = p3m.CK_PARSE_ONLY          # --parse_only  -po
CK_VALIDATE_ONLY = p3m.CK_VALIDATE_ONLY    # --validate_only  -vo
CK_WHAT_IF = p3m.CK_WHAT_IF                # --what_if  -wi
CK_ALL_WBS = "all_wbs"                # --all_wbs  -all
CK_LOAD_WORKBOOK = "load_workbook"
CK_FIX_SWITCH = "fix_switch"
CK_VALIDATE_CATEGORIES = "validate_categories"
CK_LOG_ALL = "log_all"
CK_NO_SAVE = "no_save"
CK_RECONCILE = "reconcile"
CK_JSON = "json"

# Common positional argument attribute keys, used in parsers
CK_WB_INDEX = bdm.WB_INDEX
CK_WB_LIST = "wb_list"
CK_FI_KEY = bdm.FI_KEY
CK_WF_KEY = bdm.WF_KEY
CK_WF_PURPOSE = bdm.WF_PURPOSE
CK_WF_INPUT = bdm.WF_INPUT
CK_WF_WORKING = bdm.WF_WORKING
CK_WF_OUTPUT = bdm.WF_OUTPUT
CK_WB_ID = bdm.WB_ID
CK_WB_TYPE = bdm.WB_TYPE
CK_WB_NAME = bdm.WB_NAME
CK_FILE_LIST = "file_list"
CK_WB_REF = "wb_ref"
CK_WB_INFO = "wb_info"
CK_WF_TASK = "wf_task"
CK_SRC_WF_KEY = "src_" + bdm.WF_KEY
CK_DST_WF_KEY = "dst_" + bdm.WF_KEY
CK_SRC_WF_PURPOSE = "src_" + bdm.WF_PURPOSE
CK_DST_WF_PURPOSE = "dst_" + bdm.WF_PURPOSE
CK_SRC_WB_TYPE = "src_" + bdm.WB_TYPE
CK_DST_WB_TYPE = "dst_" + bdm.WB_TYPE

# subcmd_key CV_TASK_SUBCMD_KEY argument constants

# subcmd_key CV_INTAKE_SUBCMD_KEY argument key/value constants
CK_INTAKE_TASK = "intake_task"
CV_INTAKE_MOVE_TASK = "move"
CV_INTAKE_COPY_TASK = "copy"
CV_INTAKE_LIST_TASK = "list"
CK_FILE_INDEX = "file_index"
CK_FOLDER_ID = "folder_id"
# subcmd_name CV_WORKBOOKS_SUBCMD_NAME argument key/value constants
CK_BDM_TREE = "bdm_tree"
# subcmd_name CV_CHANGE_CMD argument constants
CK_CMDLINE_WB_TYPE = "cmdline_wb_type"
CK_CMDLINE_WF_KEY = "cmdline_wf_key"
CK_CMDLINE_WF_PURPOSE = "cmdline_wf_purpose"
# subcmd_name CV_DELETE_SUBCMD argument constants
CK_DELETE_TARGET = "delete_target"
# subcmd_name CV_PARSER_ONLY_SUBCMD argument constants
CK_PO_VALUE = "po_value"
# subcmd_name BUDGET_CATEGORIES argument constants
CK_CAT_LIST = "cat_list"
CK_LEVEL = "level"
# subcmd_name CV_TASK_SUBCMD_KEY argument constants
CK_TASK_NAME = "task_name"
CV_SYNC = "sync"
VALID_TASK_NAMES = (CV_SYNC, "foo")
# subcmd_name CV_LOG_SUBCMD argument constants
CK_HANDLER_NAME = "handler_name"
CK_LIST_SWITCH = "list_switch" 
CK_LEVEL_VALUE = "level_value"
CK_ROLLOVER_SWITCH = "rollover_switch"
# subcmd_name CV_RELOAD_SUBCMD argument constants
CK_RELOAD_TARGET = "reload_target"
CV_CATEGORY_MAP = "category_map"
CV_FI_WORKBOOK_DATA_COLLECTION = bdm.FI_WORKBOOK_DATA_COLLECTION
CV_WORKFLOWS_MODULE = "budman_workflows"
# deprecated
CK_CHECK_REGISTER = "check_register"

BUDMAN_VALID_CK_ATTRS = (p3m.CK_CMD_KEY, p3m.CK_CMD_NAME, p3m.CK_SUBCMD_KEY, p3m.CK_SUBCMD_NAME, 
                        p3m.CK_CMD_EXEC_FUNC,
                        CK_PARSE_ONLY, CK_VALIDATE_ONLY, CK_WHAT_IF, 
                        CK_FI_KEY, CK_WF_KEY, CK_SRC_WF_KEY, CK_DST_WF_KEY,
                        CK_WF_PURPOSE, CK_SRC_WF_PURPOSE, CK_DST_WF_PURPOSE,
                        CK_WB_TYPE, CK_WB_NAME, CK_WB_REF,CK_WB_INFO,
                        CK_CHECK_REGISTER,CK_HANDLER_NAME,CK_LIST_SWITCH,
                        CK_LEVEL_VALUE, CK_ROLLOVER_SWITCH,CK_WB_INDEX, 
                        CK_ALL_WBS, CK_RELOAD_TARGET)

#endregion Global Constants for ViewModelCommandProcessor
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
