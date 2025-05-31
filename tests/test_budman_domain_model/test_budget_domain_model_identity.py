# ---------------------------------------------------------------------------- +
# test_budget_domain_model_identity.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
import inspect
# third-party libraries
import logging, p3_utils as p3u, p3logging as p3l
# local libraries
from budman_app import *
from budman_namespace import *
from budman_domain_model import BudgetDomainModelIdentity
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_domain_model_identity():
    """Test the BudgetDomainModelIdentity class."""
    try:
        logger.info(test_budget_domain_model_identity.__doc__)
        # Create a BudgetDomainModelIdentity instance.
        bdm = BudgetDomainModelIdentity()
        assert isinstance(bdm, BudgetDomainModelIdentity), \
            "BudgetDomainModelIdentity should be a BudgetDomainModelIdentity instance"
        assert bdm.uid is not None, \
            "BudgetDomainModelIdentity uid should not be None"
        assert isinstance(bdm.uid, str), \
            "BudgetDomainModelIdentity uid should be a string"
        assert bdm.name is not None, \
            "BudgetDomainModelIdentity name should not be None"
        assert isinstance(bdm.name, str), \
            "BudgetDomainModelIdentity name should be a string"
        bdm_store_path = bdm.bdm_store_abs_path()
        assert bdm_store_path is not None, \
            "BudgetDomainModelIdentity store path should not be None"
        assert isinstance(bdm_store_path, Path), \
            "BudgetDomainModelIdentity store path should be a Path object"
        # Brand new bdmi should not resolve yet.
        with pytest.raises(Exception) as excinfo:
            bdm.bdm_stor()
        
    except Exception as e:
        pytest.fail(f"BudgetDomainModelIdentity raised an exception: {str(e)}")