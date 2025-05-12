# ---------------------------------------------------------------------------- +
#region create_config_template.py module
""" Provide a means to create a configuration template for the budget model.
The BudgetModelTemplate class is used a a configuration template, but it
is a subclass of BudgetModel class. This approach is to have a simple module
to create the template without circular imports between BudgetModel class and
BudgetModelTemplate class."""
#endregion budget_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l

# local modules and packages
from .budget_model_template import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
def __create_config_template__() -> BudgetModelTemplate:
    """Create a BudgetModelTemplate instance.

    Returns:
        BudgetModelTemplate: A BudgetModelTemplate instance.
    """
    # Create a BudgetModelTemplate instance.
    bmt = BudgetModelTemplate()
    return bmt
