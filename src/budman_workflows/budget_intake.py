# ---------------------------------------------------------------------------- +
#region budget_intake.py module
""" Financial Budget Workflow: "categorization" of transaction workbooks.

    Workflow: intake
    Input Folder: Financial Institution (FI) Input Folder
    Output Folder: Financial Institution (FI) Categorized Folder (CF)
    FI transaction workbooks can include excel files and csv files. 

    Workflow Pattern: Apply a workflow_process (function) to each item in the 
    input folder, placing items in the output folder as appropriate to the 
    configured function. Each WorkFLow instance in the config applies one 
    function to the input with resulting output.
"""
#endregion budget_intake.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from pathlib import Path
import re, logging, time, hashlib, datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass

# third-party modules and packages
import p3logging as p3l, p3_utils as p3u, p3_mvvm as p3m
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
import budman_command_processor as cp
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_data_context import BudManAppDataContext_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region INTAKE_TASK_process() function
def INTAKE_TASK_process(cmd: p3m.CMD_OBJECT_TYPE, 
             bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """Process workflow intake subcmd tasks.

    This function processes a workflow intake subcmd. Depending on the subcmd type,
    it delegates the processing to the appropriate task functions. There could
    be a variety of tasks depending on the value of the CK_INTAKE_TASK key.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.
    """
    try:
        # Assuming the cmd parameters have been validated before reaching this point.
        if cmd[cp.CK_INTAKE_TASK] == cp.CV_INTAKE_COPY_TASK:
            # Process the copy task. 
            return INTAKE_TASK_copy_file_to_wf_folder(cmd, bdm_DC)
        else:
            m = f"Unknown intake task: {cmd[cp.CK_INTAKE_TASK]}"
            return p3m.create_CMD_RESULT_ERROR(cmd, m)
    except Exception as e:
        return p3m.create_CMD_RESULT_EXCEPTION(cmd, e)
#endregion INTAKE_TASK_process() function
# ---------------------------------------------------------------------------- +
#region INTAKE_TASK_copy_file_to_wf_folder() function
def INTAKE_TASK_copy_file_to_wf_folder(
        cmd: p3m.CMD_OBJECT_TYPE, 
        bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """INTAKE_TASK: copy a file to a specified destination wf_folder.

    Workflow Intake Task to copy a file from the source wf_folder location 
    indicated by the cmd parameters CK_CMDLINE_WF_KEY and CK_CMDLINE_WF_PURPOSE
    using the CK_FILE_INDEX to identify the file to be copied. The destination
    wf_folder is specified by the current DC values for WF_KEY and WF_PURPOSE.

    Args:
        cmd (CMD_OBJECT_TYPE): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.
    """
    try:
        # Assume the cmd parameters have been validated before reaching this point.
        cmd_result : p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_result_status = True,
            result_content_type = p3m.CV_CMD_STRING_OUTPUT,
            result_content = "",
            cmd_object = cmd
        )
        # Current DC values of wf_key and wf_purpose are the destination 
        # folder for the file to be copied. CMDLINE file_index, wf_key and 
        # wf_purpose identify the file to copy. 
        # Source file parameters
        src_wf_key: str = cmd[cp.CK_CMDLINE_WF_KEY]
        src_wf_purpose: str = cmd[cp.CK_CMDLINE_WF_PURPOSE]
        src_file_index: int = cmd[cp.CK_FILE_INDEX]
        fi_key:str = bdm_DC.dc_FI_KEY
        file_tree = cp.BUDMAN_CMD_TASK_get_file_tree(fi_key, src_wf_key, 
                                                   src_wf_purpose, bdm_DC)
        p3u.is_not_obj_of_type("src_folder_tree", file_tree, Tree, raise_error=True)
        # file_trees are a BSM concern
        src_file: cp.BSMFile = cp.BUDMAN_CMD_FILE_SERVICE_get_BSMFile(file_tree, src_file_index)
        if not src_file:
            msg = f"Source file_index '{src_file_index}' not found "
            msg += f"in folder tree: {file_tree.root}"
            logger.error(msg)
            return p3m.create_CMD_RESULT_ERROR(cmd, msg)
        # Destination workflow folder
        dst_wf_key = bdm_DC.dc_WF_KEY
        dst_wf_purpose = bdm_DC.dc_WF_PURPOSE
        msg:str = f"copy file_index {src_file_index} from {src_wf_key} "
        msg += f"to {dst_wf_key} for {dst_wf_purpose}"
        cmd_result[p3m.CK_CMD_RESULT_CONTENT] = msg
        return cmd_result
    except Exception as e:
        return p3m.create_CMD_RESULT_EXCEPTION(cmd, e)
#endregion INTAKE_TASK_copy_file_to_wf_folder() function
# ---------------------------------------------------------------------------- +
#region convert_csv_txns_to_excel_txns() function
def convert_csv_txns_to_excel_txns(csv_txns: BDMWorkbook) -> Union[bool, str]:
    """Convert a WB_TYPE_CSV_TXNS workbook to a WB_TYPE_EXCEL_TXNS workbook.

    Args:
        csv_txns (BDMWorkbook): A csv transaction workbook.
        csv_path (Path): The path to the CSV file.

    Returns:
        Union[bool, str]: True if successful, or an error message if failed.
    """
    try:
        if not csv_txns or not isinstance(csv_txns, BDMWorkbook):
            return False, "No transactions to convert or invalid data format."
        csv_path: Path = csv_txns.abs_path()
        excel_filename: str = csv_path.stem + bdm.WB_TYPE_EXCEL_TXNS + bdm.WB_FILETYPE_XLSX
        excel_path: Path = csv_path.parent / excel_filename
        
        headers = list(csv_txns[0].keys())  # Get headers from the first row
        wb = Workbook()
        ws: Worksheet = wb.active
        ws.append(headers)  # Write headers to the first row
        
        for row in csv_txns:
            ws.append(list(row.values()))
        
        wb.save(excel_path)
        logger.debug(f"Saved excel_txns to {excel_path}")
        
        return True, f"Converted CSV transactions to Excel at {excel_path}"
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        return False, str(e)
#endregion convert_csv_txns_to_excel_txns() function
# ---------------------------------------------------------------------------- +
