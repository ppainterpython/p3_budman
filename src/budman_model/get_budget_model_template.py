# ---------------------------------------------------------------------------- +
#region create_config_template.py module
""" Provide a means to obtain a reference to 
BudgetModelTemplate.budget_model_template in the blind, without circular
references from BudgetModel class. 
The BudgetModelTemplate class is used a a configuration template, but it
is a subclass of BudgetModel class. This approach is to have a simple module
to reference the budget_model_template Dict without circular imports between 
BudgetModel class and BudgetModelTemplate class."""
#endregion budget_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from typing import Dict

# third-party modules and packages

# local modules and packages
from .budget_model_template import BudgetModelTemplate
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
def __get_budget_model_template__() -> Dict:
    """Return BudgetModelTemplate.budget_model_template Dict.
    """
    return BudgetModelTemplate.get_budget_model_template()
# ---------------------------------------------------------------------------- +
