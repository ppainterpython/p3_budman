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
import re, pathlib as Path, logging, time, hashlib, datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass

# third-party modules and packages
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
import budman_command_processor.budman_cp_namespace as cp
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
from .workflow_utils import (
    categorize_transaction, category_map_count, check_register_map,
    category_histogram, clear_category_histogram, get_category_histogram,
)
from .txn_category import BDMTXNCategoryManager
from budman_data_context import BudManAppDataContext_Base
from budget_storage_model import (
    bsm_file_tree_from_folder, bsm_get_folder_structure,
)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region process_workflow_intake_tasks() function
def process_workflow_intake_tasks(cmd: Dict[str, Any], 
                       bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """Process workflow intake tasks.

    This function processes a transaction intake task command.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_DC (BudManAppDataContext_Base): The data context for the 
            BudMan application.
    """
    try:
        # Assuming the cmd parameters have been validated before reaching this point.
        if cmd[cp.CK_INTAKE_TASK] == cp.CV_INTAKE_MOVE_TASK:
            # Process the move task.
            return True, "Move task processing not implemented yet."
        elif cmd[cp.CK_INTAKE_TASK] == cp.CV_INTAKE_LIST_TASK:
            # Process the list task.
            return list_intake_files(cmd, bdm_DC)
        else:
            m = f"Unknown intake task: {cmd[cp.CK_INTAKE_TASK]}"
            logger.error(m)
            return False, m
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion process_workflow_intake_tasks() function
# ---------------------------------------------------------------------------- +
#region list_intake_files() function
def list_intake_files(cmd: Dict[str, Any],
                      bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """List all files from an indicated folder.

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
        cmd_result[bdm.CMD_RESULT_CONTENT] = folder_tree
        return True, cmd_result
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion list_intake_files() function
# ---------------------------------------------------------------------------- +
#region process_txn_intake() function
def process_txn_intake(cmd: Dict[str, Any], 
                       bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """Process a transaction intake tasks.

    This function processes a transaction intake command by loading the 
    transaction workbook, validating it, categorizing transactions, and saving 
    the categorized workbook.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_data_context (BudManAppDataContext_Base): The data context for the 
            BudMan application.
    """
    try:
        st = p3u.start_timer()
        fr: str = "Process transaction intake tasks:"
        logger.debug(f"{fr} {cmd}")
        bdm_wb: BDMWorkbook
        wb_index: int = cmd[cp.CK_WB_INDEX]
        all_wbs: bool = cmd[cp.CK_ALL_WBS]
        bdm_wb = bdm_DC.dc_WORKBOOK_by_index(wb_index)
        if bdm_wb is None:
            m = f"wb_index '{wb_index}' is not valid."
            logger.error(m)
            fr += f"\n{m}"
            return False, fr
        # Task 1: Load the csv_txns workbook
        success, result = bdm_DC.dc_WORKBOOK_content_get(bdm_wb) 
        if not success:
            return False, result
        csv_txns: bdm.DATA_LIST = result
        # Task 2: Convert the csv_txns to a excel_txns
        csv_path: Path.Path = bdm_wb.abs_path()
        if not csv_path:
            m = f"Workbook path is not valid: {bdm_wb.wb_url}"
            logger.error(m)
            return False, m
        excel_filename: str = csv_path.stem + bdm.WB_TYPE_EXCEL_TXNS + bdm.WB_FILETYPE_XLSX
        excel_path : Path = csv_path.parent / excel_filename
        headers = list(csv_txns[0].keys())  # Get headers from the first row
        
        wb_content = Workbook() # Create a new Excel workbook.
        ws: Worksheet = wb_content.active
        #TODO: get the worksheet title from settings or config.
        ws.title = "TransactionData" # Set the name of the first worksheet.

        ws.append(headers)  # Write headers to the first row
        # Need to convert date strings to datetime objects, and
        # convert amount strings to float.
        for row in csv_txns:
            for key, value in row.items():
                if key.lower() == "date":
                    value = datetime.datetime.strptime(value, "%m/%d/%Y").date()
                elif key.lower() == "amount":
                    cleaned = re.sub(r'[^\d.-]', '', value)  # Remove non-numeric characters
                    value = float(cleaned)
                row[key] = value
            ws.append(list(row.values()))
        # Task 3: Save the excel_txns workbook
        wb_content.save(excel_path)
        logger.debug(f"Saved excel_txns to {excel_path}")

        return True, f"Workflow Intake Tasks: "
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
                    # row[key].number_format = '#,##0.00'  # Set currency format in Excel
                    # row[key].number_format = 'DD/MM/YYYY'  # Set date format in Excel
#endregion process_txn_intake() function
# ---------------------------------------------------------------------------- +
#region convert_csv_txns_to_excel_txns() function
def convert_csv_txns_to_excel_txns(csv_txns: BDMWorkbook) -> Union[bool, str]:
    """Convert a WB_TYPE_CSV_TXNS workbook to a WB_TYPE_EXCEL_TXNS workbook.

    Args:
        csv_txns (BDMWorkbook): A csv transaction workbook.
        csv_path (Path.Path): The path to the CSV file.

    Returns:
        Union[bool, str]: True if successful, or an error message if failed.
    """
    try:
        if not csv_txns or not isinstance(csv_txns, BDMWorkbook):
            return False, "No transactions to convert or invalid data format."
        csv_path: Path = csv_txns.abs_path()
        excel_filename: str = csv_path.stem + bdm.WB_TYPE_EXCEL_TXNS + bdm.WB_FILETYPE_XLSX
        excel_path: Path.Path = csv_path.parent / excel_filename
        
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
#region check_schema_intake() function
def check_schema_intake(cmd: Dict[str, Any], bdm_DC: BudManAppDataContext_Base) -> bdm.BUDMAN_RESULT:
    """Check the schema of an intake workbook.

    For one or more designated workbooks, check their schema for their
    wb_type for intake.

    Args:
        cmd (Dict[str, Any]): A valid BudMan View Model Command object.
        bdm_data_context (BudManAppDataContext_Base): The data context for the 
            BudMan application.
    """
    try:
        st = p3u.start_timer()
        logger.debug(f"Process transaction intake tasks: {cmd}")
        bdm_wb: BDMWorkbook
        # Obtain the workbook.
        wb_index: int = cmd[cp.CK_WB_INDEX]
        all_wbs: bool = cmd[cp.CK_ALL_WBS]
        if all_wbs:
            # If all_wbs is True, process all workbooks in the data context.
            return False, "method not implemented for all_wbs=True"
        bdm_wb = bdm_DC.dc_WORKBOOK_by_index(wb_index)
        if bdm_wb is None:
            m = f"wb_index '{wb_index}' is not valid."
            logger.error(m)
            return False, m
        # Depending on the wb_type, check workbook schema.
        if bdm_wb.wb_type == bdm.WB_TYPE_CSV_TXNS:
            ...
        elif bdm_wb.wb_type == bdm.WB_TYPE_EXCEL_TXNS:
            ...
        elif bdm_wb.wb_type == bdm.WB_TYPE_TXN_REGISTER:
            ...
        elif  bdm_wb.wb_type == bdm.WB_TYPE_TXN_CATEGORIES:
            ...




        success, result = bdm_DC.dc_WORKBOOK_content_get(bdm_wb) 
        if not success:
            return False, result
        csv_txns: bdm.DATA_LIST = result
        # Task 2: Convert the csv_txns to a excel_txns
        csv_path: Path.Path = bdm_wb.abs_path()
        if not csv_path:
            m = f"Workbook path is not valid: {bdm_wb.wb_url}"
            logger.error(m)
            return False, m
        excel_filename: str = csv_path.stem + bdm.WB_TYPE_EXCEL_TXNS + bdm.WB_FILETYPE_XLSX
        excel_path : Path = csv_path.parent / excel_filename
        headers = list(csv_txns[0].keys())  # Get headers from the first row
        wb = Workbook()
        ws: Worksheet = wb.active
        ws.append(headers)  # Write headers to the first row
        for row in csv_txns:
            ws.append(list(row.values()))
        wb.save(excel_path)
        logger.debug(f"Saved excel_txns to {excel_path}")

        return True, f"Workflow Intake Tasks: "
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion check_schema_intake() function
# ---------------------------------------------------------------------------- +
