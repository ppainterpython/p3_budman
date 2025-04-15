# ---------------------------------------------------------------------------- +
# test_p3LogInfo.py
# ---------------------------------------------------------------------------- +
# python standard libraries
import atexit, pathlib, logging, inspect, logging.config  #, logging.handlers

# third-party libraries
import inspect, pyjson5

# local libraries
import p3Logging as p3l

THIS_APP_NAME = "Test_p3LogInfo"

root_logger = logging.getLogger()
logger = logging.getLogger(THIS_APP_NAME)
logger.propagate = True

# ---------------------------------------------------------------------------- +
#region test_get_logger_info() function
def test_get_Logger_config_info_STDOUT_LOG_CONFIG_FILE():
    config_file: str = p3l.STDOUT_LOG_CONFIG_FILE
    cfm = f"Config file: '{config_file}'"
    # Initialize the logger from a logging configuration file.
    # Apply the logging configuration from config_file
    p3l.setup_logging(config_file,start_queue=False)
    # Invoke get_logger_info() to display the current logging setup
    res = p3l.get_Logger_config_info(indent = 0)
    assert res is not None, \
        "Expected get_logger_info() to return a non-None value"
    assert isinstance(res, str) and len(res) > 0, \
        "Expected get_logger_info() to return a non-zero str"
    
#endregion test_get_logger_info() function
# ---------------------------------------------------------------------------- +
#region test_get_logger_info() function
def test_get_logger_info_showall_STDOUT_LOG_CONFIG_FILE():
    config_file: str = p3l.STDOUT_LOG_CONFIG_FILE
    cfm = f"Config file: '{config_file}'"
    # Initialize the logger from a logging configuration file.
    # Apply the logging configuration from config_file
    p3l.setup_logging(config_file,start_queue=False)
    # Invoke get_logger_info() to display the current logging setup
    res = p3l.get_logger_info(logging.getLogger(), 0, showall=True)
    assert res is not None, \
        "Expected get_logger_info() to return a non-None value"
    assert isinstance(res, str) and len(res) > 0, \
        "Expected get_logger_info() to return a non-zero str"
    
#endregion test_get_logger_info() function
# ---------------------------------------------------------------------------- +
#region test_get_logger_info_one_line() function
def test_get_logger_info_one_line_STDOUT_LOG_CONFIG_FILE():
    config_file: str = p3l.STDOUT_LOG_CONFIG_FILE
    cfm = f"Config file: '{config_file}'"
    # Initialize the logger from a logging configuration file.
    # Apply the logging configuration from config_file
    p3l.setup_logging(config_file,start_queue=False)
    # Invoke get_logger_info() to display the current logging setup
    res = p3l.get_logger_info(logging.getLogger(), 0, showall=False)
    assert res is not None, \
        "Expected get_logger_info() to return a non-None value"
    assert isinstance(res, str) and len(res) > 0, \
        "Expected get_logger_info() to return a non-zero str"
    
#endregion test_get_logger_info_one_line() function
# ---------------------------------------------------------------------------- +
if __name__ == "__main__":
    try:
        test_get_logger_info_one_line_STDOUT_LOG_CONFIG_FILE()
        test_get_logger_info_showall_STDOUT_LOG_CONFIG_FILE()
    except Exception as e:
        print(str(e))
        exit(1)
# ---------------------------------------------------------------------------- +
