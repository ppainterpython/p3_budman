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
import budman_settings as bdms
# import budman_command_services as cp
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_data_context import BudManAppDataContext_Base
from budget_domain_model import BudgetDomainModel
from budget_storage_model import (
    csv_DATA_LIST_has_header_row, 
    csv_DATA_LIST_add_header_row,
    csv_DATA_LIST_remove_columns,
    csv_DATA_LIST_add_columns
)   
from .txn_category import BDMTXNCategoryManager, TXNCategoryMap
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region INTAKE_SBCMD_router() function
# def INTAKE_SBCMD_router(cmd: p3m.CMD_OBJECT_TYPE, 
#              bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
#     """Process workflow intake subcmd tasks.

#     This function processes a workflow intake subcmd. Depending on the 
#     CK_INTAKE_TASK value in the cmd, it routes to the appropriate task function.
#     It delegates the processing to the appropriate task functions. There could
#     be a variety of tasks depending on the value of the CK_INTAKE_TASK key.

#     Args:
#         cmd (Dict[str, Any]): A valid BudMan View Model Command object.
#         bdm_DC (BudManAppDataContext_Base): The data context for the 
#             BudMan application.
#     """
#     try:
#         # Note: Each of the processing functions should do all necessary
#         # outout to the user, including error messages and exceptions.
#         # If bdm_DC is bad, just raise an error.
#         p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
#                                raise_error= True)
#         # Should be called only for workflow intake subcmd.
#         cmd_result : p3m.CMD_RESULT_TYPE = cp.verify_cmd_key(cmd, cp.CV_WORKFLOW_CMD_KEY)
#         if not cmd_result[p3m.CK_CMD_RESULT_STATUS]: return cmd_result
#         cmd_result : p3m.CMD_RESULT_TYPE = cp.verify_subcmd_key(cmd, cp.CV_INTAKE_SUBCMD_NAME)
#         if not cmd_result[p3m.CK_CMD_RESULT_STATUS]: return cmd_result
#         # Assuming the cmd parameters have been validated before reaching this point.
#         # Process the CMD_OBJECT based on its CK_INTAKE_TASK.
#         msg: str = ''
#         # Assuming the cmd parameters have been validated before this point.
#         if cmd[cp.CK_INTAKE_TASK] == cp.CV_INTAKE_COPY_TASK:
#             # Process the copy task. 
#             return INTAKE_TASK_copy_file_to_wf_folder(cmd, bdm_DC)
#         else:
#             msg = f"Unknown intake task: {cmd[cp.CK_INTAKE_TASK]}"
#             p3m.cp_user_info_message(msg)
#         return p3m.cp_CMD_RESULT_ERROR_create(cmd, msg)
#     except Exception as e:
#         return p3m.cp_CMD_RESULT_EXCEPTION_create(cmd, e)
#endregion INTAKE_SBCMD_router() function
# ---------------------------------------------------------------------------- +
#region INTAKE_TASK_convert_csv_file_schema() function
def INTAKE_TASK_convert_csv_txns_schema(csv_txns_wb: BDMWorkbook,
                                        bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT_TYPE:
    """workflow intake task: convert a .csv file schema to BudMan standard for
    .csv_txns workbook type.

    Workflow Intake Task to convert an intake/input .csv file schema from the 
    associate fi_key schema the builtin-in .csv_txns schema.

    Args:
        csv_txns_wb (BDMWorkbook): A valid BudMan Workbook object for .csv_txns.
        bdm_DC (BudManAppDataContext_Base): The data context for the BudMan application.
    """
    try:
        #region Initialization and validation
        succss: bool = False
        result: str = ''
        settings: bdms.BudManSettings = bdms.BudManSettings()
        catman: BDMTXNCategoryManager = BDMTXNCategoryManager(settings)
        fi_key: str = csv_txns_wb.fi_key
        catmap: TXNCategoryMap = catman.catalogs[fi_key]
        catmap_fi_key: str = catmap.category_map_fi_key
        catmap_csv_file_has_header: bool = catmap.csv_file_has_header
        catmap_csv_file_input_columns: List[str] = catmap.csv_file_input_columns
        catmap_csv_file_account_code: str = catmap.csv_file_account_code
        catmap_csv_file_column_transformations: Dict[str, List[str]] = catmap.csv_file_column_transformations
        #endregion Initialization and validation

        # Load the .csv_txns workbook if it is not already loaded.
        if not csv_txns_wb.wb_loaded:
            success, result = bdm_DC.dc_WORKBOOK_load(csv_txns_wb)
            if not success:
                return False, result
        # Check there is a correct header row in the .csv file.
        if not csv_DATA_LIST_has_header_row(csv_txns_wb.wb_content, catmap_csv_file_input_columns):
            # Add the correct header row to the original .csv data list.
            data: bdm.DATA_OBJECT_LIST_TYPE = csv_DATA_LIST_add_header_row(
                csv_txns_wb.wb_content, 
                catmap_csv_file_input_columns)
            csv_txns_wb.wb_content = data
            logger.debug(f"Added header row to .csv transactions data for "
                         f"fi_key '{fi_key}' using catmap_csv_file_input_columns:"
                         f" {catmap_csv_file_input_columns}")
            bdm_DC.dc_WORKBOOK_save(csv_txns_wb)
        # Apply any column transformations specified in the category map for this fi_key.
        for transform, col_list in catmap_csv_file_column_transformations.items():
            data = None
            if transform == "remove":
                data = csv_DATA_LIST_remove_columns(csv_txns_wb.wb_content, col_list)
            elif transform == "add":
                data = csv_DATA_LIST_add_columns(csv_txns_wb.wb_content, col_list)
            else:
                pass
            csv_txns_wb.wb_content = data
        bdm_DC.dc_WORKBOOK_save(csv_txns_wb)
        return True, "Successfully converted .csv file schema to BudMan standard for .csv_txns workbook type."
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        return False, str(e)
#endregion INTAKE_TASK_convert_csv_file_schema() function
# ---------------------------------------------------------------------------- +
#region INTAKE_TASK_copy_file_to_wf_folder() function
# def INTAKE_TASK_copy_file_to_wf_folder(
#         cmd: p3m.CMD_OBJECT_TYPE, 
#         bdm_DC: BudManAppDataContext_Base,
#         level: int = 0) -> p3m.CMD_RESULT_TYPE:
#     """workflow intake subcmd copy task: copy a .csv file to a specified 
#     destination wf_folder.

#     Workflow Intake subcmd Task to copy a file from the source wf_folder location 
#     indicated by the cmd parameters CK_CMDLINE_WF_KEY and CK_CMDLINE_WF_PURPOSE
#     using the CK_FILE_INDEX to identify the file to be copied. The destination
#     wf_folder is specified by the current DC values for WF_KEY and WF_PURPOSE.

#     Args:
#         cmd (CMD_OBJECT_TYPE): A valid BudMan View Model Command object.
#         bdm_DC (BudManAppDataContext_Base): The data context for the 
#             BudMan application.
#     """
#     try:
#         #region Initialization and validation
#         # Assume the cmd parameters have been validated before reaching this point.
#         level += 1
#         ts: str = "[bold dark_orange]CMD: [/bold dark_orange]"
#         m: str = f"{pad(level)}{ts} {INTAKE_TASK_copy_file_to_wf_folder.__name__}() "
#         # Start: ------------------------------------------------------------- +
#         p3m.cp_user_info_message(m + "Start: ...")
#         level += 1
#         # # Validate the cmd argsuments.
#         cmd_args: p3m.CMD_ARGS_TYPE = cp.validate_cmd_arguments(
#             cmd=cmd, 
#             bdm_DC=bdm_DC,
#             cmd_key=cp.CV_WORKFLOW_CMD_KEY, 
#             subcmd_key=cp.CV_INTAKE_SUBCMD_NAME,
#             model_aware=True,
#             required_args=[
#                 cp.CK_INTAKE_TASK,
#                 cp.CV_INTAKE_COPY_TASK,
#                 cp.CK_FILE_LIST,
#                 cp.CK_CMDLINE_WF_KEY,
#                 cp.CK_CMDLINE_WF_PURPOSE
#             ]
#         )
#         cmd_result : p3m.CMD_RESULT_TYPE = p3m.cp_CMD_RESULT_create(
#             status = True,
#             type = p3m.CV_CMD_STRING_OUTPUT,
#             content = "",
#             cmd = cmd
#         )
#         msg: str = 'Copy files task:'
#         model: BudgetDomainModel = bdm_DC.model
#         if (p3u.is_not_obj_of_type('bdm_DC.model',model, BudgetDomainModel)):
#             return cp.create_CMD_RESULT_ERROR(cmd, f"Invalid BudgetDomainModel: {model}")
#         bsm_file_tree : BSMFileTree = model.bsm_file_tree
#         if (p3u.is_not_obj_of_type('bsm_file_tree',bsm_file_tree, BSMFileTree)):
#             return cp.create_CMD_RESULT_ERROR(cmd, f"Invalid BSMFileTree in model: {bsm_file_tree}")
#         src_bsm_file: BSMFile = None
#         dst_wf_key: str = cmd[cp.CK_CMDLINE_WF_KEY]
#         if (p3u.str_empty(dst_wf_key) or not model.bdm_WF_KEY_validate(dst_wf_key)):
#             return cp.create_CMD_RESULT_ERROR(cmd, f"Invalid wf_key: '{dst_wf_key}'")
#         dst_wf_purpose: str = cmd[cp.CK_CMDLINE_WF_PURPOSE]
#         if (p3u.str_empty(dst_wf_purpose) or not model.bdm_WF_PURPOSE_validate(dst_wf_purpose)):
#             return cp.create_CMD_RESULT_ERROR(cmd, f"Invalid wf_purpose: '{dst_wf_purpose}'")
#         #endregion Initialization and validation

#         # The file indicated by cmd[cp.CK_FILE_INDEX] provide the 
#         # WF_KEY/WF_PURPOSE/WF_FOLDER of the src file to copy.
#         # The values of cmd[cp.CK_CMDLINE_WF_KEY] and 
#         # cmd[cp.CK_CMDLINE_WF_PURPOSE] indicate the destination WF)FOLDER
#         # where the file is copied. SRC to DST will imply transformation tasks
#         # to occur during the copy. The SRC file is never modified. The DST
#         # almost always is modified and has naming conventions applied.

#         for file_index in cmd[cp.CK_FILE_LIST]:
#             src_bsm_file: BSMFile = bsm_file_tree.get_BSMFile(file_index)
#             if not src_bsm_file:
#                 msg = f"Source file_index '{file_index}' not found "
#                 msg += f"in folder tree: {bsm_file_tree.root}"
#                 logger.error(msg)
#                 continue
#             logger.debug(f"BSMFile: {src_bsm_file}")
#             src_wf_key: str = src_bsm_file.wf_key
#             src_wf_purpose: str = src_bsm_file.wf_purpose
#             fi_key:str = src_bsm_file.fi_key
#             # Destination workflow folder
#             dst_wf_key = cmd[cp.CK_CMDLINE_WF_KEY]
#             dst_wf_purpose = cmd[cp.CK_CMDLINE_WF_PURPOSE]
#             msg:str = f"\n  copy file_index {file_index} from {src_wf_key} "
#             msg += f"to {dst_wf_key} for {dst_wf_purpose}"
#         cmd_result[p3m.CK_CMD_RESULT_CONTENT] = msg
#         # End: ------------------------------------------------------------- +
#         p3m.cp_user_info_message(m + "End: ...")
#         return cmd_result
#     except Exception as e:
#         return p3m.cp_CMD_RESULT_EXCEPTION_create(cmd, e)
#endregion INTAKE_TASK_copy_file_to_wf_folder() function
# ---------------------------------------------------------------------------- +
#region convert_csv_txns_to_excel_txns() function
# def convert_csv_txns_to_excel_txns(csv_txns: BDMWorkbook) -> Union[bool, str]:
#     """Convert a WB_TYPE_CSV_TXNS workbook to a WB_TYPE_EXCEL_TXNS workbook.

#     Args:
#         csv_txns (BDMWorkbook): A csv transaction workbook.
#         csv_path (Path): The path to the CSV file.

#     Returns:
#         Union[bool, str]: True if successful, or an error message if failed.
#     """
#     try:
#         if not csv_txns or not isinstance(csv_txns, BDMWorkbook):
#             return False, "No transactions to convert or invalid data format."
#         csv_path: Path = csv_txns.abs_path()
#         excel_filename: str = csv_path.stem + bdm.WB_TYPE_EXCEL_TXNS + bdm.WB_FILETYPE_XLSX
#         excel_path: Path = csv_path.parent / excel_filename
        
#         headers = list(csv_txns[0].keys())  # Get headers from the first row
#         wb = Workbook()
#         ws: Worksheet = wb.active
#         ws.append(headers)  # Write headers to the first row
        
#         for row in csv_txns:
#             ws.append(list(row.values()))
        
#         wb.save(excel_path)
#         logger.debug(f"Saved excel_txns to {excel_path}")
        
#         return True, f"Converted CSV transactions to Excel at {excel_path}"
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         return False, str(e)
#endregion convert_csv_txns_to_excel_txns() function
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region helper functions
def pad(level: int) -> str:
    """Helper function to create indentation padding for logging messages."""
    return "    " * level
#endregion helper functions
# ---------------------------------------------------------------------------- +
