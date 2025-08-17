# ---------------------------------------------------------------------------- +
#region budman_command_services.py module
""" budman_command_services.py implements functions for BudMan app commands.
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
from rich.console import Console
from rich.table import Table

# local modules and packages
import budman_command_processor as cp
import budman_namespace as bdm
import budman_settings as bdms
from budget_domain_model import BudgetDomainModel
from budman_data_context import BudManAppDataContext_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
console = Console(force_terminal=True, width=bdm.BUDMAN_WIDTH, highlight=True,
                  soft_wrap=False)
#endregion Globals and Constants
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
#region output_model_tree() methond
def output_model_tree(bdm_DC: BudManAppDataContext_Base) -> None:
    """Output a rich tree for the model to the console."""
    try:
        st = p3u.start_timer()
        logger.debug(f"Start.")
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base,
                               raise_error= True)
        model:BudgetDomainModel = bdm_DC.model
        now_str = dt.now().strftime("%Y-%m-%d %I:%M:%S %p")
        if not model:
            console.print(f"[red]Error:[/red] No model to display.")
            return
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
        model_tree = RichTree(
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
            fi_key_branch = model_tree.add(
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
        print(model_tree)
        return
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        console.print(f"[red]Error:[/red] {m}")
        return
#endregion output_model_tree
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
#region output_tree_view() function
def output_tree_view(tree_view:Tree=None) -> p3m.CMD_RESULT_TYPE:
    """Create p3_mvvm.CMD_RESULT_TYPE with the content of the tree view."""
    try:
        # Format the tree for output
        original_stdout = sys.stdout  # Save the original stdout
        buffer = io.StringIO()
        sys.stdout = buffer  # Redirect stdout to capture tree output
        tree_view.show()
        sys.stdout = original_stdout  # Reset stdout
        cmd_result = p3m.CMD_RESULT_OBJECT(
            cmd_result_status=True,
            result_content_type=bdm.CLIVIEW_WORKBOOK_TREE_VIEW,
            result_content=buffer.getvalue()
        )
        return cmd_result
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        return m
#endregion output_tree_view() function
# ---------------------------------------------------------------------------- +
