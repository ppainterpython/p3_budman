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
__name__ = "budman_domain_model"
__description__ = "Budget Manager (BudMan) Model implementation."
__license__ = "MIT"

# from .budget_domain_model_identity import BudgetDomainModelIdentity
from .budget_domain_model import BudgetDomainModel
from .budget_domain_model_config import BDMConfig
from .bdm_workbook_class import BDMWorkbook

# symbols for "from budman_model import *"
__all__ = [
    "BudgetDomainModel",
    "Model_Base",
    "Model_Binding",
    "BDMConfig",
    "BDMWorkbook"
]