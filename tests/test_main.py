#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
#region imports
# python standard libraries
import logging
# third-party modules and packages
# local modules and packages
from budman_app import BudManApp
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

