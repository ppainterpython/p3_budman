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
from .budget_model_constants import *

from .budget_domain_model_identity import (
    BudgetDomainModelIdentity,
)
from .model_base_interface import BDMBaseInterface
from .model_client_interface import BDMClientInterface

from .budget_domain_model_config import (
    BudgetDomainModelConfig,
    tryout_budget_model_config)

from .budget_domain_model import (
    BudgetDomainModel,
    log_BDM_info,
    log_BSM_info,
    check_budget_model,
)
from .budget_storage_model import (
    bsm_BUDMAN_STORE_load,
    bsm_BUDMAN_STORE_save,
    budget_storage_model_new,
)

from .budget_categorization import (
    execute_worklow_categorization,
    check_budget_category,
    map_budget_category,
)

from .budget_category_mapping import (
    map_category,
    category_map_count,
    category_map,
)

__all__ = [
    "BDMBaseInterface",
    "BDMClientInterface",
    "BudgetDomainModelIdentity",
    "BudgetDomainModel",
    "BudgetDomainModelConfig",
    "bsm_BUDMAN_STORE_load",
    "bsm_BUDMAN_STORE_save",
    "budget_storage_model_new",
    "bsm_bdm_url_abs_path",
    "log_BDM_info",
    "log_BSM_info",
    "tryout_budget_model_config",
    "execute_worklow_categorization"
    "check_budget_model",
    "map_budget_category",
    "__create_config_template__",
    "category_map_count",
    "map_category",
]
