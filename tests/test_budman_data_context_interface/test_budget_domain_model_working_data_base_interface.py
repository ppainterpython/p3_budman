# ---------------------------------------------------------------------------- +
# test_budget_domain_model_working_data_base_interface.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
# from config import settings
from budman_app import *
from budman_namespace import *
from budman_data_context import BudManDataContextBaseInterface
from budman_data_context import BDMWorkingData
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class TestBDMWorkingDataBaseInterface():
    """TestBDMWorkingDataBaseInterface: A test class for the BDMWorkingDataBaseInterface."""
    # def __init__(self):
    #     self.bdm_wd_base_interface = BDMWorkingDataBaseInterface()
    #     self.bdm_wd_base_interface.dc_initialize()
    # ------------------------------------------------------------------------ +
    @pytest.fixture
    def bdmwd_bi(self):
        """Fixture to set up the BDMWorkingDataBaseInterface instance."""
        try:
            logger.info(self.bdmwd_bi.__doc__)
            bdmwd_bi_value = BDMWorkingData()
            bdmwd_bi_value.dc_initialize()
        except Exception as e:
            m = f"bdmwd_bi() fixture raised an exception: {p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)
        return bdmwd_bi_value
    # ------------------------------------------------------------------------ +    
    def test_bdm_wd_base_interface__init__and_initialize(self):
        """Test the BDMWorkingDataBaseInterface class __init__() and initialize()."""
        try:
            logger.info(self.test_bdm_wd_base_interface__init__and_initialize.__doc__)
            bdmwd_bi = BDMWorkingData()
            assert not bdmwd_bi.dc_INITIALIZED, "Expected INITIALIZED to be False for new instance"
            assert bdmwd_bi.dc_FI_KEY is None, "Expected dc_FI_KEY to be None for new instance"
            assert bdmwd_bi.dc_WF_KEY is None, "Expected dc_WF_KEY to be None for new instance"
            assert bdmwd_bi.dc_WB_TYPE is None, "Expected dc_WB_TYPE to be None for new instance"
            assert bdmwd_bi.dc_WB_NAME is None, "Expected dc_WB_NAME to be None for new instance"
            assert bdmwd_bi.dc_BUDMAN_STORE is None, "Expected dc_BUDMAN_STORE to be None for new instance"
            assert bdmwd_bi.dc_WORKBOOKS is None, "Expected dc_WORKBOOKS to be None for new instance"
            assert bdmwd_bi.dc_LOADED_WORKBOOKS is None, "Expected dc_LOADED_WORKBOOKS to be None for new instance"
            bdmwd_bi.dc_initialize()
            assert bdmwd_bi.dc_INITIALIZED is True, "Expected INITIALIZED to be True after initialization"
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            pytest.fail(f"BDMWorkingDataBaseInterface() raised an exception: {str(e)}")
    # ------------------------------------------------------------------------ +
    def test_test_bdm_wd_base_interface_dc_override_methods(self):
        """Test the BDMWorkingDataBaseInterface class override methods."""
        try:
            logger.info(self.test_test_bdm_wd_base_interface_dc_override_methods.__doc__)
            try:
                bdmwd_bi = BDMWorkingData().dc_initialize()
            except Exception as e:
                m = p3u.exc_err_msg(e)
                logger.error(m)
                pytest.fail(f"BDMWorkingDataBaseInterface() raised an exception: {m}")
            assert bdmwd_bi is not None, "BudManDataContextBaseInterface() should not be None"
            assert isinstance(bdmwd_bi, BDMWorkingData), \
                "Expected BDMWorkingDataBaseInterface to be a subclass of BudManDataContextBaseInterface, got: " + str(type(bdmwd_bi))
            assert bdmwd_bi.dc_INITIALIZED is True, "Expected INITIALIZED to be True after instantiation"
            bdmwd_bi.dc_FI_KEY = "test_fi_key"
            assert bdmwd_bi.dc_FI_KEY == "test_fi_key", \
                f"Expected bdmwd_bi.dc_FI_KEY to be equal to 'test_fi_key' not {bdmwd_bi.dc_FI_KEY}"
            assert bdmwd_bi.dc_FI_KEY_validate("test_fi_key"), \
                "Expected dc_FI_KEY_validate to return True for valid FI_KEY('test_fi_key')"
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            pytest.fail(f"Something raised an exception: {m}")
    # ------------------------------------------------------------------------ +
    def test_bdm_wd_base_interface_dc_interface_properties(self,bdmwd_bi):
        """Test BDMWorkingDataBaseInterface class coverage of BudManDataContextClientInterface class properties."""
        try:
            logger.info(self.test_bdm_wd_base_interface_dc_interface_properties.__doc__)
            assert bdmwd_bi is not None, "BDMWorkingDataBaseInterface should not be None"
            assert isinstance(bdmwd_bi, BDMWorkingData), "Expected bdmwd_bi to be a BDMWorkingDataBaseInterface instance, got: " + str(type(bdmwd_bi))
            # assert bdmwd_bi.data_context is not None, "bdmwd_bi.data_context should not be None"
            # assert isinstance(bdmwd_bi.data_context, BDMWorkingDataBaseInterface), "Expected bdmwd_bi.data_context to be a BDMWorkingDataBaseInterface instance, got: " + str(type(bdmwd_bi.data_context))
            # assert bdmwd_bi.data_context.dc_INITIALIZED is True, "Expected bdmwd_bi.data_context.INITIALIZED to be True after instantiation"
            bdmwd_bi.dc_FI_KEY = "test_fi_key"
            assert bdmwd_bi.dc_FI_KEY == "test_fi_key", "Expected bdmwd_bi.dc_FI_KEY to be 'test_fi_key', got: " + str(bdmwd_bi.dc_FI_KEY)
            bdmwd_bi.dc_WF_KEY = "test_wf_key"
            assert bdmwd_bi.dc_WF_KEY == "test_wf_key", "Expected bdmwd_bi.dc_WF_KEY to be 'test_wf_key', got: " + str(bdmwd_bi.dc_WF_KEY)
            bdmwd_bi.dc_WB_TYPE = "test_wb_type"
            assert bdmwd_bi.dc_WB_TYPE == "test_wb_type", "Expected bdmwd_bi.dc_WB_TYPE to be 'test_wb_type', got: " + str(bdmwd_bi.dc_WB_TYPE)
            bdmwd_bi.dc_WB_NAME = "test_wb_name"
            assert bdmwd_bi.dc_WB_NAME == "test_wb_name", "Expected bdmwd_bi.dc_WB_NAME to be 'test_wb_name', got: " + str(bdmwd_bi.dc_WB_NAME)
            bdmwd_bi.dc_BUDMAN_STORE = "test_budman_store"
            assert bdmwd_bi.dc_BUDMAN_STORE == "test_budman_store", "Expected bdmwd_bi.dc_BUDMAN_STORE to be 'test_budman_store', got: " + str(bdmwd_bi.dc_BUDMAN_STORE)
            bdmwd_bi.dc_WORKBOOKS = []
            assert bdmwd_bi.dc_WORKBOOKS == [], "Expected bdmwd_bi.dc_WORKBOOKS to be an empty list, got: " + str(bdmwd_bi.dc_WORKBOOKS)
            bdmwd_bi.dc_LOADED_WORKBOOKS = []
            assert bdmwd_bi.dc_LOADED_WORKBOOKS == [], "Expected bdmwd_bi.dc_LOADED_WORKBOOKS to be an empty list, got: " + str(bdmwd_bi.dc_LOADED_WORKBOOKS)
            assert bdmwd_bi.dc_FI_KEY_validate("test_fi_key") is True, "Expected dc_FI_KEY_validate to return True for valid FI_KEY('test_fi_key')"
            assert bdmwd_bi.dc_FI_KEY_validate("") is False, "Expected dc_FI_KEY_validate to return False for empty FI_KEY"
            assert bdmwd_bi.dc_WF_KEY_validate("test_wf_key") is True, "Expected dc_WF_KEY_validate to return True for valid WF_KEY('test_wf_key')"
            assert bdmwd_bi.dc_WF_KEY_validate("") is False, "Expected dc_WF_KEY_validate to return False for empty WF_KEY"
            assert bdmwd_bi.dc_WB_TYPE_validate("test_wb_type") is True, "Expected dc_WB_TYPE_validate to return True for valid WB_TYPE('test_wb_type')"
            assert bdmwd_bi.dc_WB_TYPE_validate("") is False, "Expected dc_WB_TYPE_validate to return False for empty WB_TYPE"
            assert bdmwd_bi.dc_WB_NAME_validate("test_wb_name") is True, "Expected dc_WB_NAME_validate to return True for valid WB_NAME('test_wb_name')"
            assert bdmwd_bi.dc_WB_NAME_validate("") is False, "Expected dc_WB_NAME_validate to return False for empty WB_NAME"
            assert bdmwd_bi.dc_WB_REF_validate("test_wb_ref") is True, "Expected dc_WB_REF_validate to return True for valid WB_REF('test_wb_ref')"
            assert bdmwd_bi.dc_WB_REF_validate("") is False, "Expected dc_WB_REF_validate to return False for empty WB_REF"
            wb = bdmwd_bi.dc_WORKBOOK_load("test_workbook.xlsx")
            assert wb is not None, "dc_WORKBOOK_load should return a Workbook instance"
            assert isinstance(wb, Workbook), "Expected dc_WORKBOOK_load to return a Workbook instance, got: " + str(type(wb))
            assert bdmwd_bi.dc_WORKBOOK_loaded("test_workbook.xlsx") is True, "Expected dc_WORKBOOK_loaded to return True for loaded workbook"
            assert bdmwd_bi.dc_WORKBOOK_loaded("non_existent_workbook.xlsx") is False, "Expected dc_WORKBOOK_loaded to return False for non-existent workbook"
            # Test saving the workbook
            bdmwd_bi.dc_WORKBOOK_save("test_workbook.xlsx", wb)
            assert os.path.exists("test_workbook.xlsx"), "Expected test_workbook.xlsx to exist after saving"
            # Test removing the workbook
            bdmwd_bi.dc_WORKBOOK_remove("test_workbook.xlsx")
            assert not os.path.exists("test_workbook.xlsx"), "Expected test_workbook.xlsx to be removed after dc_WORKBOOK_remove"
            # Test adding a new workbook
            new_wb = Workbook()
            bdmwd_bi.dc_WORKBOOK_add("new_workbook.xlsx", new_wb)
            assert bdmwd_bi.dc_WORKBOOK_loaded("new_workbook.xlsx") is True, "Expected dc_WORKBOOK_loaded to return True for newly added workbook"
            assert os.path.exists("new_workbook.xlsx") is False, "Expected new_workbook.xlsx to not exist after dc_WORKBOOK_add"
            # Clean up the created workbook files
            if os.path.exists("test_workbook.xlsx"):
                os.remove("test_workbook.xlsx")
            if os.path.exists("new_workbook.xlsx"):
                os.remove("new_workbook.xlsx")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            pytest.fail(f"Exception: {m}")
    # ------------------------------------------------------------------------ +
    def test_budman_data_context_client_interface_methods(self):
        """Test the BudManDataContextClientInterface class Methods."""
        try:
            logger.info(self.test_budman_data_context_client_interface_methods.__doc__)
            # try:
            #     # Try to instantiate the abstract base class, should raise TypeError.
            #     bdmdc = BudManDataContextBaseInterface().dc_initialize()
            #     bdmwd_bi = BudManDataContextClientInterface(bdmdc).dc_initialize()
            # except Exception as e:
            #     m = p3u.exc_err_msg(e)
            #     logger.error(m)
            #     pytest.fail(f"Constructing raised an exception: {m}")
            # assert bdmwd_bi is not None, "BudManDataContextClientInterface should not be None"
            # assert isinstance(bdmwd_bi, BudManDataContextClientInterface), \
            #     "Expected bdmwd_bi to be a BudManDataContextClientInterface instance, got: " + str(type(bdmwd_bi))
            # assert bdmwd_bi.data_context is not None, "bdmwd_bi.data_context should not be None"
            # assert isinstance(bdmwd_bi.data_context, BDMWorkingDataBaseInterface), \
            #     "Expected bdmwd_bi.data_context to be a BDMWorkingDataBaseInterface instance, got: " + str(type(bdmwd_bi.data_context))
            # assert bdmwd_bi.data_context.dc_INITIALIZED is True, \
            #     "Expected bdmwd_bi.data_context.INITIALIZED to be True after instantiation"
            # assert bdmwd_bi.dc_FI_KEY_validate("test_fi_key") is True, \
            #     "Expected dc_FI_KEY_validate to return True for valid FI_KEY"
            # assert bdmwd_bi.dc_FI_KEY_validate("") is False, \
            #     "Expected dc_FI_KEY_validate to return False for empty FI_KEY"
            # assert bdmwd_bi.dc_WF_KEY_validate("test_wf_key") is True, \
            #     "Expected dc_WF_KEY_validate to return True for valid WF_KEY"
            # assert bdmwd_bi.dc_WF_KEY_validate("") is False, \
            #     "Expected dc_WF_KEY_validate to return False for empty WF_KEY"
            # assert bdmwd_bi.dc_WB_TYPE_validate("test_wb_type") is True, \
            #     "Expected dc_WB_TYPE_validate to return True for valid WB_TYPE"
            # assert bdmwd_bi.dc_WB_TYPE_validate("") is False, \
            #     "Expected dc_WB_TYPE_validate to return False for empty WB_TYPE"
            # assert bdmwd_bi.dc_WB_NAME_validate("test_wb_name") is True, \
            #     "Expected dc_WB_NAME_validate to return True for valid WB_NAME"
            # assert bdmwd_bi.dc_WB_NAME_validate("") is False, \
            #     "Expected dc_WB_NAME_validate to return False for empty WB_NAME"
            # assert bdmwd_bi.dc_WB_REF_validate("test_wb_ref") is True, \
            #     "Expected dc_WB_REF_validate to return True for valid WB_REF"
            # assert bdmwd_bi.dc_WB_REF_validate("") is False, \
            #     "Expected dc_WB_REF_validate to return False for empty WB_REF"
            # wb = bdmwd_bi.dc_WORKBOOK_load("test_workbook.xlsx")
            # assert wb is not None, "WORKBOOK_load should return a Workbook instance"
            # assert isinstance(wb, Workbook), \
            #     "Expected WORKBOOK_load to return a Workbook instance, got: " + str(type(wb))
            # assert bdmwd_bi.dc_WORKBOOK_loaded("test_workbook.xlsx"), \
            #     "Expected WORKBOOK_loaded to return True for loaded workbook"
            
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            pytest.fail(f"Something raised an exception: {m}")


