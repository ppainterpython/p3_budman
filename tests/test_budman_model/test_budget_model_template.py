# ---------------------------------------------------------------------------- +
# test_budget_model_template.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path

# third-party libraries
import inspect

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
import budman_model as p3bt
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(p3bt.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
def test_budget_model_template_constructor() -> None:
    """Test the BudgetModelTemplate() function."""
    try:
        # Initialize the logger from a logging configuration file.
        # p3l.setup_logging(THIS_APP_NAME,p3l.STDOUT_FILE_LOG_CONFIG_FILE)
        st = p3u.start_timer()
        logger.info(test_budget_model_template_constructor.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        
        # Check if the budget model is a dictionary
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"        
        assert bmt._initialized, "Budget model should be initialized"
        assert bmt._bdm_id is not None, "Created date should not be None"
        assert bmt._created_date is not None, "Created date should not be None"
        assert bmt._last_modified_date is not None, "Last modified date should not be None"
        assert bmt._last_modified_by is not None, "Last modified by should not be None"
        assert bmt._options is not None, "Options should not be None"
        assert bmt._budget_folder is not None, "Budget folder should not be None"
        assert bmt._bdm_url is not None, "Budget model store path should not be None"
        assert bmt._workflows is not None, "Workflows should not be None"
        assert bmt._financial_institutions is not None, "Financial institutions should not be None"
        logger.debug(f"Test Complete: {p3u.stop_timer(st)}")   
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
def test_bsm_initialize() -> None:
    """Test the BudgetModelStorage.bsm_initialize() Method."""
    try:
        # Initialize the logger from a logging configuration file.
        # p3l.setup_logging(THIS_APP_NAME,p3l.STDOUT_FILE_LOG_CONFIG_FILE)
        st = p3u.start_timer()
        logger.info(test_bsm_initialize.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        
        # Check if the budget model is a dictionary
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelStorage instance"
        
        assert bmt._initialized, "Budget model should be initialized"
        bmt.bsm_initialize()
        assert bmt._initialized, "Budget model should be initialized"
        logger.debug(f"Test Complete: {p3u.stop_timer(st)}")   
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bsm_BDM_Folder_Path_methods() -> None:
    """Test BM Folder (BF) Path methods."""
    try:
        logger.info(test_bsm_BDM_Folder_Path_methods.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        exptd_s = str(Path(p3bt.BDM_DEFAULT_BUDGET_FOLDER))
        assert (_s := bmt.bsm_BDM_FOLDER_path_str()) == exptd_s, \
            f"Expected: {exptd_s}, Got: {_s}"
        exptd_p = Path(_s).expanduser()
        assert (_p := bmt.bsm_BDM_FOLDER_path()) == exptd_p, \
            f"Expected: {exptd_p}, Got: {_p}"
        exptd_ap = Path(_p).resolve()
        assert (_ap := bmt.bsm_BDM_FOLDER_abs_path()) == exptd_ap, \
            f"Expected: {exptd_ap}, Got: {_ap}" 
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bsm_FI_Path_methods() -> None:
    """Test FI Path methods."""
    try:
        logger.info("Testing BudgetModelStorage constructor.")
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected values based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bt.VALID_FI_KEYS:
            assert bmt.bdm_FI_KEY_validate(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert bmt.bsm_FI_FOLDER_path_str(fi_key) is not None, \
                f"Expected: {fi_key} folder path string to be valid."
            assert bmt.bsm_FI_FOLDER_path(fi_key) is not None, \
                f"Expected: {fi_key} folder path to be valid."
            assert bmt.bsm_FI_FOLDER_abs_path(fi_key) is not None, \
                f"Expected: {fi_key} folder absolute path to be valid."
            assert bmt.bsm_FI_FOLDER_abs_path_str(fi_key) is not None, \
                f"Expected: {fi_key} folder absolute path string to be valid."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_WF_OBJECT_Path_methods() -> None:
    """Test WF Object Path methods."""
    try:
        logger.info(test_WF_OBJECT_Path_methods.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected values based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bt.VALID_FI_KEYS:
            assert bmt.bdm_FI_KEY_validate(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            for wf_key in p3bt.BDM_VALID_WORKFLOWS:
                assert bmt.bdm_WF_KEY_validate(wf_key), \
                    f"Expected: {wf_key} to be a valid WF key."
                for f_id in p3bt.WF_FOLDER_PATH_ELEMENTS:
                    _s = bmt.bsm_WF_FOLDER_path_str(fi_key,wf_key, f_id)
                    logger.debug(f"WF: {wf_key} bsm_{f_id}_path_str(): '{_s}'")
                    if _s is not None:
                        assert isinstance(_s, str), \
                            f"Expected: {wf_key} {f_id} path to be string."
                        assert (_p := bmt.bsm_WF_FOLDER_path(fi_key,wf_key,f_id)) is not None, \
                            f"Expected: {wf_key} {f_id} path to be valid."
                        assert (_ap := bmt.bsm_WF_FOLDER_abs_path(fi_key,wf_key,f_id)) is not None, \
                            f"Expected: {wf_key} {f_id} absolute path to be valid."
                        assert (_aps := bmt.bsm_WF_FOLDER_abs_path_str(fi_key,wf_key,f_id)) is not None, \
                            f"Expected: {wf_key} {f_id} absolute path string to be valid."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_FI_DATA_pseudo_Property_Methods():
    """Test BDM FI Object Pseudo Property Methods."""
    try:
        logger.info(test_BDM_FI_DATA_pseudo_Property_Methods.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected values based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bt.VALID_FI_KEYS:
            assert bmt.bdm_FI_KEY_validate(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert (bdm_fi := bmt.bdm_FI_OBJECT(fi_key)) is not None, \
                f"Expected: {fi_key} to be a valid FI dict."
            assert len(bdm_fi) == len(p3bt.FI_OBJECT_VALID_ATTR_KEYS), \
                f"Expected: {fi_key} workbooks_in to be non-None."
            assert isinstance(bdm_fi, dict), \
                f"Expected: {fi_key} workbooks_in to be valid dict."
            assert bmt.bdm_FI_KEY(fi_key) == fi_key, \
                f"Expected bdm_FI_KEY('{fi_key}'): '{fi_key}', got '{bdm_fi.bdm_FI_KEY(fi_key)}'."
            assert bmt.bdm_FI_NAME(fi_key) in p3bt.BDM_FI_NAMES, \
                f"Expected one of: {p3bt.BDM_FI_NAMES}, got '{bmt.bdm_FI_NAME(fi_key)}'"
            assert bmt.bdm_FI_TYPE(fi_key) in p3bt.VALID_FI_TYPES, \
                f"Expected one of: {p3bt.BDM_FI_TYPES}, got '{bmt.bdm_FI_TYPE(fi_key)}'"
            assert bmt.bdm_FI_FOLDER(fi_key) is not None , \
                f"Expected bmt.bdm_FI_FOLDER({fi_key}) to be non-None"
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BDM_WF_Dictionary_Pseudo_Property_Methods():
    """Test BDM WF Dictionary Pseudo Property Methods."""
    try:
        logger.info(test_BDM_WF_Dictionary_Pseudo_Property_Methods.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected values based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for wf_key in p3bt.BDM_VALID_WORKFLOWS:
            assert bmt.bdm_WF_KEY_validate(wf_key), \
                f"Expected: {wf_key} to be a valid WF key."
            assert (bdm_WF_OBJECT := bmt.bdm_WF_OBJECT(wf_key)) is not None, \
                f"Expected: {wf_key} to be a valid WF dict."
            assert len(bdm_WF_OBJECT) == len(p3bt.WF_OBJECT_VALID_ATTR_KEYS), \
                f"Expected: {wf_key} workbooks_in to be non-None."
            assert isinstance(bdm_WF_OBJECT, dict), \
                f"Expected: {wf_key} workbooks_in to be valid dict."
            assert bmt.bdm_WF_KEY(wf_key) == wf_key, \
                f"Expected bdm_WF_KEY('{wf_key}'): '{wf_key}', got '{bdm_WF_OBJECT.bdm_WF_KEY(wf_key)}'."
            assert bmt.bdm_WF_NAME(wf_key) is not None, \
                f"Expected bmt.bdm_WF_NAME({wf_key}) to be non-None"
            assert bmt.bdm_WF_NAME(wf_key) in p3bt.BDM_VALID_WORKFLOWS, \
                f"Expected one of: {p3bt.BDM_VALID_WORKFLOWS}, got '{bmt.bdm_WF_NAME(wf_key)}'"
            assert isinstance(bmt.bdm_WF_FOLDER(wf_key, p3bt.WF_INPUT_FOLDER), (str, type(None))), \
                f"Expected bmt.bdm_WF_INPUT_FOLDER({wf_key}) to type: None or str"
            assert isinstance(bmt.bdm_WF_FOLDER(wf_key,p3bt.WF_OUTPUT_FOLDER), (str, type(None))), \
                f"Expected bmt.bdm_WF_OUTPUT_FOLDER{wf_key}) to type: None or str"
            # assert isinstance(bmt.bdm_WF_OBJECT_workbooks_in(wf_key),(dict, type(None))), \
            #     f"Expected: {wf_key} workbooks_in to be dict or None."
            # assert isinstance(bmt.bdm_WF_OBJECT_workbooks_out(wf_key), (dict, type(None))), \
            #     f"Expected: {wf_key} workbooks_out to be dict or None."
            assert isinstance(bmt.bdm_WF_PREFIX_IN(wf_key), (str, type(None))), \
                f"Expected bmt.bdm_WF_PREFIX_IN({wf_key}) to be str or None"
            assert isinstance(bmt.bdm_WF_PREFIX_OUT(wf_key), (str, type(None))), \
                f"Expected bmt.bdm_WF_PREFIX_OUT({wf_key}) to be str or None" 
            
            # assert bmt.bsm_WF_WORKBOOKS_IN(wf_key) is not None, \
            #     f"Expected: {wf_key} workbooks_in to be non-None."
            # assert isinstance(bmt.bsm_WF_WORKBOOKS_IN(wf_key), dict), \
            #     f"Expected: {wf_key} workbooks_in to be valid dict."
            # assert len(bmt.bsm_WF_WORKBOOKS_IN(wf_key)) >= 0, \
            #     f"Expected: {wf_key} workbooks_in to have valid length."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")