#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from abc import ABC, abstractmethod
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
from budman_app import *
from budman_namespace import *
from budman_data_context import BudManDataContextBaseInterface
#endregion imports
#------------------------------------------------------------------------------+
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_main_default(caplog) -> None:
    """Test operation of default logging config."""
    with caplog.at_level(logging.DEBUG):
        BudManApp().budman_app_start(testmode=True)
    assert "warning message" in caplog.text, \
        "Expected 'Warning message' in log output"
    assert "debug message" in caplog.text, \
        "Expected 'Debug message' in log output"
    assert "info message" in caplog.text, \
        "Expected 'Info message' in log output"
    assert "error message" in caplog.text, \
        "Expected 'Error message' in log output"
    assert "critical message" in caplog.text, \
        "Expected 'Critical message' in log output"
    assert "division by zero" in caplog.text, \
        "Expected 'division by zero' in log output"

