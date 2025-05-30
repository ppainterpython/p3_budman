"""
Budget Manager - budman_model package

Budget Manager (budman) follows a budgeting domain model based on 
transactions from financial institutions (FI). This package 
has the functionality to intake transactions from a financial institution (FI) 
and process them into a budget model. The package is designed to work with 
Excel workbooks, specifically for budgeting.
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_model"
__description__ = "Budget Manager (BudMan) Model implementation."
__license__ = "MIT"

from .budget_domain_model_identity import BudgetDomainModelIdentity
from .model_base_interface import BDMBaseInterface
from .model_client_interface import BDMClientInterface
from .budget_domain_model import BudgetDomainModel
from .budget_category_mapping import (
    map_category, category_map, category_map_count
)
from .budget_domain_model_config import (
    BudgetDomainModelConfig
)
from .budget_categorization import (
    check_budget_category, map_budget_category
)
from .budget_storage_model import (
    bsm_verify_folder,
    bsm_BUDMAN_STORE_save,
    bsm_BUDMAN_STORE_load,

)

# symbols for "from budman_model import *"
__all__ = [
    "budget_category_mapping",  # list modules here to use importlib.reload()
    "BudgetDomainModel",
    "BDMBaseInterface",
    "BDMClientInterface",
    "BudgetDomainModelIdentity",
    "BudgetDomainModelConfig",
    "check_budget_category",
    "map_budget_category",
    "map_category",
    "category_map",
    "category_map_count",
    "bsm_verify_folder",
    "bsm_BUDMAN_STORE_save",
    "bsm_BUDMAN_STORE_load"
]