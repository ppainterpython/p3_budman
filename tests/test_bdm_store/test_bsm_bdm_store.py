# ---------------------------------------------------------------------------- +
# test_bsm_bdm_store.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
# third-party modules and packages
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
from budget_storage_model import *
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
BAD_JSON_FILE = "bdm_store_invalid_json.json"
EMPTY_JSON_FILE = "bdm_store_empty_file.json"
TEXT_FILE = "bdm_store_text_file.txt"
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
import shutil
import pytest
from pathlib import Path


# ------------------------------------------------------------------------ +
@pytest.fixture(scope="session", autouse=True)
def temp_dir(tmp_path_factory):
    """Copy test files from 'tests' folder into a temporary directory and
    create 'file:///' urls."""
    try:
        tmp_root = tmp_path_factory.getbasetemp()
        logger.info(f"tmp_root = '{tmp_root}'")
        tmp = tmp_path_factory.mktemp("test_data")
        source_dir = Path(__file__).parent.parent / "testdata/BDM_STORE"
        # Copy all files from 'tests/testdata' to temp_dir
        for file in source_dir.iterdir():
            if file.is_file():
                shutil.copy(file, tmp / file.name)
        logger.info(f"temp_dir = '{tmp}'")
        return tmp
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
# ------------------------------------------------------------------------ +
def test_bsm_BDM_STORE_url_load(temp_dir):
    """Test the BDM_STORE URL loading functionality."""
    try:
        logger.info(test_bsm_BDM_STORE_url_load.__doc__)
        test_urls = []
        assert temp_dir is not None, "Temporary directory is None"
        assert temp_dir.exists()  # ✅ Ensures file was copied
        for file in temp_dir.iterdir():
            if file.is_file():
                file_url = f"file:///{file.resolve()}"
                test_urls.append(file_url)
        # Happy path = Run through the test URLs and test each one
        assert len(test_urls) > 0, "No test URLs found"
        logger.info(f"Test URLs: {test_urls}")
        for url in test_urls:
            bdms_path  = Path.from_uri(url)
            assert bdms_path is not None, f"Path from URI failed for {url}"
            logger.info(f"  Test URL: {url}")
            if bdms_path.name == BAD_JSON_FILE:
                # File with invalid JSON content
                with pytest.raises(Exception) as exc_info:
                    logger.info(f"    Expecting exception for '{bdms_path.name}':' "
                                f" for invalid json file")
                    bsm_BDM_STORE_url_load(url)
            elif bdms_path.name == TEXT_FILE:
                # file with unsupported file type
                with pytest.raises(ValueError) as exc_info:
                    logger.info(f"    Expecting exception ValueError for '{bdms_path.name}':' "
                                f" for BDM_STORE file unsupported file type")
                    bsm_BDM_STORE_url_load(url)
                assert exc_info.type is ValueError, \
                    f"Expected ValueError, got: {exc_info.type}"
                exp_content = "bdms_path filetype is not supported"
                assert exp_content in str(exc_info.value), \
                    f"Expected '{exp_content}' in message, got: {exc_info.value}"
            elif bdms_path.name == EMPTY_JSON_FILE:
                # empty JSON file
                with pytest.raises(ValueError) as exc_info:
                    logger.info(f"    Expecting exception ValueError for '{bdms_path.name}':' "
                                f" for BDM_STORE file empty json file")
                    bsm_BDM_STORE_url_load(url)
                assert exc_info.type is ValueError, \
                    f"Expected ValueError, got: {exc_info.type}"
                exp_content = "file is empty"
                assert exp_content in str(exc_info.value), \
                    f"Expected '{exp_content}' in message, got: {exc_info.value}"
            else:
                bdm_store = bsm_BDM_STORE_url_load(url)
                assert bdm_store is not None
                assert isinstance(bdm_store, dict)
        # Unhappy path tests
        # Invalid file URL with non-absolute path, not specifically caught in target function
        with pytest.raises(ValueError) as exc_info:
            logger.info("    Expecting exception FileNotFoundError for invalid path")
            bsm_BDM_STORE_url_load("file:///xxxxxxxx.json")
        exp_content = "URI is not absolute:"
        assert exp_content in str(exc_info.value), \
            f"Expected '{exp_content}' in message, got: {exc_info.value}"
        # Invalid file URL to non-existent file
        with pytest.raises(FileNotFoundError) as exc_info:
            logger.info("    Expecting exception FileNotFoundError for invalid path")
            bsm_BDM_STORE_url_load("file:///C:\\xxxxxxxx.json")
        exp_content = "file does not exist:"
        assert exp_content in str(exc_info.value), \
            f"Expected '{exp_content}' in message, got: {exc_info.value}"
        # Invalid file URL with no scheme
        with pytest.raises(ValueError) as exc_info:
            logger.info("    Expecting exception ValueError for invalid url")
            bsm_BDM_STORE_url_load("xxxxxxxx.json")
        exp_content = "Invalid URL"
        assert exp_content in str(exc_info.value), \
            f"Expected '{exp_content}' in message, got: {exc_info.value}"
        # Non-str for URL
        with pytest.raises(TypeError) as exc_info:
            logger.info("    Expecting exception TypeError non-str URL")
            bsm_BDM_STORE_url_load(123)
        exp_content = "must be type:'str', not type:"
        assert exp_content in str(exc_info.value), \
            f"Expected '{exp_content}' in message, got: {exc_info.value}"
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        pytest.fail(m)
# ------------------------------------------------------------------------ +
def test_bsm_BDM_STORE_file_load(temp_dir):
    """Test the BDM_STORE file loading functionality."""
    try:
        logger.info(test_bsm_BDM_STORE_file_load.__doc__)
        test_files = []
        assert temp_dir is not None, "Temporary directory is None"
        assert temp_dir.exists()  # ✅ Ensures file was copied
        for file in temp_dir.iterdir():
            if file.is_file():
                file_path = file.resolve()
                test_files.append(file_path)
        # Run through the provided test files and test each one
        assert len(test_files) > 0, "No test files found"
        logger.info(f"Test files: {test_files}")
        for test_path in test_files:
            assert test_path.exists(), f"File does not exist {test_path}"
            logger.info(f"  Test File: {test_path}")
            if test_path.name == BAD_JSON_FILE:
                with pytest.raises(Exception) as exc_info:
                    logger.info(f"    Expecting exception for '{test_path.name}':' "
                                f" for invalid json file")
                    bsm_BDM_STORE_file_load(test_path)
            else:
                bdm_store = bsm_BDM_STORE_file_load(test_path)
                assert bdm_store is not None
                assert isinstance(bdm_store, dict)
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        pytest.fail(m)
# ------------------------------------------------------------------------ +
        
