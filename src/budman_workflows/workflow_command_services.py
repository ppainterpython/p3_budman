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
import logging, shutil
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
from budman_data_context import BudManAppDataContext_Base
from budget_storage_model import (BSMFile, BSMFileTree,
                                  csv_DATA_LIST_url_get) 
from .budget_intake import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region WORKFLOW_CMD_process() function
def WORKFLOW_CMD_process(cmd: p3m.CMD_OBJECT_TYPE, 
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
#endregion WORKFLOW_CMD_process() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_transfer() function
def WORKFLOW_TASK_transfer(cmd: p3m.CMD_OBJECT_TYPE, 
                    bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """WORKFLOW_TRANSFER_subcmd: Transfer data between workflows.

    Tasks required to transfer files to a workflow for a specified purpose.
    Processing requirements vary based on the specific workflow, purpose and 
    workbook types.

    Arguments:
        cmd (CMD_OBJECT_TYPE): The command object to process.
        bdm_DC (BudManAppDataContext_Base): The data context for the BudMan application.
        Required cmd arguments:
            cp.CK_FILE_LIST - list of file_index values from the file_list
            cp.CK_WF_KEY - wf_folder wf_key
            cp.CK_WF_PURPOSE - wf_folder wf_purpose
            cp.CK_WB_TYPE - dst workflow workbook type

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
        # Validate the cmd argsuments.
        cmd_args: p3m.CMD_ARGS_TYPE = cp.validate_cmd_arguments(
            cmd=cmd, 
            bdm_DC=bdm_DC,
            cmd_key=cp.CV_WORKFLOW_CMD_KEY, 
            subcmd_key=cp.CV_WORKFLOW_TRANSFER_SUBCMD_KEY,
            model_aware=True,
            required_args=[
                cp.CK_FILE_LIST,
                cp.CK_WF_KEY,
                cp.CK_WF_PURPOSE,
                cp.CK_WB_TYPE
            ]
        )
        model: BudgetDomainModel = bdm_DC.model
        bsm_file_tree : BSMFileTree = model.bsm_file_tree
        # Extract and validate required parameters from the command.
        wf_key = cmd_args.get(cp.CK_WF_KEY)
        wf_purpose = cmd_args.get(cp.CK_WF_PURPOSE)
        src_file_list = cmd_args.get(cp.CK_FILE_LIST)
        wb_type = cmd_args.get(cp.CK_WB_TYPE)
        fi_key: str = bdm_DC.dc_FI_KEY
        bsm_files: List[cp.BSMFile] = []
        bsm_files = bsm_file_tree.validate_file_list(src_file_list)
        result_content: str = ""
        msg: str = ""
        # Supported cases:
        # 1. transfer .csv files from file_list to a .csv_txns workbooks
        success: bool = False
        result: str = ""
        bsm_file: BSMFile = None
        cvs_wb: BDMWorkbook = None
        for bsm_file in bsm_files:
            # Process for supported transfer dst wb_types.
            if wb_type == bdm.WB_TYPE_CSV_TXNS:
                # Transfer a csv file to a csv_txns workbook.
                # Input file must have .csv extension.
                if bsm_file.extension == bdm.WB_FILETYPE_CSV:
                    # Transfer a .csv file to a .csv_txns workbook.
                    # Create a file_url for the new file being transferred.
                    success, result = WORKFLOW_TASK_construct_bdm_workbook(
                        src_filename=bsm_file.filename,
                        wb_type=wb_type,
                        fi_key=fi_key,
                        wf_key=wf_key,
                        wf_purpose=wf_purpose,
                        bdm_DC=bdm_DC
                    )
                    if not success:
                        msg = (f"Failed to construct file URL for file: "
                               f"'{bsm_file.file_index:2}:{bsm_file.full_filename}'"
                               f" Error: {result}")
                        logger.error(msg)
                        result_content += msg + "\n"
                        continue
                    csv_wb = result
                    success, result = WORKFLOW_TASK_transfer_csv_file_to_workbook(
                        src_file_url=bsm_file.file_url,
                        dst_wb=csv_wb,
                        wb_type=wb_type
                    )
                    if not success:
                        msg = (f"Failed to transfer file: "
                               f"'{bsm_file.file_index:2}:{bsm_file.full_filename}' "
                               f" to .csv_txns workbook. Error: {result}")
                        logger.error(msg)
                        result_content += msg + "\n"
                        continue
                else:
                    # Unsupported file type for transfer.
                    msg = (f"Unsupported source file type file "
                            f"'{bsm_file.file_index:2}:{bsm_file.full_filename}'"
                            f" must be .csv file.")
                    logger.error(msg)
                    result_content += msg + "\n"
                    continue
                # Add the new workbook to the wdc.
                wdc = bdm_DC.dc_WORKBOOK_DATA_COLLECTION
                wb_id = csv_wb.wb_id
                wdc[wb_id] = csv_wb
            else:
                # Unsupported dst wb_type for transfer.
                msg = (f"Unsupported destination workbook type for transfer: {wb_type}")
                logger.error(msg)
                result_content += msg + "\n"
                continue
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
#region WORKFLOW_TASK_transfer_csv_file()
def WORKFLOW_TASK_transfer_csv_file_to_workbook(src_file_url: str,
                                    dst_wb: BDMWorkbook,
                                    wb_type: str) -> bdm.BUDMAN_RESULT_TYPE:
    """Transfer a CSV file to the specified wb_type.

    Args:
        src_file_url (str): The source file URL.
        dst_wb (BDMWorkbook): The destination workbook object.
        wb_type (str): The desired workbook type for the destination workbook.

    Returns:
        bdm.BUDMAN_RESULT_TYPE: The result of the transfer operation.
    """
    try:
        if wb_type == bdm.WB_TYPE_CSV_TXNS:
            # bsm_file must be a .csv file. Transfer to .csv_txns workbook
            # is just a copy to the new file_url.
            src: Path = Path.from_uri(src_file_url)
            dst: Path = Path.from_uri(dst_wb.wb_url)
            shutil.copyfile(src, dst)
            return True, f"Transferred .csv to .csv_txns workbook: {dst_wb.wb_url}"
        else:
            err_msg = f"Unsupported wb_type for CSV transfer: {wb_type}"
            logger.error(err_msg)
            return False, err_msg
    except Exception as e:
        m = p3u.exc_err_msg(e)
        err_msg = (f"Exception transfer_csv_file_to_workbook(): {m}")
        logger.error(err_msg)
        return False, err_msg
#endregion WORKFLOW_TASK_transfer_csv_file()
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
        msg: str = f"DEPRECATED: Syncing WORKBOOK_DATA_COLLECTION for FI_KEY: '{fi_key}'"
        logger.debug(f"Start Task: {task_name} {msg}")
        r_msg: str = ""
        # discovered_wdc: bdm.WORKBOOK_DATA_COLLECTION_TYPE = None
        # discovered_wdc, r_msg = model.bsm_FI_WORKBOOK_DATA_COLLECTION_resolve(fi_key)
        return True, msg
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion WORKFLOW_TASK_sync_wdc() function
# ---------------------------------------------------------------------------- +
#region WORKFLOW_TASK_contstruct_wb_file_url() function
def WORKFLOW_TASK_construct_bdm_workbook(src_filename: str,
                                       wb_type: str,
                                       fi_key: str,
                                       wf_key: str,
                                       wf_purpose: str,
                                       bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT_TYPE:
    """Construct a workbook file URL based on the provided parameters.
    This function targets a workbook file url for for filename using:
        fi_key, wf_key, wf_purpose and wb_type.

    Args:
        filename (str): The base filename without extension.
        wb_type (str): The workbook type (e.g., 'excel_txns').
        fi_key (str): The financial institution key.
        wf_key (str): The workflow key.
        wf_purpose (str): The workflow purpose.

    Returns:
        bdm.BUDMAN_RESULT_TYPE: A tuple containing boolean indicating success, 
        and the constructed workbook file URL or an error message.
    """
    try:
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        model:BudgetDomainModel = bdm_DC.model
        if not model:
            m = "No BudgetDomainModel binding in the DC."
            logger.error(m)
            return False, m
        # Validate the provided parameters.
        if p3u.str_empty(src_filename):
            m = "Empty filename provided."
            logger.error(m)
            return False, m
        if not model.bdm_FI_KEY_validate(fi_key):
            m = f"Invalid fi_key: '{fi_key}'"
            logger.error(m)
            return False, m
        if not model.bdm_WF_KEY_validate(wf_key):
            m = f"Invalid wf_key: '{wf_key}'"
            logger.error(m)
            return False, m
        if not model.bdm_WF_PURPOSE_validate(wf_purpose):
            m = f"Invalid wf_purpose: '{wf_purpose}'"
            logger.error(m)
            return False, m
        if wb_type not in bdm.VALID_WB_TYPE_VALUES:
            m = f"Invalid wb_type: '{wb_type}'"
            logger.error(m)
            return False, m
        # Construct the workbook file URL.
        wb_extension: str = bdm.WB_FILETYPE_MAP[wb_type]
        wb_prefix: str = model.bdm_FI_WF_FOLDER_CONFIG_ATTRIBUTE(
            fi_key=fi_key, wf_key=wf_key, wf_purpose=wf_purpose,
            attribute=bdm.WF_PREFIX, raise_errors=True)
        wf_folder_url: str = model.bdm_FI_WF_FOLDER_CONFIG_ATTRIBUTE(
            fi_key=fi_key, wf_key=wf_key, wf_purpose=wf_purpose,
            attribute=bdm.WF_FOLDER_URL, raise_errors=True)
        wf_folder: str = model.bdm_FI_WF_FOLDER_CONFIG_ATTRIBUTE(
            fi_key=fi_key, wf_key=wf_key, wf_purpose=wf_purpose,
            attribute=bdm.WF_FOLDER, raise_errors=True)
        filename = f"{wb_prefix}{src_filename}{wb_type}"
        full_filename: str = f"{filename}{wb_extension}"
        folder_path = Path.from_uri(wf_folder_url) 
        file_path = folder_path / full_filename
        # Check if the dst file already exists.
        if file_path.exists():
            m = (f"Destination file already exists: "
                 f"'{file_path.as_uri()}'")
            logger.error(m)
        file_url: str = file_path.as_uri()
        new_wb: BDMWorkbook = BDMWorkbook()
        new_wb.wb_type = wb_type
        new_wb.wb_name = full_filename
        new_wb.wb_filename = filename
        new_wb.wb_filetype = wb_extension
        new_wb.wb_url = file_url
        new_wb.fi_key = fi_key
        new_wb.wf_key = wf_key
        new_wb.wf_purpose = wf_purpose
        new_wb.wf_folder_url = wf_folder_url
        new_wb.wf_folder = wf_folder
        return True, new_wb
    except Exception as e:
        m = p3u.exc_err_msg(e)
        err_msg = (f"Exception during WORKFLOW_TASK_construct_wb_file_url: {m}")
        logger.error(err_msg)
        return False, err_msg
#endregion WORKFLOW_TASK_contstruct_wb_file_url() function
# ---------------------------------------------------------------------------- +
