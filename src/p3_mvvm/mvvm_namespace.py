# ---------------------------------------------------------------------------- +
#region mvvm_namespace.py module
""" mvvm_namespace.py defines symbol constants for the p3_mvvm package."""
#endregion mvvm_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from typing import List, Type, Generator, Dict, Tuple, Any, Callable, Optional

# third-party modules and packages

# local modules and packages

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants

# The namespace is used as a centralized place to define symbol constants used
# throughout an application applying the p3_mvvm capabilities.

# ---------------------------------------------------------------------------- +
#region Global Constants for p3_mvvm Command Processor pattern.
# The Command Processor capability uses dictionaries to implement 
# a CMD_OBJECT constructed by client modules or an application to represent
# commands to be executed somewhere in the application modules. This design
# anticipates that modules in the front-end of an application create CMD_OBJECTs
# and pass them to service modules in the application to perform 
# application-specific actions based on the attributes in the CMD_OBJECT. 
 
# The p3_mvvm Command Processor pattern enables a basic framework of interfaces 
# and data models to support these capabilities as base classes upon which 
# application-specific commands are constructed.

# In essence, a CMD_OBJECT is constructed, validated, and then executed
# returning a CMD_RESULT dictionary.

type CMD_OBJECT_TYPE = Dict[str, Any]  # type hint for a CMD_OBJECT dictionary.
type CMD_RESULT_TYPE = Dict[str, Any]  # type hint for a CMD_RESULT dictionary.
type CMD_ARGS_TYPE = Dict[str, Any]    # type hint for command arguments dict.
# ---------------------------------------------------------------------------- +
# A CMD_OBJECT dictionary has keys and values per basic Python. 
# Naming Convention for Constants: 
#    "CK_" - CommandKey - prefix attribute key names in a command object dict. 
#    "CV_" - CommandValue - prefixes attribute values used as predefined 
#            values in a command object dict. 
# A CV_ CommandValue name is a predefined value. Of course, not all 
# CommandValues are predefined. There may be CV_ values that are values entered 
# by client code, such as in a user interface entered dynamically from 
# user input.
# 
# Required CMD_OBJECT attributes:
CMD_KEY_SUFFIX = "_cmd"
CK_CMD_NAME = "cmd_name"
"""Key for storing the command name value. All commands have a unique name."""
CK_CMD_KEY = "cmd_key"
"""Key storing a command key value based on the command name. A cmd_key value
is made by appending the CMD_KEY_SUFFIX to the command name str."""
CK_CMD_EXEC_FUNC = "cmd_exec_func"
"""The cmd object key assigned the command execution function callable value."""
REQUIRED_CMD_OBJECT_KEYS = [
    CK_CMD_NAME, CK_CMD_KEY, CK_CMD_EXEC_FUNC
]
# Optional CMD_OBJECT attributes:
# Commands may have a sub-command, a second part which the command processor 
# can use when dispatching the EXEC_FUNC via the cmd_map. An EXEC_FUNCTION 
# can be bound to a cmd_key or a subcmd_key. When no CK_SUBCMD_KEY is bound in 
# the cmd_map, the EXEC_FUNC is bound to the cmd_key. When a CK_SUBCMD_KEY is 
# bound in the cmd_map, the EXEC_FUNC is called directly.
CK_SUBCMD_NAME = "subcmd_name"
"""Optional key storing a subcmd name value. A subcmd is optional."""
CK_SUBCMD_KEY = "subcmd_key"
"""A key storing a subcmd key value, based on the cmd_key and subcmd_name. 
A subcmd_key is formed by appending the cmd_key with underscore and the 
subcmd_name."""
BASE_COMMAND_OBJECT_KEYS = [
    CK_CMD_NAME, CK_CMD_KEY, CK_SUBCMD_NAME, CK_SUBCMD_KEY, CK_CMD_EXEC_FUNC
]
# Builtin CK_CMD_KEY and CK_CMD_NAME values.
CV_P3_UNKNOWN_CMD_NAME = "p3_unknown"
CV_P3_UNKNOWN_CMD_KEY = CV_P3_UNKNOWN_CMD_NAME + CMD_KEY_SUFFIX
# Builtin command parameter support:
# CommandProcessor supports these cmd options inherently.
CK_PARSE_ONLY = "parse_only"
CK_VALIDATE_ONLY = "validate_only"
CK_WHAT_IF = "what_if"

# ---------------------------------------------------------------------------- +
# CMD_RESULT_OBJECT dictionary key constants
CMD_RESULT_STATUS = "cmd_result_status"
CMD_RESULT_CONTENT_TYPE = "cmd_result_content_type"
CMD_RESULT_CONTENT = "cmd_result_content"
CMD_OBJECT_VALUE = "cmd_object_value"
REQUIRED_CMD_RESULT_KEYS = [
    CMD_RESULT_STATUS, CMD_RESULT_CONTENT_TYPE, CMD_RESULT_CONTENT,
    CMD_OBJECT_VALUE
]
# CMD_RESULT_CONTENT_TYPE values
# CMD_TREE_OBJECT is a treeblib.Tree object.
CMD_STRING_OUTPUT = "string_output"
CMD_JSON_OUTPUT = "json_output"
CMD_TREE_OBJECT = "tree_object"
CMD_WORKBOOK_INFO_TABLE = "workbook_info_table_output"
CMD_WORKBOOK_TREE_OBJECT = "workbook_tree_object"
CMD_FILE_TREE_OBJECT = "file_tree_object"
CMD_ERROR_STRING_OUTPUT = "error_string_output"
#endregion Types and Constants
