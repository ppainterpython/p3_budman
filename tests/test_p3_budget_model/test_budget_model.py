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
