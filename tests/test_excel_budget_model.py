# ---------------------------------------------------------------------------- +
#region test_excel_budget_model.py
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
import budman_app
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
THIS_APP_NAME = "Test_p3_excel_files"
#endregion Globals
# ---------------------------------------------------------------------------- +
#region test_init_budget_model() -> dict
# def test_init_budget_model() -> None:
#     """Test the init_budget_model function."""
#     try:
#         # Initialize the logger from a logging configuration file.
#         # p3l.setup_logging(THIS_APP_NAME,p3l.STDOUT_FILE_LOG_CONFIG_FILE)
#         budget_model = p3bt.init_budget_model(p3bt.budget_config)
        
#         # Check if the budget model is a dictionary
#         assert isinstance(budget_model, dict), "Budget model should be a dictionary"
        
#         # Check if the budget model contains expected keys
#         expected_keys = ['income', 'expenses', 'savings']
#         for key in expected_keys:
#             assert key in budget_model, f"Key '{key}' not found in budget model"
        
#     except Exception as e:
#         pytest.fail(f"init_budget_model raised an exception: {str(e)}")
#endregion test_init_budget_model() -> dict
# ---------------------------------------------------------------------------- +
