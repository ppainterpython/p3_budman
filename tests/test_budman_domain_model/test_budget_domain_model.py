# ---------------------------------------------------------------------------- +
# test_budget_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
# third-party libraries
import inspect
import logging, p3_utils as p3u, p3logging as p3l
# local libraries
from budman_namespace import *
from budget_domain_model import (BudgetDomainModel, BDMConfig)
from budget_domain_model.budget_domain_model import (log_BDM_info, log_BSM_info)
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_model_construction_with_no_config_object() -> None:
    """Test BudgetModel() construction with no config_object."""
    try:
        logger.info(test_budget_model_construction_with_no_config_object.__doc__)
        # Expecting an empty core BudgetModel instance.
        bdm = BudgetDomainModel()
        
        # With no config_object provided to BudgetModel.__init__(), 
        # this instance should be mostly empty.
        assert isinstance(bdm, BudgetDomainModel)        
        assert not bdm.bdm_initialized, "BudgetModel inst should NOT be initialized"
        assert bdm.bdm_id is not None, "bdm_id should be set, not be None"
        assert bdm.bdm_folder is None, "bdm_folder should be None"
        assert bdm.bdm_url is not None, "bdm_url should not be None"
        assert (bdm.bdm_fi_collection is not None and 
                isinstance(bdm.bdm_fi_collection, dict) and 
                len(bdm.bdm_fi_collection) == 0), \
            "bdm_fi_collection should be empty dictionary"    
        assert (bdm.bdm_wf_collection is not None and 
                isinstance(bdm.bdm_wf_collection, dict) and 
                len(bdm.bdm_wf_collection) == 0), \
            "bdm_wf_collection should be empty dictionary"
        assert bdm.bdm_options is not None, "bm_options should not be None"
        assert bdm.bdm_created_date is not None, "bdm_created_date should be set"
        assert bdm.bdm_last_modified_date is not None, \
            "bdm_last_modified_date should be set"
        assert bdm.bdm_last_modified_by is not None, \
            "bdm_last_modified_by should be set"
        assert (bdm.bdm_working_data is not None and 
                isinstance(bdm.bdm_working_data, dict) and 
                len(bdm.bdm_working_data) == 0), \
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
        bdm = BudgetDomainModel(BDMConfig.BDM_CONFIG_default())
        
        # With no config_object provided to BudgetModel.__init__(), 
        # this instance should be mostly empty.
        assert isinstance(bdm, BudgetDomainModel), \
            "BudgetModel() should return a BudgetModel instance"        
        assert not bdm.bdm_initialized, "BudgetModel inst should NOT be initialized"
        assert bdm.bdm_id is not None, "bdm_id should be set, not be None"
        assert bdm.bdm_folder is None, "bm_folder should be None"
        assert bdm.bdm_url is not None, "bdm_url should not be None"
        assert (bdm.bdm_fi_collection is not None and 
                isinstance(bdm.bdm_fi_collection, dict) and 
                len(bdm.bdm_fi_collection) == 0), \
            "bdm_fi_collection should be empty dictionary"    
        assert (bdm.bdm_wf_collection is not None and 
                isinstance(bdm.bdm_wf_collection, dict) and 
                len(bdm.bdm_wf_collection) == 0), \
            "bdm_wf_collection should be empty dictionary"
        assert bdm.bdm_options is not None, "bm_options should not be None"
        assert bdm.bdm_created_date is not None, "bdm_created_date should be set"
        assert bdm.bdm_last_modified_date is not None, \
            "bdm_last_modified_date should be set"
        assert bdm.bdm_last_modified_by is not None, \
            "bdm_last_modified_by should be set"
        assert (bdm.bdm_working_data is not None and 
                isinstance(bdm.bdm_working_data, dict) and 
                len(bdm.bdm_working_data) == 0), \
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
        bdm = BudgetDomainModel(BDMConfig.BDM_CONFIG_default())
        # Initialize the budget model with the template as config_object.
        bdm.bdm_initialize()
        
        # This instance should be full with resolved values and settings.
        assert isinstance(bdm, BudgetDomainModel), \
            "Budget model should be a BudgetModel instance"        
        assert bdm.bdm_initialized, "Budget model should be initialized"
        assert bdm.bdm_id is not None, "bdm.bdm_id should be set, not be None"
        assert bdm.bdm_config_object is not None, \
            "bdm.bdm_config_object should be set, not be None"
        assert bdm.bdm_folder is not None, "bdm.bdm_folder should be set"
        assert bdm.bdm_url is not None, \
            "bdm.bdm_url should be None"
        assert (bdm.bdm_fi_collection is not None and 
                isinstance(bdm.bdm_fi_collection, dict) and 
                len(bdm.bdm_fi_collection) > 0), \
            "Financial institutions should non-empty dictionary"    
        assert (bdm.bdm_wf_collection is not None and 
                isinstance(bdm.bdm_wf_collection, dict) and 
                len(bdm.bdm_wf_collection) > 0), \
            "bdm.bdm_wf_collection should be non-empty dictionary"    
        assert bdm.bdm_options is not None, "bdm.bdm_options should be set"
        assert bdm.bdm_created_date is not None, "bdm.bdm_created_date should be set"
        assert bdm.bdm_last_modified_date is not None, \
            "bdm._last_modified_date should be set"
        assert bdm.bdm_last_modified_by is not None, \
            "bdm.bdm_last_modified_by should not be None"
        assert (bdm.bdm_working_data is not None and 
                isinstance(bdm.bdm_working_data, dict)), \
            "bdm.bdm_working_data should be an empty dictionary"    
    except Exception as e:
        pytest.fail(f"BudgetDomainModel() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_FI_DATA_pseudo_Property_Methods():
    """Test BDM FI Object Pseudo Property Methods."""
    try:
        from budget_domain_model import __get_budget_model_config__
        logger.info(test_BDM_FI_DATA_pseudo_Property_Methods.__doc__)
        bdm = BudgetDomainModel()
        bdm.bdm_initialize(bsm_init=True)
        assert isinstance(bdm, BudgetDomainModel), \
            "Budget model should be a BudgetModel instance"
        # Test expected values based on the settings in
        # the budget_model_config in the source code. 

        # Expect valid values to work from default setup.
        for fi_key in VALID_FI_KEYS:
            assert bdm.bdm_FI_KEY_validate(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert (bdm_fi := bdm.bdm_FI_OBJECT(fi_key)) is not None, \
                f"Expected: {fi_key} to be a valid FI dict."
            assert len(bdm_fi) == len(FI_OBJECT_VALID_ATTR_KEYS), \
                f"Expected: {fi_key} workbooks_in to be non-None."
            assert isinstance(bdm_fi, dict), \
                f"Expected: {fi_key} workbooks_in to be valid FI_DATA."
            assert bdm.bdm_FI_KEY(fi_key) == fi_key, \
                f"Expected bdm_FI_KEY('{fi_key}'): '{fi_key}', got '{bdm_fi.bdm_FI_KEY(fi_key)}'."
            assert bdm.bdm_FI_NAME(fi_key) in BDM_FI_NAMES, \
                f"Expected one of: {BDM_FI_NAMES}, got '{bdm.bdm_FI_NAME(fi_key)}'"
            assert bdm.bdm_FI_TYPE(fi_key) in VALID_FI_TYPES, \
                f"Expected one of: {VALID_FI_TYPES}, got '{bdm.bdm_FI_TYPE(fi_key)}'"
            assert bdm.bdm_FI_FOLDER(fi_key) is not None , \
                f"Expected bdm.bdm_FI_FOLDER({fi_key}) to be non-None"
            assert isinstance(bdm.bdm_FI_DATA_COLLECTION(fi_key), 
                              (dict, type(None))), \
                f"bdm_FI_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bdm.bdm_FI_DATA_COLLECTION_count(fi_key), int), \
                f"Expected bdm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            assert bdm.bdm_FI_DATA_COLLECTION_count(fi_key) >= 0, \
                f"Expected bdm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_FI_WF_DATA_OBJECT_pseudo_Property_Methods():
    """Test BDM_FI_WF_DATA_OBJECT() Pseudo Property Method."""
    try:
        logger.info(test_BDM_FI_WF_DATA_OBJECT_pseudo_Property_Methods.__doc__)
        bdm = BudgetDomainModel()
        bdm.bdm_initialize(bsm_init=True)
        assert isinstance(bdm, BudgetDomainModel), \
            "Budget model should be a BudgetModel instance"
        # Test expected values based on the settings in
        # the budget_model_config in the source code. 

        # Expect valid values to work from default setup.
        for fi_key in VALID_FI_KEYS:
            assert isinstance(bdm.bdm_FI_DATA_COLLECTION(fi_key), 
                              (dict, type(None))), \
                f"bdm_FI_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bdm.bdm_FI_DATA_COLLECTION_count(fi_key), int), \
                f"Expected bdm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            assert bdm.bdm_FI_DATA_COLLECTION_count(fi_key) >= 0, \
                f"Expected bdm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            if bdm.bdm_FI_DATA_COLLECTION_count(fi_key) == 0:
                return
            # Test access to FI WF_DATA_OBJECTs.
            for wf_key in BDM_VALID_WORKFLOWS:
                wf_do = bdm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key)
                assert isinstance(wf_do := bdm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key),(dict,type(None))), \
                    f"bdm_FI_DATA({fi_key}, {wf_key}) should None or WF_DATA_OBJECT"
                if wf_do is not None:
                    l = len(wf_do)
                    assert isinstance(wf_do, dict), \
                        f"Expected bdm.bdm_FI_DATA({fi_key}, {wf_key}) to be a WF_OBJECT"
                    for wf_do_key in wf_do.keys():
                        assert wf_do_key in WF_DATA_OBJECT_VALID_ATTR_KEYS, \
                            f"Expected: {wf_do_key} to be a valid WF_OBJECT key."
                        if wf_do_key == WF_INPUT:
                            assert bdm.bdm_WF_TYPE_MAP(wf_key,wf_do_key) == WF_INPUT_FOLDER, \
                                f"Expected: key: '{wf_do_key}' to be '{WF_INPUT_FOLDER}'."
                        elif wf_do_key == WF_OUTPUT:
                            assert bdm.bdm_WF_TYPE_MAP(wf_key,wf_do_key) == WF_OUTPUT_FOLDER, \
                                f"Expected: key: '{wf_do_key}' to be '{WF_OUTPUT_FOLDER}'."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bdm_FI_WF_WORKBOOK_LIST():
    """Test test_bdm_FI_WF_WORKBOOK_LIST() Pseudo Property Method."""
    try:
        logger.info(test_bdm_FI_WF_WORKBOOK_LIST.__doc__)
        bdm = BudgetDomainModel().bdm_initialize()
        assert isinstance(bdm, BudgetDomainModel), \
            "Budget model should be a BudgetModel instance"

        for fi_key in VALID_FI_KEYS:
            assert isinstance(bdm.bdm_FI_DATA_COLLECTION(fi_key), 
                              (dict, type(None))), \
                f"bdm_FI_DATA({fi_key}) should be type(None) or WF_DATA_COLLECTION"
            assert isinstance(bdm.bdm_FI_DATA_COLLECTION_count(fi_key), int), \
                f"Expected bdm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            assert bdm.bdm_FI_DATA_COLLECTION_count(fi_key) >= 0, \
                f"Expected bdm.bdm_FI_DATA_COLLECTION_count({fi_key}) to be > 0"
            if bdm.bdm_FI_DATA_COLLECTION_count(fi_key) == 0:
                return
            # Test access to FI WF_DATA_OBJECTs.
            for wf_key in BDM_VALID_WORKFLOWS:
                wf_do = bdm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key)
                assert isinstance(wf_do := bdm.bdm_FI_WF_DATA_OBJECT(fi_key, wf_key),(dict,type(None))), \
                    f"bdm_FI_DATA({fi_key}, {wf_key}) should None or WF_DATA_OBJECT"
                if wf_do is not None:
                    assert len(wf_do) != 0, \
                        f"Expected: WF_DATA_OBJECT({fi_key},{wf_key}) to be non-zero length."
                    assert isinstance(wf_do, dict), \
                        f"Expected bdm.bdm_FI_DATA({fi_key}, {wf_key}) to be a WF_OBJECT"
                    for wf_do_key in wf_do.keys():
                        wbl = bdm.bdm_FI_WF_WORKBOOK_LIST(fi_key, wf_key, wf_do_key)
                        if wbl is not None:
                            assert isinstance(wbl, list), \
                                f"Expected: {wf_do_key} to be a valid WORKBOOK_LIST object."
                            assert bdm.bdm_FI_WF_WORKBOOK_LIST_count(fi_key, wf_key, wf_do_key) >= 0, \
                                f"Expected: count of WORKBOOK_LIST >= 0."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_log_BDM_info():
    """Test log_BDM_info() function."""
    try:
        logger.info(test_log_BDM_info.__doc__)
        bm = BudgetDomainModel().bdm_initialize(bsm_init=True)
        assert isinstance(bm, BudgetDomainModel), \
            "Budget model should be a BudgetModel instance"
        assert log_BDM_info(bm) is None, \
            "log_BDM_info() should return None"
    except Exception as e:
        pytest.fail(f"log_BDM_info() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_log_BSM_info():
    """Test log_BSM_info() function."""
    try:
        logger.info(test_log_BSM_info.__doc__)
        bm = BudgetDomainModel().bdm_initialize(bsm_init=True)
        assert isinstance(bm, BudgetDomainModel), \
            "Budget model should be a BudgetModel instance"
        assert log_BSM_info(bm) is None, \
            "log_BSM_info() should return None"
    except Exception as e:
        pytest.fail(f"log_BSM_info() raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
