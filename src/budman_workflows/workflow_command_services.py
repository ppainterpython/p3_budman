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
import budman_command_processor as cp
import budman_namespace as bdm
from budman_namespace import BDMWorkbook
from budget_domain_model import BudgetDomainModel
from budget_storage_model import BSMFile
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
        if cmd[p3m.CK_SUBCMD_KEY] == cp.CV_WORKFLOW_TRANSFER_SUBCMD_KEY:
            return WORKFLOW_TASK_transfer(cmd, bdm_DC)
        if cmd[p3m.CK_SUBCMD_KEY] == cp.CV_WORKFLOW_INTAKE_SUBCMD_KEY:
            return INTAKE_TASK_process(cmd, bdm_DC)
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
#region WORKFLOW_TASK_transfer() function
def WORKFLOW_TASK_transfer(cmd: p3m.CMD_OBJECT_TYPE, 
                    bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """WORKFLOW_TRANSFER_subcmd: Transfer data between workflows.

    Tasks required to transfer files from one workflow folder to another, either
    within a single workflow, or between different workflows. Processing
    requirements vary based on the specific workflows and file types involved.

    Arguments:
        cmd (CMD_OBJECT_TYPE): The command object to process.
        bdm_DC (BudManAppDataContext_Base): The data context for the BudMan application.
        Required cmd arguments:
            cp.CK_SRC_WF_KEY - src wf_folder wf_key
            cp.CK_SRC_WF_PURPOSE - src wf_folder purpose
            cp.CK_FILE_LIST - list of file_index values to transfer
            cp.CK_DST_WF_KEY - dst wf_folder wf_key
            cp.CK_DST_WF_PURPOSE - dst wf_folder purpose
            cp.CK_DST_WB_TYPE - dst workbook type

    Files are in wf_folders. A list of file_index values references files to 
    transfer from a source (src) workflow folder to a destination (dst) 
    wf_folder. Depending on the dst wf_key and wf_purpose, naming conventions 
    applied to the files being transferred. The dst wb_type also impacts the 
    dst filename and possible conversion, or transformation tasks applied during
    the transfer operation.

    At present, the workflow processes are fixed: intake, categorize_transactions,
    and budget. Each workflow may have up to three wf_folders configured for
    the wf_purpose values of: wf_input, wf_working, and wf_output. Also, a 
    wf_prefix value may be applied to files arriving anew in a wf_folder.

    Hence, a dst full_file_name could have the following structure:
        <wf_prefix><filename><wb_type>.<extension>

    The src_filename is parsed for the four components, wf_prefix may be None and
    wb_type may be None for a file that is not yet a workbook.

    The dst_filename is constructed considering the dst_wf_prefix and dst_wb_type.
    The extension is determined by the wb_type.

    Returns:
        p3m.CMD_RESULT_TYPE: The result of the command processing.

    Raises:
        p3m.CMDValidationException: For unrecoverable errors.
    """
    try:
        cmd_args: p3m.CMD_ARGS_TYPE = cp.validate_cmd_arguments(
            cmd=cmd, 
            bdm_DC=bdm_DC,
            cmd_key=cp.CV_WORKFLOW_CMD_KEY, 
            subcmd_key=cp.CV_WORKFLOW_TRANSFER_SUBCMD_KEY,
            required_args=[
                cp.CK_SRC_WF_KEY,
                cp.CK_SRC_WF_PURPOSE,
                cp.CK_FILE_LIST,
                cp.CK_DST_WF_KEY,
                cp.CK_DST_WF_PURPOSE,
                cp.CK_DST_WB_TYPE
            ]
        )
        # Extract and validate required parameters from the command.
        src_wf_key = cmd_args.get(cp.CK_SRC_WF_KEY)
        src_wf_purpose = cmd_args.get(cp.CK_SRC_WF_PURPOSE)
        src_file_list = cmd_args.get(cp.CK_FILE_LIST)
        dst_wf_key = cmd_args.get(cp.CK_DST_WF_KEY)
        dst_wf_purpose = cmd_args.get(cp.CK_DST_WF_PURPOSE)
        dst_wb_type = cmd_args.get(cp.CK_DST_WB_TYPE)

        # Validate the files indicated for a transfer. Raise error if any file is invalid.
        cmd_result = cp.validate_wf_folder_file_list(cmd, bdm_DC, src_file_list,
                                                     src_wf_key, src_wf_purpose)

        # Perform the data transfer operation tasks.
        bsm_files: List[cp.BSMFile] = cmd_result.get(p3m.CMD_RESULT_CONTENT, [])
        for bsm_file in bsm_files:
            # Process for supported transfer dst wb_types.
            if dst_wb_type == bdm.WB_TYPE_EXCEL_TXNS:
                # BUDMAN_CMD_TASK_transfer_to_excel_txns
                if bsm_file.extension == bdm.WB_FILETYPE_CSV:
                    # Convert to 
                    # BUDMAN_CMD_TASK_transfer_csv_file
                    pass
                elif bsm_file.extension == bdm.WB_FILETYPE_XLSX:
                    # BUDMAN_CMD_TASK_transfer_xlsx_file
                    pass
                else:
                    # Unsupported file type for transfer.
                    logger.error(f"Unsupported file type for transfer: {bsm_file.extension}")
                    continue
            else:
                # Unsupported dst wb_type for transfer.
                logger.error(f"Unsupported dst wb_type for transfer: {dst_wb_type}")
                continue
            # BUDMAN_CMD_TASK_construct_dst_file_url
            pass
        return p3m.create_CMD_RESULT_OBJECT(
            cmd_object=cmd,
            cmd_result_status=True,
            result_content_type=p3m.CMD_DICT_OUTPUT,
            result_content="all done"
        )
    except p3m.CMDValidationException as e:
        logger.error(e.message)
        raise
    except Exception as e:
        m = p3u.exc_err_msg(e)
        err_msg = (f"Exception during WORKFLOW_TASK_transfer: {m}")
        logger.error(err_msg)
        cmd_result_error = p3m.create_CMD_RESULT_ERROR(cmd, err_msg)
        raise p3m.CMDValidationException(cmd=cmd, 
                                         msg=err_msg,
                                         cmd_result_error=cmd_result_error)
#endregion WORKFLOW_TASK_transfer() function
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
