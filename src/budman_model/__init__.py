"""
Budget Manager - p3_budman package

Budget Manager (budman) follows a budgeting domain model based on 
transactions from financial institutions (FI). This package 
has the functionality to intake transactions from a financial institution (FI) 
and process them into a budget model. The package is designed to work with 
Excel workbooks, specifically for budgeting.
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "p3_budget_manager"
__description__ = "Budget Manager (BudMan) a p3 application."
__license__ = "MIT"

from .budget_model_constants import *

from .budget_domain_model_identity import (
    BudgetDomainModelIdentity,
)
from .budget_domain_model import (
    BudgetModel,
    log_BDM_info,
    log_BSM_info,
    check_budget_model,
)

from .budget_model_template import (
    BudgetModelTemplate,
    tryout_budget_model_template)

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
)

__all__ = [
    "BudgetDomainModelIdentity",
    "bsm_BUDMAN_STORE_load",
    "bsm_BUDMAN_STORE_save",
    "budget_storage_model_new",
    "bsm_bdm_url_abs_path",
    "BudgetModel",
    "log_BDM_info",
    "log_BSM_info",
    "BudgetModelTemplate",
    "tryout_budget_model_template",
    "execute_worklow_categorization"
    "check_budget_model",
    "__create_config_template__"
]
