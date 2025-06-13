# ---------------------------------------------------------------------------- +
# test_bsm.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from typing import Type, Any
# third-party libraries
import inspect
import logging, p3_utils as p3u, p3logging as p3l
# local libraries
from budget_storage_model import *
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class TestBSM:
    """BSM - BudMan Storage Model testing."""
    def test_bsm_BDM_STORE_url_load(self) -> None:
        """Test loading from BDM_STORE json objects from url."""
        try:
            logger.info(self.test_bsm_BDM_STORE_url_load.__doc__)
            # Save and load test BDM_STORE data.

        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)
    def test_bsm_get_workbook_names(self) -> None:
        """Test loading from BDM_STORE json objects from url."""
        try:
            # TODO: can't leave this hardcoded path here, but it is a good test.
            folder = "C:\\Users\\ppain\\OneDrive\\budget\\boa\\data\\new"
            logger.info(self.test_bsm_get_workbook_names.__doc__)
            wb_paths = bsm_get_workbook_names2(Path(folder))
            assert isinstance(wb_paths, list), "Expected a list of workbook paths."
            assert all(isinstance(p, Path) for p in wb_paths), "All items should be Path objects."

        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)

