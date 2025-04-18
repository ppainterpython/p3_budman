#------------------------------------------------------------------------------+
# test_main.py
#------------------------------------------------------------------------------+
import logging, pytest

import p3Logging as p3l
from main import THIS_APP_NAME, main

#------------------------------------------------------------------------------+
def test_logging_setup() -> None:
    """Test operation of logging config."""
    assert p3l.quick_logging_test(
        THIS_APP_NAME, 
        p3l.STDERR_JSON_FILE_LOG_CONFIG_FILE)        
    
#------------------------------------------------------------------------------+
