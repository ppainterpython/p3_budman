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
#region Global Constants for p3_mvvm Command Processor pattern.
# The Command Processor capability uses dictionaries to implement 
# Command Objects constructed by client modules or an application to represent
# commands to be executed other application modules. In general, this design
# anticipates that modules in the front-end of an application create command
# objects and send them to service modules in the application to perform
# actions implied by the command object design and content. It will be very
# application-specific. The p3_mvvm Command Processor pattern enables a basic
# framework of interfaces and data models to support these capabilities as base
# classes upon which application-specific commands are constructed.
# 
# The namespace is used as a centralized place to define symbol constancts used
# throughout an application applying the capabilities.
# 
# A Command Object Dictionary has keys and values per basic Python. Constants 
# defined here use a naming convention. "CK_" prefixes attribute keys used as 
# Command Key attributes in a command object dictionary. "CV_" prefixes attribute
# values used as Command Value attributes in a command object dictionary. 
# A Command Value name here with a CV_ constant is a predefined value. There may 
# also be values entered by client code, such as in a user interface, derived
# dynamically from user input, hence, will not have a CV_ constant.
# 
type CMD_OBJECT_TYPE = Dict[str, Any]
type CMD_RESULT_TYPE = Dict[str, Any]  # Command result dictionary
# ---------------------------------------------------------------------------- +


# All CMD_OBJECT required attributes
CMD_KEY_SUFFIX = "_cmd"
CK_CMD_NAME = "cmd_name"
"""Key for storing the command name value. All commands have a unique name."""
CK_CMD_KEY = "cmd_key"
"""Key storing a command key value based on the command name. A cmd_key value
is made by appending the CMD_KEY_SUFFIX to the command name str."""
CK_CMD_EXEC_FUNC = "cmd_exec_func"
"""The cmd object key assigned the command execution function callable value."""
# Optional CMD_OBJECT SUBCMD attributes - many commands have a sub-command
# second part which the command processor can use when dispatching the EXEC_FUNC
# via the cmd_map. An EXEC_FUNCTION can be bound to a cmd_key or a subcmd_key.
# When no CK_SUBCMD_KEY is bound in the cmd_map, the EXEC_FUNC is bound
# to the cmd_key and it will handled further sub-processing directly. When a
# CK_SUBCMD_KEY is bound in the cmd_map, the EXEC_FUNC will be called to process
# the sub-command directly.
CK_SUBCMD_NAME = "subcmd_name"
"""Optional key storing a subcmd name value. A subcmd is optional."""
CK_SUBCMD_KEY = "subcmd_key"
"""A key storing a subcmd key value, based on the cmd_key and subcmd_name. 
A subcmd_key is formed by appending the cmd_key with underscore and the 
subcmd_name."""
BASE_COMMAND_OBJECT_ATTRIBUTES = [
    CK_CMD_NAME, CK_CMD_KEY, CK_SUBCMD_NAME, CK_SUBCMD_KEY, CK_CMD_EXEC_FUNC
]
# CMD_RESULT_OBJECT dictionary key constants
CMD_RESULT_STATUS = "cmd_result_status"
CMD_RESULT_CONTENT_TYPE = "cmd_result_content_type"
CMD_RESULT_CONTENT = "cmd_result_content"
CMD_OBJECT_VALUE = "cmd_object_value"
# CMD_RESULT_CONTENT_TYPE values
CMD_STRING_OUTPUT = "string_output"
CMD_JSON_OUTPUT = "json_output"
CMD_WORKBOOK_INFO_TABLE = "workbook_info_table_output"
CMD_WORKBOOK_TREE_VIEW = "workbook_tree_view_output"
CMD_FILE_TREE_VIEW = "file_tree_view_output"
CMD_ERROR_STRING_OUTPUT = "error_string_output"
#endregion Types and Constants
