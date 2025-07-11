# ---------------------------------------------------------------------------- +
#region txn_category.py module
""" Financial Budget Workflow: "categorization" of transaction workbooks.

    Workflow: categorization of transactions.
"""
#endregion txn_category.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import re, pathlib as Path, logging, io, sys, time, hashlib, datetime
import csv
from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict, field

# third-party modules and packages
import toml
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
import budman_settings as bdms
from budget_storage_model import (
    bsm_WORKBOOK_CONTENT_url_get,
    bsm_WORKBOOK_CONTENT_url_put
)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region BDMTXNCategory class (@dataclass)
@dataclass
class BDMTXNCategory:
    """ BDMTXNCategory is a dataclass that represents a transaction category.
    
    Attributes:
        cat_id (str): Unique identifier for the category.
        full_cat (str): The full category name, including all levels.
        level1 (str): The first level of the category hierarchy.
        level2 (str): The second level of the category hierarchy.
        level3 (str): The third level of the category hierarchy.
        payee (str): The payee associated with the category.
        description (str): A description of the category.
        essential (bool): Whether the category is essential.
        pattern (Optional[re.Pattern]): A regular expression pattern
    """
    cat_id: str = field(default="")
    full_cat: str = field(default="")
    level1: str = field(default="")
    level2: str = field(default="")
    level3: str = field(default="")
    payee: str = field(default="")
    description: str = field(default="")
    essential: bool = field(default=False)
    pattern: Optional[re.Pattern] = field(default=None, repr=False)
    total: int = field(default=0)
    
    def __post_init__(self):
        """Post-initialization to ensure levels are trimmed."""
        self.full_cat = self.full_cat.strip() if self.full_cat else ""
        self.level1 = self.level1.strip() if self.level1 else ""
        self.level2 = self.level2.strip() if self.level2 else ""
        self.level3 = self.level3.strip() if self.level3 else ""
        self.payee = self.payee.strip() if self.payee else ""
#endregion BDMTXNCategory class (@dataclass)
# ---------------------------------------------------------------------------- +
#region BDMTXNCategoryManager class intrinsics
class BDMTXNCategoryManager:
    #region BDMTXNCategoryManager class doc string
    """BDMTXNCategoryManager: manage transaction categories definition and use.
    
    Manages a catalog of transaction category sets, based on different financial
    institution requirements. 

    Attributes:
        settings (bdms.BudManSettings): App settings.
        config (Dict[str, Any]): The config part user session settings.
        catalog (Dict[str, Dict[str, BDMTXNCategory]]): The catalog of 
            transaction categories, the FI_KEY is the key.
        ccm (Dict[str, Dict[re.Pattern, str]]): Compiled category maps for FIs.

    In storage, each financial institution designated by an fi_key, has 
    workbooks with the definitions of budget category rules and other metadata. 
    The 'catalog' attribute is a dictionary holding 
    WB_TYPE_TXN_CATEGORIES wb_content for an FI with the following structure:
    
        # example with 'citibank' as fi_key:

        catalog = {
        "boa": {
            "name": "All_TXN_Categories.txn_categories.json",
            "categories": {
                "cat_id1": BDMTXNCategory.to_dict(),
                "cat_id2": BDMTXNCategory.to_dict(),
                },
        "citibank": {
            "name": "All_TXN_Categories.txn_categories.json",
            "categories": {
                "cat_id1": BDMTXNCategory.to_dict(),
                "cat_id2": BDMTXNCategory.to_dict(),
                }
        }

    
    """
    #endregion BDMTXNCategoryManager class doc string
    # ------------------------------------------------------------------------ +
    #region BDMTXNCategoryManager class __init__()
    def __init__(self, settings:bdms.BudManSettings):
        """Initialize the BDMTXNCategoryManager with settings."""
        self._settings: bdms.BudManSettings = settings
        """App settings for configuration information."""
        self._catalog: Dict[str, Dict[str, BDMTXNCategory]] = {}
        """Catalog of transaction categories, keyed by financial institution."""
        self._ccm: Dict[str, Dict[re.Pattern, str]] = {}
        """Compiled category maps for FI's."""
    #endregion BDMTXNCategoryManager class __init__()
    # ------------------------------------------------------------------------ +
    #region class properties
    @property
    def settings(self) -> bdms.BudManSettings:
        """Get the settings for the BDMTXNCategoryManager."""
        return self._settings
    @settings.setter
    def settings(self, value: bdms.BudManSettings):
        """Set the settings for the BDMTXNCategoryManager."""
        self._settings = value

    @property
    def catalog(self) -> Dict[str, Dict[str, BDMTXNCategory]]:
        """Get the catalog of transaction categories."""
        return self._catalog
    @catalog.setter
    def catalog(self, value: Dict[str, Dict[str, BDMTXNCategory]]):
        """Set the catalog of transaction categories."""
        self._catalog = value

    @property
    def ccm(self) -> Dict[str, Dict[re.Pattern, str]]:
        """Get the compiled category maps for financial institutions."""
        return self._ccm
    @ccm.setter
    def ccm(self, value: Dict[str, Dict[re.Pattern, str]]):
        """Set the compiled category maps for financial institutions."""
        self._ccm = value
    #endregion class properties
    # ------------------------------------------------------------------------ +
#endregion BDMTXNCategoryManager class intrinsics
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region BDMTXNCategoryManager methods
    # ------------------------------------------------------------------------ +
    #region FI_WB_TYPE_TXN_CATEGORIES_update_CATEGORY_MAP()
    def FI_WB_TYPE_TXN_CATEGORIES_update_CATEGORY_MAP(self, fi_key: str) -> None:
        """For the fi_key, refresh the transaction category catalog in-memory
        from the category_map.

        Load the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            # Load the catalog for an FI
            cat_map_wb: bdm.CATEGORY_MAP_WORKBOOK = None
            cat_map_wb = self.FI_CATEGORY_MAP_WORKBOOK_load(fi_key)
            # Construct a new TXN_CATEGORIES_WORKBOOK
            txn_categories_wb: bdm.TXN_CATEGORIES_WORKBOOK = None
            txn_categories_wb = self.FI_TXN_CATEGORIES_WORKBOOK(fi_key, cat_map_wb)
            self.FI_TXN_CATEGORIES_WORKBOOK_save(fi_key, txn_categories_wb)
            # self.FI_TXN_CATEGORIES_WORKBOOK_add(fi_key, txn_categories_wb)
        except Exception as e:
            logger.error(f"Error updating CATEGORY_MAP for FI_KEY('{fi_key}') {e}")
            raise
    #endregion FI_WB_TYPE_TXN_CATEGORIES_update_CATEGORY_MAP()
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK_add()
    def FI_TXN_CATEGORIES_WORKBOOK_add(self, fi_key: str, 
                    txn_categories_wb: bdm.TXN_CATEGORIES_WORKBOOK) -> None:
        """Add the WB_TYPE_TXN_CATEGORIES workbook to the catalog for the FI.

        Add the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            if (not isinstance(txn_categories_wb, dict) or
                bdm.WB_CATEGORY_COLLECTION not in txn_categories_wb or
                 not isinstance(txn_categories_wb[bdm.WB_CATEGORY_COLLECTION], dict) or
                 len(txn_categories_wb[bdm.WB_CATEGORY_COLLECTION]) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {txn_categories_wb}")
            cat_data: Dict[str, Any] = txn_categories_wb[bdm.WB_CATEGORY_COLLECTION]
            ccm = self.WB_TYPE_TXN_CATEGORIES_compile(cat_data)
            self.catalog[fi_key] = txn_categories_wb
            self.ccm[fi_key] = ccm
            logger.info(f"Loaded {len(self.catalog[fi_key])} categories for {fi_key}.")
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion FI_TXN_CATEGORIES_WORKBOOK_add()
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK_load()
    def FI_TXN_CATEGORIES_WORKBOOK_load(self, 
                fi_key: str,) -> None:
        """Load the WB_TYPE_TXN_CATEGORIES workbook content for an FI.

        Load the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            # Load the catalog for an FI
            test_txn_cat_wb_url = "file:///C:/Users/ppain/OneDrive/budget/boa/TEST_All_TXN_Categories.txn_categories.json"
            cat_url = test_txn_cat_wb_url #self.FI_TXN_CATEGORIES_WORKBOOK_url(fi_key)
            txn_cat_wb_content: bdm.TXN_CATEGORIES_WORKBOOK = None
            txn_cat_wb_content = bsm_WORKBOOK_CONTENT_url_get(cat_url,
                                        wb_type=bdm.WB_TYPE_TXN_CATEGORIES,)
            if (not isinstance(txn_cat_wb_content, dict) or
                bdm.WB_CATEGORY_COLLECTION not in txn_cat_wb_content or
                 not isinstance(txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION], dict) or
                 len(txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION]) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {cat_url}")
            cat_collection_json: Dict[str, Any] = txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION]
            # Rehydrate the BDMTXNCategory objects from the json load.
            cat_collection : Dict[str, BDMTXNCategory] = {
                cat_id: BDMTXNCategory(**data) 
                    for cat_id, data in cat_collection_json.items()
            }
            ccm = self.WB_TYPE_TXN_CATEGORIES_compile(cat_collection)
            self.catalog[fi_key] = cat_collection
            self.ccm[fi_key] = ccm
            count = txn_cat_wb_content.get(bdm.WB_CATEGORY_COUNT, 0)
            logger.debug(f"Loaded '{count}' categories for FI_KEY('{fi_key}').")
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion FI_TXN_CATEGORIES_WORKBOOK_load()
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK_save()
    def FI_TXN_CATEGORIES_WORKBOOK_save(self, 
                fi_key: str,
                txn_cat_wb_input: Optional[bdm.TXN_CATEGORIES_WORKBOOK]=None) -> None:
        """Save the WB_TYPE_TXN_CATEGORIES workbook content for an FI.

        Save the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
            txn_cat_wb_input (Optional[bdm.TXN_CATEGORIES_WORKBOOK]): 
                If provided, save this workbook. If not, extract from catalog.
        """
        try:
            test_txn_cat_wb_url = "file:///C:/Users/ppain/OneDrive/budget/boa/TEST_All_TXN_Categories.txn_categories.json"
            self.valid_state()  # Ensure the manager is in a valid state
            # Load the catalog for an FI
            txn_cat_wb_content: bdm.TXN_CATEGORIES_WORKBOOK = None
            txn_cat_wb_url = test_txn_cat_wb_url #self.FI_TXN_CATEGORIES_WORKBOOK_url(fi_key)
            if txn_cat_wb_input is not None:
                # If input is provided, use it directly.
                txn_cat_wb_content = txn_cat_wb_input
            else:
                # Otherwise, load from the catalog.
                if fi_key not in self.catalog:
                    raise KeyError(f"FI_KEY '{fi_key}' not found in catalog.")
                cat_collection = self.catalog[fi_key]
                txn_cat_wb_content = self.FI_TXN_CATEGORIES_WORKBOOK(fi_key, 
                                                                cat_collection)
            bsm_WORKBOOK_CONTENT_url_put(txn_cat_wb_content,txn_cat_wb_url,
                                        wb_type=bdm.WB_TYPE_TXN_CATEGORIES)
            count = txn_cat_wb_content.get(bdm.WB_CATEGORY_COUNT, 0)
            logger.debug(f"Saved TXN_CATEGORIES_WORKBOOK ({count}) "
                         f"for FI_KEY('{fi_key}').")
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion FI_TXN_CATEGORIES_WORKBOOK_save()
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK_url()
    def FI_TXN_CATEGORIES_WORKBOOK_url(self, fi_key: str) -> str:
        """Get the URL for the transaction categories workbook for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The URL for the transaction categories workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            txn_cat_path: Path = self.FI_WB_TYPE_TXN_CATEGORIES_abs_path(fi_key)
            if not txn_cat_path.exists():
                raise FileNotFoundError(f"WB_TYPE_TXN_CATEGORIES file not "
                                        f"found: {txn_cat_path}")
            return txn_cat_path.as_uri()
        except KeyError as e:
            logger.error(f"WB_TYPE_TXN_CATEGORIES file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion FI_TXN_CATEGORIES_WORKBOOK_url()
    # ------------------------------------------------------------------------ +
    #region FI_WB_TYPE_TXN_CATEGORIES_abs_path()
    def FI_WB_TYPE_TXN_CATEGORIES_abs_path(self, fi_key: str) -> Path:
        """Get the absolute path for the WB_TYPE_TXN_CATEGORIES workbook 
        for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The URL for the transaction categories workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            txn_cat_filename = self.settings[bdms.CATEGORY_CATALOG][fi_key][bdms.TXN_CATEGORIES_FULL_FILENAME]
            fi_folder = self.settings.FI_FOLDER_abs_path(fi_key)
            txn_cat_path = fi_folder / txn_cat_filename
            if not txn_cat_path.exists():
                raise FileNotFoundError(f"Transaction Categories file not "
                                        f"found: {txn_cat_path}")
            return txn_cat_path
        except KeyError as e:
            logger.error(f"WB_TYPE_TXN_CATEGORIES file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion FI_WB_TYPE_TXN_CATEGORIES_abs_path()
    # ------------------------------------------------------------------------ +
    #region WB_TYPE_TXN_CATEGORIES_compile()
    def WB_TYPE_TXN_CATEGORIES_compile(self, cat_data: Dict[str, BDMTXNCategory]) -> Dict[str, Dict[re.Pattern, str]]:
        """Get the compiled category map from the category data.
        
        Args:
            cat_data (Dict[str, Any]): The category data to compile.
        
        Returns:
            Dict[str, Dict[re.Pattern, str]]: The compiled category map.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            ccm = {}
            for cat_id, bdm_tc in cat_data.items():
                compiled_pattern = re.compile(bdm_tc.pattern)
                ccm[compiled_pattern] = bdm_tc.full_cat
            return ccm
        except Exception as e:
            logger.error(f"Error compiling transaction categories: {e}")
            raise
    #endregion WB_TYPE_TXN_CATEGORIES_compile()
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK()
    def FI_TXN_CATEGORIES_WORKBOOK(self, fi_key: str, 
        category_map: bdm.CATEGORY_MAP_WORKBOOK) -> bdm.TXN_CATEGORIES_WORKBOOK:
        """Constructor for TXN_CATEGORIES_WORKBOOK wb_content dictionary for an FI.
        
        Args:
            fi_key (str): The key for the financial institution.
            cat_map (Dict[str, Any]): The CATEGORY_MAP data.
        
        Returns:
            WB_TYPE_TXN_CATEGORIES workbook content dictionary:
                { "name": "<filename>.txn_categories.json",
                   "categories": { "cat_id1": BDMTXNCategory.to_dict(),
                                   "cat_id2": BDMTXNCategory.to_dict(),
                                   ... 
                                }
                }
                Also adds CATEGORY_MAP to the catalog and to ccm.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            txn_cat_wb_path: Path = self.FI_WB_TYPE_TXN_CATEGORIES_abs_path(fi_key)

            txn_cat_wb_content = {
                bdm.WB_NAME: txn_cat_wb_path.stem,
                bdm.WB_CATEGORY_COUNT: 0,
                bdm.WB_CATEGORY_COLLECTION: {}
            }
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
                txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION][cat_id] = bdm_tc
            c = len(txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION]) 
            txn_cat_wb_content[bdm.WB_CATEGORY_COUNT] = c
            return txn_cat_wb_content
        except Exception as e:
            logger.error(f"Error compiling transaction categories: {e}")
            raise
    #endregion FI_TXN_CATEGORIES_WORKBOOK()
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_file_load()
    def FI_CATEGORY_MAP_WORKBOOK_load(self, fi_key: str) -> bdm.CATEGORY_MAP_WORKBOOK:
        """Load the CATEGORY_MAP file for an FI ( financial institution).

        Load the content from the CATEGORY_MAP workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            # Load the category_map_workbook for an FI
            cat_map_workbook: bdm.CATEGORY_MAP_WORKBOOK = None
            cat_map_wb_url = self.CATEGORY_MAP_WORKBOOK_url(fi_key)
            cat_map_workbook = bsm_WORKBOOK_CONTENT_url_get(cat_map_wb_url,
                                                    bdm.WB_TYPE_CATEGORY_MAP,)
            if (not isinstance(cat_map_workbook, dict) or
                 len(cat_map_workbook) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {cat_map_wb_url}")
            logger.info(f"BizEVENT: Loaded CATEGORY_MAP for FI_KEY('{fi_key}'), "
                        f"len='{len(cat_map_workbook)}', abs_Path='{cat_map_wb_url}'")
            return cat_map_workbook
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion CATEGORY_MAP_file_load()
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_WORKBOOK_url()
    def CATEGORY_MAP_WORKBOOK_url(self, fi_key: str) -> str:
        """Get the URL for the CATEGORY_MAP_WORKBOOK for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The URL for the transaction categories workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            cat_map_path: Path = self.CATEGORY_MAP_WORKBOOK_abs_path(fi_key)
            return cat_map_path.as_uri()
        except KeyError as e:
            logger.error(f"Category Map file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion CATEGORY_MAP_WORKBOOK_url()
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_WORKBOOK_abs_path()
    def CATEGORY_MAP_WORKBOOK_abs_path(self, fi_key: str) -> Path:
        """Get the absolute path for the CATEGORY_MAP_WORKBOOK for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The absolute path for the CATEGORY_MAP workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            cat_map_filename = self.settings[bdms.CATEGORY_CATALOG][fi_key][bdms.CATEGORY_MAP_FULL_FILENAME]
            fi_folder: Path = self.settings.FI_FOLDER_abs_path(fi_key)
            cat_map_path: Path= fi_folder / cat_map_filename
            if not cat_map_path.exists():
                raise FileNotFoundError(f"Category Map file not "
                                        f"found: {cat_map_path}")
            return cat_map_path
        except KeyError as e:
            logger.error(f"CATEGORY_MAP_WORKBOOK file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion CATEGORY_MAP_WORKBOOK_abs_path()
    # ------------------------------------------------------------------------ +
    #region valid_state()
    def valid_state(self) -> None:
        """Raise an error if the BDMTXNCategoryManager is NOT in a valid state."""
        try:
            if not self.settings or not isinstance(self.settings, bdms.BudManSettings):
                raise ValueError("Invalid catalog state, BudManSettings not found.")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion valid_state()
    # ------------------------------------------------------------------------ +
    #endregion BDMTXNCategoryManager methods
    # ------------------------------------------------------------------------ +
