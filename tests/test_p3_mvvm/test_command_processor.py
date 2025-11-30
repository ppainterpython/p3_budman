# ---------------------------------------------------------------------------- +
#region tests/test_p3_mvvm/test_command_processor.py
"""Tests for the p3_mvvm.command_processor module."""
#endregion tests/test_p3_mvvm/test_command_processor.py
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard libraries
import pytest, logging
# third-party libraries

# local libraries
from p3_mvvm.command_processor import CommandProcessor
from p3_mvvm.mvvm_namespace import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class TestCommandProcessor:
    """Tests for the CommandProcessor class."""
    def setup_method(self) -> None:
        """Setup for each test method."""
        self.cmd_processor = CommandProcessor()

    def test_construction(self) -> None:
        """Test construction of CommandProcessor."""
        assert self.cmd_processor is not None, "CommandProcessor instance should not be None."
        assert isinstance(self.cmd_processor, CommandProcessor), "cmd_processor should be an instance of CommandProcessor."

    def test_cp_validate_cmd_object_before_cp_initialize(self) -> None:
        """Test using validate_cmd_object before initialization."""
        with pytest.raises(RuntimeError) as exc_info:
            self.cmd_processor.cp_validate_cmd_object(cmd={"action": "test"},
                                                      raise_error=True)
        assert "Command Processor is not initialized." in str(exc_info.value), "Expected RuntimeError for uninitialized CommandProcessor."

    def test_cp_initialize(self) -> None:
        """Test initialization of CommandProcessor."""
        self.cmd_processor.cp_initialize()
        assert self.cmd_processor.cp_initialized is True, "CommandProcessor should be initialized."  

    def test_initialize_worker_thread(self) -> None:
        """Test worker thread initialization."""
        self.cmd_processor.cp_initialize()
        self.cmd_processor.cp_initialize_worker_thread()
        assert self.cmd_processor.cp_worker_thread is not None, "Worker thread should be initialized."
        assert self.cmd_processor.cp_worker_thread.is_alive() is True, "Worker thread should be alive."



