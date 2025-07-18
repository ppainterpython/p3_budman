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
import types
import importlib.util

# third-party modules and packages
import toml
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
from budman_namespace import BDMSingletonMeta
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
    full_cat: str = field(default="")
    level1: str = field(default="")
    level2: str = field(default="")
    level3: str = field(default="")
    payee: str = field(default="")
    description: str = field(default="")
    essential: bool = field(default=False)
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

# ---------------------------------------------------------------------------- +
#region TXNCategoryCatalog class
class TXNCategoryCatalog:
    #region TXNCategoryCatalog class intrinsics
    """Represents a single transaction category catalog for one FI."""
    def __init__(self, fi_key: str, settings: bdms.BudManSettings,
                 txn_categories_workbook: bdm.TXN_CATEGORIES_WORKBOOK = None,
                 category_collection: bdm.CATEGORY_COLLECTION = None):
        self._fi_key: str = fi_key
        self._settings: bdms.BudManSettings = settings
        self._txn_categories_workbook: bdm.TXN_CATEGORIES_WORKBOOK = txn_categories_workbook
        self._category_collection: bdm.CATEGORY_COLLECTION = category_collection
        self._category_map : bdm.CATEGORY_MAP_WORKBOOK = None
        self._category_map_module : types.ModuleType =  None
        self._compiled_category_map: Dict[re.Pattern, str] = None
    # ------------------------------------------------------------------------ +
    #region TXNCategoryCatalogItem properties
    @property
    def valid(self) -> bool:
        """Raise error if the TXNCategoryCatalog is not in a valid state."""
        p3u.is_not_non_empty_str("fi_key property", self.fi_key, raise_error=True)
        p3u.is_not_obj_of_type("settings property", self.settings, 
                               bdms.BudManSettings, raise_error=True)
        p3u.is_not_obj_of_type("txn_categories_workbook property", self.txn_categories_workbook, 
                               dict, raise_error=True)
        p3u.is_not_obj_of_type("txn_categories_workbook[bdm.CATEGORY_COLLECTION]", 
                               self.txn_categories_workbook[bdm.WB_CATEGORY_COLLECTION],
                               dict, raise_error=True)
        if self.txn_categories_workbook[bdm.WB_CATEGORY_COUNT] == 0:
            m = f"No transaction categories found for FI key: {self.fi_key}"
            logger.error(m)
            raise ValueError(m)
        p3u.is_not_obj_of_type("category_collection property", self.category_collection, 
                               dict, raise_error=True)
        p3u.is_not_obj_of_type("category_map property", self.category_map, 
                               dict, raise_error=True)
        p3u.is_not_obj_of_type("category_map_module property", self.category_map_module, 
                               types.ModuleType, raise_error=True)
        p3u.is_not_obj_of_type("compiled_category_map property", self.compiled_category_map, 
                               dict, raise_error=True)
        return True
    
    @property
    def fi_key(self) -> str:
        """Get the financial institution key."""
        return self._fi_key
    
    @property
    def settings(self) -> bdms.BudManSettings:
        """Get the settings for the transaction catalog item."""
        return self._settings

    @property
    def txn_categories_workbook(self) -> bdm.TXN_CATEGORIES_WORKBOOK:
        """Get the transaction categories workbook."""
        return self._txn_categories_workbook
    @txn_categories_workbook.setter
    def txn_categories_workbook(self, value: bdm.TXN_CATEGORIES_WORKBOOK):
        """Set the transaction categories workbook."""
        self._txn_categories_workbook = value

    @property
    def category_collection(self) -> bdm.CATEGORY_COLLECTION:
        """Get the category collection."""
        return self._category_collection 
    @category_collection.setter
    def category_collection(self, value: bdm.CATEGORY_COLLECTION):
        """Set the category collection."""
        self._category_collection = value

    @property
    def category_map(self) -> bdm.CATEGORY_MAP_WORKBOOK:
        """Get the category map."""
        return self._category_map
    @category_map.setter
    def category_map(self, value: bdm.CATEGORY_MAP_WORKBOOK):
        """Set the category map."""
        self._category_map = value

    @property
    def category_map_module(self) -> types.ModuleType:
        """Get the category map module."""
        return self._category_map_module
    @category_map_module.setter
    def category_map_module(self, value: types.ModuleType):
        """Set the category map module."""
        self._category_map_module = value

    @property
    def compiled_category_map(self) -> bdm.COMPLIED_CATEGORY_MAP:
        """Get the compiled category map."""
        return self._compiled_category_map
    @compiled_category_map.setter
    def compiled_category_map(self, value: bdm.COMPLIED_CATEGORY_MAP):
        """Set the compiled category map."""
        self._compiled_category_map = value
    #endregion TXNCategoryCatalogItem properties
    # ------------------------------------------------------------------------ +
    #endregion TXNCategoryCatalog class intrinsics
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_WORKBOOK methods
    # ------------------------------------------------------------------------ +
    #region CATEGORY_COLLECTION_create() method
    def CATEGORY_COLLECTION_create(self, 
        category_map: bdm.CATEGORY_MAP_WORKBOOK) -> bdm.CATEGORY_COLLECTION :
        """Construct and return a CATEGORY_COLLECTION from a CATEGORY_MAP_WORKBOOK.

        Args:
            category_map (bdm.CATEGORY_MAP_WORKBOOK): The category map to extract from.
        """
        try:
            # Construct a CATEGORY_COLLECTION content dict.
            category_collection: bdm.CATEGORY_COLLECTION = {}

            for cat in category_map.values():
                l1, l2, l3 = p3u.split_parts(cat)
                bdm_tc = BDMTXNCategory(
                    full_cat=cat,
                    level1=l1,
                    level2=l2,
                    level3=l3,
                    payee=None,
                    description=f"Level 1 Category: {l1}",
                    essential=False, 
                    total=0
                )
                if cat not in category_collection:
                    # Only add a category once, no duplicates. Multiple patterns
                    # map to the same category.
                    category_collection[cat] = bdm_tc
            cnt = len(category_collection)
            logger.info(f"Extracted '{cnt}' categories from {len(category_map)} patterns.")
            return category_collection
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion CATEGORY_COLLECTION_create() method
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_WORKBOOK_import()
    def CATEGORY_MAP_WORKBOOK_import(self) -> None:
        """Load the CATEGORY_MAP_WORKBOOK from the URL.
        
        A CATEGORY_MAP_WORKBOOK is a python module that must be imported one
        time and then reloaded subsequently. It contains python code defining
        the category_map for the FI.
        """
        try:
            # Convert the url to a abs_pathname, then load or reload the module
            mod_path: Path = self.CATEGORY_MAP_WORKBOOK_abs_path(self._fi_key)
            mod_name: str = f"{self._fi_key}_category_map"
            mod = p3u.import_module_from_path(mod_name, mod_path)
            self.category_map_module = mod
            self.category_map = mod.category_map
            self.compiled_category_map = mod.compile_category_map(mod.category_map)
            if not isinstance(self._category_map, dict):
                raise TypeError(f"Invalid CATEGORY_MAP_WORKBOOK content from: '{self._category_map_workbook_url}'")
        except Exception as e:
            logger.error(f"Error loading CATEGORY_MAP_WORKBOOK: {e}")
            raise
    #endregion CATEGORY_MAP_WORKBOOK_import()
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
            # self.valid_state()  # Ensure the manager is in a valid state
            cat_map_filename = self.settings[bdms.CATEGORY_CATALOG][fi_key][bdms.CATEGORY_MAP_WORKBOOK_FULL_FILENAME]
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
    #endregion CATEGORY_MAP_WORKBOOK methods
    # ------------------------------------------------------------------------ +
#endregion TXNCategoryCatalog class
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region BDMTXNCategoryManager class 
class BDMTXNCategoryManager(metaclass=BDMSingletonMeta):
    #region BDMTXNCategoryManager class doc string
    """BDMTXNCategoryManager: manage transaction category catalogs.
    
    Manages a set of transaction category catalogs, at most one per financial
    institution (fi_key). 

    Attributes:
        settings (bdms.BudManSettings): App settings.
        catalogs (Dict[fi_key:str, TXNCategoryCatalog]): TXNCategoryCatalog for an FI_KEY.
    """
    #endregion BDMTXNCategoryManager class doc string
    # ------------------------------------------------------------------------ +
    #region BDMTXNCategoryManager class intrinsics
    # ------------------------------------------------------------------------ +
    #region BDMTXNCategoryManager class __init__()
    def __init__(self, settings:bdms.BudManSettings):
        """Initialize the BDMTXNCategoryManager with settings."""
        self._settings: bdms.BudManSettings = settings
        """App settings: bdms.BudManSettings object."""
        self._catalogs: Dict[str, TXNCategoryCatalog] = {} # bdm.DATA_OBJECT
        """Catalog: key: fi_key, value: TXNCategoryCatalogItem object."""
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
    def catalogs(self) -> Dict[str, Dict[str, BDMTXNCategory]]:
        """Get the catalog of transaction categories."""
        return self._catalogs
    @catalogs.setter
    def catalogs(self, value: Dict[str, TXNCategoryCatalog]):
        """Set the catalog of transaction categories."""
        self._catalogs = value

    #endregion class properties
    # ------------------------------------------------------------------------ +
    #endregion BDMTXNCategoryManager class intrinsics
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region BDMTXNCategoryManager methods
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK_update()
    def FI_TXN_CATEGORIES_WORKBOOK_update(self, fi_key: str) -> str:
        """For the fi_key, refresh the transaction category catalog in-memory
        from the category_map.

        Extract the current unique list of categories from the 
        CATEGORY_MAP_WORKBOOK, and update the TXN_CATEGORIES_WORKBOOK
        category_collection. A user edits the CATEGORY_MAP_WORKBOOK to add or
        remove map patterns for categories, remove or change categories etc.
        Only merge new categories into the TXN_CATEGORIES_WORKBOOK and then
        remove categories that are no longer in the CATEGORY_MAP_WORKBOOK.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            if fi_key not in self.catalogs:
                raise KeyError(f"FI_KEY '{fi_key}' not found in catalog.")
            tcc: TXNCategoryCatalog = self.catalogs[fi_key]
            if not tcc or tcc.txn_categories_workbook is None:
                raise ValueError(f"Invalid TXNCategoryCatalog for FI_KEY '{fi_key}'.")
            # Load the CATEGORY_MAP_WORKBOOK from the TXNCategoryCatalog
            tcc.CATEGORY_MAP_WORKBOOK_import() # sets tcc.category_map
            cm_count = len(tcc.category_map)
            # Construct a CATEGORY_COLLECTION from the CATEGORY_MAP_WORKBOOK values.
            category_collection: bdm.CATEGORY_COLLECTION = None
            category_collection = tcc.CATEGORY_COLLECTION_create(tcc.category_map)
            if not category_collection:
                raise ValueError(f"Updated CATEGORY_COLLECTION for FI_KEY '{fi_key}' is None.")
            cc_count = len(category_collection)
            msg: str = f"Updating TXN_CATEGORIES_WORKBOOK for FI_KEY: {fi_key}"
            msg += f"\n  CATEGORY_MAP_WORKBOOK has {cm_count} patterns."
            msg += f"\n  TXN_CATEGORIES_WORKBOOK has {cc_count} categories."
            # Now merge any new categories from the CATEGORY_MAP_WORKBOOK into
            # the TXN_CATEGORIES_WORKBOOK category_collection. Do not modify
            # any existing categories, just add new ones.
            txn_cat_wb: bdm.TXN_CATEGORIES_WORKBOOK = tcc.txn_categories_workbook
            for key, value in category_collection.items():
                if key not in txn_cat_wb[bdm.WB_CATEGORY_COLLECTION]:
                    # Add new category to the TXN_CATEGORIES_WORKBOOK
                    txn_cat_wb[bdm.WB_CATEGORY_COLLECTION][key] = value
                    m = f"added new category '{key}' to TXN_CATEGORIES_WORKBOOK."
                    msg += f"\n  {m}"
                    logger.debug(f"FI_KEY '{fi_key}' {m}")
            cc_keys : List[str] = list(txn_cat_wb[bdm.WB_CATEGORY_COLLECTION].keys())
            for key in cc_keys:
                if key not in category_collection:
                    # Remove the category from the TXN_CATEGORIES_WORKBOOK
                    del txn_cat_wb[bdm.WB_CATEGORY_COLLECTION][key]
                    m = f"removed category '{key}' from TXN_CATEGORIES_WORKBOOK."
                    msg += f"\n  {m}"
                    logger.debug(f"FI_KEY '{fi_key}' {m}")
            # Save the updated TXN_CATEGORIES_WORKBOOK
            self.FI_TXN_CATEGORIES_WORKBOOK_save(fi_key, txn_cat_wb)
            cm_count = len(tcc.category_map)
            cc_count = len(category_collection)
            msg += f"\n  Updated TXN_CATEGORIES_WORKBOOK saved for FI_KEY: {fi_key}."
            msg += f"\n  CATEGORY_MAP_WORKBOOK has {cm_count} patterns."
            msg += f"\n  TXN_CATEGORIES_WORKBOOK has {cc_count} categories."
            msg += f"\n  TXN_CATEGORIES_WORKBOOK saved to: {self.FI_TXN_CATEGORIES_WORKBOOK_url(fi_key)}"
            return msg
        except Exception as e:
            logger.error(f"Error updating CATEGORY_MAP for FI_KEY('{fi_key}') {e}")
            raise
    #endregion FI_TXN_CATEGORIES_WORKBOOK_update()
    # ------------------------------------------------------------------------ +
    #region FI_TXN_CATEGORIES_WORKBOOK_load()
    def FI_TXN_CATEGORIES_WORKBOOK_load(self, fi_key: str,) -> TXNCategoryCatalog:
        """Load (or reload)the WB_TYPE_TXN_CATEGORIES workbook content for an FI.

        Load the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI). Urls from for TXN_CATEGORIES_WORKBOOK
        and CATEGORY_MAP_WORKBOOK files are based on settings values, configured
        for each financial institution (fi). Also, load the 
        CATEGORY_MAP_WORKBOOK file, and compile it. Create a 
        TXNCategoryCatalogItem populated. Then add or replace it in the 
        BDMTXNCategoryManager's catalog.

        This method fully (re-) initializes an FI's Category Catalog.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            # Load the TXN_CATEGORIES_WORKBOOK file for an FI
            txn_cat_wb_url = self.FI_TXN_CATEGORIES_WORKBOOK_url(fi_key)
            txn_cat_wb_content: bdm.TXN_CATEGORIES_WORKBOOK = None
            txn_cat_wb_content = bsm_WORKBOOK_CONTENT_url_get(txn_cat_wb_url,
                                        wb_type=bdm.WB_TYPE_TXN_CATEGORIES,)
            if (not isinstance(txn_cat_wb_content, dict) or
                bdm.WB_CATEGORY_COLLECTION not in txn_cat_wb_content or
                 not isinstance(txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION], dict) or
                 len(txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION]) == 0):
                raise TypeError(f"Invalid TXN_CATEGORIES_WORKBOOK content from: '{txn_cat_wb_url}'")
            # Rehydrate the BDMTXNCategory objects from the json load.
            category_collection : Dict[str, BDMTXNCategory] = {
                cat_id: BDMTXNCategory(**data) 
                    for cat_id, data in txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION].items()
            }
            txn_cat_wb_content[bdm.WB_CATEGORY_COLLECTION] = category_collection

            # Create a TXNCategoryCatalog to hold the content.
            tcc_params = {
                "fi_key": fi_key,
                "settings": self.settings,
                "txn_categories_workbook": txn_cat_wb_content,
                "category_collection": category_collection
            }
            txn_category_catalog: TXNCategoryCatalog = None
            txn_category_catalog = TXNCategoryCatalog(**tcc_params)
            # Load the CATEGORY_MAP_WORKBOOK from the URL.
            txn_category_catalog.CATEGORY_MAP_WORKBOOK_import()

            # Add/replace catalog item
            self.catalogs[fi_key] = txn_category_catalog
            count = txn_cat_wb_content.get(bdm.WB_CATEGORY_COUNT, 0)
            logger.debug(f"Loaded '{count}' categories for FI_KEY('{fi_key}').")
            return txn_category_catalog
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
            txn_cat_wb_url = self.FI_TXN_CATEGORIES_WORKBOOK_url(fi_key)
            if txn_cat_wb_input is not None:
                # If input is provided, use it directly.
                txn_cat_wb_content = txn_cat_wb_input
            else:
                # Otherwise, load from the catalog.
                if fi_key not in self.catalogs:
                    raise KeyError(f"FI_KEY '{fi_key}' not found in catalog.")
                cat_collection = self.catalogs[fi_key]
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
            txn_cat_path: Path = self.FI_TXN_CATEGORIES_WORKBOOK_abs_path(fi_key)
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
    #region FI_TXN_CATEGORIES_WORKBOOK_abs_path()
    def FI_TXN_CATEGORIES_WORKBOOK_abs_path(self, fi_key: str) -> Path:
        """Get the absolute path for the WB_TYPE_TXN_CATEGORIES workbook 
        for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The URL for the transaction categories workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            txn_cat_filename = self.settings[bdms.CATEGORY_CATALOG][fi_key][bdms.TXN_CATEGORIES_WORKBOOK_FULL_FILENAME]
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
    #endregion FI_TXN_CATEGORIES_WORKBOOK_abs_path()
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
            txn_cat_wb_path: Path = self.FI_TXN_CATEGORIES_WORKBOOK_abs_path(fi_key)

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
    #region FI_CATEGORY_MAP_WORKBOOK_load()
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
            cat_map_wb_url = self.FI_CATEGORY_MAP_WORKBOOK_url(fi_key)
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
    #endregion FI_CATEGORY_MAP_WORKBOOK_load()
    # ------------------------------------------------------------------------ +
    #region FI_CATEGORY_MAP_WORKBOOK_url()
    def FI_CATEGORY_MAP_WORKBOOK_url(self, fi_key: str) -> str:
        """Get the URL for the CATEGORY_MAP_WORKBOOK for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The URL for the transaction categories workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            cat_map_path: Path = self.FI_CATEGORY_MAP_WORKBOOK_abs_path(fi_key)
            return cat_map_path.as_uri()
        except KeyError as e:
            logger.error(f"Category Map file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion FI_CATEGORY_MAP_WORKBOOK_url()
    # ------------------------------------------------------------------------ +
    #region FI_CATEGORY_MAP_WORKBOOK_abs_path()
    def FI_CATEGORY_MAP_WORKBOOK_abs_path(self, fi_key: str) -> Path:
        """Get the absolute path for the FI_CATEGORY_MAP_WORKBOOK for a given FI.

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
    #endregion FI_CATEGORY_MAP_WORKBOOK_abs_path()
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
#endregion BDMTXNCategoryManager class 
# ---------------------------------------------------------------------------- +

