# ---------------------------------------------------------------------------- +
#region budman_command_services.py module
""" budman_command_services.py implements functions for BudMan app commands.

    The budman_command_processor package provides modules with functions
    to execute validated commands within the BudMan application. In general,
    a CMD_OBJECT is dispatched to the appropriate command handler for execution.
    A handler will decompose a CMD_OBJECT into a series of CMD tasks to be
    executed.

    In general, services should return either data objects or command result 
    objects. Leave it to the caller, such as a View, or ViewMModel to handle 
    additional services, such as a pipeline, or to perform output functions.

    A key aspect of the BudMan application patterns is the treatement of 
    workbooks versus files. Workbooks returned in lists or tree objects are
    in the Budget Domain Model (BDM) abstraction, with the container structure
    being bdm_folder, bdm_FI_FOLDER, and wf_folders bases on wf_key and 
    wf_purpose. CMDs associated with workbooks use the "workbooks" parameter.

    Some CMDs are aimed at the files in the Budget Storage Model (BSM). Files
    returned in lists or tree objects are based on the configured storage model,
    but are the usual hierarchy of folders and files.
"""
#endregion budman_command_services.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, io, sys, getpass, time, copy, importlib
from pathlib import Path
from typing import List, Type, Optional, Dict, Tuple, Any, Callable
from datetime import datetime as dt

# third-party modules and packages
from arrow import now
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
from openpyxl import Workbook, load_workbook
from treelib import Tree
from rich import print
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree as RichTree
from rich.table import Table

# local modules and packages
import budman_command_processor as cp
import budman_namespace as bdm
import budman_settings as bdms
from budman_namespace import BDMWorkbook
from budget_domain_model import BudgetDomainModel
from budman_data_context import BudManAppDataContext_Base
from budget_storage_model import bsm_file_tree_from_folder
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region BudMan Application Command Task functions
# ---------------------------------------------------------------------------- +
#region CMD_TASK_process() function
def CMD_TASK_process(cmd: p3m.CMD_OBJECT_TYPE,
                     bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """Process a CMD_TASK command.

    Args:
        cmd (CMD_OBJECT_TYPE): The command object to process.
        bdm_DC (BudManAppDataContext_Base): The data context for the command.

    Returns:
        CMD_RESULT_TYPE: The result of the command processing.
    """
    try:
        # If bdm_DC is bad, just raise an error.
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        # Assuming the CMD_OBJECT has been validated before reaching this point.
        # Construct CMD_RESULT for return.
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_object=cmd
        )
        # Process the CMD_OBJECT based on its cmd_key and subcmd_key.
        if cmd[p3m.CK_CMD_KEY] == cp.CV_LIST_CMD_KEY:
            if cmd[p3m.CK_SUBCMD_KEY] == cp.CV_LIST_WORKBOOKS_SUBCMD_KEY:
                return CMD_TASK_list_workbooks(cmd, bdm_DC)
            elif cmd[cp.p3m.CK_SUBCMD_NAME] == cp.CV_BDM_STORE_SUBCMD_NAME:
                return CMD_TASK_list_bdm_store_json(cmd, bdm_DC)
            elif cmd[cp.p3m.CK_SUBCMD_NAME] == cp.CV_FILES_SUBCMD_NAME:
               return CMD_TASK_list_files(cmd, bdm_DC)
            else:
                return p3m.unknown_CMD_RESULT_ERROR(cmd)
        else:
            return p3m.unknown_CMD_RESULT_ERROR(cmd)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion CMD_TASK_process() function
# ---------------------------------------------------------------------------- +
#region CMD_TASK_list_workbooks()
def CMD_TASK_list_workbooks(cmd: p3m.CMD_OBJECT_TYPE,
        bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """List workbooks in the BudMan application data context.

    Args:
        cmd (CMD_OBJECT_TYPE): The command object to process.
        bdm_DC (BudManAppDataContext_Base): The data context for the BudMan application.
        CMD parameters:
            cp.CK_BDM_TREE (bool): --bdm_tree | -t switch, dispaly result as
            a tree, else display a table.
    Returns:
        p3m.CMD_RESULT_TYPE: The result of the command execution.
    """
    try:
        # Construct CMD_RESULT for return.
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_object=cmd
        )
        # check bdm_tree flag
        bdm_tree: bool = cmd.get(cp.CK_BDM_TREE, False)
        if bdm_tree:
            # Return all workbooks in a RichTree
            result_tree: RichTree = CMD_TASK_get_workbook_tree(bdm_DC)
            if result_tree is None:
                # Failed to construct the model_tree for workbooks
                cmd_result[p3m.CMD_RESULT_CONTENT] = "Model workbooks tree not constructed."
                cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_ERROR_STRING_OUTPUT
                logger.error(cmd_result[p3m.CMD_RESULT_CONTENT])
                return cmd_result
            # Success for workbook_tree
            cmd_result[p3m.CMD_RESULT_STATUS] = True
            cmd_result[p3m.CMD_RESULT_CONTENT] = result_tree
            cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_WORKBOOK_TREE_OBJECT
            return cmd_result
        else:
            # CMD_TASK_list_workbook_info_table()
            # List the workbooks selected by list command line arguments.
            selected_bdm_wb_list : List[BDMWorkbook] = None
            selected_bdm_wb_list = process_selected_workbook_input(cmd, bdm_DC)
            # Collect the wb info for workbooks in the selected_bdm_wb_list.
            # Construct the output dictionary result
            cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_WORKBOOK_INFO_TABLE
            cmd_result[p3m.CMD_RESULT_CONTENT] = list()
            for wb in selected_bdm_wb_list:
                wb_index = bdm_DC.dc_WORKBOOK_index(wb.wb_id)
                cmd_result[p3m.CMD_RESULT_CONTENT].append(wb.wb_info_dict(wb_index))
            if len(selected_bdm_wb_list) == 1:
                    bdm_DC.dc_WORKBOOK = wb
            # Success for workbook_tree
            cmd_result[p3m.CMD_RESULT_STATUS] = True
            return cmd_result
    except Exception as e:
        return p3m.create_CMD_RESULT_ERROR(cmd, e)
#endregion CMD_TASK_list_workbooks()
# ---------------------------------------------------------------------------- +
#region CMD_TASK_list_bdm_store_json()
def CMD_TASK_list_bdm_store_json(cmd: p3m.CMD_OBJECT_TYPE,
                                  bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """List the BDM store in JSON format.
    Args:
        cmd (CMD_OBJECT_TYPE): The command object to process.
        bdm_DC (BudManAppDataContext_Base): The data context for the BudMan application.
        CMD parameters:
            cp.CK_BDM_TREE (bool): --bdm_tree | -t switch, dispaly result as
            a tree, else display a table.
    Returns:
        p3m.CMD_RESULT_TYPE: The result of the command execution.
    """
    try:
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error=True)
        model: BudgetDomainModel = bdm_DC.model
        if not model:
            m = "No BudgetDomainModel binding in the DC."
            logger.error(m)
            return p3m.create_CMD_RESULT_OBJECT(
                cmd_object=cmd,
                cmd_result_status=False,
                result_content_type=p3m.CMD_STRING_OUTPUT,
                result_content=m
            )
        # Construct CMD_RESULT for return.
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_object=cmd
        )
        cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_JSON_OUTPUT
        cmd_result[p3m.CMD_RESULT_CONTENT] = bdm_DC.model.bdm_BDM_STORE_json()
        cmd_result[p3m.CMD_RESULT_STATUS] = True
        return cmd_result
    except Exception as e:
        return p3m.create_CMD_RESULT_ERROR(cmd, e)
#endregion CMD_TASK_list_bdm_store_json()
# ---------------------------------------------------------------------------- +    
#region CMD_TASK_list_files()
def CMD_TASK_list_files(cmd: p3m.CMD_OBJECT_TYPE,
                         bdm_DC: BudManAppDataContext_Base) -> p3m.CMD_RESULT_TYPE:
    """List the files in the BDM store.
    Args:
        cmd (CMD_OBJECT_TYPE): The command object to process.
        bdm_DC (BudManAppDataContext_Base): The data context for the BudMan application.
    Returns:
        p3m.CMD_RESULT_TYPE: The result of the command execution.
    """
    try:
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error=True)
        # Validate DC is Model-aware
        model: BudgetDomainModel = bdm_DC.model
        if not model:
            m = "No BudgetDomainModel binding in the DC."
            logger.error(m)
            return p3m.create_CMD_RESULT_OBJECT(
                cmd_object=cmd,
                cmd_result_status=False,
                result_content_type=p3m.CMD_STRING_OUTPUT,
                result_content=m
            )
        # Construct CMD_RESULT for return.
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_object=cmd
        )
        # If wf_key is not present in cmd, try to get it from the data context
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
        #if wf_purpose is not present in cmd, try to get it from the data context
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
        folder_tree: Tree = CMD_TASK_get_file_tree(fi_key, wf_key, wf_purpose, bdm_DC)
        if not folder_tree:
            cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_ERROR_STRING_OUTPUT
            cmd_result[p3m.CMD_RESULT_CONTENT] = (
                f"No wf_folder found for FI_KEY: "
                f"'{fi_key}', WF_KEY: '{wf_key}', WF_PURPOSE: '{wf_purpose}'"
            )
            logger.error(cmd_result[p3m.CMD_RESULT_CONTENT])
            return cmd_result
        cmd_result[p3m.CMD_RESULT_STATUS] = True
        cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_FILE_TREE_OBJECT
        cmd_result[p3m.CMD_RESULT_CONTENT] = folder_tree
        # msg = f"Workflow Folder Tree for WORKFLOW('{wf_key}') "
        # msg += f"PURPOSE('{wf_purpose}')"

        return cmd_result
    except Exception as e:
        return p3m.create_CMD_RESULT_ERROR(cmd, e)
#endregion CMD_TASK_list_files()
# ---------------------------------------------------------------------------- +    
#region CMD_TASK_get_workbook_tree() method
def CMD_TASK_get_workbook_tree(bdm_DC: BudManAppDataContext_Base) -> RichTree:
    """Return a workbook_tree (RichTree) for the BDM workbooks in bdm_DC."""
    try:
        st = p3u.start_timer()
        logger.debug(f"Start.")
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        model:BudgetDomainModel = bdm_DC.model
        now_str = dt.now().strftime("%Y-%m-%d %I:%M:%S %p")
        if not model:
            return None
        settings = bdms.BudManSettings()
        p3u.is_not_obj_of_type("settings", settings, bdms.BudManSettings, raise_error=True)
        bdm_store_full_filename = (settings[bdms.BDM_STORE_FILENAME] +
                                   settings[bdms.BDM_STORE_FILETYPE])
        bdm_folder = settings[bdms.BDM_FOLDER] + '/'
        purpose_icon = {
            "wf_input": ":inbox_tray:",
            "wf_output": ":outbox_tray:",
            "wf_working": ":gear:"
        }
        p_str: str = f"model['{bdm_folder + bdm_store_full_filename}'] {now_str}" 
        workbook_tree = RichTree(
            f":open_file_folder: {escape(p_str)}",
            guide_style="bold white"
        )
        wdc : bdm.WORKBOOK_DATA_COLLECTION_TYPE = None
        # For all Financial Institutions (FI) in the model.
        for fi_key, fi_obj in model.bdm_fi_collection.items():
            fi_folder = model.bdm_FI_FOLDER(fi_key)
            fi_name = model.bdm_FI_NAME(fi_key)
            # fi_key node.
            wdc = model.bdm_FI_WORKBOOK_DATA_COLLECTION(fi_key)
            count = len(wdc) if wdc else 0
            fi_key_branch = workbook_tree.add(
                f"[bold cyan]:open_file_folder: "
                f"'{fi_folder}' :bank: workbook count: '{count}'",
                guide_style="bold white"
            )
            if count == 0: 
                continue
            # Put the wdc in wb_index order, which is sorted by wb_id key.
            wdc = dict(sorted(wdc.items(), key=lambda item: item[0]))
            for wf_key, wf_folder_config_list in model.bdm_FI_WF_FOLDER_CONFIG_COLLECTION(fi_key).items():
                x_key = f"{fi_key}_{wf_key}"
                wf_key_branch = fi_key_branch.add(
                    f"[bold yellow]:repeat: {wf_key} workflow",
                    guide_style="bold white"
                )
                for wf_folder_config in wf_folder_config_list:
                    # wf_purpose node.
                    wf_purpose = wf_folder_config[bdm.WF_PURPOSE]
                    wf_folder = wf_folder_config[bdm.WF_FOLDER]
                    y_key = f"{fi_key}_{wf_key}_{wf_purpose}" # node key
                    wf_purpose_branch = wf_key_branch.add(
                        f"[bold gold3]:open_file_folder: '{wf_folder}' "
                        f"{purpose_icon.get(wf_purpose, '')}",
                        guide_style="bold white"
                    )
                    # wf_purpose workbook names.
                    wb_names = workbook_names(wdc, wf_key, wf_purpose)
                    logger.debug(f"FI: '{fi_key}', WF: '{wf_key}', WF_PURPOSE: '{wf_purpose}', workbooks({len(wb_names)}): {wb_names}")
                    if len(wb_names) > 0:
                        for wb_name in wb_names:
                            wf_purpose_branch.add(
                                f"[bold green]:page_facing_up: '{wb_name}' (wb_name)",
                            )
        logger.debug(f"Complete.")
        return workbook_tree
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        return None
#endregion CMD_TASK_get_workbook_tree
# ---------------------------------------------------------------------------- +    
#region CMD_TASK_get_file_tree() function
def CMD_TASK_get_file_tree(fi_key: str, wf_key: str, wf_purpose: str, 
                             bdm_DC: BudManAppDataContext_Base) -> Tree:
    """Obtain a file tree based on fi_key, wf_key and wf_purpose.

     A file tree is a treelib.Tree object with the folders and files from a
     folder in the storage system.

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
#endregion CMD_TASK_get_file_tree() function
# ---------------------------------------------------------------------------- +
#region extract_bdm_tree() function
def extract_bdm_tree(bdm_DC: BudManAppDataContext_Base) -> Tree:
    """Return a tree structure of the BDM in the provided DataContext."""
    try:
        st = p3u.start_timer()
        logger.debug(f"Start.")
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        model:BudgetDomainModel = bdm_DC.model
        now_str = dt.now().strftime("%Y-%m-%d %I:%M:%S %p")
        if not model:
            m = "No BudgetDomainModel binding in the DC."
            logger.error(m)
            return False, m
        settings = bdms.BudManSettings()
        p3u.is_not_obj_of_type("settings", settings, bdms.BudManSettings, raise_error=True)
        bdm_store_full_filename = (settings[bdms.BDM_STORE_FILENAME] +
                                   settings[bdms.BDM_STORE_FILETYPE])
        bdm_folder = settings[bdms.BDM_FOLDER] + '/'
        p_str: str = f"BDM_STORE['{bdm_folder + bdm_store_full_filename}'] {now_str}" 
        tree = Tree()
        tree.create_node(f"model: {p_str}", "root")  # root node
        wdc : bdm.WORKBOOK_DATA_COLLECTION_TYPE = None
        # For all Financial Institutions (FI) in the model.
        for fi_key, fi_obj in model.bdm_fi_collection.items():
            fi_folder = model.bdm_FI_FOLDER(fi_key)
            fi_name = model.bdm_FI_NAME(fi_key)
            # fi_key node.
            wdc = model.bdm_FI_WORKBOOK_DATA_COLLECTION(fi_key)
            if wdc is None or len(wdc) == 0:
                tag = f"'{fi_folder}' (fi_folder) workbook count: '0'"
                tree.create_node(tag, f"{fi_key}", parent="root")  # fi_key node
                continue
            tag = f"'{fi_folder}' (fi_folder) workbook count: '{len(wdc)}'"
            tree.create_node(tag, f"{fi_key}", parent="root") # fi_key node
            # Put the wdc in wb_index order, which is sorted by wb_id key.
            wdc = dict(sorted(wdc.items(), key=lambda item: item[0]))
            for wf_key, wf_folder_config_list in model.bdm_FI_WF_FOLDER_CONFIG_COLLECTION(fi_key).items():
                x_key = f"{fi_key}_{wf_key}"
                tree.create_node(f"{wf_key} workflow (wf_key)", x_key, parent=f"{fi_key}") # wf_key node
                for wf_folder_config in wf_folder_config_list:
                    # wf_purpose node.
                    wf_purpose = wf_folder_config[bdm.WF_PURPOSE]
                    wf_folder = wf_folder_config[bdm.WF_FOLDER]
                    y_key = f"{fi_key}_{wf_key}_{wf_purpose}" # node key
                    tree.create_node(f"'{wf_folder}' {wf_purpose} (wf_folder)", 
                                     y_key, parent=x_key) # wf_purpose node
                    # wf_purpose workbook names.
                    wb_names = workbook_names(wdc, wf_key, wf_purpose)
                    logger.debug(f"FI: '{fi_key}', WF: '{wf_key}', WF_PURPOSE: '{wf_purpose}', workbooks({len(wb_names)}): {wb_names}")
                    if len(wb_names) > 0:
                        for wb_name in wb_names:
                            tree.create_node(f"'{wb_name}' (wb_name)", # workbook node
                                             f"{y_key}_{wb_name}", 
                                             parent=y_key)
        print
        logger.debug(f"Complete.")
        return tree
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion extract_bdm_tree() function
# ---------------------------------------------------------------------------- +
#endregion BudMan Application Command Task functions
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region BudMan Application Command Helper functions
# ---------------------------------------------------------------------------- +
#region workbook_names() function
def workbook_names(wdc: bdm.WORKBOOK_DATA_COLLECTION_TYPE, wf_key: str, wf_purpose: str) -> List[str]:
    """Return a list of workbook names for the given wf_key and wf_purpose."""
    try:
        wb_name_list: List[str] = []
        if wdc is None or len(wdc) == 0:
            return wb_name_list
        wb_id_list: List[str] = list(wdc.keys())
        for wb_id,bdm_wb in wdc.items():
            if not isinstance(bdm_wb, bdm.BDMWorkbook):
                continue
            if bdm_wb.wf_key != wf_key:
                continue
            if bdm_wb.wf_purpose != wf_purpose:
                continue
            wb_index = wb_id_list.index(wb_id)
            name_str: str = f"{str(wb_index):>4} {bdm_wb.wb_name}"
            wb_name_list.append(name_str)
        return wb_name_list
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        return []
#endregion workbook_names() function
# ---------------------------------------------------------------------------- +
#region process_selected_workbook_input()
def process_selected_workbook_input(cmd: p3m.CMD_OBJECT_TYPE,
                                    bdm_DC: BudManAppDataContext_Base) -> List[BDMWorkbook]:
    """Process the workbook input from the command, return a list of 
    BDMWorkbooks, which may be empty.

    Arguments:
        cmd (Dict): A p3m.CMD_OBJECT.

    Returns:
        List[BDMWorkbook]: A list of BDMWorkbook objects.
    """
    try:
        # Extract common command attributes to select workbooks for task action.
        wb_list : List[int] = cmd.get(cp.CK_WB_LIST, [])
        all_wbs : bool = cmd.get(cp.CK_ALL_WBS, bdm_DC.dc_ALL_WBS)
        selected_bdm_wb_list : List[BDMWorkbook] = []
        load_workbook:bool = cmd.get(cp.CK_LOAD_WORKBOOK, False)
        if all_wbs:
            # If all_wbs is True, process all workbooks in the data context.
            selected_bdm_wb_list = list(bdm_DC.dc_WORKBOOK_DATA_COLLECTION.values())
        elif len(wb_list) > 0:
            for wb_index in wb_list:
                bdm_wb = bdm_DC.dc_WORKBOOK_by_index(wb_index)
                selected_bdm_wb_list.append(bdm_wb)
        else:
            # No workbooks selected by the command parameters.
            return selected_bdm_wb_list
        for bdm_wb in selected_bdm_wb_list:
            bdm_wb_abs_path = bdm_wb.abs_path()
            if bdm_wb_abs_path is None:
                selected_bdm_wb_list.remove(bdm_wb)
                m = f"Excluded workbook: '{bdm_wb.wb_id}', "
                m += f"workbook url is not valid: {bdm_wb.wb_url}"   
                logger.error(m)
                continue
            if load_workbook and not bdm_wb.wb_loaded:
                # Load the workbook content if it is not loaded.
                success, result = bdm_DC.dc_WORKBOOK_content_get(bdm_wb)
                if not success:
                    selected_bdm_wb_list.remove(bdm_wb)
                    m = f"Excluded workbook: '{bdm_wb.wb_id}', "
                    m += f"failed to load: {result}"
                    logger.error(m)
                    continue
                if not bdm_wb.wb_loaded:
                    logger.warning(f"Workbook '{bdm_wb.wb_id}' wb_loaded was False!")
                    bdm_wb.wb_loaded = True
                # self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id] = wb_content
        return selected_bdm_wb_list
    except Exception as e:
        m = f"Error processing workbook input: {p3u.exc_err_msg(e)}"
        logger.error(m)
        raise RuntimeError(m)
#endregion process_selected_workbook_input()
# ------------------------------------------------------------------------ +    
#region verify_cmd_key()
def verify_cmd_key( cmd: p3m.CMD_OBJECT_TYPE, 
                   expected_cmd_key: str) -> p3m.CMD_RESULT_TYPE:
    """Verify the command key in the command object.

    Args:
        cmd (Dict): A p3m.CMD_OBJECT.
        expected_cmd_key (str): The expected command key.

    Returns:
        CMD_RESULT_TYPE: True if the command key matches, False otherwise,
        with a returnable CMD_RESULT_TYPE.
    """
    cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
        cmd_result_status=True,
        result_content_type=p3m.CMD_STRING_OUTPUT,
        result_content=f"Expected cmd_key: {expected_cmd_key} is valid.",
        cmd_object=cmd
    )
    actual_cmd_key = cmd.get(p3m.CK_CMD_KEY)
    if actual_cmd_key != expected_cmd_key:
        # Invalid cmd_key
        m = (f"Invalid cmd_key: {cmd[p3m.CK_CMD_KEY]} "
             f"expected: {expected_cmd_key}")
        logger.error(m)
        cmd_result[p3m.CMD_RESULT_STATUS] = False
        cmd_result[p3m.CMD_RESULT_CONTENT] = m
        cmd_result[p3m.CMD_RESULT_CONTENT_TYPE] = p3m.CMD_ERROR_STRING_OUTPUT
    return cmd_result
#endregion verify_cmd_key()
