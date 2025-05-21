#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
import os, sys
import logging, pytest
from config import settings

# sys.path.insert(0,  '../src')
print("\nCurrent working directory:", os.getcwd())
print("Resolving path to current file:", os.path.abspath(__file__))
print("sys.path:", sys.path)

# Ensure the path to p3logging is added to sys.path
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import p3logging as p3l
from p3_budman.p3_budman import *

#------------------------------------------------------------------------------+
def test_main_default(caplog) -> None:
    """Test operation of default logging config."""
    with caplog.at_level(logging.DEBUG):
        budman_app_start(testmode=True)
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

