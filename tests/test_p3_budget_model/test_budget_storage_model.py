# ---------------------------------------------------------------------------- +
# test_budget_storage_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect, pyjson5 as json5

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
import data.p3_budget_model as p3bm
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(p3bm.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_bsm_save():
    """Test bsm_save() function."""
    try:
        logger.info(test_bsm_save.__doc__)
        bm = p3bm.BudgetModel().bdm_initialize()
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
        assert p3bm.bsm_save(bm) is None, \
            "bsm_save() should return None"
        del bm
    except Exception as e:
        pytest.fail(f"bsm_save() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bsm_load():
    """Test bsm_load() function."""
    try:
        logger.info(test_bsm_load.__doc__)
        store_abs_path = p3bm.bsm_bm_store_abs_path()
        assert store_abs_path is not None, \
            "Budget model store path should not be None"
        assert isinstance(store_abs_path, Path), \
            "Budget model store path should be a Path object"
        assert isinstance((bm_store_dict := p3bm.bsm_load(store_abs_path)), dict), \
            "Budget model store should be a dictionary"
        bm = p3bm.BudgetModel().bdm_initialize(bm_store_dict)
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
    except Exception as e:
        pytest.fail(f"bsm_save() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
