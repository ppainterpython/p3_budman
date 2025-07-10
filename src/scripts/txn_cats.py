#------------------------------------------------------------------------------+
# txn_cats.py - a place to fool around with experiments, not a dependent.
#------------------------------------------------------------------------------+
#region Imports
from pprint import pprint
import logging, re, sys, csv, cmd2, toml
from cmd2 import (Bg, Fg, ansi, Cmd2ArgumentParser, with_argparser)
from pathlib import Path
from typing import Dict, Optional
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
# local modules and packages
import budman_namespace as bdm
import budman_settings as bdms
from budman_workflows.txn_category import (
    BDMTXNCategory, BDMTXNCategoryManager
)
from budman_workflows.budget_category_mapping import get_category_map
from budman_workflows.workflow_utils import (
    extract_txn_categories,
    output_bdm_tree,
    output_category_tree
)
from budget_storage_model import (
    bsm_BDM_WORKBOOK_content_load,
    bsm_BDM_WORKBOOK_content_put,
    csv_DATA_LIST_url_get, 
    csv_DATA_LIST_file_load
)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region argparse definitions
base_parser = cmd2.Cmd2ArgumentParser()
base_subparsers = base_parser.add_subparsers()

parser_catalog = base_subparsers.add_parser(
    "catalog",
    aliases=["cat"], 
    help="Manage transaction categories catalog.")
parser_catalog.add_argument(
    "-i", "--init",
    action="store_true",
    help="Initialize Catalog Manager."
)
parser_catalog.add_argument(
    "fi_key", 
    nargs="?",
    action="store",
    default='boa',
    help="fi_key to initialize."
)
parser_catalog.add_argument(
    "-l", "--list",
    action="store_true",
    help="List all transaction categories."
)

#endregion argparse definitions
# ---------------------------------------------------------------------------- +
#region CmdLineApp class
class CmdLineApp(cmd2.Cmd):
    """Transaction Categories Command Line Application."""
    #region CmdLineApp Class intrinsics
    def __init__(self,settings:bdms.BudManSettings):
        super().__init__(allow_cli_args=False, persistent_history_file="txn_cats_history.txt")
        self.allow_style = ansi.AllowStyle.TERMINAL
        self.settings = settings if settings else bdms.BudManSettings()
        self._catman: BDMTXNCategoryManager = BDMTXNCategoryManager(self.settings)
    
    @property
    def catman(self) -> BDMTXNCategoryManager:
        """Get the BDMTXNCategoryManager instance."""
        return self._catman
    @catman.setter
    def catman(self, value: Optional[BDMTXNCategoryManager]) -> None:
        """Set the BDMTXNCategoryManager instance."""
        self._catman = value
    #endregion CmdLineApp Class intrinsics
    # ------------------------------------------------------------------------ +
    #region do_catalog()
    @cmd2.with_argparser(parser_catalog)
    def do_catalog(self, args: str) -> None:
        """Manage transaction categories catalog."""
        try:
            self.check_catalog() # raise error if no catman configured.
            init_flag = args.init
            list_flag = args.list
            if init_flag:
                self.catman = BDMTXNCategoryManager(self.settings)
                self.catman.FI_TXN_CATEGORIES_WORKBOOK_file_load(args.fi_key)
            if list_flag:
                if not self.catman:
                    self.poutput("Transaction Category Manager is not initialized.")
                cat_data = self.catman.catalog
                if not cat_data:
                    self.poutput("No transaction categories found.")
                self.display_catman()
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.poutput(f"Error: {m}")

    do_cat = do_catalog
    #endregion do_catalog()
    # ------------------------------------------------------------------------ +
    #region do_update() method
    def do_update(self, statement) -> None:
        """Update transaction categories."""
        try:
            self.check_catalog()
            self.catman.FI_WB_TYPE_TXN_CATEGORIES_update_CATEGORY_MAP('boa')

            self.poutput(f"Updated transaction categories.")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.poutput(f"Error: {m}")
    #endregion do_update() method
    # ------------------------------------------------------------------------ +
    #region do_extract() method
    def do_extract(self, statement) -> None:
        """Extract transaction categories."""
        try:
            self.check_catalog()
            save_category_map(fi_key='boa', test=True)
            # category_map: bdm.DATA_OBJECT = extract_txn_categories()
            self.poutput(f"Extracted category_map.")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.poutput(f"Error: {m}")
    #endregion do_extract() method
    # ------------------------------------------------------------------------ +
    #region do_foo() method
    def do_foo(self, statement) -> None:
        """Manage foo."""
        try:
            self.check_catalog()
            self.poutput(f"foo {statement}")
            self.poutput(f"foo {statement!r}")
            pprint(self.catman)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.poutput(f"Error: {m}")
    #endregion do_foo() method
    # ------------------------------------------------------------------------ +
    #region display_catman() method
    def display_catman(self) -> None:
        """Display a summary of the Category Manager content."""
        self.check_catalog()
        cat_man_len = len(self.catman.catalog)
        ccp_len = len(self.catman.ccm)
        for fi_key, cat_data in self.catman.catalog.items():
            self.poutput(f"FI Key: {fi_key}, Categories: {len(cat_data)}")
    #endregion display_catman() method
    # ------------------------------------------------------------------------ +
    #region check_catalog() method
    def check_catalog(self) -> None:
        """If catalog is empty, raise error. """
        if self.catman is None:
            raise ValueError("Transaction Category Manager is not initialized.")
    #endregion check_catalog() method
#endregion CmdLineApp class
# ---------------------------------------------------------------------------- +
#region extract_txn_categories2() method
def extract_txn_categories2(all_cats_url: str) -> dict:
    """Extract transaction categories from the budget_category_mapping.py 
    module, save to a WB_TYPE_TXN_CATEGORIES workbook.

    This function is being used to refactor away from the global 
    category_map dictionary and to use a file-based approach.

    Args:
        wb_url (str): The URL of the workbook.
        cr_url (str): The URL of the check register.
    """
    try:
        # Create a WB_TYPE_TXN_CATEGORIES workbook's content in memory
        # from the category_map definition in the module now.
        tc_path = p3u.verify_url_file_path(all_cats_url, test=False)
        cat_data = {
            "name": tc_path.stem,
            "categories": {}
        }

        c_map = {}
        category_map: Dict[str, str] = get_category_map()
        for pattern, cat in category_map.items():
            l1, l2, l3 = p3u.split_parts(cat)
            # if l1 not in ["Housing", "Housing-2", "Food"]: continue
            cat_id = p3u.gen_hash_key(str(pattern), length=8)
            bdm_tc = BDMTXNCategory(
                cat_id=cat_id,
                full_cat=cat,
                level1=l1,
                level2=l2,
                level3=l3,
                payee=None,
                description=f"Level 1 Category: {l1}",
                essential=False, 
                pattern=pattern,
                total=0
            )
            if cat_id in cat_data["categories"]:
                logger.warning(f"Duplicate category ID '{cat_id}' found for "
                               f"category '{cat}'. Overwriting existing entry.")
            cat_data["categories"][cat_id] = bdm_tc
        bsm_BDM_WORKBOOK_content_put(cat_data, all_cats_url)
        cnt = len(cat_data["categories"])
        logger.info(f"Extracted '{cnt}' categories from budget_category_mapping "
                    f"module, saved to : '{all_cats_url}'")
        return cat_data
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion extract_txn_categories2() method
# -------------------------------------------------------------------------- +
def save_txn_categories():
    all_cats_url = "file:///C:/Users/ppain/OneDrive/budget/boa/All_TXN_Categories.txn_categories.json"
    try:
        settings = bdms.BudManSettings()
        category_map = get_category_map()
        # Extract transaction categories from the budget_category_mapping.py
        # module, save to a WB_TYPE_TXN_CATEGORIES workbook.
        cat_data : Dict[str, Dict] = extract_txn_categories2(all_cats_url)

        catman = BDMTXNCategoryManager(settings)
        catman.FI_TXN_CATEGORIES_WORKBOOK_file_load("boa")
        bsm_BDM_WORKBOOK_content_put(catman.catalog["boa"], 
                                     all_cats_url,
                                     bdm.WB_TYPE_TXN_CATEGORIES)
        logger.info(f"Transaction categories extracted and saved to: {all_cats_url}")
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")

def save_category_map(fi_key:str='boa',test:bool=False):
    try:
        p3u.is_non_empty_str("fi_key", fi_key, save_category_map, "fi_key must be a non-empty string.")
        settings = bdms.BudManSettings()
        category_map = get_category_map()
        cat_map_filename = settings[bdms.CATEGORY_CATALOG][fi_key][bdms.CATEGORY_MAP_FULL_FILENAME]
        if test:
            cat_map_filename = "test_" + cat_map_filename
        fi_folder: Path = settings.FI_FOLDER_abs_path(fi_key)
        cat_map_path: Path = fi_folder / cat_map_filename
        with open(cat_map_path, 'w', encoding='utf-8') as f:
            toml.dump(category_map, f)
        # Now test reading it back in.
        cat_map_in = toml.load(cat_map_path)
        # bsm_BDM_WORKBOOK_content_put(catman.catalog["boa"], 
        #                              all_cats_url,
        #                              bdm.WB_TYPE_TXN_CATEGORIES)
        logger.info(f"Transaction categories extracted and saved to: {cat_map_path}")
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    logger.info(f"Complete.")

def test_regex(file_path, pattern, show_matches=False):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        regex = re.compile(pattern)
        matches = []
        
        for line in lines:
            match = regex.search(line)
            if match:
                pay_to = match.group(1) if match.groups() else None
                matches.append(line.strip())
        
        print(f"Total lines in file: {len(lines)}")
        print(f"Lines matching the pattern: {len(matches)}")
        
        if show_matches and matches:
            print("\nMatching lines:")
            for match in matches:  
                print(match)
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except re.error as e:
        print(f"Error in regex pattern: {e}")

def extract_column_from_csv(file_path:Path, column_name:str, output_path:Path,
                            append=True):
    try:
        folder_path ='C:\\Users\\ppain\\OneDrive\\budget\\boa\\raw_data\\boa\\'
        descriptions_file_path = folder_path + "All.txn_descriptions.txt"
        orig_desc = 'Original Description'
        descriptions_file = Path(descriptions_file_path)
        csv_data = csv_DATA_LIST_file_load(file_path)
        mode = 'a' if append else 'w'
        with open(descriptions_file, mode, encoding='utf-8') as f:
            for txn in csv_data:
                desc = txn.get(orig_desc, 'what?')
                f.write(f"{desc}\n")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error extracting column: {e}")

# ------------------------------------------------------------------------ +
#region configure_logging() method
def configure_logging(logger_name : str = __name__, logtest : bool = False) -> None:
    """Setup the application logger."""
    try:
        # Configure logging
        log_config_file = "budget_model_logging_config.jsonc"
        _ = p3l.setup_logging(
            logger_name = logger_name,
            config_file = log_config_file
            )
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger = logging.getLogger(logger_name)
        logger.propagate = True
        logger.setLevel(logging.DEBUG)
        prog = Path(__file__).name
        logger.info(f"+ {60 * '-'} +")
        logger.info(f"+ running {prog}({logger_name}) ...")
        logger.info(f"+ {60 * '-'} +")
        if(logtest): 
            p3l.quick_logging_test(logger_name, log_config_file, reload = False)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion configure_logging() function
# ------------------------------------------------------------------------ +
#region extract_descriptions() method
def extract_descriptions(file_path: Path) -> list[str]:
    """Extract transaction descriptions from a CSV file."""
    wb_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    cr_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/CheckRegister_ToDate20250609.csv"
    june_2025_url = "file:///C:/Users/ppain/OneDrive/budget/boa/raw_data/boa/June2025_ALL.csv"
    all_cats_url = "file:///C:/Users/ppain/OneDrive/budget/boa/All_TXN_Categories.txn_categories.json"

    folder_path ='C:\\Users\\ppain\\OneDrive\\budget\\boa\\raw_data\\boa\\'
    june_2025_path = folder_path + "June2025_ALL.csv"
    may_2025_path = folder_path + "May2025_ALL.csv"
    april_2025_path = folder_path + "April2025_ALL.csv"
    Q1_2025_path = folder_path + "BOA2025.csv"
    all_2024_path = folder_path + "BOA2024.csv"
    all_2023_path = folder_path + "BOA2023.csv"
    descriptions_file_path = folder_path + "All.txn_descriptions.txt"
    try:
        settings = bdms.BudManSettings()
        configure_logging(__name__, logtest=False)

        orig_desc = 'Original Description'
        descriptions_file = Path(descriptions_file_path)
        if descriptions_file.exists():
            logger.info(f"Removing existing file: {descriptions_file}")
            descriptions_file.unlink()  # Remove the file if it exists

        for path_str in [june_2025_path, may_2025_path, april_2025_path,
                  Q1_2025_path, all_2024_path, all_2023_path]:
            path = Path(path_str)
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                continue
            logger.info(f"Extracting '{orig_desc}' from: {path}")
            # Extract the original description column from the csv file.
            extract_column_from_csv(path, orig_desc, descriptions_file)
        # extract_column_from_csv(june_2025_path, orig_desc, descriptions_file)

        test_regex(
            file_path=descriptions_file,
            pattern=r"(?im)^\bPAYPAL.*?ID:(\w+)",
            show_matches=True
        )


        logger.info(f"Done.")


    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")

#endregion extract_descriptions() method
# ---------------------------------------------------------------------------- +
#region __main__() method
if __name__ == "__main__":
    try:
        settings = bdms.BudManSettings()
        configure_logging(__name__, logtest=False)

        app = CmdLineApp(settings)
        sys.exit(app.cmdloop())
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
exit(0)
#endregion __main__() method


#region attic
# ---------------------------------------------------------------------------- +
        # filename : str = settings.config["category_catalog"]["boa"]
        # fi_folder : Path = settings.FI_FOLDER_abs_path("boa") 
        # cat_path = fi_folder / filename
        # cat_uri = cat_path.as_uri()

        # cat_data = {
        #     "name": "all_categories",
        #     "categories": {}
        # }
        # cat_data2 = {
        #     "name": "all_categories",
        #     "categories": {}
        # }
        # in_cat_data : Dict = bsm_WORKBOOK_content_url_get(all_cats_url)
        # if in_cat_data is None:
        #     raise ValueError(f"Failed to load categories from: {all_cats_url}")
        # for cat_id, bdm_tc_data in in_cat_data["categories"].items():
        #     logger.info(f"category: '{cat_id}': '{repr(bdm_tc_data)}'")
        #     bdm_tc = BDMTXNCategory(**bdm_tc_data)
        #     logger.info(f"BDMTXNCategory: {bdm_tc}")
        #     cat_data2["categories"][cat_id] = bdm_tc
        #     cp = re.compile(bdm_tc.pattern)
        #     c_map[cp] = bdm_tc.full_cat
        # logger.info(f"Read all categories to: {all_cats_url}")
        # len1 = len(cat_data["categories"])
        # len2 = len(cat_data2)
        # if len(cat_data2["categories"]) == len(cat_data["categories"]):
        #     logger.info(f"All categories read successfully: {len(cat_data2)}")
# ---------------------------------------------------------------------------- +
#     wb_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
#     cr_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/CheckRegister_ToDate20250609.csv"
#     try:
#         configure_logging(__name__, logtest=False)
#         wb_path = p3u.verify_url_file_path(cr_url, test=False)
#         # wb_path.parent  = abs_path to the parent directory
#         # wb_path.stem = filename
#         # wb_path.suffix = filetype
#         # wb_path.name = full_filename
#         # path mapping:  
#         # BDM: FI: bdm_id / fi_folder(fi_key) / fi_data_coll(wf_key) / workbook_list(wf_purpose) / (wb_name.wb_type, wb_url)
#         # bsm:   '~/budget/'              'boa/'                                        'data/new/' data.xlsx
#         #      WF: bdm_id \ wf_key \  wf_folder(wf_purpose) \ wb_name.wb_type
#         #bdm_folder
#         #
#         bdms = bsm_BDM_STORE_url_get(wb_url)
#         fi_folders = list(bdms[BDM_FI_COLLECTION].keys())     
#         bdm_folder = bdms[BDM_FOLDER]
#         all_paths = []
#         fi_col = bdms[BDM_FI_COLLECTION]
#         wf_col = bdms[BDM_WF_COLLECTION]
#         for fi_key, fi_obj in bdms[BDM_FI_COLLECTION].items():
#             fi_folder = fi_obj[FI_FOLDER]
#             fi_name = fi_obj[FI_NAME]
#             print(f"'{fi_folder}' [{fi_key}]'{fi_name}'")
#             if fi_obj[FI_WORKFLOW_DATA_COLLECTION] is None:
#                 logger.warning(f"FI_DATA_COLLECTION is None for FI_KEY: {fi_key}")
#                 continue
#             for wf_key, data_obj in fi_obj[FI_WORKFLOW_DATA_COLLECTION].items():
#                 wf_obj = wf_col[wf_key]
#                 wf_name = wf_obj[WF_NAME] 
#                 # print(f"  '{wf_key}' wf_name: '{wf_obj[WF_NAME]}'")
#                 wf_folders = {}
#                 wf_folders[WF_INPUT] = wf_obj[WF_INPUT_FOLDER]
#                 wf_folders[WF_WORKING] = wf_obj[WF_WORKING_FOLDER]
#                 wf_folders[WF_OUTPUT] = wf_obj[WF_OUTPUT_FOLDER]
#                 for wb_type, tuple_list in data_obj.items():
#                     f = wf_folders[wb_type]
#                     tm = wf_obj[WF_PURPOSE_FOLDER_MAP][wb_type]
#                     print(f"  '{f}' [{wf_key}]'{tm}' ")
#                     for tup in tuple_list:
#                         print(f"     '{tup[0]}' wb_path: {tup[1]}")


#         logger.info(f"wb_path: '{wb_path}' url:'{wb_url}'")

#     except Exception as e:
#         m = p3u.exc_err_msg(e)
#         logger.error(m)
#     # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
#     logger.info(f"Complete.")

# exit(0)
# ---------------------------------------------------------------------------- +
    # bdms_url = "file:///C:/Users/ppain/OneDrive/budget/p3_budget_manager_ca063e8b.jsonc"
    # try:
    #     bdms_json = bsm_BDM_STORE_url_load(bdms_url)
    #     parsed_url = urlparse(bdms_url)
    # except Exception as e:
    #     logger.error(p3u.exc_err_msg(e))
    #     raise ValueError(f"store_url is not a valid URL: {bdms_url}")
    # if not parsed_url.scheme:
    #     raise ValueError(f"store_url has no scheme: {bdms_url}")
    # if parsed_url.scheme not in ["file", "http", "https"]:
    #     raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
    # # If the scheme is file, load the BDM_STORE from a file.
    # if parsed_url.scheme == "file":
    #     # Decode the URL and convert it to a Path object.
    #     bdms_path = Path.from_uri(bdms_url)
    #     print(f"Loading BDM_STORE from path:'{bdms_path}' url:'{bdms_url}'")
    #     j = bsm_BDM_STORE_file_load(bdms_path)
    # # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    # print(f"complete")
# ---------------------------------------------------------------------------- +
# def bsm_BDM_STORE_url_load_foo(store_url : str = None) -> Dict:
#     """BSM: Load a BDM_STORE object from a URL.
    
#     Entry point for a BDM_STORE file load operation. Parse the URL and decide
#     how to load the BDM_STORE object based on the URL scheme.

#     Args:
#         store_url (str): The URL to the BDM_STORE object to load.
#     """
#     try:
#         # store_url must be a non-empty string.
#         p3u.is_non_empty_str(store_url, "store_url",raise_error=True)
#         # store_url must be a valid URL.
#         try:
#             parsed_url = urlparse(store_url)
#         except Exception as e:
#             logger.error(p3u.exc_err_msg(e))
#             raise ValueError(f"store_url is not a valid URL: {store_url}")
#         if not parsed_url.scheme:
#             raise ValueError(f"store_url has no scheme: {store_url}")
#         if parsed_url.scheme not in ["file", "http", "https"]:
#             raise ValueError(f"store_url scheme is not supported: {parsed_url.scheme}")
#         # If the scheme is file, load the BDM_STORE from a file.
#         if parsed_url.scheme == "file":
#             # Decode the URL and convert it to a Path object.
#             file_path = unquote(parsed_url.path)
#             store_path = Path(file_path).expanduser().resolve()
#             logger.info(f"Loading BDM_STORE from file: {store_path}")
#             return {} #bsm_BDM_STORE_load(store_path)
#         raise ValueError(f"Unsupported store_url scheme: {parsed_url.scheme}")
#     # except json5.Json5DecoderException as e:
#     #     logger.error(p3u.exc_err_msg(e))
#     #     raise
#     except Exception as e:
#         logger.error(p3u.exc_err_msg(e))
#         raise
#endregion attic