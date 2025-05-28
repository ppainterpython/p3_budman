# ---------------------------------------------------------------------------- +
# test_budman_cli_view_datacontext.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect
from config import settings
import logging, p3_utils as p3u, p3logging as p3l

# local libraries
import budman_model as p3bm
import budman_view_model.budman_cli_view_datacontext as bm_view_dc
import budman_view_model.budman_view_model as p3bmvm
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(settings.app_name)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_BudgetManagerCLIViewDataContext__init__():
    """Test the BudgetManagerCLIViewDataContext constructor."""
    try:
        logger.info(test_BudgetManagerCLIViewDataContext__init__.__doc__)
        # Create a BudgetManagerCLIViewDataContext instance
        bmv_dc = bm_view_dc.BudManCLIViewDataContext(None)
        assert isinstance(bmv_dc, bm_view_dc.BudManCLIViewDataContext), \
            f"Expected BudgetManagerCLIViewDataContext, got: " + str(type(bmv_dc))
        assert not bmv_dc.initialized, \
            "Should not be initialized"
        assert bmv_dc.view_model is None, \
            "view_model property should be None"
        assert bmv_dc.data_context is None, \
            "data_context property should be None"
        assert bmv_dc.dc is None, \
            "dc property should be None"
        assert bmv_dc.command_processor is None, \
            "command_processor property should be None"
        assert bmv_dc.cp is None, \
            "cp property should be None"
    except Exception as e:
        pytest.fail(f"BudgetManagerCLIViewDataContext() raised an exception: {str(e)}")

def test_BudgetManagerCLIViewDataContext__init__with_viewmodel():
    """Test BudgetManagerCLIViewDataContext() with view_model provided."""
    try:
        logger.info(test_BudgetManagerCLIViewDataContext__init__with_viewmodel.__doc__)
        # Need a ViewModel to initialize the DataContext
        bmvm = p3bmvm.BudManViewModel().initialize()
        assert isinstance(bmvm, p3bmvm.BudManViewModel), \
            "Expected BudManCommandViewModel, got: " + str(type(bmvm))
        assert bmvm.initialized, \
            "view_model should be initialized"
        # Create a BudgetManagerCLIViewDataContext instance with a ViewModel      
        bmv_dc = bm_view_dc.BudManCLIViewDataContext(bmvm)
        assert isinstance(bmv_dc, bm_view_dc.BudManCLIViewDataContext), \
            f"Expected BudgetManagerCLIViewDataContext, got: " + str(type(bmv_dc))
        assert not bmv_dc.initialized, \
            "Should not be initialized yet"
        assert bmv_dc.view_model is not None, \
            "view_model property should not be None"
        assert bmv_dc.data_context is None, \
            "data_context property should be None"
        assert bmv_dc.dc is None, \
            "dc property should be None"
        assert bmv_dc.command_processor is None, \
            "command_processor property should be None"
        assert bmv_dc.cp is None, \
            "cp property should be None"
    except Exception as e:
        pytest.fail(f"BudgetManagerCLIViewDataContext() raised an exception: {str(e)}")

def test_BudgetManagerCLIViewDataContext_initialize():
    """Test BudgetManagerCLIViewDataContext initialize() method."""
    try:
        logger.info(test_BudgetManagerCLIViewDataContext_initialize.__doc__)
        # Need a ViewModel to initialize the DataContext
        bmvm = p3bmvm.BudManViewModel().initialize()
        assert isinstance(bmvm, p3bmvm.BudManViewModel), \
            "Expected BudManCommandViewModel, got: " + str(type(bmvm))
        assert bmvm.initialized, \
            "view_model should be initialized"
        # Create a BudgetManagerCLIViewDataContext instance with a ViewModel      
        bmv_dc = bm_view_dc.BudManCLIViewDataContext(bmvm)
        assert isinstance(bmv_dc, bm_view_dc.BudManCLIViewDataContext), \
            f"Expected BudgetManagerCLIViewDataContext, got: " + str(type(bmv_dc))
        assert not bmv_dc.initialized, \
            "Should not be initialized yet"
        assert bmv_dc.view_model is not None, \
            "view_model property should not be None"
        assert bmv_dc.data_context is None, \
            "data_context property should be None"
        assert bmv_dc.dc is None, \
            "dc property should be None"
        assert bmv_dc.command_processor is None, \
            "command_processor property should be None"
        assert bmv_dc.cp is None, \
            "cp property should be None"
        # Now initialize the DataContext
        bmv_dc.initialize(cp=bmvm.BMVM_execute_cmd, dc=bmvm.data_context)
        assert bmv_dc.initialized, \
            "Should be initialized now"
        assert bmv_dc.view_model is not None, \
            "view_model property should not be None"
        assert bmv_dc.data_context is not None, \
            "data_context property should not be None"
        assert bmv_dc.dc is not None, \
            "dc property should not be None"
        assert bmv_dc.command_processor is not None, \
            "command_processor property should not be None"
        assert bmv_dc.cp is not None, \
            "cp property should not be None"
    except Exception as e:
        pytest.fail(f"BudgetManagerCLIViewDataContext() raised an exception: {str(e)}")

def test_BudgetManagerCLIViewDataContext_execute_cmd():
    """Test BudgetManagerCLIViewDataContext execute_cmd() method."""
    try:
        logger.info(test_BudgetManagerCLIViewDataContext_execute_cmd.__doc__)
        # Need a ViewModel to initialize the DataContext
        bmvm = p3bmvm.BudManViewModel().initialize()
        assert isinstance(bmvm, p3bmvm.BudManViewModel), \
            "Expected BudManCommandViewModel, got: " + str(type(bmvm))
        assert bmvm.initialized, \
            "view_model should be initialized"
        # Create a BudgetManagerCLIViewDataContext instance with a ViewModel      
        bmv_dc = bm_view_dc.BudManCLIViewDataContext(bmvm)
        assert isinstance(bmv_dc, bm_view_dc.BudManCLIViewDataContext), \
            f"Expected BudgetManagerCLIViewDataContext, got: " + str(type(bmv_dc))
        assert not bmv_dc.initialized, \
            "Should not be initialized yet"
        # Now initialize the DataContext
        bmv_dc.initialize(cp=bmvm.BMVM_execute_cmd, dc=bmvm.data_context)
        assert bmv_dc.initialized, \
            "Should be initialized now"
        assert bmv_dc.view_model is not None, \
            "view_model property should not be None"
        assert bmv_dc.data_context is not None, \
            "data_context property should not be None"
        assert bmv_dc.dc is not None, \
            "dc property should not be None"
        assert bmv_dc.command_processor is not None, \
            "command_processor property should not be None"
        assert bmv_dc.cp is not None, \
            "cp property should not be None"
        # Test the command_processor execute_cmd() method
        cmd ={"unknown_cmd": None}
        success, result = bmv_dc.execute_cmd(cmd)
        assert not success, \
            "Expected execute_cmd() to return False"
        exp_msg = "Command key 'unknown_cmd' not found in command map."
        assert result == exp_msg, \
            f"Expected execute_cmd() to return '{exp_msg}', got: {result}"
    except Exception as e:
        pytest.fail(f"BudgetManagerCLIViewDataContext() raised an exception: {str(e)}")


