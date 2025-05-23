# ---------------------------------------------------------------------------- +
# test_budman_command_view_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect
from config import settings
import logging, p3_utils as p3u, p3logging as p3l

# local libraries
import budman_model as p3bm
import budman_view_model.budman_view_model_interface as p3bmvm
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(settings.app_name)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_BUDMAN_STORE_load():
    """Test the BudManCommandViewModel.BUDMAN_STORE_load() method."""
    try:
        logger.info(test_BUDMAN_STORE_load.__doc__)
        # Create a BudgetDomainModelIdentity instance and initialize it
        # from the user's BDM_STORE file.
        bmvm = p3bmvm.BudgetManagerViewModelInterface().initialize(load_user_store=True)
        assert isinstance(bmvm, p3bmvm.BudgetManagerViewModelInterface), \
            "Expected BudManCommandViewModel, got: " + str(type(bmvm))
        assert bmvm.BUDMAN_STORE_loaded, \
            "BUDMAN_STORE should be loaded"
        assert bmvm.budget_model is not None, \
            "bmvm.budget_model should not be None"
        assert isinstance(bmvm.budget_model, p3bm.BudgetDomainModel), \
            "Expected bmvm.budget_model to be a BudgetModel instance, got: " + str(type(bmvm.budget_model))        
    except Exception as e:
        pytest.fail(f"BudgetManagerViewModelInterface raised an exception: {str(e)}")