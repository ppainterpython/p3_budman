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
    csv_DATA_LIST_remove_columns,
    csv_DATA_LIST_add_columns,
    csv_DATA_LIST_remove_extra_columns,
    csv_DATA_LIST_merge_columns,
    csv_DATA_LIST_rename_columns,
    csv_DATA_LIST_file_validate_header
)   
from .category_manager import BDMTXNCategoryManager, TXNCategoryMap
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
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

        # Resolve the header line question at the BSM file level.
        csv_path: Path = csv_txns_wb.abs_path()
        return_path: Path = csv_DATA_LIST_file_validate_header(csv_path, 
                                                               catmap_csv_file_input_columns,
                                                               inplace=True)

        # Load the .csv_txns workbook if it is not already loaded.
        if not csv_txns_wb.wb_loaded:
            success, result = bdm_DC.dc_WORKBOOK_load(csv_txns_wb)
            if not success:
                return False, result

        # Apply any column transformations specified in the category map for this fi_key.
        for transform, col_list in catmap_csv_file_column_transformations.items():
            data = None
            if transform == "remove":
                data = csv_DATA_LIST_remove_columns(csv_txns_wb.wb_content, col_list)
            elif transform == "merge":
                data = csv_DATA_LIST_merge_columns(csv_txns_wb.wb_content, col_list)
            elif transform == "rename":
                data = csv_DATA_LIST_rename_columns(csv_txns_wb.wb_content, col_list)
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
#region helper functions
def pad(level: int) -> str:
    """Helper function to create indentation padding for logging messages."""
    return "    " * level
#endregion helper functions
# ---------------------------------------------------------------------------- +
