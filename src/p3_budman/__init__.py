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
__copyright__ = "2024 Paul Painter"
__name__ = "p3_budman"
__description__ = "Budget Manager (BudMan) a p3 application."
__license__ = "MIT"

import budman_model, budman_view_model, budman_cli_view

def __create_config_template__() -> budman_model.BudgetModelTemplate:
    """Create a BudgetModelTemplate instance."""
    """

    Returns:
        BudgetModelTemplate: A BudgetModelTemplate instance.
    """
    # Create a BudgetModelTemplate instance.
    bmt = budman_model.BudgetModelTemplate()
    return bmt