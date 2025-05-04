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
import data.p3_budget_model as p3bt
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
        logger.info("Testing BudgetModelTemplate constructor.")
        bmt = p3bt.BudgetModelTemplate()
        
        # Check if the budget model is a dictionary
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        
        assert bmt._initialized, "Budget model should be initialized"
        assert bmt._created_date is not None, "Created date should not be None"
        assert bmt._last_modified_date is not None, "Last modified date should not be None"
        assert bmt._last_modified_by is not None, "Last modified by should not be None"
        assert bmt._options is not None, "Options should not be None"
        assert bmt._budget_folder is not None, "Budget folder should not be None"
        assert bmt._budget_model_store_uri is not None, "Budget model store URI should not be None"
        assert bmt._workflows is not None, "Workflows should not be None"
        assert bmt._financial_institutions is not None, "Financial institutions should not be None"
                
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
def test_bms_initialize() -> None:
    """Test the BudgetModelStorage.bms_initialize() Method."""
    try:
        # Initialize the logger from a logging configuration file.
        # p3l.setup_logging(THIS_APP_NAME,p3l.STDOUT_FILE_LOG_CONFIG_FILE)
        logger.info("Testing BudgetModelStorage constructor.")
        bmt = p3bt.BudgetModelTemplate()
        
        # Check if the budget model is a dictionary
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelStorage instance"
        
        assert bmt._initialized, "Budget model should be initialized"
        bmt.bms_inititalize()
        assert bmt._initialized, "Budget model should be initialized"


    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bms_BM_Folder_Path_methods() -> None:
    """Test BM Folder (BF) Path methods."""
    try:
        logger.info("Testing BudgetModelStorage constructor.")
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        exptd_s = str(Path(p3bt.BM_DEFAULT_BUDGET_FOLDER))
        assert (_s := bmt.bms_bm_folder_path_str()) == exptd_s, \
            f"Expected: {exptd_s}, Got: {_s}"
        exptd_p = Path(_s).expanduser()
        assert (_p := bmt.bms_bm_folder_path()) == exptd_p, \
            f"Expected: {exptd_p}, Got: {_p}"
        exptd_ap = Path(_p).resolve()
        assert (_ap := bmt.bms_bm_folder_abs_path()) == exptd_ap, \
            f"Expected: {exptd_ap}, Got: {_ap}" 
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_bms_FI_Path_methods() -> None:
    """Test FI Path methods."""
    try:
        logger.info("Testing BudgetModelStorage constructor.")
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected valuees based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bt.VALID_FI_KEYS:
            assert bmt.bmd_validate_fi_key(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert bmt.bms_fi_folder_path_str(fi_key) is not None, \
                f"Expected: {fi_key} folder path string to be valid."
            assert bmt.bms_fi_folder_path(fi_key) is not None, \
                f"Expected: {fi_key} folder path to be valid."
            assert bmt.bms_fi_folder_abs_path(fi_key) is not None, \
                f"Expected: {fi_key} folder absolute path to be valid."
            assert bmt.bms_fi_folder_abs_path_str(fi_key) is not None, \
                f"Expected: {fi_key} folder absolute path string to be valid."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_WF_Path_methods() -> None:
    """Test WF Path methods."""
    try:
        logger.info("Testing WF Path methods.")
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected valuees based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bt.VALID_FI_KEYS:
            assert bmt.bmd_validate_fi_key(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            for wf_key in p3bt.BM_VALID_WORKFLOWS:
                assert bmt.bmd_validate_wf_key(wf_key), \
                    f"Expected: {wf_key} to be a valid WF key."
                _s = bmt.bms_wf_folder_in_path_str(fi_key,wf_key)
                logger.debug(f"WF: {wf_key} bms_wf_folder_in_path_str(): '{_s}'")
                if _s is not None:
                    assert isinstance(_s, str), \
                        f"Expected: {wf_key} folder path to be string."
                    assert (_p := bmt.bms_wf_folder_in_path(fi_key,wf_key)) is not None, \
                        f"Expected: {wf_key} folder path to be valid."
                    assert (_ap := bmt.bms_wf_folder_in_abs_path(fi_key,wf_key)) is not None, \
                        f"Expected: {wf_key} folder absolute path to be valid."
                    assert (_aps := bmt.bms_wf_folder_in_abs_path_str(fi_key,wf_key)) is not None, \
                        f"Expected: {wf_key} folder absolute path string to be valid."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BMD_FI_pseudo_Property_Methods():
    """Test BMD FI Pseudo Property Methods."""
    try:
        logger.info(test_BMD_FI_pseudo_Property_Methods.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected valuees based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for fi_key in p3bt.VALID_FI_KEYS:
            assert bmt.bmd_validate_fi_key(fi_key), \
                f"Expected: {fi_key} to be a valid FI key."
            assert (bmd_fi := bmt.bmd_fi(fi_key)) is not None, \
                f"Expected: {fi_key} to be a valid FI dict."
            assert len(bmd_fi) == len(p3bt.FI_EXPECTED_KEYS), \
                f"Expected: {fi_key} workbooks_in to be non-None."
            assert isinstance(bmd_fi, dict), \
                f"Expected: {fi_key} workbooks_in to be valid dict."
            assert bmt.bmd_fi_key(fi_key) == fi_key, \
                f"Expected bmd_fi_key('{fi_key}'): '{fi_key}', got '{bmd_fi.bmd_fi_key(fi_key)}'."
            assert bmt.bmd_fi_name(fi_key) in p3bt.BMD_FI_NAMES, \
                f"Expected one of: {p3bt.BMD_FI_NAMES}, got '{bmt.bmd_fi_name(fi_key)}'"
            assert bmt.bmd_fi_type(fi_key) in p3bt.VALID_FI_TYPES, \
                f"Expected one of: {p3bt.BMD_FI_TYPES}, got '{bmt.bmd_fi_type(fi_key)}'"
            assert (fldr := bmt.bmd_fi_folder(fi_key)) is not None , \
                f"Expected bmt.bmd_fi_folder({fi_key}) to be non-None"
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")
# ---------------------------------------------------------------------------- +
def test_BMD_WF_Dictioonary_Pseudo_Property_Methods():
    """Test BMD WF Dictionary Pseudo Property Methods."""
    try:
        logger.info(test_BMD_WF_Dictioonary_Pseudo_Property_Methods.__doc__)
        bmt = p3bt.BudgetModelTemplate()
        assert isinstance(bmt, p3bt.BudgetModelTemplate), \
            "Budget model should be a BudgetModelTemplate instance"
        # Test expected valuees based on the settings in
        # the budget_model_template in the source code. All default 
        # settings are mastered there and budget_model_constants.py.

        # Expect valid values to work from default setup.
        for wf_key in p3bt.BM_VALID_WORKFLOWS:
            assert bmt.bmd_validate_wf_key(wf_key), \
                f"Expected: {wf_key} to be a valid WF key."
            assert (bmd_wf := bmt.bmd_wf(wf_key)) is not None, \
                f"Expected: {wf_key} to be a valid WF dict."
            assert len(bmd_wf) == len(p3bt.WF_EXPECTED_KEYS), \
                f"Expected: {wf_key} workbooks_in to be non-None."
            assert isinstance(bmd_wf, dict), \
                f"Expected: {wf_key} workbooks_in to be valid dict."
            assert bmt.bmd_wf_key(wf_key) == wf_key, \
                f"Expected bmd_wf_key('{wf_key}'): '{wf_key}', got '{bmd_wf.bmd_wf_key(wf_key)}'."
            assert bmt.bmd_wf_name(wf_key) is not None, \
                f"Expected bmt.bmd_wf_name({wf_key}) to be non-None"
            assert bmt.bmd_wf_name(wf_key) in p3bt.BM_VALID_WORKFLOWS, \
                f"Expected one of: {p3bt.BM_VALID_WORKFLOWS}, got '{bmt.bmd_wf_name(wf_key)}'"
            assert isinstance(bmt.bmd_wf_folder_in(wf_key), (str, type(None))), \
                f"Expected bmt.bmd_wf_folder_in({wf_key}) to type: None or str"
            assert isinstance(bmt.bmd_wf_folder_out(wf_key), (str, type(None))), \
                f"Expected bmt.bmd_wf_folder_out{wf_key}) to type: None or str"
            assert isinstance(bmt.bmd_wf_workbooks_in(wf_key),(dict, type(None))), \
                f"Expected: {wf_key} workbooks_in to be dict or None."
            assert isinstance(bmt.bmd_wf_workbooks_out(wf_key), (dict, type(None))), \
                f"Expected: {wf_key} workbooks_out to be dict or None."
            assert isinstance(bmt.bmd_wf_in_prefix(wf_key), (str, type(None))), \
                f"Expected bmt.bmd_wf_in_prefix({wf_key}) to be str or None"
            assert isinstance(bmt.bmd_wf_out_prefix(wf_key), (str, type(None))), \
                f"Expected bmt.bmd_wf_out_prefix({wf_key}) to be str or None" 
            
            # assert bmt.bms_wf_workbooks_in(wf_key) is not None, \
            #     f"Expected: {wf_key} workbooks_in to be non-None."
            # assert isinstance(bmt.bms_wf_workbooks_in(wf_key), dict), \
            #     f"Expected: {wf_key} workbooks_in to be valid dict."
            # assert len(bmt.bms_wf_workbooks_in(wf_key)) >= 0, \
            #     f"Expected: {wf_key} workbooks_in to have valid length."
    except Exception as e:
        pytest.fail(f"init_budget_model raised an exception: {str(e)}")