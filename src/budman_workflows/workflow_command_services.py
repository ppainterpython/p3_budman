# ---------------------------------------------------------------------------- +
#region workflow_command_services.py module
""" workflow_command_services.py implements functions for BudMan app
workflow-related commands.
"""
#endregion workflow_command_services.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging
from pathlib import Path
from typing import List, Type, Optional, Dict, Tuple, Any, Callable
from treelib import Tree
from datetime import datetime as dt

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_mvvm import (Model_Base, Model_Binding)
import budman_command_processor as cp
import budman_settings as bdms
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budget_storage_model import (
    bsm_file_tree_from_folder
)
from budget_domain_model import BudgetDomainModel
from budman_data_context import BudManAppDataContext_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_process() function
def WORKFLOW_TASK_process(cmd: p3m.CMD_OBJECT_TYPE, 
                       bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """Process workflow tasks.

    This function processes various worklow tasks as requested in the validated
    CMD_OBJECT.

    Args:
        cmd (CMD_OBJECT_TYPE): 
            A validated CommandProcessor CMD_OBJECT_TYPE. Contains
            the command attributes and parameters to execute.
        bdm_DC (BudManAppDataContext_Base): 
            The data context for the BudMan application.
    """
    try:
        # Assuming the cmd parameters have been validated before reaching this point.
        if cmd[cp.p3m.CK_SUBCMD_KEY] == cp.CV_SET_SUBCMD_KEY:
            # Process the set_value task.
            return WORKFLOW_TASK_set_value(cmd, bdm_DC)
        elif cmd[cp.p3m.CK_SUBCMD_KEY] == cp.CV_LIST_SUBCMD_KEY:
            # Process the list_folder_tree task.
            return WORKFLOW_TASK_list_folder_tree(cmd, bdm_DC)
        elif (cmd[cp.p3m.CK_SUBCMD_KEY] == cp.CV_TASK_SUBCMD_KEY and
              cmd[cp.CK_TASK_NAME] == cp.CV_SYNC):
            # Process the wf sync task.
            recon: bool = cmd.get(cp.CK_RECONCILE, False)
            return WORKFLOW_TASK_sync_wdc(recon, bdm_DC)
        else:
            m = f"Unknown workflow task: {cmd[cp.p3m.CK_SUBCMD_KEY]}"
            logger.error(m)
            return False, m
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_process() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_set_value() function
def WORKFLOW_TASK_set_value(cmd: Dict[str, Any], 
                       bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT_TYPE:
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
                      bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """List all files from an indicated workflow folder under current DC FI_KEY.

    Args:
        cmd (CMD_OBJECT_TYPE): 
            A validated CommandProcessor CMD_OBJECT_TYPE. Contains
            the command attributes and parameters to execute.
        bdm_DC (BudManAppDataContext_Base): 
            The data context for the BudMan application.
        cmd should contain:
            - cp.CK_CMDLINE_WF_KEY: The wf_key of interest.
            - cp.CK_CMDLINE_WF_PURPOSE: The wf_purpose of interest.

        Returns:
            p3m.CMD_RESULT_TYPE:
                The outcome of the command execution. 
    """
    try:
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_result_status=False,
            result_content_type=p3m.CMD_STRING_OUTPUT,
            result_content="No result content.",
            cmd_object=cmd
        )
        wf_key: str = cmd.get(cp.CK_CMDLINE_WF_KEY, None)
        if not wf_key:
            # No wf_key in cmdline, try DC
            wf_key = bdm_DC.dc_WF_KEY
            if not wf_key:
                # No wf_key to work with
                cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_ERROR_STRING_OUTPUT
                cmd_result[p3m.CMD_RESULT_CONTENT] = "No wf_key from cmd args or DC."
                logger.error(cmd_result[p3m.CMD_RESULT_CONTENT])
                return cmd_result
        wf_purpose: str = cmd.get(cp.CK_CMDLINE_WF_PURPOSE, None)
        if not wf_purpose:
            # No wf_purpose in cmdline, try DC
            wf_purpose = bdm_DC.dc_WF_PURPOSE
            if not wf_purpose:
                # No wf_purpose to work with
                cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_ERROR_STRING_OUTPUT
                cmd_result[p3m.CMD_RESULT_CONTENT] = "No wf_purpose from cmd args or DC."
                logger.error(cmd_result[p3m.CMD_RESULT_CONTENT])
                return cmd_result
        fi_key: str = bdm_DC.dc_FI_KEY
        folder_tree: Tree = WORKFLOW_get_folder_tree(fi_key, wf_key, wf_purpose, bdm_DC)
        if not folder_tree:
            cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_ERROR_STRING_OUTPUT
            cmd_result[p3m.CMD_RESULT_CONTENT] = (
                f"No wf_folder found for FI_KEY: "
                f"'{fi_key}', WF_KEY: '{wf_key}', WF_PURPOSE: '{wf_purpose}'"
            )
            logger.error(cmd_result[p3m.CMD_RESULT_CONTENT])
            return cmd_result
        msg = f"Workflow Folder Tree for WORKFLOW('{wf_key}') "
        msg += f"PURPOSE('{wf_purpose}')"
        # TODO: Convert return to cmd_result
        return cp.output_tree_view(msg, folder_tree)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_list_folder_tree() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_sync_wdc() function
def WORKFLOW_TASK_sync_wdc(reconcile:bool, 
                           bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT_TYPE:
    """Model-Aware: Sync the WORKBOOK_DATA_COLLECTION for the current FI_KEY.

    For the current DC FI_KEY, synchronize the WORKBOOK_DATA_COLLECTION with 
    files in storage. Use the BSM functions.

    Args:
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.

    Returns:
        treelib.Tree: The folder tree for the specified workflow.
    """
    try:
        st = p3u.start_timer()
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        fi_key: str = bdm_DC.dc_FI_KEY
        if not fi_key:
            m = "No FI_KEY set in the DC."
            logger.error(m)
            return False, m
        model:BudgetDomainModel = bdm_DC.model
        if not model:
            m = "No BudgetDomainModel binding in the DC."
            logger.error(m)
            return False, m
        task_name: str = "sync_wdc()"
        msg: str = f"Syncing WORKBOOK_DATA_COLLECTION for FI_KEY: '{fi_key}'"
        logger.debug(f"Start Task: {task_name} {msg}")
        r_msg: str = ""
        discovered_wdc: bdm.WORKBOOK_DATA_COLLECTION_TYPE = None
        discovered_wdc, r_msg = model.bsm_FI_WORKBOOK_DATA_COLLECTION_resolve(fi_key)
        return True, msg
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_sync_wdc() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_get_folder_tree() function
def WORKFLOW_get_folder_tree(fi_key: str, wf_key: str, wf_purpose: str, 
                             bdm_DC: BudManAppDataContext_Base) -> Tree:
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
        # Validate the model binding.
        model: BudgetDomainModel = bdm_DC.model
        if not model:
            m = "No BudgetDomainModel binding in the DC."
            logger.error(m)
            raise ValueError(m)
        fi_wf_folder_url: str = model.bdm_FI_WF_FOLDER_URL(fi_key, wf_key, 
                                                           wf_purpose, 
                                                           raise_errors=False)
        if not fi_wf_folder_url:
            return None
        folder_tree: Tree = bsm_file_tree_from_folder(fi_wf_folder_url)
        return folder_tree
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_get_folder_tree() function
# ---------------------------------------------------------------------------- +
