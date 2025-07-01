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
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from treelib import Tree

# local modules and packages
import budman_namespace.design_language_namespace as bdl
import budman_settings as bdms
from budget_storage_model import (
    bsm_WORKBOOK_content_url_get,
    bsm_WORKBOOK_content_url_put
)
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
#region BDMTXNCategory class (@dataclass)
@dataclass
class BDMTXNCategory:
    """ BDMTXNCategory is a dataclass that represents a transaction category.
    
    Attributes:
        level1 (str): The first level of the category hierarchy.
        level2 (str): The second level of the category hierarchy.
        level3 (str): The third level of the category hierarchy.
        description (str): A description of the category.
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
    
    def __post_init__(self):
        """Post-initialization to ensure levels are trimmed."""
        self.level1 = self.level1.strip()
        self.level2 = self.level2.strip()
        self.level3 = self.level3.strip()
#endregion BDMTXNCategory class (@dataclass)
# ---------------------------------------------------------------------------- +
#region BDMTXNCategoryManager class intrinsics
class BDMTXNCategoryManager:
    """BDMTXNCategoryManager a class to manage transaction categories.
    
    Manages a catalog of transaction category sets, based on different financial
    institution requirements.

    Attributes:
        settings (bdms.BudManSettings): The settings for the BDMTXNCategoryManager
        catalog (Dict[str, Dict[str, BDMTXNCategory]]): The catalog of 
            transaction categories, the FI_KEY is the key.
    """
    def __init__(self, settings:bdms.BudManSettings):
        """Initialize the BDMTXNCategoryManager with settings."""
        self._settings: bdms.BudManSettings = settings
        self._config: Dict[str, Any] = settings.config
        self._catalog: Dict[str, Dict[str, BDMTXNCategory]] = {}
        """Catalog of transaction categories, keyed by financial institution."""
        self._ccm: Dict[str, Dict[re.Pattern, str]] = {}
        """Compiled category maps for FI's."""
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
    def config(self) -> Dict[str, Any]:
        """Get the configuration for the BDMTXNCategoryManager."""
        return self._config
    @config.setter
    def config(self, value: Dict[str, Any]):
        """Set the configuration for the BDMTXNCategoryManager."""
        self._config = value

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
    def load_catalog(self, fi_key: str) -> None:
        """Load the transaction category catalog for a given financial institution.

        Load the content from the WB_TYPE_TXN_CATEGORIES workbook for the given
        financial institution (FI), computing its url from settings.
        A WB_TYPE_TXN_CATEGORIES workbook is structured as:
        {
             "name": "e.g., all_categories",
             "categories": {BDMTXNCategory.to_dict() for each category}
        }
        Also compiles the category map for the financial institution.

        Args:
            fi_key (str): The key for the financial institution.
        """
        try:
            # Load the catalog for an FI
            filename : str = self.config[bdms.CATEGORY_CATALOG][fi_key]
            fi_folder : Path = self.settings.FI_FOLDER_abs_path(fi_key) 
            cat_path = fi_folder / filename
            cat_url = cat_path.as_uri()
            if not cat_path.exists():
                raise FileNotFoundError(f"Transaction Categories file not "
                                        f"found: {cat_path}")
            txn_cat_content: Dict = bsm_WORKBOOK_content_url_get(cat_url)
            if (not isinstance(txn_cat_content, dict) or 
                'categories' not in txn_cat_content or
                 not isinstance(txn_cat_content['categories'], dict) or 
                 len(txn_cat_content['categories']) == 0):
                raise TypeError(f"Expected a non-empty dictionary from {cat_url}")
            cat_dict: Dict[str, Any] = txn_cat_content['categories']
            cat_data : Dict[str, BDMTXNCategory] = {
                cat_id: BDMTXNCategory(**data) 
                    for cat_id, data in cat_dict.items()
            }
            ccm = self.get_compiled_category_map(cat_data)
            self.catalog[fi_key] = cat_data
            self.ccm[fi_key] = ccm
            logger.info(f"Loaded {len(self._catalog[fi_key])} categories for {fi_key}.")
        except Exception as e:
            logger.error(f"Error loading catalog fi_key: '{fi_key}' {e}")
            raise

    def get_compiled_category_map(self, cat_data: Dict[str, BDMTXNCategory]) -> Dict[str, Dict[re.Pattern, str]]:
        """Get the compiled category map from the category data.
        
        Args:
            cat_data (Dict[str, Any]): The category data to compile.
        
        Returns:
            Dict[str, Dict[re.Pattern, str]]: The compiled category map.
        """
        ccm = {}
        for cat_id, bdm_tc in cat_data.items():
            pattern = re.compile(bdm_tc.pattern)
            ccm[pattern] = bdm_tc.full_cat
        return ccm
    #region BDMTXNCategoryManager methods
