#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
import os, sys
import logging, pytest

# sys.path.insert(0,  '../src')
print("\nCurrent working directory:", os.getcwd())
print("Resolving path to current file:", os.path.abspath(__file__))
print("sys.path:", sys.path)

# Ensure the path to p3logging is added to sys.path
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import p3logging as p3l
from budmod import *

#------------------------------------------------------------------------------+
def test_main_default(caplog) -> None:
    """Test operation of default logging config."""
    with caplog.at_level(logging.DEBUG):
        budmod()
    assert "Warning message" in caplog.text, \
        "Expected 'Warning message' in log output"
    assert "Debug message" in caplog.text, \
        "Expected 'Debug message' in log output"
    assert "Info message" in caplog.text, \
        "Expected 'Info message' in log output"
    assert "Error message" in caplog.text, \
        "Expected 'Error message' in log output"
    assert "Critical message" in caplog.text, \
        "Expected 'Critical message' in log output"
    assert "division by zero" in caplog.text, \
        "Expected 'division by zero' in log output"
    assert len(caplog.records) == 7

def test_main_stdout(caplog) -> None:
    """Test operation of AT_STDOUT_LOG_CONFIG_FILE logging config."""
    with caplog.at_level(logging.DEBUG):
        budmod(p3l.STDOUT_LOG_CONFIG_FILE)
    assert "Warning message" in caplog.text, \
        "Expected 'Warning message' in log output"
    assert "Debug message" in caplog.text, \
        "Expected 'Debug message' in log output"
    assert "Info message" in caplog.text, \
        "Expected 'Info message' in log output"
    assert "Error message" in caplog.text, \
        "Expected 'Error message' in log output"
    assert "Critical message" in caplog.text, \
        "Expected 'Critical message' in log output"
    assert "division by zero" in caplog.text, \
        "Expected 'division by zero' in log output"
    assert len(caplog.records) == 7

def test_main_stderr_json_file(caplog) -> None:
    """Test operation of AT_STDERR_JSON_FILE_LOG_CONFIG_FILE logging config."""
    with caplog.at_level(logging.DEBUG):
        budmod(p3l.STDERR_JSON_FILE_LOG_CONFIG_FILE)
    assert "Warning message" in caplog.text, \
        "Expected 'Warning message' in log output"
    assert "Debug message" in caplog.text, \
        "Expected 'Debug message' in log output"
    assert "Info message" in caplog.text, \
        "Expected 'Info message' in log output"
    assert "Error message" in caplog.text, \
        "Expected 'Error message' in log output"
    assert "Critical message" in caplog.text, \
        "Expected 'Critical message' in log output"
    assert "division by zero" in caplog.text, \
        "Expected 'division by zero' in log output"
    assert len(caplog.records) == 7

def test_main_queued_stderr_json_file(caplog) -> None:
    """Test operation of AT_QUEUED_STDERR_JSON_FILE_LOG_CONFIG_FILE logging config."""
    with caplog.at_level(logging.DEBUG):
        budmod(p3l.QUEUED_STDERR_JSON_FILE_LOG_CONFIG_FILE)
    assert "Warning message" in caplog.text, \
        "Expected 'Warning message' in log output"
    assert "Debug message" in caplog.text, \
        "Expected 'Debug message' in log output"
    assert "Info message" in caplog.text, \
        "Expected 'Info message' in log output"
    assert "Error message" in caplog.text, \
        "Expected 'Error message' in log output"
    assert "Critical message" in caplog.text, \
        "Expected 'Critical message' in log output"
    assert "division by zero" in caplog.text, \
        "Expected 'division by zero' in log output"
    assert len(caplog.records) == 7

def test_setup_logging(caplog) -> None:
    """Test the setup_logging function."""
    try:
        logger = logging.getLogger(THIS_APP_NAME)
        logger.propagate = True        
        root_logger = logging.getLogger()
        # Initialize the logger from a logging configuration file.
        ln = THIS_APP_NAME; cf = p3l.STDERR_JSON_FILE_LOG_CONFIG_FILE; verbose = True
        p3l.setup_logging(cf)
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message for testing")
            logger.info("Info message for testing")
            logger.warning("Warning message for testing")
            logger.error("Error message for testing")
            logger.critical("Critical message for testing")
        assert "Warning message" in caplog.text, \
            "Expected 'Warning message' in log output"
        assert "Debug message" in caplog.text, \
            "Expected 'Debug message' in log output"
        assert "Info message" in caplog.text, \
            "Expected 'Info message' in log output"
        assert "Error message" in caplog.text, \
            "Expected 'Error message' in log output"
        assert "Critical message" in caplog.text, \
            "Expected 'Critical message' in log output"
        assert logger is not None, "Logger should be initialized"
        assert root_logger.level == logging.DEBUG, "Logger level should be DEBUG"
        try:
            1 / 0
        except ZeroDivisionError as e:
            logger.exception(f"Exception message: {str(e)}")
        assert "division by zero" in caplog.text, \
            "Expected 'Exception message' in log output"
    except Exception as e:
        pytest.fail(f"setup_logging raised an exception: {str(e)}")
#------------------------------------------------------------------------------+
#region testickle_logger_exception_message
def testickle_logger_exception_message(caplog)    -> None:
    """Test function to demonstrate logging an exception."""
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception(f"Exception message: {str(e)}")
    assert "division by zero" in caplog.text, \
           "Expected 'Exception message' in log output"
#endregion testickle_logger_exception_message
#------------------------------------------------------------------------------+
