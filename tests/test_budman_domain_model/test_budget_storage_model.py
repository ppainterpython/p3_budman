# ---------------------------------------------------------------------------- +
# test_budget_storage_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest
from pathlib import Path
# third-party libraries
import logging, p3_utils as p3u, p3logging as p3l

# local libraries
from budget_storage_model.budget_storage_model import budget_storage_model_new
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_storage_model_new():
    """Test bsm_budget_storage_model_new() function."""
    try:
        logger.info(test_budget_storage_model_new.__doc__)
        bdm_url_path_str = budget_storage_model_new()
        assert bdm_url_path_str is not None, \
            "Budget model store path should not be None"
        assert Path(bdm_url_path_str).exists(), \
            "Budget model store path should exist"
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        pytest.fail(f"bsm_save() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
# def test_bsm_save():
#     """Test bsm_save() function."""
#     try:
#         logger.info(test_bsm_save.__doc__)
#         # bmt = p3bm.BudgetModelTemplate()
#         # bm = p3bm.BudgetModel().bdm_initialize(bm_config_src=bmt)
#         bm = p3bm.BudgetModel().bdm_initialize()
#         assert isinstance(bm, p3bm.BudgetModel), \
#             "Budget model should be a BudgetModel instance"
#         assert p3bm.bsm_save(bm) is None, \
#             "bsm_save() should return None"
#         del bm
#     except Exception as e:
#         pytest.fail(f"bsm_save() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
# def test_bsm_load():
#     """Test bsm_load() function."""
#     try:
#         logger.info(test_bsm_load.__doc__)
#         bm = p3bm.BudgetModel().bdm_initialize(bdm_url_dict)
#         store_abs_path = p3bm.bsm_bdm_url_abs_path()
#         assert store_abs_path is not None, \
#             "Budget model store path should not be None"
#         assert isinstance(store_abs_path, Path), \
#             "Budget model store path should be a Path object"
#         assert isinstance((bdm_url_dict := p3bm.bsm_load(store_abs_path)), dict), \
#             "Budget model store should be a dictionary"


#         assert isinstance(bm, p3bm.BudgetModel), \
#             "Budget model should be a BudgetModel instance"
#     except Exception as e:
#         pytest.fail(f"bsm_save() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
