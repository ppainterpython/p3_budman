# ---------------------------------------------------------------------------- +
#region workflow_command_services.py module
""" workflow_command_services.py implements functions for BudMan app
workflow-related commands.

In general, services should return either data objects or command result objects.
Leave it to the caller, such as a View, or ViewMModel to handle additional
services, such as a pipeline, or to perform output functions.
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
from budget_domain_model import BudgetDomainModel
from budman_data_context import BudManAppDataContext_Base
from .budget_intake import *
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
        # If bdm_DC is bad, just raise an error.
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        # Should be called only for workflow cmd.
        cmd_result : p3m.CMD_RESULT_TYPE = cp.verify_cmd_key(cmd, cp.CV_WORKFLOW_CMD_KEY)
        if not cmd_result[p3m.CMD_RESULT_STATUS]: return cmd_result
        # Assuming the cmd parameters have been validated before reaching this point.
        # Process the CMD_OBJECT based on its CK_SUBCMD_KEY.
        # workflow intake command
        if cmd[p3m.CK_SUBCMD_KEY] == cp.CV_WORKFLOW_INTAKE_SUBCMD_KEY:
            return process_workflow_intake_tasks(cmd, bdm_DC)
        # workflow set command
        elif cmd[p3m.CK_SUBCMD_KEY] == cp.CV_SET_SUBCMD_KEY:
            # Process the set_value task.
            return WORKFLOW_TASK_set_value(cmd, bdm_DC)
        # workflow task sync command
        elif (cmd[p3m.CK_SUBCMD_KEY] == cp.CV_TASK_SUBCMD_KEY and
              cmd[cp.CK_TASK_NAME] == cp.CV_SYNC):
            # Process the wf sync task.
            recon: bool = cmd.get(cp.CK_RECONCILE, False)
            return WORKFLOW_TASK_sync_wdc(recon, bdm_DC)
        # workflow unknown command
        else:
            return p3m.unknown_CMD_RESULT_ERROR(cmd)
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
