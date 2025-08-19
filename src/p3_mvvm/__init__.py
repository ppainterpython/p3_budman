"""
p3_MVVM - a simple MVVM framework for Python.

MVVM - Model-View-ViewModel - is a design pattern framework for a
software application. Uses the concepts of Model, View, ViewModel, 
Command Processor and Data Context.

A lightweight Dependency Injection capability is provided but only within a
single process application without threading or asynchronous support. Uses
binding to link client objects to provider objects via abstract base classes as 
interfaces.
"""
__version__ = "0.2.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "p3_mvvm"
__description__ = "p3_MVVM - a simple MVVM framework for Python."
__license__ = "MIT"

from .model_binding_ABC import (
    Model_Binding
)
from .model_base_ABC import (
    Model_Base
)
from .data_context_binding import (
    DataContext_Binding
)
from .data_context_base_ABC import (
    DataContext_Base
)
from .data_context import (
    DataContext
)
from .command_processor_Binding import (
    CommandProcessor_Binding
)
from .command_processor_Base_ABC import (
    CommandProcessor_Base
)
from .command_processor import (
    # Classes
    CommandProcessor,
    # Functions
    create_CMD_OBJECT, 
    validate_cmd_key_with_name,
    validate_subcmd_key_with_name,
    create_CMD_RESULT_OBJECT,
    is_CMD_RESULT,
    create_CMD_RESULT_ERROR
)
from .mvvm_namespace import (
    # Types
    CMD_OBJECT_TYPE,
    CMD_RESULT_TYPE,
    # Constants
    CMD_KEY_SUFFIX,
    CK_CMD_NAME,
    CK_CMD_KEY,
    CK_SUBCMD_NAME,
    CK_SUBCMD_KEY,
    CK_CMD_EXEC_FUNC,
    CMD_RESULT_STATUS,
    CMD_RESULT_CONTENT_TYPE,
    CMD_RESULT_CONTENT,
    CMD_OBJECT_VALUE,
    CMD_STRING_OUTPUT,
    CMD_JSON_OUTPUT,
    CMD_WORKBOOK_INFO_TABLE,
    CMD_WORKBOOK_TREE_VIEW,
    CMD_FILE_TREE_VIEW,
    CMD_ERROR_STRING_OUTPUT
)
# target for 'from budman_app import *'
__all__ = [
    # Model
    "Model_Binding",
    "Model_Base",
    # Data Context
    "DataContext_Binding",
    "DataContext_Base",
    "DataContext",
    # Command Processor Types
    "CommandProcessor_Binding",
    "CommandProcessor_Base",
    "CommandProcessor",
    "CMD_OBJECT_TYPE",
    "CMD_RESULT_TYPE",
    # Command Processor Constants
    "CMD_KEY_SUFFIX",
    "CK_CMD_NAME",
    "CK_CMD_KEY",
    "CK_SUBCMD_NAME",
    "CK_SUBCMD_KEY",
    "CK_CMD_EXEC_FUNC",
    "CMD_RESULT_STATUS",
    "CMD_RESULT_CONTENT_TYPE",
    "CMD_RESULT_CONTENT",
    "create_CMD_OBJECT",
    "CMD_STRING_OUTPUT",
    "CMD_JSON_OUTPUT",
    "CMD_WORKBOOK_INFO_TABLE",
    "CMD_WORKBOOK_TREE_VIEW",
    "CMD_FILE_TREE_VIEW",
    "CMD_ERROR_STRING_OUTPUT",
    # Command Processor Functions
    "create_CMD_OBJECT",
    "validate_cmd_key_with_name",
    "validate_subcmd_key_with_name",
    "create_CMD_RESULT_OBJECT",
    "is_CMD_RESULT",
    "create_CMD_RESULT_ERROR"
]

