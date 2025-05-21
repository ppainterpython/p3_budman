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
import budman_model as p3bm
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(p3bm.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_model_construction_with_no_config_object() -> None:
    """Test BudgetModel() construction with no config_object."""
    try:
        logger.info(test_budget_model_construction_with_no_config_object.__doc__)
        # Expecting an empty core BudgetModel instance.
        bm = p3bm.BudgetModel()
        
        # With no config_object provided to BudgetModel.__init__(), 
        # this instance should be mostly empty.
        assert isinstance(bm, p3bm.BudgetModel), \
            "BudgetModel() should return a BudgetModel instance"        
        assert not bm.bm_initialized, "BudgetModel inst should NOT be initialized"
        assert bm.bdm_id is not None, "bdm_id should be set, not be None"
        assert bm.bm_folder is None, "bm_folder should be None"
        assert bm.bdm_url is not None, "bdm_url should not be None"
        assert (bm.bdm_fi_collection is not None and 
                isinstance(bm.bdm_fi_collection, dict) and 
                len(bm.bdm_fi_collection) == 0), \
            "bdm_fi_collection should be empty dictionary"    
        assert (bm.bdm_wf_collection is not None and 
                isinstance(bm.bdm_wf_collection, dict) and 
                len(bm.bdm_wf_collection) == 0), \
            "bdm_wf_collection should be empty dictionary"
        assert bm.bm_options is not None, "bm_options should not be None"
        assert bm.bm_created_date is not None, "bm_created_date should be set"
        assert bm.bm_last_modified_date is not None, \
            "bm_last_modified_date should be set"
        assert bm.bm_last_modified_by is not None, \
            "bm_last_modified_by should be set"
        assert (bm.bdm_working_data is not None and 
                isinstance(bm.bdm_working_data, dict) and 
                len(bm.bdm_working_data) == 0), \
            "bdm_working_data should empty dictionary"
        logger.info(f"Complete:")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        pytest.fail(f"BudgetModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_budget_model_construction_with_BMT_as_config_object() -> None:
    """Test BudgetModel() construction with BMT as config_object."""
    try:
        logger.info(test_budget_model_construction_with_BMT_as_config_object.__doc__)
        # Expecting an empty core BudgetModel instance.
        bm = p3bm.BudgetModel(p3bm.BudgetModelTemplate.get_budget_model_template())
        
        # With no config_object provided to BudgetModel.__init__(), 
        # this instance should be mostly empty.
        assert isinstance(bm, p3bm.BudgetModel), \
            "BudgetModel() should return a BudgetModel instance"        
        assert not bm.bm_initialized, "BudgetModel inst should NOT be initialized"
        assert bm.bdm_id is not None, "bdm_id should be set, not be None"
        assert bm.bm_folder is None, "bm_folder should be None"
        assert bm.bdm_url is not None, "bdm_url should not be None"
        assert (bm.bdm_fi_collection is not None and 
                isinstance(bm.bdm_fi_collection, dict) and 
                len(bm.bdm_fi_collection) == 0), \
            "bdm_fi_collection should be empty dictionary"    
        assert (bm.bdm_wf_collection is not None and 
                isinstance(bm.bdm_wf_collection, dict) and 
                len(bm.bdm_wf_collection) == 0), \
            "bdm_wf_collection should be empty dictionary"
        assert bm.bm_options is not None, "bm_options should not be None"
        assert bm.bm_created_date is not None, "bm_created_date should be set"
        assert bm.bm_last_modified_date is not None, \
            "bm_last_modified_date should be set"
        assert bm.bm_last_modified_by is not None, \
            "bm_last_modified_by should be set"
        assert (bm.bdm_working_data is not None and 
                isinstance(bm.bdm_working_data, dict) and 
                len(bm.bdm_working_data) == 0), \
            "bdm_working_data should empty dictionary"
        logger.info(f"Complete:")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        pytest.fail(f"BudgetModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_budget_model_initialize_with_template() -> None:
    """Test BudgetModel() constructor with with template."""
    try:
        logger.info(test_budget_model_initialize_with_template.__doc__)
        bm = p3bm.BudgetModel(p3bm.BudgetModelTemplate.get_budget_model_template())
        # Initialize the budget model with the template as config_object.
        bm.bdm_initialize()
        
        # This instance should be full with resolved values and settings.
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"        
        assert bm.bm_initialized, "Budget model should be initialized"
        assert bm.bdm_id is not None, "bm.bdm_id should be set, not be None"
        assert bm.bdm_config_object is not None, \
            "bm.bdm_config_object should be set, not be None"
        assert bm.bm_folder is not None, "bm.bm_folder should be set"
        assert bm.bdm_url is not None, \
            "bm.bdm_url should be None"
        assert (bm.bdm_fi_collection is not None and 
                isinstance(bm.bdm_fi_collection, dict) and 
                len(bm.bdm_fi_collection) > 0), \
            "Financial institutions should non-empty dictionary"    
        assert (bm.bdm_wf_collection is not None and 
                isinstance(bm.bdm_wf_collection, dict) and 
                len(bm.bdm_wf_collection) > 0), \
            "bm.bdm_wf_collection should be non-empty dictionary"    
        assert bm.bm_options is not None, "bm.bm_options should be set"
        assert bm.bm_created_date is not None, "bm.bm_created_date should be set"
        assert bm.bm_last_modified_date is not None, \
            "bm._last_modified_date should be set"
        assert bm.bm_last_modified_by is not None, \
            "bm.bm_last_modified_by should not be None"
        assert (bm.bdm_working_data is not None and 
                isinstance(bm.bdm_working_data, dict)), \
            "bm.bdm_working_data should be an empty dictionary"    
    except Exception as e:
        pytest.fail(f"BudgetModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_FI_DATA_pseudo_Property_Methods():
    """Test BDM FI Object Pseudo Property Methods."""
    try:
        from src.budman_model.get_budget_model_template import __get_budget_model_template__
        logger.info(test_BDM_FI_DATA_pseudo_Property_Methods.__doc__)
        bm = p3bm.BudgetModel()
        bm.bdm_initialize(bsm_init=True)
        assert isinstance(bm, p3bm.BudgetModel), \
            "Budget model should be a BudgetModel instance"
        # Test expected values based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bm.VALID_FI_KEYS:
            assert bm.bdm_FI_KEY_validate(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert (bdm_fi := bm.bdm_FI_OBJECT(fi_key)) is not None, \
                f"Expected: {fi_key} to be a valid FI dict."
            assert len(bdm_fi) == len(p3bm.FI_OBJECT_VALID_ATTR_KEYS), \
                f"Expected: {fi_key} workbooks_in to be non-None."
            assert isinstance(bdm_fi, dict), \
                f"Expected: {fi_key} workbooks_in to be valid FI_DATA."
            assert bm.bdm_FI_KEY(fi_key) == fi_key, \
                f"Expected bdm_FI_KEY('{fi_key}'): '{fi_key}', got '{bdm_fi.bdm_FI_KEY(fi_key)}'."
            assert bm.bdm_FI_NAME(fi_key) in p3bm.BDM_FI_NAMES, \
                f"Expected one of: {p3bm.BDM_FI_NAMES}, got '{bm.bdm_FI_NAME(fi_key)}'"
            assert bm.bdm_FI_TYPE(fi_key) in p3bm.VALID_FI_TYPES, \
                f"Expected one of: {p3bm.BDM_FI_TYPES}, got '{bm.bdm_FI_TYPE(fi_key)}'"
            assert bm.bdm_FI_FOLDER(fi_key) is not None , \
                f"Expected bm.bdm_FI_FOLDER({fi_key}) to be non-None"
            assert isinstance(bm.bdm_FI_DATA_COLLECTION(fi_key), 
                              (dict, type(None))), \
                f"bdm_FI_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bm.bdm_FI_DATA_COLLECTION_count(fi_key), int), \
                f"Expected bm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            assert bm.bdm_FI_DATA_COLLECTION_count(fi_key) >= 0, \
                f"Expected bm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
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
        # Test expected values based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bm.VALID_FI_KEYS:
            assert isinstance(bm.bdm_FI_DATA_COLLECTION(fi_key), 
                              (dict, type(None))), \
                f"bdm_FI_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bm.bdm_FI_DATA_COLLECTION_count(fi_key), int), \
                f"Expected bm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            assert bm.bdm_FI_DATA_COLLECTION_count(fi_key) >= 0, \
                f"Expected bm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            if bm.bdm_FI_DATA_COLLECTION_count(fi_key) == 0:
                return
            # Test access to FI WF_DATA_OBJECTs.
            for wf_key in p3bm.BM_VALID_WORKFLOWS:
                wf_do = bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key)
                assert isinstance(wf_do := bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key),(dict,type(None))), \
                    f"bdm_FI_DATA({fi_key}, {wf_key}) should None or WF_DATA_OBJECT"
                if wf_do is not None:
                    l = len(wf_do)
                    assert isinstance(wf_do, dict), \
                        f"Expected bm.bdm_FI_DATA({fi_key}, {wf_key}) to be a WF_OBJECT"
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
            assert isinstance(bm.bdm_FI_DATA_COLLECTION(fi_key), 
                              (dict, type(None))), \
                f"bdm_FI_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bm.bdm_FI_DATA_COLLECTION_count(fi_key), int), \
                f"Expected bm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            assert bm.bdm_FI_DATA_COLLECTION_count(fi_key) >= 0, \
                f"Expected bm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            if bm.bdm_FI_DATA_COLLECTION_count(fi_key) == 0:
                return
            # Test access to FI WF_DATA_OBJECTs.
            for wf_key in p3bm.BM_VALID_WORKFLOWS:
                wf_do = bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key)
                assert isinstance(wf_do := bm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key),(dict,type(None))), \
                    f"bdm_FI_DATA({fi_key}, {wf_key}) should None or WF_DATA_OBJECT"
                if wf_do is not None:
                    assert len(wf_do) != 0, \
                        f"Expected: WF_DATA_OBJECT({fi_key},{wf_key}) to be non-zero length."
                    assert isinstance(wf_do, dict), \
                        f"Expected bm.bdm_FI_DATA({fi_key}, {wf_key}) to be a WF_OBJECT"
                    for wf_do_key in wf_do.keys():
                        wbl = bm.bdm_FI_WF_WORKBOOK_LIST(fi_key, wf_key, wf_do_key)
                        if wbl is not None:
                            assert isinstance(wbl, list), \
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
