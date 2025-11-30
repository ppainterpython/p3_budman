# ---------------------------------------------------------------------------- +
#region test_bdms.py
"""Tests the BudManSettings class and its methods."""
#endregion test_bdms.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from typing import Type, Any
# third-party libraries
import inspect
import logging, p3_utils as p3u, p3logging as p3l
# local libraries
from budman_namespace.bdm_singleton_meta import BDMSingletonMeta
from budman_namespace.design_language_namespace import (
    BUDMAN_SETTINGS_FILES_ENV_VAR, BUDMAN_FOLDER_ENV_VAR
)
from budman_settings import *
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
@pytest.fixture(autouse=True)
def setup_env(monkeypatch) -> None:
    """Setup environment variables for BudManSettings tests."""
    project_root = Path(__file__).parent.parent.parent  # Go up from test file to project root
    testdata = project_root / "tests/testdata"
    test_settings_filename = "budman_settings_example.toml"
    test_settings_file = testdata / test_settings_filename
    # Setup environment variables for the test
    monkeypatch.setenv(BUDMAN_FOLDER_ENV_VAR, str(testdata))
    monkeypatch.setenv(BUDMAN_SETTINGS_FILES_ENV_VAR, 
                            f'["{str(test_settings_filename)}"]')
    monkeypatch.setenv("HOME", "/tmp/fake_home")
    monkeypatch.setenv("USERPROFILE", "C:\\tmp\\fake_home")
# ---------------------------------------------------------------------------- +
class TestBudManSettings:
    """BudManSettings testing."""
    def setup_method(self, monkeypatch) -> None:
        """Setup for each test method."""
        logger.info(self.setup_method.__doc__)
        logger.info(f"{BUDMAN_FOLDER_ENV_VAR} = '{os.getenv(BUDMAN_FOLDER_ENV_VAR)}'") 
        logger.info(f"{BUDMAN_SETTINGS_FILES_ENV_VAR} = '{os.getenv(BUDMAN_SETTINGS_FILES_ENV_VAR)}'")
        self.bdms : BudManSettings = BudManSettings()
        assert isinstance(self.bdms, BudManSettings), "bdms should be an instance of BudManSettings."
        assert self.bdms.budman.bdm_folder is not None, "BDM_FOLDER should not be None."

    def test_budman_settings_initialization(self, monkeypatch) -> None:
        """Test initialization of BudManSettings with env variables."""
        try:
            logger.info(self.test_budman_settings_initialization.__doc__)
            expected_BDM_FOLDER = "~/OneDrive/budget"
            assert self.bdms.budman.bdm_folder == expected_BDM_FOLDER, f"BDM_FOLDER should be '{expected_BDM_FOLDER  }'."
            expected_default_workflow = "categorization"
            assert self.bdms.budman.default_workflow == expected_default_workflow, f"BDM_DEFAULT_WORKFLOW should be '{expected_default_workflow}'."
        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)

    def test_budman_settings_initialization2(self, monkeypatch) -> None:
        """Test initialization of BudManSettings with constructor arguments."""
        try:
            logger.info(self.test_budman_settings_initialization2.__doc__)
            project_root = Path(__file__).parent.parent.parent  # Go up from test file to project root
            testdata = project_root / "tests/testdata"
            test_settings_filename = "budman_settings_example.toml"
            test_settings_file = testdata / test_settings_filename
            assert test_settings_file.exists(), f"Test settings file '{str(test_settings_file)}' does not exist."

            # Setup environment variables for the test
            settings_files = f'["{str(test_settings_filename)}"]'
            root_path = str(testdata)
            bdms : BudManSettings = BudManSettings(settings_files=settings_files,
                                                   root_path=root_path)
            assert isinstance(bdms, BudManSettings), "bdms should be an instance of BudManSettings."
            assert bdms.budman.bdm_folder is not None, "BDM_FOLDER should not be None."
            expected_BDM_FOLDER = "~/OneDrive/budget"
            assert bdms.budman.bdm_folder == expected_BDM_FOLDER, f"BDM_FOLDER should be '{expected_BDM_FOLDER  }'."
            expected_default_workflow = "categorization"
            assert bdms.budman.default_workflow == expected_default_workflow, f"BDM_DEFAULT_WORKFLOW should be '{expected_default_workflow}'."
        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)

    def test_budman_settings_constructor_exception(self, monkeypatch) -> None:
        """Test BudManSettings __init__() with internal exception."""
        try:
            logger.info(self.test_budman_settings_constructor_exception.__doc__)
            # Test internal exception to test outer except clause
            def fake_home():
                raise RuntimeError("Simulated home error.")
            
            with pytest.raises(RuntimeError) as excinfo:
                monkeypatch.setattr(Path, "home", fake_home)
                # Clear the BDMSingleton cache, force constructor to run
                BDMSingletonMeta._instances = {}
                _ = BudManSettings()
            assert excinfo.type == RuntimeError
        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)

    def test_BDM_STORE_abs_path(self, monkeypatch) -> None:
        """Test BDM_STORE absolute path resolution."""
        try:
            logger.info(self.test_BDM_STORE_abs_path.__doc__)

            # Test function happy path, uses setup_env fixture
            bdm_store_url : Path = self.bdms.BDM_STORE_abs_path().as_uri()
            assert bdm_store_url is not None, "BDM_STORE_URL should not be None."
            assert bdm_store_url == self.bdms.budman.store_url, \
                    f"BDM_STORE_URL should be '{self.bdms.budman.store_url}'."
            
            # Test internal exception to test outer except clause
            def fake_expanduser(self):
                raise RuntimeError("Simulated expanduser error.")
            
            with pytest.raises(RuntimeError) as excinfo:
                monkeypatch.setattr(Path, "expanduser", fake_expanduser)
                _ = self.bdms.BDM_STORE_abs_path()
            assert excinfo.type == RuntimeError

        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)

    def test_BUDMAN_FOLDER_abs_path(self, monkeypatch) -> None:
        """Test BUDMAN_FOLDER absolute path resolution."""
        try:
            logger.info(self.test_BUDMAN_FOLDER_abs_path.__doc__)

            # Test function happy path, uses setup_env fixture
            bdm_folder : Path = self.bdms.BUDMAN_FOLDER_abs_path()
            assert bdm_folder is not None, "BUDMAN_FOLDER_URL should not be None."
            bdm_store_folder = Path.from_uri(self.bdms.budman.store_url).parent
            assert bdm_folder == bdm_store_folder, \
                    f"BDM_FOLDER should be '{bdm_store_folder}'."

            # Test internal exception to test outer except clause
            def fake_expanduser(self):
                raise RuntimeError("Simulated expanduser error.")
            
            with pytest.raises(RuntimeError) as excinfo:
                monkeypatch.setattr(Path, "expanduser", fake_expanduser)
                _ = self.bdms.BUDMAN_FOLDER_abs_path()
            assert excinfo.type == RuntimeError

        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)

    def test_FI_FOLDER_abs_path(self, monkeypatch) -> None:
        """Test FI_FOLDER absolute path resolution."""
        try:
            logger.info(self.test_FI_FOLDER_abs_path.__doc__)

            # Test function happy path, uses setup_env fixture
            bdm_folder : Path = self.bdms.BUDMAN_FOLDER_abs_path()
            fi_key = "test_folder"
            expected_fi_folder = bdm_folder / fi_key
            fi_folder : Path = self.bdms.FI_FOLDER_abs_path(fi_key)
            assert fi_folder is not None, "FI_FOLDER_URL should not be None."
            assert fi_folder == expected_fi_folder, \
                    f"FI_FOLDER should be '{expected_fi_folder}'."

            # Test internal exception to test outer except clause
            def fake_expanduser(self):
                raise RuntimeError("Simulated expanduser error.")
            
            with pytest.raises(RuntimeError) as excinfo:
                monkeypatch.setattr(Path, "expanduser", fake_expanduser)
                _ = self.bdms.FI_FOLDER_abs_path(fi_key)
            assert excinfo.type == RuntimeError

        except Exception as e:
            m = f"{p3u.exc_err_msg(e)}"
            logger.error(m)
            pytest.fail(m)
# ---------------------------------------------------------------------------- +