# ---------------------------------------------------------------------------- +
# test_budman_command_view_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os, inspect
from pathlib import Path
# third-party libraries
import logging, p3_utils as p3u, p3logging as p3l
# local libraries
from budman_app import BudManApp
from budman_namespace import *
from budman_domain_model import BudgetDomainModel
from budman_view_model import BudManViewModel
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_BDM_STORE_load():
    """Test the BudManCommandViewModel.BDM_STORE_load() method."""
    try:
        logger.info(test_BDM_STORE_load.__doc__)
        # Create a BudgetDomainModelIdentity instance and initialize it
        # from the user's BDM_STORE file.
        bmvm = BudManViewModel().initialize(load_user_store=True)
        assert isinstance(bmvm, BudManViewModel), \
            "Expected BudManCommandViewModel, got: " + str(type(bmvm))
        assert bmvm.BDM_STORE_loaded, \
            "BDM_STORE should be loaded"
        assert bmvm.budget_model is not None, \
            "bmvm.budget_model should not be None"
        assert isinstance(bmvm.budget_model, BudgetDomainModel), \
            "Expected bmvm.budget_model to be a BudgetModel instance, got: " + str(type(bmvm.budget_model))        
    except Exception as e:
        pytest.fail(f"BudgetManagerViewModelInterface raised an exception: {str(e)}")