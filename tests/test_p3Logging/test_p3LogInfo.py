# ---------------------------------------------------------------------------- +
# test_p3LogInfo.py
# ---------------------------------------------------------------------------- +
# python standard libraries
import logging, pytest

# third-party libraries
import inspect, pyjson5

# local libraries
import p3Logging as p3l

THIS_APP_NAME = "Test_p3LogInfo"

root_logger = logging.getLogger()
logger = logging.getLogger(THIS_APP_NAME)
logger.propagate = True
# ---------------------------------------------------------------------------- +
#region Tests for p3LogConfig.get_Logger_config_info() function
# ---------------------------------------------------------------------------- +
#region test_get_logger_info() function
def test_get_Logger_config_info_STDOUT_LOG_CONFIG_FILE():
    config_file: str = p3l.STDOUT_LOG_CONFIG_FILE
    # Initialize the logger from a logging configuration file.
    # Apply the logging configuration from config_file
    p3l.setup_logging(config_file,start_queue=False)
    # Invoke get_logger_info() to display the current logging setup
    res = p3l.get_Logger_config_info(indent = 0)
    # captured = capsys.readouterr()
    assert res is not None, \
        "Expected get_Logger_config_info() to return a non-None value"
    assert isinstance(res, str) and len(res) > 0, \
        "Expected get_Logger_config_info() to return a non-zero str"
    
#endregion test_get_logger_info() function
# ---------------------------------------------------------------------------- +
#region test_get_logger_info() function
def test_get_Logger_config_None_Input():
    config_file: str = None
    # Initialize the logger from a logging configuration file.
    # Apply the logging configuration from config_file
    p3l.setup_logging(config_file,start_queue=False)
    # Invoke get_logger_info() to display the current logging setup
    res = p3l.get_Logger_config_info(log_configDict=config_file)
    # captured = capsys.readouterr()
    assert res is not None, \
        "Expected get_Logger_config_info() to return a non-None value"
    assert isinstance(res, str) and len(res) > 0, \
        "Expected get_Logger_config_info() to return a non-zero str"
    
#endregion test_get_logger_info() function
# ---------------------------------------------------------------------------- +

#endregion Tests for p3LogConfig.get_Logger_config_info() function
# ---------------------------------------------------------------------------- +
#region Tests for p3LogConfig.get_Logger_root_config_info() function
# ---------------------------------------------------------------------------- +
#region test_get_Logger_root_config_info() function
def test_get_Logger_root_config_info():
    config_file: str = p3l.STDOUT_LOG_CONFIG_FILE
    cfm = f"Config file: '{config_file}'"
    # Initialize the logger from a logging configuration file.
    # Apply the logging configuration from config_file
    p3l.setup_logging(config_file,start_queue=False)
    # Invoke get_logger_info() to display the current logging setup
    log_config = p3l.get_configDict()
    assert log_config is not None, \
        "Expected get_configDict() to return a non-None value"
    assert isinstance(log_config, dict) and len(log_config) > 0, \
        "Expected get_configDict() to return a non-zero dict"
    assert "root" in log_config, \
        "Expected get_configDict() to contain 'root' key"
    res = p3l.get_Logger_root_config_info(log_config['root'])
    assert res is not None, \
        "Expected get_root_Logger_config_info() to return a non-None value"
    assert isinstance(res, str) and len(res) > 0, \
        "Expected get_root_Logger_config_info() to return a non-zero str"
    assert "root config[" in res, \
        "Expected get_root_Logger_config_info() to contain 'root config['"
    # captured = capsys.readouterr() root config[
    
#endregion test_get_Logger_root_config_info() function
# ---------------------------------------------------------------------------- +
#region test_get_Logger_root_config_info_None() function
def test_get_Logger_root_config_info_None():
    res = p3l.get_Logger_root_config_info(root_log_configDict=None)
    assert (isinstance(res, str) and len(res) == 0), \
        "Expected empty string result for 'None' input to root_log_configDict"
#endregion test_get_Logger_root_config_info_None() function
# ---------------------------------------------------------------------------- +
#region test_get_Logger_root_config_info_wrong_type() function
def test_get_Logger_root_config_info_wrong_type():
    with pytest.raises(TypeError) as excinfo:
        p3l.get_Logger_root_config_info(root_log_configDict=101)
        
    expected_msg = "Invalid root_log_configDict: type:'int' value = '101'"
    assert expected_msg in str(excinfo.value), \
        "Expected ValueError for None root_log_configDict"
#endregion test_get_Logger_root_config_info_wrong_type() function
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
#endregion Tests for p3LogConfig.get_Logger_root_config_info() function
# ---------------------------------------------------------------------------- +
if __name__ == "__main__":
    try:
        test_get_logger_info_one_line_STDOUT_LOG_CONFIG_FILE()
        test_get_logger_info_showall_STDOUT_LOG_CONFIG_FILE()
    except Exception as e:
        print(str(e))
        exit(1)
# ---------------------------------------------------------------------------- +
