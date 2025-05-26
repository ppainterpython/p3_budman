# ---------------------------------------------------------------------------- +
# test_budman_data_context_client_interface.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from abc import ABC, abstractmethod
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budget_manager_domain_model import design_language_namespace as bdmns
from budman_data_context_interface import BudManDataContextBaseInterface
from budman_data_context_interface import BudManDataContextClientInterface
from budman_data_context_interface import BudManDataContextInterface

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(bdmns.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budman_data_context_interface_initialize():
    """Test the BudManDataContextInterface class __init__() and initialize()."""
    try:
        logger.info(test_budman_data_context_interface_initialize.__doc__)
        # Try to instantiate the abstract base class, should raise TypeError.
        bdmdc = BudManDataContextInterface()
        assert not bdmdc.INITIALIZED, "Expected INITIALIZED to be False for new instance"
        assert bdmdc.dc_FI_KEY is None, "Expected dc_FI_KEY to be None for new instance"
        assert bdmdc.dc_WF_KEY is None, "Expected dc_WF_KEY to be None for new instance"
        assert bdmdc.dc_WB_TYPE is None, "Expected dc_WB_TYPE to be None for new instance"
        assert bdmdc.dc_WB_NAME is None, "Expected dc_WB_NAME to be None for new instance"
        assert bdmdc.dc_BUDMAN_STORE is None, "Expected dc_BUDMAN_STORE to be None for new instance"
        assert bdmdc.dc_WORKBOOKS is None, "Expected dc_WORKBOOKS to be None for new instance"
        assert bdmdc.dc_LOADED_WORKBOOKS is None, "Expected dc_LOADED_WORKBOOKS to be None for new instance"
        bdmdc.initialize()
        assert bdmdc.INITIALIZED is True, "Expected INITIALIZED to be True after initialization"
    except Exception as e:
        pytest.fail(f"BudManDataContextBaseInterface() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_budman_data_context_client_interface_initialize():
    """Test the BudManDataContextClientInterface class __init__() and initialize()."""
    try:
        logger.info(test_budman_data_context_client_interface_initialize.__doc__)
        try:
            # Try to instantiate the abstract base class, should raise TypeError.
            bdmdc = BudManDataContextInterface().initialize()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            pytest.fail(f"BudManDataContextInterface() raised an exception: {str(e)}")
        assert bdmdc is not None, "BudManDataContextInterface() should not be None"
        assert isinstance(bdmdc, BudManDataContextBaseInterface), \
            "Expected BudManDataContextInterface to be a subclass of BudManDataContextInterface, got: " + str(type(bdmdc))
        assert bdmdc.INITIALIZED is True, "Expected INITIALIZED to be True after instantiation"
        try:
            dc_client = BudManDataContextClientInterface(bdmdc).initialize()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            pytest.fail(f"BudManDataContextClientInterface() raised TypeError: {str(e)}")
        assert dc_client is not None, "BudManDataContextClientInterface should not be None"
        assert isinstance(dc_client, BudManDataContextClientInterface), \
            "Expected dc_client to be a BudManDataContextClientInterface instance, got: " + str(type(dc_client))
        assert dc_client.data_context is not None, "dc_client.data_context should not be None"
        assert isinstance(dc_client.data_context, BudManDataContextBaseInterface), \
            "Expected dc_client.data_context to be a BudManDataContextBaseInterface instance, got: " + str(type(dc_client.data_context))
        assert dc_client.data_context.INITIALIZED is True, \
            "Expected dc_client.data_context.INITIALIZED to be True after instantiation"
    except Exception as e:
        pytest.fail(f"Something raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_budman_data_context_client_interface_properties():
    """Test the BudManDataContextClientInterface class properties."""
    try:
        logger.info(test_budman_data_context_client_interface_properties.__doc__)
        try:
            # Try to instantiate the abstract base class, should raise TypeError.
            bdmdc = BudManDataContextInterface().initialize()
            dc_client = BudManDataContextClientInterface(bdmdc).initialize()
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            pytest.fail(f"Constructing raised an exception: {m}")
        assert dc_client is not None, "BudManDataContextClientInterface should not be None"
        assert isinstance(dc_client, BudManDataContextClientInterface), \
            "Expected dc_client to be a BudManDataContextClientInterface instance, got: " + str(type(dc_client))
        assert dc_client.data_context is not None, "dc_client.data_context should not be None"
        assert isinstance(dc_client.data_context, BudManDataContextBaseInterface), \
            "Expected dc_client.data_context to be a BudManDataContextBaseInterface instance, got: " + str(type(dc_client.data_context))
        assert dc_client.data_context.INITIALIZED is True, \
            "Expected dc_client.data_context.INITIALIZED to be True after instantiation"
        dc_client.dc_FI_KEY = "test_fi_key"
        assert dc_client.dc_FI_KEY == "test_fi_key", \
            "Expected dc_client.dc_FI_KEY to be 'test_fi_key', got: " + str(dc_client.dc_FI_KEY)
        assert dc_client.DC.dc_FI_KEY == "test_fi_key", \
            "Expected dc_client.DC.dc_FI_KEY to be 'test_fi_key', got: " + str(dc_client.DC.dc_FI_KEY)
        assert dc_client.dc_FI_KEY == dc_client.DC.dc_FI_KEY, \
            "Expected dc_client.dc_FI_KEY to be equal to dc_client.DC.dc_FI_KEY"
        dc_client.dc_WF_KEY = "test_wf_key"
        assert dc_client.dc_WF_KEY == "test_wf_key", \
            "Expected dc_client.dc_WF_KEY to be 'test_wf_key', got: " + str(dc_client.dc_WF_KEY)
        assert dc_client.DC.dc_WF_KEY == "test_wf_key", \
            "Expected dc_client.DC.dc_WF_KEY to be 'test_wf_key', got: " + str(dc_client.DC.dc_WF_KEY)
        assert dc_client.dc_WF_KEY == dc_client.DC.dc_WF_KEY, \
            "Expected dc_client.dc_WF_KEY to be equal to dc_client.DC.dc_WF_KEY"
        dc_client.dc_WB_TYPE = "test_wb_type"
        assert dc_client.dc_WB_TYPE == "test_wb_type", \
            "Expected dc_client.dc_WB_TYPE to be 'test_wb_type', got: " + str(dc_client.dc_WB_TYPE)
        assert dc_client.DC.dc_WB_TYPE == "test_wb_type", \
            "Expected dc_client.DC.dc_WB_TYPE to be 'test_wb_type', got: " + str(dc_client.DC.dc_WB_TYPE)
        assert dc_client.dc_WB_TYPE == dc_client.DC.dc_WB_TYPE, \
            "Expected dc_client.dc_WB_TYPE to be equal to dc_client.DC.dc_WB_TYPE"
        dc_client.dc_WB_NAME = "test_wb_name"
        assert dc_client.dc_WB_NAME == "test_wb_name", \
            "Expected dc_client.dc_WB_NAME to be 'test_wb_name', got: " + str(dc_client.dc_WB_NAME)
        assert dc_client.DC.dc_WB_NAME == "test_wb_name", \
            "Expected dc_client.DC.dc_WB_NAME to be 'test_wb_name', got: " + str(dc_client.DC.dc_WB_NAME)
        assert dc_client.dc_WB_NAME == dc_client.DC.dc_WB_NAME, \
            "Expected dc_client.dc_WB_NAME to be equal to dc_client.DC.dc_WB_NAME"
        dc_client.dc_BUDMAN_STORE = "test_budman_store"
        assert dc_client.dc_BUDMAN_STORE == "test_budman_store", \
            "Expected dc_client.dc_BUDMAN_STORE to be 'test_budman_store', got: " + str(dc_client.dc_BUDMAN_STORE)
        assert dc_client.DC.dc_BUDMAN_STORE == "test_budman_store", \
            f"Expected dc_client.DC.dc_BUDMAN_STORE to be 'test_budman_store', got: {str(dc_client.DC.dc_BUDMAN_STORE)}"
        assert dc_client.dc_BUDMAN_STORE == dc_client.DC.dc_BUDMAN_STORE, \
            "Expected dc_client.dc_BUDMAN_STORE to be equal to dc_client.DC.dc_BUDMAN_STORE"
        dc_client.dc_WORKBOOKS = []
        assert dc_client.dc_WORKBOOKS == [], \
            "Expected dc_client.dc_WORKBOOKS to be an empty list, got: " + str(dc_client.dc_WORKBOOKS)
        assert dc_client.DC.dc_WORKBOOKS == [], \
            "Expected dc_client.DC.dc_WORKBOOKS to be an empty list, got: " + str(dc_client.DC.dc_WORKBOOKS)
        assert dc_client.dc_WORKBOOKS == dc_client.DC.dc_WORKBOOKS, \
            "Expected dc_client.dc_WORKBOOKS to be equal to dc_client.DC.dc_WORKBOOKS"
        dc_client.dc_LOADED_WORKBOOKS = []
        assert dc_client.dc_LOADED_WORKBOOKS == [], \
            "Expected dc_client.dc_LOADED_WORKBOOKS to be an empty list, got: " + str(dc_client.dc_LOADED_WORKBOOKS)
        assert dc_client.DC.dc_LOADED_WORKBOOKS == [], \
            "Expected dc_client.DC.dc_LOADED_WORKBOOKS to be an empty list, got: " + str(dc_client.DC.dc_LOADED_WORKBOOKS)
        assert dc_client.dc_LOADED_WORKBOOKS == dc_client.DC.dc_LOADED_WORKBOOKS, \
            "Expected dc_client.dc_LOADED_WORKBOOKS to be equal to dc_client.DC.dc_LOADED_WORKBOOKS"
        
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        pytest.fail(f"Something raised an exception: {m}")
# ---------------------------------------------------------------------------- +
def test_budman_data_context_client_interface_methods():
    """Test the BudManDataContextClientInterface class Methods."""
    try:
        logger.info(test_budman_data_context_client_interface_methods.__doc__)
        try:
            # Try to instantiate the abstract base class, should raise TypeError.
            bdmdc = BudManDataContextInterface().initialize()
            dc_client = BudManDataContextClientInterface(bdmdc).initialize()
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            pytest.fail(f"Constructing raised an exception: {m}")
        assert dc_client is not None, "BudManDataContextClientInterface should not be None"
        assert isinstance(dc_client, BudManDataContextClientInterface), \
            "Expected dc_client to be a BudManDataContextClientInterface instance, got: " + str(type(dc_client))
        assert dc_client.data_context is not None, "dc_client.data_context should not be None"
        assert isinstance(dc_client.data_context, BudManDataContextBaseInterface), \
            "Expected dc_client.data_context to be a BudManDataContextBaseInterface instance, got: " + str(type(dc_client.data_context))
        assert dc_client.data_context.INITIALIZED is True, \
            "Expected dc_client.data_context.INITIALIZED to be True after instantiation"
        assert dc_client.dc_FI_KEY_validate("test_fi_key") is True, \
            "Expected dc_FI_KEY_validate to return True for valid FI_KEY"
        assert dc_client.dc_FI_KEY_validate("") is False, \
            "Expected dc_FI_KEY_validate to return False for empty FI_KEY"
        assert dc_client.dc_WF_KEY_validate("test_wf_key") is True, \
            "Expected dc_WF_KEY_validate to return True for valid WF_KEY"
        assert dc_client.dc_WF_KEY_validate("") is False, \
            "Expected dc_WF_KEY_validate to return False for empty WF_KEY"
        assert dc_client.dc_WB_TYPE_validate("test_wb_type") is True, \
            "Expected dc_WB_TYPE_validate to return True for valid WB_TYPE"
        assert dc_client.dc_WB_TYPE_validate("") is False, \
            "Expected dc_WB_TYPE_validate to return False for empty WB_TYPE"
        assert dc_client.dc_WB_NAME_validate("test_wb_name") is True, \
            "Expected dc_WB_NAME_validate to return True for valid WB_NAME"
        assert dc_client.dc_WB_NAME_validate("") is False, \
            "Expected dc_WB_NAME_validate to return False for empty WB_NAME"
        assert dc_client.dc_WB_REF_validate("test_wb_ref") is True, \
            "Expected dc_WB_REF_validate to return True for valid WB_REF"
        assert dc_client.dc_WB_REF_validate("") is False, \
            "Expected dc_WB_REF_validate to return False for empty WB_REF"
        wb = dc_client.WORKBOOK_load("test_workbook.xlsx")
        assert wb is not None, "WORKBOOK_load should return a Workbook instance"
        assert isinstance(wb, Workbook), \
            "Expected WORKBOOK_load to return a Workbook instance, got: " + str(type(wb))
        assert dc_client.WORKBOOK_loaded("test_workbook.xlsx"), \
            "Expected WORKBOOK_loaded to return True for loaded workbook"
        
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        pytest.fail(f"Something raised an exception: {m}")


