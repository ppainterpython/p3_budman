# ---------------------------------------------------------------------------- +
#region workflow_utils.py module
""" Financial Budget Workflow: "categorization" of transaction workbooks.

    Workflow: categorization
    Input Folder: Financial Institution (FI) Incoming Folder (IF)
    Output Folder: Financial Institution (FI) Categorized Folder (CF)
    FI transaction workbooks are typically excel files. 

    Workflow Pattern: Apply a workflow_process (function) to each item in the 
    input folder, placing items in the output folder as appropriate to the 
    configured function. Each WorkFLow instance in the config applies one 
    function to the input with resulting output.

    TODO: Consider xlwings package for Excel integration.
"""
#endregion workflow_utils.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import re, pathlib as Path, logging, io, sys, time, hashlib, datetime
import csv
from datetime import datetime as dt
from typing import Dict, List, Optional, Union, Tuple

# third-party modules and packages
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_namespace.design_language_namespace import P2
import budman_settings as bdms
import budman_namespace as bdm
from budman_data_context import BudManAppDataContext_Base
from budget_storage_model import (
    bsm_BDM_STORE_url_get,
    bsm_WORKBOOK_CONTENT_url_put
)
from .txn_category import (
    BDMTXNCategoryManager, 
    TXNCategoryCatalog, 
    BDMTXNCategory
) 
from .budget_category_mapping import (
    compiled_category_map, get_category_map, 
    check_register_map, 
    category_histogram, clear_category_histogram,
    get_category_histogram, get_compiled_category_map,
    )
# from budget_domain_model import (BudgetDomainModel)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region extract_category_tree()
def dot(n1:str=None, n2:str=None, n3:str=None) -> str:
    """Format provided nodes with a dot in between."""
    if not n1: return None
    c = f"{n1}.{n2}" if n2 else n1
    if not n2: return c
    return f"{n1}.{n2}.{n3}" if n3 else c  

def extract_category_tree(level:int=2) -> Tree:
    """Extract the category tree from the category_map."""
    try:
        global check_register_map
        now = dt.now()
        now_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
        tree = Tree()
        bct = tree.create_node("Budget", "root")  # Root node
        filter_list = ["Darkside"]
        cat_map = get_category_map()
        combined_category_map = {**cat_map, **check_register_map}
        for _, category in combined_category_map.items():
            l1, l2, l3 = p3u.split_parts(category)
            if l1 in filter_list:
                continue
            if tree.contains(l1): 
                # If Level 1 already exists, find it
                l1_node = tree.get_node(l1)
            else:
                l1_node = tree.create_node(l1, l1, parent="root")
            if not l2 or level < 2:
                continue
            c = dot(l1, l2)
            if tree.contains(c):
                # If Level 2 already exists, find it
                l2_node = tree.get_node(c)
            else:
                l2_node = tree.create_node(l2, c, parent=l1_node)
            if not l3 or level < 3:
                continue
            c = dot(l1, l2, l3)
            if tree.contains(c):
                # If Level 3 already exists, find it
                l3_node = tree.get_node(c)
            else:
                l3_node = tree.create_node(l3, c, parent=l2_node)
        return tree
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion extract_category_tree()
# ---------------------------------------------------------------------------- +
#region output_category_tree()
def output_category_tree(level:int=2,cat_list:list[str]=[]) -> str:
    """Extract and output the category tree from the category_map."""
    try:
        now = dt.now()
        now_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
        tree : Tree = extract_category_tree(level)
        original_stdout = sys.stdout  # Save the original stdout
        buffer = io.StringIO()
        sys.stdout = buffer  # Redirect stdout to capture tree output
        if len(cat_list) == 0:
            print(f"Budget Category List(level {level}) {now_str}\n")
            tree.show()
        else: 
            # Show only the categories in the cat_list
            for cat in cat_list:
                if tree.contains(cat):
                    print(f"Budget Category Item('{cat}') {now_str}\n")
                    tree.show(cat)
        sys.stdout = original_stdout  # Reset stdout
        output = buffer.getvalue()
        return output
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion output_category_tree()
# ---------------------------------------------------------------------------- +
#region category_tree_to_csv()
def category_tree_to_csv(level:int=2):
    """Extract the category, convert to dict, write to csv file."""
    try:
        tree : Tree = extract_category_tree(level)
        tree_dict = {}
        for cat in tree.nodes.keys():
            l1, l2, l3 = p3u.split_parts(cat)
            # print(f"cat_key = '{cat}', L1 = '{l1}', L2 = '{l2}', L3 = '{l3}'")
            tree_dict[cat] = {
                'Budget Category': cat, 
                'Level1': l1,
                'Level2': l2,
                'Level3': l3
            }
        v = tree_dict.pop('root', None)  # Remove the root node
        filename = f"level_{level}_categories.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fields = ['Budget Category', 'Level1', 'Level2', 'Level3']
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in tree_dict.values():
                writer.writerow(row)

        return None
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion output_category_tree()
# ---------------------------------------------------------------------------- +
#region category_map_count() function
def category_map_count():
    return len(get_category_map())

def clear_category_map():
    global category_map
    old_map = category_map
    del category_map
    category_map = {}
    logger.info(f"Cleared category_map, old map had {len(old_map)} items.")
    del old_map
    return    
#endregion category_map_count() function
# ---------------------------------------------------------------------------- +
#region categorize_transaction() function
def categorize_transaction(description : str, txn_catalog:TXNCategoryCatalog,
                           log_all : bool) -> Tuple[str,str]:
    """Use txn_catalog patterns to map description text to a category."""
    try:
        p3u.is_non_empty_str("description", description, raise_error=True)
        p3u.is_not_obj_of_type("txn_catalog", txn_catalog, TXNCategoryCatalog,
                               raise_error=True)
        txn_catalog.valid
        fi_key: str = txn_catalog.fi_key
        txn_category_collection = txn_catalog.txn_categories_workbook[bdm.WB_CATEGORY_COLLECTION]
        tcc_keys = list(txn_category_collection.keys())
        ccm: bdm.COMPLIED_CATEGORY_MAP = txn_catalog.compiled_category_map
        ch = get_category_histogram()
        payee = ""
        rule_index = 0
        for rule_index, (pattern, category) in enumerate(ccm.items()):
            payee = ""
            m = pattern.search(description)
            if m:
                if category not in tcc_keys:
                    logger.warning(f"FI key '{fi_key}' rule_index: '{rule_index}', "
                                   f"Category '{category}', not found in "
                                   f"transaction category collection.")
                gc = len(m.groups())
                if gc == 0 or m[1] is None:
                    if log_all:
                        logger.debug(f"{P2}Matched rule_index: '{rule_index}', "
                                     f"pattern: '{pattern.pattern}' "
                                     f"category: '{category}', "
                                     f"groups: '{gc}', no payee found.")
                    return ch.count(category), payee, rule_index
                payee = m[1]
                # print(f"Matched pattern: '{pattern.pattern}' with payee: '{payee}'")
                if log_all:
                    logger.debug(f"{P2}Matched rule_index: '{rule_index}', "
                                 f"pattern: '{pattern.pattern}' "
                                 f"category: '{category}', "
                                 f"payee: '{payee}', groups: '{gc}'.")
                return ch.count(category), payee, rule_index
        logger.debug(f"{P2}No Match Description: [{description}]")
        return ch.count('Other'), 'Other', -1  # Default category if no match is found
    except re.PatternError as e:
        logger.error(p3u.exc_err_msg(e))
        logger.error(f'Pattern error: compiled_category_map dict: ' 
                     f'{{ \"{e.pattern}\": \"{category}\" }}')
        raise
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion categorize_transaction() function
# ---------------------------------------------------------------------------- +
#region txn_category_url_save() function
def txn_category_url_save(cat_url: str) -> None:
    """Save transaction categories to a URL.

    Args:
        cat_data (dict): The transaction category data to save.
        cat_url (str): The URL to save the data to.
    """
    try:
        p3u.is_non_empty_str("cat_url", cat_url, raise_error=True)
        cat_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/All_TXN_Categories.txn_categories.json"
        # Verify the URL file path.
        tc_path = p3u.verify_url_file_path(cat_url, test=False)
        # Save the category data to the URL.
        cat_data = {
            "name": "all_categories",
            "categories": {}
        }
        for cat in category_map.values():
            l1, l2, l3 = p3u.split_parts(cat)
            cat_id = p3u.gen_hash_key(cat, length=8)
            bdm_tc = BDMTXNCategory(
                cat_id=cat_id,
                full_cat=cat,
                level1=l1,
                level2=l2,
                level3=l3,
                description=f"Level 1 Category: {l1}",
                payee=None
            )
            cat_data["categories"][cat_id] = bdm_tc
            # print(f"category: '{cat_id}': '{repr(bdm_tc )}'")
        bsm_WORKBOOK_CONTENT_url_put(cat_data, cat_url,bdm.WB_TYPE_TXN_CATEGORIES)
        logger.info(f"Saved transaction categories to: {cat_url}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion txn_category_url_save() function
# ---------------------------------------------------------------------------- +
#region workbook_names() function
def workbook_names(wdc: bdm.WORKBOOK_DATA_COLLECTION, wf_key: str, wf_folder_id: str) -> List[str]:
    """Return a list of workbook names for the given workflow key and folder."""
    try:
        wb_name_list: List[str] = []
        if wdc is None or len(wdc) == 0:
            return wb_name_list
        wb_id_list: List[str] = list(wdc.keys())
        for wb_id,bdm_wb in wdc.items():
            if not isinstance(bdm_wb, BDMWorkbook):
                continue
            if bdm_wb.wf_key != wf_key:
                continue
            if bdm_wb.wf_folder_id != wf_folder_id:
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
#region extract_bdm_tree() function
def extract_bdm_tree(bdm_DC: BudManAppDataContext_Base) -> Tree:
    try:
        logger.debug(f"Start.")
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, BudManAppDataContext_Base, raise_error=True)
        settings = bdms.BudManSettings()
        p3u.is_not_obj_of_type("settings", settings, bdms.BudManSettings, raise_error=True)
        bdm_store = bdm_DC.dc_BDM_STORE
        if not bdm_store:
            m = "BudManAppDataContext_Base instance does not have a valid bdm_store."
            logger.error(m)
            raise ValueError(m)
        bdm_store_full_filename = (settings[bdms.BDM_STORE_FILENAME] +
                                   settings[bdms.BDM_STORE_FILETYPE])
        bdm_folder = settings[bdms.BDM_FOLDER] + '/'
        p_str: str = bdm_folder + bdm_store_full_filename
        tree = Tree()
        tree.create_node(f"BDM_STORE: '{p_str}'", "root")  # root node
        wdc : bdm.WORKBOOK_DATA_COLLECTION = None
        # For all Financial Institutions (FI) in the BDM_STORE
        for fi_key, fi_obj in bdm_store[bdm.BDM_FI_COLLECTION].items():
            fi_folder = fi_obj[bdm.FI_FOLDER]
            fi_name = fi_obj[bdm.FI_NAME]
            wdc = fi_obj[bdm.FI_WORKBOOK_DATA_COLLECTION]
            if wdc is None or len(wdc) == 0:
                tag = f"'{fi_folder}' (fi_folder) workbook count: '0'"
                tree.create_node(tag, f"{fi_key}", parent="root")
                continue
            tag = f"'{fi_folder}' (fi_folder) workbook count: '{len(wdc)}'"
            tree.create_node(tag, f"{fi_key}", parent="root")
            # Put the wdc in wb_index order, which is sorted by wb_id key.
            wdc = dict(sorted(wdc.items(), key=lambda item: item[0]))
            for wf_key in bdm_store[bdm.BDM_WF_COLLECTION]:
                wf_obj = bdm_store[bdm.BDM_WF_COLLECTION][wf_key]
                wf_name = wf_obj[bdm.WF_NAME]
                x_key = f"{fi_key}_{wf_key}"
                tree.create_node(f"{wf_key} (wf_key)", x_key, parent=f"{fi_key}")
                # wf_input workbooks
                wb_names = workbook_names(wdc, wf_key, bdm.WF_INPUT_FOLDER)
                logger.debug(f"FI: '{fi_key}', WF: '{wf_key}', FOLDER_ID: '{bdm.WF_INPUT_FOLDER}', workbooks({len(wb_names)}): {wb_names}")
                if len(wb_names) > 0:
                    tree.create_node(f"'{wf_obj[bdm.WF_INPUT_FOLDER]}' (wf_input)", 
                                     f"{x_key}_input", parent=x_key)
                    for wb_name in wb_names:
                        tree.create_node(f"{wb_name} (wb_name)", 
                        f"{x_key}_input_{wb_name}", parent=f"{x_key}_input")
                # wf_working workbooks
                wb_names = workbook_names(wdc, wf_key, bdm.WF_WORKING_FOLDER)
                logger.debug(f"FI: '{fi_key}', WF: '{wf_key}', FOLDER_ID: '{bdm.WF_WORKING_FOLDER}', workbooks({len(wb_names)}): {wb_names}")
                if len(wb_names) > 0:
                    tree.create_node(f"'{wf_obj[bdm.WF_WORKING_FOLDER]}' (wf_working)", 
                                    f"{x_key}_working", parent=x_key)
                    for wb_name in wb_names:
                        tree.create_node(f"{wb_name} (wb_name)", 
                            f"{x_key}_working_{wb_name}", parent=f"{x_key}_working")
                # wf_output workbooks
                wb_names = workbook_names(wdc, wf_key, bdm.WF_OUTPUT_FOLDER)
                logger.debug(f"FI: '{fi_key}', WF: '{wf_key}', FOLDER_ID: '{bdm.WF_OUTPUT_FOLDER}', workbooks({len(wb_names)}): {wb_names}")
                if len(wb_names) > 0:
                    tree.create_node(f"'{wf_obj[bdm.WF_OUTPUT_FOLDER]}' (wf_output)", 
                                    f"{x_key}_output", parent=x_key)
                    for wb_name in wb_names:
                        tree.create_node(f"{wb_name} (wb_name)", 
                                f"{x_key}_output_{wb_name}", parent=f"{x_key}_output")
        logger.debug(f"Complete.")
        return tree
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion extract_bdm_tree() function
# ---------------------------------------------------------------------------- +
#region extract_dc_wb_tree() function
def extract_dc_wb_tree(bdm_DC: BudManAppDataContext_Base) -> Tree:
    """Return a tree structure of the workbook data collection in the provided
    BudManAppDataContext_Base instance."""
    try:
        logger.debug(f"Start.")
        p3u.is_not_obj_of_type("bdm_DC", bdm_DC, 
                               BudManAppDataContext_Base, raise_error=True)
        settings = bdms.BudManSettings()
        fi_key = bdm_DC.fi_key
        if not fi_key:
            m = "BudManAppDataContext_Base instance does not have a valid fi_key."
            logger.error(m)
            raise ValueError(m)
        tree = Tree()
        tree.create_node(f"FI)KEY('{fi_key}') Data Context", "root")  # root node
        wdc : bdm.WORKBOOK_DATA_COLLECTION = bdm_DC.dc_WORKBOOK_DATA_COLLECTION
        for wf_key in bdm_DC.dc_BDM_STORE[bdm.BDM_WF_COLLECTION]:
            wf_obj = bdm_DC.dc_BDM_STORE[bdm.BDM_WF_COLLECTION][wf_key]
            wf_name = wf_obj[bdm.WF_NAME]
            x_key = f"{fi_key}_{wf_key}"
            tree.create_node(f"{wf_key} (wf_key)", x_key, parent=f"{fi_key}")
            tree.create_node(f"{wf_obj[bdm.WF_INPUT_FOLDER]} (wf_input)", 
                             f"{x_key}_input", parent=x_key)
            wb_names = workbook_names(fi_obj, wf_key, bdm.WF_INPUT_FOLDER)
            for wb_name in wb_names:
                tree.create_node(f"{wb_name} (wb_name)", 
                                 f"{x_key}_input_{wb_name}", 
                                 parent=f"{x_key}_input")
            tree.create_node(f"{wf_obj[bdm.WF_WORKING_FOLDER]} (wf_working)", 
                             f"{x_key}_working", parent=x_key)
            wb_names = workbook_names(fi_obj, wf_key, bdm.WF_WORKING_FOLDER)
            for wb_name in wb_names:
                tree.create_node(f"{wb_name} (wb_name)", 
                                 f"{x_key}_working_{wb_name}", 
                                 parent=f"{x_key}_working")
            tree.create_node(f"{wf_obj[bdm.WF_OUTPUT_FOLDER]} (wf_output)", 
                             f"{x_key}_output", parent=x_key)
            wb_names = workbook_names(fi_obj, wf_key, bdm.WF_OUTPUT_FOLDER)
            for wb_name in wb_names:
                tree.create_node(f"{wb_name} (wb_name)", 
                                 f"{x_key}_output_{wb_name}", 
                                 parent=f"{x_key}_output")
        logger.debug(f"Complete.")
        return tree
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion extract_dc_wb_tree() function
# ---------------------------------------------------------------------------- +
#region outout_bdm_tree() function
def output_bdm_tree(bdm_DC: BudManAppDataContext_Base) -> str:
    """Output the BDM tree to the console."""
    try:
        tree = extract_bdm_tree(bdm_DC)
        return tree.show(stdout=False) if tree else "No BDM tree found."
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        return m
#endregion outout_bdm_tree() function
# ---------------------------------------------------------------------------- +
#region extract_txn_categories() method
def extract_txn_categories() -> bdm.DATA_OBJECT:
    """Extract transaction categories from the category_map in 
    the budget_category_mapping.py module and return them as a dict.

    This function is being used to refactor away from the global 
    category_map dictionary and to use a file-based approach.

    Args:
        wb_url (str): The URL of the workbook.
        cr_url (str): The URL of the check register.
    """
    try:
        # Create a WB_TYPE_TXN_CATEGORIES workbook's in memory content
        # from the category_map definition in the module now.
        # tc_path = p3u.verify_url_file_path(all_cats_url, test=False)
        cat_data = {
            bdm.WB_NAME: "un_set", #tc_path.stem,
            bdm.WB_CATEGORY_COUNT: 0,
            bdm.WB_CATEGORY_COLLECTION: {}
        }

        c_map = {}
        category_map: Dict[str, str] = get_category_map()
        for pattern, cat in category_map.items():
            l1, l2, l3 = p3u.split_parts(cat)
            cat_id = p3u.gen_hash_key(str(pattern), length=8)
            bdm_tc = BDMTXNCategory(
                cat_id=cat_id,
                full_cat=cat,
                level1=l1,
                level2=l2,
                level3=l3,
                description=f"Level 1 Category: {l1}",
                pattern=pattern,
                essential=False,  # Default to False, can be set later
                payee=None
            )
            if cat_id in cat_data["categories"]:
                logger.warning(f"Duplicate category ID '{cat_id}' found for "
                               f"category '{cat}'. Overwriting existing entry.")
            cat_data["categories"][cat_id] = bdm_tc
        # bsm_BDM_WORKBOOK_content_put(cat_data, all_cats_url)
        cnt = len(cat_data["categories"])
        logger.info(f"Extracted '{cnt}' categories from budget_category_mapping "
                    f"module, count is: '{cnt}' rules.")
        return cat_data
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion extract_txn_categories() method
# ---------------------------------------------------------------------------- +
#region fi_wb_index() function
#endregion fi_wb_index()