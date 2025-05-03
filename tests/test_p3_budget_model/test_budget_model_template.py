# ---------------------------------------------------------------------------- +
#region test_budget_model_template.py
# ---------------------------------------------------------------------------- +
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect

# local libraries
import p3_utils as p3u, p3logging as p3l
import data.p3_budget_model as p3bt
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
THIS_APP_NAME = "Test_p3_excel_files"
#endregion Globals
# ---------------------------------------------------------------------------- +
#region test_init_budget_model() -> dict
def test_init_budget_model_template() -> None:
    """Test the BudgetModelTemplate() function."""
    try:
        # Initialize the logger from a logging configuration file.
        # p3l.setup_logging(THIS_APP_NAME,p3l.STDOUT_FILE_LOG_CONFIG_FILE)
        bmt = p3bt.BudgetModelTemplate()
        
        # Check if the budget model is a dictionary
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
                
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
#endregion test_init_budget_model() -> dict
# ---------------------------------------------------------------------------- +
