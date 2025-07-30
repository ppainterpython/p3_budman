# ---------------------------------------------------------------------------- +
#region cp_utils.py module
""" cp_utils.py implements utility functions for command processing.
"""
#endregion cp_utils.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, io, sys, getpass, time, copy, importlib
from pathlib import Path
from typing import List, Type, Optional, Dict, Tuple, Any, Callable
from treelib import Tree
from datetime import datetime as dt

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_mvvm import (Model_Base, Model_Binding)
import budman_command_processor as cp
from budman_settings import *
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budget_storage_model import (
    bsm_file_tree_from_folder
)
from budman_data_context import BudManAppDataContext_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region process_workflow_intake_tasks() function
def process_workflow_tasks(cmd: Dict[str, Any], 
                       bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """Process workflow  tasks.

    This function processes various worklow tasks.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.
    """
    try:
        # Assuming the cmd parameters have been validated before reaching this point.
        if cmd[cp.CK_SUBCMD_KEY] == cp.CV_LIST_SUBCMD_KEY:
            # Process the list task.
            return extract_workflow_folder_tree(cmd, bdm_DC)
        else:
            m = f"Unknown workflow task: {cmd[cp.CK_SUBCMD_KEY]}"
            logger.error(m)
            return False, m
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion process_workflow_intake_tasks() function
# ---------------------------------------------------------------------------- +
#region extract_workflow_folder_tree() function
def extract_workflow_folder_tree(cmd: Dict[str, Any],
                      bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """List all files from an indicated workflow folder.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.

        cmd should contain:
            - cp.CK_FOLDER_ID: The ID of the folder to list files from.

    Returns:
        BUDMAN_RESULT: Tuple[bool, cmd_result]:
    """
    try:
        cmd_result : Dict[str, Any] = {
            bdm.CMD_RESULT_TYPE: bdm.CLIVIEW_FOLDER_TREE_VIEW,
            bdm.CMD_RESULT_CONTENT: None
        }
        wf_key: str = cmd.get(cp.CK_CMDLINE_WF_KEY, None)
        if not wf_key:
            m = "No wf_key provided in data context."
            logger.error(m)
            return False, m
        wf_purpose: str = cmd.get(cp.CK_CMDLINE_WF_PURPOSE, None)
        if not wf_purpose:
            m = "No wf_purpose provided in command."
            logger.error(m)
            return False, m
        wf_purpose_folder_abs_path: Path.Path = bdm_DC.dc_WF_PURPOSE_FOLDER_abs_path(wf_key, wf_purpose)
        folder_tree: Tree = bsm_file_tree_from_folder(wf_purpose_folder_abs_path)
        # Format the tree for output
        now = dt.now()
        now_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
        original_stdout = sys.stdout  # Save the original stdout
        buffer = io.StringIO()
        sys.stdout = buffer  # Redirect stdout to capture tree output
        print(f"Workflow Folder Tree for '{wf_key}' with purpose '{wf_purpose}' ({now_str})\n")
        folder_tree.show()
        sys.stdout = original_stdout  # Reset stdout
        cmd_result[bdm.CMD_RESULT_CONTENT] = buffer.getvalue()
        return True, cmd_result
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion extract_workflow_folder_tree() function
# ---------------------------------------------------------------------------- +
