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
    bsm_BDM_WORKBOOK_content_load,
    bsm_BDM_WORKBOOK_content_put
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
            cat_map: bdm.DATA_OBJECT = self.FI_CATEGORY_MAP_file_load(fi_key)
            txn_cat_content = self.FI_WB_TYPE_TXN_CATEGORIES(fi_key, cat_map)

            self.FI_WB_TYPE_TXN_CATEGORIES_add(fi_key, txn_cat_content)
        except Exception as e:
            logger.error(f"Error updating CATEGORY_MAP for FI_KEY('{fi_key}') {e}")
            raise
    #endregion FI_WB_TYPE_TXN_CATEGORIES_update_CATEGORY_MAP()
    # ------------------------------------------------------------------------ +
    #region FI_WB_TYPE_TXN_CATEGORIES_add()
    def FI_WB_TYPE_TXN_CATEGORIES_add(self, fi_key: str, 
                                      txn_cat_content: bdm.DATA_OBJECT) -> None:
        """Add the WB_TYPE_TXN_CATEGORIES workbook to the catalog for the FI.

        Add the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            if (not isinstance(txn_cat_content, dict) or
                'categories' not in txn_cat_content or
                 not isinstance(txn_cat_content['categories'], dict) or 
                 len(txn_cat_content['categories']) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {txn_cat_content}")
            cat_data: Dict[str, Any] = txn_cat_content['categories']
            # cat_data : Dict[str, BDMTXNCategory] = {
            #     cat_id: BDMTXNCategory(**data) 
            #         for cat_id, data in cat_dict.items()
            # }
            ccm = self.WB_TYPE_TXN_CATEGORIES_compile(cat_data)
            self.catalog[fi_key] = txn_cat_content
            self.ccm[fi_key] = ccm
            logger.info(f"Loaded {len(self.catalog[fi_key])} categories for {fi_key}.")
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion FI_WB_TYPE_TXN_CATEGORIES_add()
    # ------------------------------------------------------------------------ +
    #region FI_WB_TYPE_TXN_CATEGORIES_file_load()
    def FI_WB_TYPE_TXN_CATEGORIES_file_load(self, fi_key: str) -> None:
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
            cat_url = self.FI_WB_TYPE_TXN_CATEGORIES_url(fi_key)
            bdm_wb : BDMWorkbook = BDMWorkbook(
                wb_type=bdm.WB_TYPE_TXN_CATEGORIES,
                wb_url=cat_url,
                fi_key=fi_key
            )
            txn_cat_content_json: Dict = bsm_BDM_WORKBOOK_content_load(bdm_wb)
            if (not isinstance(txn_cat_content_json, dict) or
                'categories' not in txn_cat_content_json or
                 not isinstance(txn_cat_content_json['categories'], dict) or 
                 len(txn_cat_content_json['categories']) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {cat_url}")
            cat_dict: Dict[str, Any] = txn_cat_content_json['categories']
            cat_data : Dict[str, BDMTXNCategory] = {
                cat_id: BDMTXNCategory(**data) 
                    for cat_id, data in cat_dict.items()
            }
            ccm = self.WB_TYPE_TXN_CATEGORIES_compile(cat_data)
            self.catalog[fi_key] = cat_data
            self.ccm[fi_key] = ccm
            logger.info(f"Loaded {len(self.catalog[fi_key])} categories for {fi_key}.")
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion FI_WB_TYPE_TXN_CATEGORIES_file_load()
    # ------------------------------------------------------------------------ +
    #region FI_WB_TYPE_TXN_CATEGORIES_url()
    def FI_WB_TYPE_TXN_CATEGORIES_url(self, fi_key: str) -> str:
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
    #endregion FI_WB_TYPE_TXN_CATEGORIES_url()
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
    #region WB_TYPE_TXN_CATEGORIES_compile()
    def FI_WB_TYPE_TXN_CATEGORIES(self, fi_key: str, cat_map: bdm.DATA_OBJECT) -> bdm.DATA_OBJECT:
        """Constructor for WB_TYPE_TXN_CATEGORIES wb_content dictionary for an FI.
        
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
            txn_cat_path: Path = self.FI_WB_TYPE_TXN_CATEGORIES_abs_path(fi_key)

            txn_cat_content = {
                "name": txn_cat_path.stem,
                "categories": {}
            }
            category_map: bdm.DATA_OBJECT = cat_map['category_map']
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
                txn_cat_content["categories"][cat_id] = bdm_tc
            return txn_cat_content
        except Exception as e:
            logger.error(f"Error compiling transaction categories: {e}")
            raise
    #endregion WB_TYPE_TXN_CATEGORIES_compile()
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_file_load()
    def FI_CATEGORY_MAP_file_load(self, fi_key: str) -> bdm.DATA_OBJECT:
        """Load the CATEGORY_MAP file for an FI ( financial institution).

        Load the content from the CATEGORY_MAP workbook for the given
        financial institution (FI), configuring its url from settings.
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            # Load the category_map for an FI
            cat_map_abs_path = self.CATEGORY_MAP_abs_path(fi_key)
            cat_map_dict: bdm.DATA_OBJECT = toml.load(cat_map_abs_path)
            if (not isinstance(cat_map_dict, dict) or
                 len(cat_map_dict) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {cat_map_abs_path}")
            logger.info(f"BizEVENT: Loaded CATEGORY_MAP for FI_KEY('{fi_key}'), "
                        f"len='{len(cat_map_dict)}', abs_Path='{cat_map_abs_path}'")
            return cat_map_dict
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise
    #endregion CATEGORY_MAP_file_load()
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_url()
    def CATEGORY_MAP_url(self, fi_key: str) -> str:
        """Get the URL for the CATEGORY_MAP workbook for a given FI.

        Args:
            fi_key (str): The key for the financial institution.
        
        Returns:
            str: The URL for the transaction categories workbook.
        """
        try:
            self.valid_state()  # Ensure the manager is in a valid state
            cat_map_path: Path = self.CATEGORY_MAP_abs_path(fi_key)
            return cat_map_path.as_uri()
        except KeyError as e:
            logger.error(f"Category Map file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion CATEGORY_MAP_url()
    # ------------------------------------------------------------------------ +
    #region CATEGORY_MAP_abs_path()
    def CATEGORY_MAP_abs_path(self, fi_key: str) -> Path:
        """Get the absolute path for the CATEGORY_MAP workbook for a given FI.

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
            logger.error(f"Category Map file not found for FI key: {fi_key}")
            raise e
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion CATEGORY_MAP_abs_path()
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
