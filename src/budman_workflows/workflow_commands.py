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
from .workflow_utils import output_tree_view
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_process() function
def WORKFLOW_TASK_process(cmd: Dict[str, Any], 
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
        if cmd[cp.CK_SUBCMD_KEY] == cp.CV_SET_SUBCMD_KEY:
            # Process the set_value task.
            return WORKFLOW_TASK_set_value(cmd, bdm_DC)
        elif cmd[cp.CK_SUBCMD_KEY] == cp.CV_LIST_SUBCMD_KEY:
            # Process the list_folder_tree task.
            return WORKFLOW_TASK_list_folder_tree(cmd, bdm_DC)
        else:
            m = f"Unknown workflow task: {cmd[cp.CK_SUBCMD_KEY]}"
            logger.error(m)
            return False, m
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_process() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_set_value() function
def WORKFLOW_TASK_set_value(cmd: Dict[str, Any], 
                       bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """WORKFLOW_SET_subcmd: Set values in the DC for workflow tasks.

    This function sets values in the data context for workflow tasks based on the
    provided command object.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.
        Associate cmd object keys for the set subcmd:
            cp.CK_CMDLINE_WF_KEY
            cp.CK_CMDLINE_WF_PURPOSE
    """
    try:
        # Assuming the cmd parameters have been validated before reaching this point.
        wf_key: str = cmd.get(cp.CK_CMDLINE_WF_KEY, None)
        wf_purpose: str = cmd.get(cp.CK_CMDLINE_WF_PURPOSE, None)
        msg: str = ""
        if wf_key:
            bdm_DC.dc_WF_KEY = wf_key
            msg += f"Workflow key set to: '{wf_key}'"
        sep = ", " if wf_key else ""
        if wf_purpose:
            bdm_DC.dc_WF_PURPOSE = wf_purpose
            msg += f"{sep}Workflow purpose set to: '{wf_purpose}' "
        return True, msg
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_set_value() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_list_folder_tree() function
def WORKFLOW_TASK_list_folder_tree(cmd: Dict[str, Any],
                      bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """List all files from an indicated workflow folder.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.

        cmd should contain:
            - cp.CK_CMDLINE_WF_KEY: The wf_key of interest.
            - cp.CK_CMDLINE_WF_PURPOSE: The wf_purpose of interest.

    Returns:
        BUDMAN_RESULT: Tuple[bool, CMD_RESULT]:
    """
    try:
        wf_key: str = cmd.get(cp.CK_CMDLINE_WF_KEY, None)
        if not wf_key:
            # No wf_key in cmdline, try DC
            wf_key = bdm_DC.dc_WF_KEY
            if not wf_key:
                # No wf_key to work with
                m = "No wf_key from cmd args or DC."
                logger.error(m)
                return False, m
        wf_purpose: str = cmd.get(cp.CK_CMDLINE_WF_PURPOSE, None)
        if not wf_purpose:
            # No wf_purpose in cmdline, try DC
            wf_purpose = bdm_DC.dc_WF_PURPOSE
            if not wf_purpose:
                # No wf_purpose to work with
                m = "No wf_purpose from cmd args or DC."
                logger.error(m)
                return False, m
        folder_tree: Tree = WORKFLOW_get_folder_tree(wf_key, wf_purpose, bdm_DC)
        msg = f"Workflow Folder Tree for WORKFLOW('{wf_key}') "
        msg += f"PURPOSE('{wf_purpose}')"
        return output_tree_view(msg, folder_tree)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_list_folder_tree() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_get_folder_tree() function
def WORKFLOW_get_folder_tree(wf_key: str, wf_purpose: str, bdm_DC: BudManAppDataContext_Base) -> Tree:
    """Obtain a folder tree based on wf_key and wf_purpose.

     A folder tree is a treelib.Tree object with the folders and files from a
     folder in the storage system, in this case a workflow folder.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.

        cmd should contain:
            - cp.CK_CMDLINE_WF_KEY: The ID of the folder to list files from.
            - cp.CK_CMDLINE_WF_PURPOSE: The purpose of the workflow, used to determine the folder.

    Returns:
        treelib.Tree: The folder tree for the specified workflow.
    """
    try:
        wf_purpose_folder_abs_path: Path.Path = bdm_DC.dc_WF_PURPOSE_FOLDER_abs_path(wf_key, wf_purpose)
        folder_tree: Tree = bsm_file_tree_from_folder(wf_purpose_folder_abs_path)
        return folder_tree
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_get_folder_tree() function
# ---------------------------------------------------------------------------- +
