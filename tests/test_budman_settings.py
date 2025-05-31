# ---------------------------------------------------------------------------- +
# test_bs1.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
# third-party modules and packages
import logging, p3logging as p3l
# local modules and packages
# from config import settings
from budman_settings import *
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class TestBudmanSettings:
    """TestBudmanSettings class contains tests for the BudManApp_settings."""
    
    def test_bs1(self):
        """Test that BudManApp_settings is a dictionary."""
        bs1 = BudManSettings()
        assert isinstance(bs1, BudManSettings)
        assert (bs := bs1.settings) is not None
        assert (bs2 := BudManSettings()) == bs1, "BudManSettings as Singleton should return self again."
