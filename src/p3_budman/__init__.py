"""
p3_fi_transactions package

Budget Model applies mostly to transactions from financial institutions (FI). This package 
has the functionality to intake transactions from a financial institution (FI) and process them into
a budget model. The package is designed to work with Excel workbooks, specifically for budgeting.
"""
__version__ = "0.2.0"
__author__ = "Paul Painter"
__copyright__ = "2024 Paul Painter"
__name__ = "p3_budman"
__description__ = "Budget Manager (BudMan) a p3 application."
__license__ = "MIT"

from ..budman_model.budget_model_constants import *

from ..budman_model.budget_domain_model import (
    BudgetModel,
    log_BDM_info,
    log_BSM_info,
    check_budget_model,
)

from ..budman_model.budget_model_template import (
    BudgetModelTemplate,
    tryout_budget_model_template)

from ..budman_model.budget_storage_model import (
    bsm_save,
    bsm_load,
    bsm_bm_store_abs_path,
)

from ..budman_model.budget_categorization import (
    execute_worklow_categorization,
    check_budget_category,
    map_budget_category,
)

from ..budman_model.budget_category_mapping import (
    map_category,
    category_map_count,
)

__all__ = [
    "bsm_save",
    "bsm_load",
    "bsm_bm_store_abs_path",
    "BudgetModel",
    "log_BDM_info",
    "log_BSM_info",
    "BudgetModelTemplate",
    "tryout_budget_model_template",
    "execute_worklow_categorization"
    "check_budget_model",
    "__create_config_template__"
]

def __create_config_template__() -> BudgetModelTemplate:
    """Create a BudgetModelTemplate instance."""
    """

    Returns:
        BudgetModelTemplate: A BudgetModelTemplate instance.
    """
    # Create a BudgetModelTemplate instance.
    bmt = BudgetModelTemplate()
    return bmt