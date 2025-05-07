# ---------------------------------------------------------------------------- +
# test_budget_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
import data.p3_budget_model as p3bm
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(p3bm.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_model_constructor() -> None:
    """Test BudgetModel() constructor."""
    try:
        logger.info(test_budget_model_constructor.__doc__)
        bm = p3bm.BudgetModel()
        
        # With the bare BudgetModel.__init__(), this instance should be empty.
        #
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"        
        assert not bm.bm_initialized, "Budget model should NOT be initialized"
        assert bm.bm_folder is None, "Budget folder should be None"
        assert bm.bm_store_uri is None, \
            "Budget model store URI should not be None"
        assert (bm.bm_fi_collection is not None and 
                isinstance(bm.bm_fi_collection, dict) and 
                len(bm.bm_fi_collection) == 0), \
            "Financial institutions should empty dictionary"    
        assert (bm.bm_wf_collection is not None and 
                isinstance(bm.bm_wf_collection, dict) and 
                len(bm.bm_wf_collection) == 0), \
            "WF_WORKFLOW_COLLECTION should empty dictionary"
        assert bm.bm_options is not None, "Options should not be None"
        assert bm.bm_created_date is not None, "Created date should not be None"
        assert bm.bm_last_modified_date is not None, \
            "Last modified date should not be None"
        assert bm.bm_last_modified_by is not None, \
            "Last modified by should not be None"
        assert bm.bm_working_data is not None, "Workflows should not be None"
        assert (bm.bm_working_data is not None and 
                isinstance(bm.bm_working_data, dict) and 
                len(bm.bm_working_data) == 0), \
            "WF_WORKING_DATA should empty dictionary"
    except Exception as e:
        pytest.fail(f"BudgetModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_budget_model_initialize_no_template() -> None:
    """Test BudgetModel() constructor with no template."""
    try:
        logger.info(test_budget_model_initialize_no_template.__doc__)
        bm = p3bm.BudgetModel()
        # Initialize the budget model with no template, force internal
        # creation of the BudgetModelTemplate.
        bm.bdm_initialize()
        
        # This instance should be empty.
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"        
        assert bm._initialized, "Budget model should be initialized"
        assert bm._created_date is not None, "Created date should not be None"
        assert bm._last_modified_date is not None, \
            "Last modified date should not be None"
        assert bm._last_modified_by is not None, \
            "Last modified by should not be None"
        assert bm._options is not None, "Options should not be None"
        assert bm._budget_folder is not None, "Budget folder should not be None"
        assert bm._budget_model_store_uri is not None, \
            "Budget model store URI should not be None"
        assert (bm._financial_institutions is not None and 
                isinstance(bm._financial_institutions, dict) and 
                len(bm._financial_institutions) > 0), \
            "Financial institutions should non-empty dictionary"    
    except Exception as e:
        pytest.fail(f"BudgetModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_budget_model_initialize_with_template() -> None:
    """Test BudgetModel() constructor with with template."""
    try:
        logger.info(test_budget_model_initialize_with_template.__doc__)
        bmt = p3bm.BudgetModelTemplate()
        bm = p3bm.BudgetModel()
        # Initialize the budget model with a template
        bm.bdm_initialize(bmt)
        
        # This instance should be empty.
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"        
        assert bm._initialized, "Budget model should be initialized"
        assert bm._created_date is not None, "Created date should not be None"
        assert bm._last_modified_date is not None, \
            "Last modified date should not be None"
        assert bm._last_modified_by is not None, \
            "Last modified by should not be None"
        assert bm._options is not None, "Options should not be None"
        assert bm._budget_folder is not None, "Budget folder should not be None"
        assert bm._budget_model_store_uri is not None, \
            "Budget model store URI should not be None"
        assert (bm._financial_institutions is not None and 
                isinstance(bm._financial_institutions, dict) and 
                len(bm._financial_institutions) > 0), \
            "Financial institutions should non-empty dictionary"    
    except Exception as e:
        pytest.fail(f"BudgetModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_FI_OBJECT_pseudo_Property_Methods():
    """Test BDM FI Object Pseudo Property Methods."""
    try:
        logger.info(test_BDM_FI_OBJECT_pseudo_Property_Methods.__doc__)
        bm = p3bm.BudgetModel()
        bm.bdm_initialize(bsm_init=True)
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
        # Test expected valuees based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bm.VALID_FI_KEYS:
            assert bm.bdm_validate_FI_KEY(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert (bdm_fi := bm.bdm_FI_OBJECT(fi_key)) is not None, \
                f"Expected: {fi_key} to be a valid FI dict."
            assert len(bdm_fi) == len(p3bm.FI_OBJECT_VALID_KEYS), \
                f"Expected: {fi_key} workbooks_in to be non-None."
            assert isinstance(bdm_fi, p3bm.FI_OBJECT), \
                f"Expected: {fi_key} workbooks_in to be valid FI_OBJECT."
            assert bm.bdm_FI_KEY(fi_key) == fi_key, \
                f"Expected bdm_FI_KEY('{fi_key}'): '{fi_key}', got '{bdm_fi.bdm_FI_OBJECT_key(fi_key)}'."
            assert bm.bdm_FI_NAME(fi_key) in p3bm.BDM_FI_NAMES, \
                f"Expected one of: {p3bm.BDM_FI_NAMES}, got '{bm.bdm_FI_OBJECT_name(fi_key)}'"
            assert bm.bdm_FI_TYPE(fi_key) in p3bm.VALID_FI_TYPES, \
                f"Expected one of: {p3bm.BDM_FI_TYPES}, got '{bm.bdm_FI_OBJECT_type(fi_key)}'"
            assert (fldr := bm.bdm_FI_FOLDER(fi_key)) is not None , \
                f"Expected bm.bdm_FI_FOLDER({fi_key}) to be non-None"
            assert isinstance(bm.bdm_FI_WORKFLOW_DATA(fi_key), 
                              (p3bm.WF_DATA_COLLECTION, type(None))), \
                f"bdm_FI_WORKFLOW_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bm.bdm_FI_WORKFLOW_DATA_count(fi_key), int), \
                f"Expected bm.bdm_FI_WORKFLOW_DATA_count({fi_key}) to be > 0"
            assert bm.bdm_FI_WORKFLOW_DATA_count(fi_key) >= 0, \
                f"Expected bm.bdm_FI_WORKFLOW_DATA_count({fi_key}) to be > 0"
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_FI_WF_DATA_OBJECT_pseudo_Property_Methods():
    """Test BDM_FI_WF_DATA_OBJECT() Pseudo Property Method."""
    try:
        logger.info(test_BDM_FI_WF_DATA_OBJECT_pseudo_Property_Methods.__doc__)
        bm = p3bm.BudgetModel()
        bm.bdm_initialize(bsm_init=True)
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
        # Test expected valuees based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bm.VALID_FI_KEYS:
            assert isinstance(bm.bdm_FI_WORKFLOW_DATA(fi_key), 
                              (p3bm.WF_DATA_COLLECTION, type(None))), \
                f"bdm_FI_WORKFLOW_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bm.bdm_FI_WORKFLOW_DATA_count(fi_key), int), \
                f"Expected bm.bdm_FI_WORKFLOW_DATA_count({fi_key}) to be > 0"
            assert bm.bdm_FI_WORKFLOW_DATA_count(fi_key) >= 0, \
                f"Expected bm.bdm_FI_WORKFLOW_DATA_count({fi_key}) to be > 0"
            if bm.bdm_FI_WORKFLOW_DATA_count(fi_key) == 0:
                return
            # Test access to FI WF_DATA_OBJECTs.
            for wf_key in p3bm.BM_VALID_WORKFLOWS:
                wf_do = bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key)
                assert isinstance(wf_do := bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key),(p3bm.WF_DATA_OBJECT,type(None))), \
                    f"bdm_FI_WORKFLOW_DATA({fi_key}, {wf_key}) should None or WF_DATA_OBJECT"
                if wf_do is not None:
                    l = len(wf_do)
                    assert isinstance(wf_do, p3bm.WF_OBJECT), \
                        f"Expected bm.bdm_FI_WORKFLOW_DATA({fi_key}, {wf_key}) to be a WF_OBJECT"
                    for wf_do_key in wf_do.keys():
                        assert wf_do_key in p3bm.WF_DATA_OBJECT_VALID_KEYS, \
                            f"Expected: {wf_do_key} to be a valid WF_OBJECT key."
                        if wf_do_key == p3bm.WF_WORKBOOKS_IN:
                            assert bm.bdm_WF_WORKBOOK_MAP(wf_key,wf_do_key) == p3bm.WF_FOLDER_IN, \
                                f"Expected: key: '{wf_do_key}' to be '{p3bm.WF_FOLDER_IN}'."
                        elif wf_do_key == p3bm.WF_WORKBOOKS_OUT:
                            assert bm.bdm_WF_WORKBOOK_MAP(wf_key,wf_do_key) == p3bm.WF_FOLDER_OUT, \
                                f"Expected: key: '{wf_do_key}' to be '{p3bm.WF_FOLDER_OUT}'."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bdm_FI_WF_WORKBOOK_LIST():
    """Test test_bdm_FI_WF_WORKBOOK_LIST() Pseudo Property Method."""
    try:
        logger.info(test_bdm_FI_WF_WORKBOOK_LIST.__doc__)
        bm = p3bm.BudgetModel().bdm_initialize()
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"

        for fi_key in p3bm.VALID_FI_KEYS:
            assert isinstance(bm.bdm_FI_WORKFLOW_DATA(fi_key), 
                              (p3bm.WF_DATA_COLLECTION, type(None))), \
                f"bdm_FI_WORKFLOW_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bm.bdm_FI_WORKFLOW_DATA_count(fi_key), int), \
                f"Expected bm.bdm_FI_WORKFLOW_DATA_count({fi_key}) to be > 0"
            assert bm.bdm_FI_WORKFLOW_DATA_count(fi_key) >= 0, \
                f"Expected bm.bdm_FI_WORKFLOW_DATA_count({fi_key}) to be > 0"
            if bm.bdm_FI_WORKFLOW_DATA_count(fi_key) == 0:
                return
            # Test access to FI WF_DATA_OBJECTs.
            for wf_key in p3bm.BM_VALID_WORKFLOWS:
                wf_do = bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key)
                assert isinstance(wf_do := bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key),(p3bm.WF_DATA_OBJECT,type(None))), \
                    f"bdm_FI_WORKFLOW_DATA({fi_key}, {wf_key}) should None or WF_DATA_OBJECT"
                if wf_do is not None:
                    assert len(wf_do) != 0, \
                        f"Expected: WF_DATA_OBJECT({fi_key},{wf_key}) to be non-zero length."
                    assert isinstance(wf_do, p3bm.WF_OBJECT), \
                        f"Expected bm.bdm_FI_WORKFLOW_DATA({fi_key}, {wf_key}) to be a WF_OBJECT"
                    for wf_do_key in wf_do.keys():
                        wbl = bm.bdm_FI_WF_WORKBOOK_LIST(fi_key, wf_key, wf_do_key)
                        if wbl is not None:
                            assert isinstance(wbl, p3bm.WORKBOOK_LIST), \
                                f"Expected: {wf_do_key} to be a valid WORKBOOK_LIST object."
                            assert bm.bdm_FI_WF_WORKBOOK_LIST_count(fi_key, wf_key, wf_do_key) >= 0, \
                                f"Expected: count of WORKBOOK_LIST >= 0."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_log_BDM_info():
    """Test log_BDM_info() function."""
    try:
        logger.info(test_log_BDM_info.__doc__)
        bm = p3bm.BudgetModel().bdm_initialize(bsm_init=True)
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
        assert p3bm.log_BDM_info(bm) is None, \
            "log_BDM_info() should return None"
    except Exception as e:
        pytest.fail(f"log_BDM_info() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_log_BSM_info():
    """Test log_BSM_info() function."""
    try:
        logger.info(test_log_BSM_info.__doc__)
        bm = p3bm.BudgetModel().bdm_initialize(bsm_init=True)
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
        assert p3bm.log_BSM_info(bm) is None, \
            "log_BSM_info() should return None"
    except Exception as e:
        pytest.fail(f"log_BSM_info() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
