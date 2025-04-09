#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
import logging, pytest
from main import *

#------------------------------------------------------------------------------+
def test_main_default(caplog) -> None:
    """Test operation of default logging config."""
    with caplog.at_level(logging.DEBUG):
        main()
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
    """Test operation of AT_STDOUT_LOG_CONFIG logging config."""
    with caplog.at_level(logging.DEBUG):
        main(AT_STDOUT_LOG_CONFIG)
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
    """Test operation of AT_STDERR_JSON_FILE_LOG_CONFIG logging config."""
    with caplog.at_level(logging.DEBUG):
        main(AT_STDERR_JSON_FILE_LOG_CONFIG)
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
    """Test operation of AT_QUEUED_STDERR_JSON_FILE_LOG_CONFIG logging config."""
    with caplog.at_level(logging.DEBUG):
        main(AT_QUEUED_STDERR_JSON_FILE_LOG_CONFIG)
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

def test_atlogging_setup(caplog) -> None:
    """Test the atlogging_setup function."""
    try:
        logger = logging.getLogger(AT_APP_NAME)
        logger.propagate = True        
        root_logger = logging.getLogger()
        # Initialize the logger from a logging configuration file.
        ln = AT_APP_NAME; cf = AT_STDERR_JSON_FILE_LOG_CONFIG; verbose = True
        atlogging_setup(cf)
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
        pytest.fail(f"atlogging_setup raised an exception: {str(e)}")
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
