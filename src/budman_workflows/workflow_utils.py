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
from typing import Dict, List, Optional, Union

# third-party modules and packages
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
from budman_namespace import *
from budget_storage_model import bsm_WORKBOOK_content_put
from .txn_category import BDMTXNCategory, BDMTXNCategoryManager
from .budget_category_mapping import (
    compiled_category_map, get_category_map, 
    check_register_map, 
    category_histogram, clear_category_histogram,
    get_category_histogram, get_compiled_category_map,
    )
from budget_domain_model import (BudgetDomainModel)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region generate_hash_key(text:str) -> str
def generate_hash_key(text: str, length:int=12) -> str:
    """Generate a hash key for the given text.
    
    The hash key is generated by removing all non-alphanumeric characters 
    from the text, converting it to lowercase, and then hashing it using 
    SHA-256. The resulting hash is then converted to a hexadecimal string.

    Args:
        text (str): The input text to generate a hash key for.

    Returns:
        str: The generated hash key.
    """
    try:
        if not isinstance(text, str):
            raise TypeError(f"Expected 'text' arg to be a str, got {type(text)}")
        # Remove non-alphanumeric characters and convert to lowercase.
        # cleaned_text = re.sub(r'\W+', '', text).lower()
        # Generate the SHA-256 hash of the cleaned text.
        hash_object = hashlib.sha256(text.encode())
        # Convert the hash to a hexadecimal string.
        return hash_object.hexdigest()[:length]  #.[:HASH_KEY_LENGTH]
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion generate_hash_key(text:str) -> str
# ---------------------------------------------------------------------------- +
#region split_budget_category() -> tuple function
def split_budget_category(budget_category: str) -> tuple[str, str, str]:
    """Split a budget category string into three levels.
    
    The budget category is expected to be in the format "Level1.Level2.Level3".
    If the budget category does not have all three levels, the missing levels 
    will be set to an empty string.

    Args:
        budget_category (str): The budget category string to split.

    Returns:
        tuple[str, str, str]: A tuple containing Level1, Level2, and Level3.
    """
    try:
        if not isinstance(budget_category, str):
            raise TypeError(f"Expected 'budget_category' to be a str, got {type(budget_category)}")
        l1 = l2 = l3 = ""
        c = budget_category.count('.')
        if c > 2:
            # Split the budget category by '.' and ensure we have 3 parts.
            logger.warning(f"Budget category '{budget_category}' "
                           f"has more than 3 levels. ")
            l1, l2, l3 = budget_category.split('.', 2)
        elif c == 2:
            # Split the budget category by '.' and ensure we have 3 parts.
            l1, l2, l3 = budget_category.split('.',2)
        elif c == 1:
            # Split the budget category by '.' and ensure we have 2 parts.
            l1, l2 = budget_category.split('.',1)
        else:
            # If no '.' is present, treat the whole string as Level1.
            l1 = budget_category
        return l1, l2, l3
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion split_budget_category() function
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
            l1, l2, l3 = split_budget_category(category)
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
            l1, l2, l3 = split_budget_category(cat)
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
#region map_category() function deprecated
# def map_category(src_str) -> str:
#     """Map a transaction description to a budget category."""
#     # Run the src_str through the category_map to find a match.
#     try:
#         global category_histogram
#         ch = get_category_histogram()
#         for pattern, category in category_map.items():
#             if re.search(pattern, str(src_str), re.IGNORECASE):
#                 return ch.count(category)
#         return ch.count('Other')  # Default category if no match is found
#     except re.PatternError as e:
#         logger.error(p3u.exc_err_sg(e))
#         logger.error(f'Pattern error: category_map dict: ' 
#                      f'{{ \"{e.pattern}\": \"{category}\" }}')
#         raise
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#endregion map_category() function
# ---------------------------------------------------------------------------- +
#region categorize_transaction() function
def categorize_transaction(description : str, ccm : Dict[re.Pattern, str]) -> str:
    """Use the provided compiled category map to map the description to a category."""
    try:
        p3u.is_non_empty_str("description", description, raise_error=True)
        p3u.is_non_empty_dict("ccm", ccm, raise_error=True)
        for pattern, category in ccm.items():
            if pattern.search(description):
                return category
        return 'Other'  # Default category if no match is found
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
            l1, l2, l3 = split_budget_category(cat)
            cat_id = generate_hash_key(cat, length=8)
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
        bsm_WORKBOOK_content_put(cat_data, cat_url)
        logger.info(f"Saved transaction categories to: {cat_url}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion txn_category_url_save() function
# ---------------------------------------------------------------------------- +