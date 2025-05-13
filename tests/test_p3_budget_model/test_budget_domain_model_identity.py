# ---------------------------------------------------------------------------- +
# test_budget_domain_model_identity.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
import budman_model as p3bm
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(p3bm.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_domain_model_identity():
    """Test the BudgetDomainModelIdentity class."""
    try:
        logger.info(test_budget_domain_model_identity.__doc__)
        # Create a BudgetDomainModelIdentity instance.
        bdm = p3bm.BudgetDomainModelIdentity()
        assert isinstance(bdm, p3bm.BudgetDomainModelIdentity), \
            "BudgetDomainModelIdentity should be a BudgetDomainModelIdentity instance"
        assert bdm.uid is not None, \
            "BudgetDomainModelIdentity uid should not be None"
        assert isinstance(bdm.uid, str), \
            "BudgetDomainModelIdentity uid should be a string"
        assert bdm.name is not None, \
            "BudgetDomainModelIdentity name should not be None"
        assert isinstance(bdm.name, str), \
            "BudgetDomainModelIdentity name should be a string"
    except Exception as e:
        pytest.fail(f"BudgetDomainModelIdentity raised an exception: {str(e)}")