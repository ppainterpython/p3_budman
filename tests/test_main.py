#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
import logging, pytest
from main import *

#------------------------------------------------------------------------------+
def test_main(caplog) -> None:
    """Test function to demonstrate logging an exception."""
    with pytest.raises(ZeroDivisionError):
        testickle_logger_exception_message()
    assert "division by zero" in caplog.text, \
        "Expected 'division by zero' in log output"
    assert len(caplog.records) == 1

def test_atlogging_setup(caplog) -> None:
    """Test the atlogging_setup function."""
    try:
        logger = logging.getLogger(AT_APP_NAME)
        logger.propagate = True        
        root_logger = logging.getLogger()
        # Initialize the logger from a logging configuration file.
        ln = AT_APP_NAME; cf = AT_STDERR_JSON_FILE_LOG_CONFIG; verbose = True
        atlogging_setup(ln, cf, verbose)
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message for testing")
            logger.info("Info message for testing")
            logger.warning("Warning message for testing")
        assert "Warning message" in caplog.text, \
            "Expected 'Warning message' in log output"
        assert "Debug message" in caplog.text, \
            "Expected 'Debug message' in log output"
        assert "Info message" in caplog.text, \
            "Expected 'Info message' in log output"
        assert logger is not None, "Logger should be initialized"
        assert root_logger.level == logging.DEBUG, "Logger level should be DEBUG"
    except Exception as e:
        pytest.fail(f"atlogging_setup raised an exception: {str(e)}")
