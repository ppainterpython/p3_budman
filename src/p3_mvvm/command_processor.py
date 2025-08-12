# ---------------------------------------------------------------------------- +
#region command_processor.py module
""" CommandProcessor class concrete implementation. 

    This module implements the CommandProcessor class, which is a concrete
    implementation of the CommandProcessor_Base abstract base class. It provides
    the necessary methods and properties to process commands in a p3_mvvm
    application.

    The CommandProcessor class is designed to be subclassed by applications to
    enable application-specific capability. With the p3_mvvm design pattern,
    access to a DataContext is a basic provision, either through inheritance or 
    binding.

    A critical aspect of the CommandProcessor is the CMD_OBJECT. Here, a 
    dictionary is used to contain the key attributes of a p3_mvvm command. A
    valid CMD_OBJECT may have a variable number of attributes, based on the
    need of the command. But, there are some required attributes and several
    common attributes which may be in any valid CMD_OBJECT. Constants are
    defined for these attribute keys and values, as appropriate. Note, these
    are the basic requirements used in the Command Processor for functional
    operation and are not specific to any application.

    Required CMD_OBJECT Attributes:
    - 'cmd_name': "name string"  The unique name of the command.
    - 'cmd_key': "key string"    A unique key for the command, derived from the
        command name by appending the CMD_KEY_SUFFIX, e.g., "_cmd".
    - 'cmd_exec_func': Callable  A callable function to execute the command.
        Constants:
            CMD_KEY_SUFFIX = "_cmd"
            CK_CMD_NAME = "cmd_name"
            CK_CMD_KEY = "cmd_key"
            CK_CMD_EXEC_FUNC = "cmd_exec_func"
        Notes: A cmd_key is constructed by appending the CMD_KEY_SUFFIX to
        the cmd_name. For example: cmd_name = 'list' has cmd_key = 'list_cmd'.

    Optional common CMD_OBJECT Attributes:
    - 'subcmd_name': "name string"  The name of a sub-command, if applicable.
    - 'subcmd_key': "key string"    A unique key for the sub-command, derived from
        the sub-command name by appending the CMD_KEY_SUFFIX, e.g., "_cmd".
        Constants:
            CK_SUBCMD_NAME = "subcmd_name"
            CK_SUBCMD_KEY = "subcmd_key"
        Notes: A subcmd_key is constructed by appending the CMD_KEY with
        underscore '_' and the subcmd_name. For example: cmd_key = 'list_cmd'
        and subcmd_name = 'workbooks' results in 
        subcmd_key = 'list_cmd_workbooks'.

"""
#endregion command_processor.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging
from typing import List, Type, Generator, Dict, Tuple, Any, Callable, Optional
# third-party modules and packages
from h11 import Data
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
from .command_processor_Base_ABC import CommandProcessor_Base
from .data_context_binding import DataContext_Binding
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals
# ---------------------------------------------------------------------------- +
#region Types and Constants
type CMD_OBJECT_TYPE = Dict[str, Any]
type CMD_RESULT_TYPE = Dict[str, Any]  # Command result dictionary

# All CMD_OBJECT required attributes
CMD_KEY_SUFFIX = "_cmd"
CK_CMD_NAME = "cmd_name"
"""Key for storing the command name value. All commands have a unique name."""
CK_CMD_KEY = "cmd_key"
"""Key storing a command key value based on the command name. A cmd_key value
is made by appending the CMD_KEY_SUFFIX to the command name str."""
CK_SUBCMD_NAME = "subcmd_name"
"""Optional key storing a subcmd name value. A subcmd is optional."""
CK_SUBCMD_KEY = "subcmd_key"
"""A key storing a subcmd key value, based on the cmd_key and subcmd_name. 
A subcmd_key is formed by appending the cmd_key with underscore and the 
subcmd_name."""
CK_CMD_EXEC_FUNC = "cmd_exec_func"
"""The cmd object key assigned the command execution function callable value."""
BASE_COMMAND_OBJECT_ATTRIBUTES = [
    CK_CMD_NAME, CK_CMD_KEY, CK_SUBCMD_NAME, CK_SUBCMD_KEY, CK_CMD_EXEC_FUNC
]
# CMD_RESULT dictionary key constants
CMD_RESULT_TYPE_KEY = "cmd_result_type"
CMD_RESULT_CONTENT_KEY = "cmd_result_content"
#endregion Types and Constants
# ---------------------------------------------------------------------------- +
#region CommandProcessor class
class CommandProcessor(CommandProcessor_Base, DataContext_Binding):
    #region CommandProcessor class doc string
    """Concrete Class for CommandProcessor_Base."""
    #endregion CommandProcessor class doc string
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        super().__init__()
        self._initialized : bool = False
        self._cp : Callable = None 
        self._cmd_map : Dict[str, Callable] = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Binding Properties
    @property
    def cp_cmd_map(self) -> Dict[str, Callable]:
        """Return the command map for the command processor."""
        return self._cmd_map
    @cp_cmd_map.setter
    def cp_cmd_map(self, value : Dict[str, Callable]) -> None:
        """Set the command map for the command processor."""
        if not isinstance(value, dict):
            raise ValueError("cp_cmd_map must be a dictionary.")
        self._cmd_map = value

    #endregion CommandProcessor_BindingProperties
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self, cp : Optional[Callable]) -> "CommandProcessor":
        """Initialize the CommandProcessor."""
        try:
            self.CP = cp
            self.initialized = True
            logger.debug(f"CommandProcessor initialized.")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #region cp_initialize_cmd_map() method
    def cp_initialize_cmd_map(self) -> None:
        """Initialize the CommandProcessor."""
        try:
            self.initialized = True
            logger.debug(f"CommandProcessor cmd_map initialized.")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #region cp_execute_cmd() method
    def cp_execute_cmd(self, cmd : Dict = None,
                       raise_error : bool = False) -> Tuple[bool, Any]:
        """Execute a command with the bound command processor.

        Pass the command request through to the command processor for
        execution. The command processor is a callable object within the 
        ViewModel.

        Arguments:
            cmd (Dict): The command to execute along with any arguments.
        
        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution.
        """
        try:
            return True, str(cmd)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            if raise_error:
                raise RuntimeError(m)
            return False, m
    #endregion cp_execute_cmd() method
#endregion CommandProcessor class
# ---------------------------------------------------------------------------- +

# --------------------------------------------------------------------------- +
#region CMD OBJECT functions
# ---------------------------------------------------------------------------- +
#region CMD_OBJECT()
def CMD_OBJECT(
    cmd_name: str = None,
    cmd_key: str = None,
    subcmd_name: str = None,
    subcmd_key: str = None,
    cmd_exec_func: Callable = None,
    other_attrs: Optional[Dict[str, Any]] = None
) -> CMD_OBJECT_TYPE:
    """Create a command object."""
    cmd_obj = {
        CK_CMD_NAME: cmd_name,
        CK_CMD_KEY: cmd_key,
        CK_SUBCMD_NAME: subcmd_name,
        CK_SUBCMD_KEY: subcmd_key,
        CK_CMD_EXEC_FUNC: cmd_exec_func
    }
    if other_attrs:
        # Perform non-destructive merge, adding keys from other_attrs not present
        # in cmd_obj.
        cmd_obj.update({k: v for k, v in other_attrs.items() if k not in cmd_obj})
    return cmd_obj.copy()
#endregion CMD_OBJECT()
# ---------------------------------------------------------------------------- +
#region validate_cmd_key_with_name() function
def validate_cmd_key_with_name(cmd_name: str, cmd_key: str) -> bool:
    if p3u.str_empty(cmd_name) or p3u.str_empty(cmd_key):
        return False
    return True if cmd_key == f"{cmd_name}{CMD_KEY_SUFFIX}" else False
#endregion validate_cmd_key_with_name() function
# ---------------------------------------------------------------------------- +
#region validate_subcmd_key_with_name() function
def validate_subcmd_key_with_name(subcmd_name: str, cmd_key: str, 
                                  subcmd_key: str) -> bool:
    if p3u.str_empty(subcmd_name) or p3u.str_empty(cmd_key) or p3u.str_empty(subcmd_key):
        return False
    return True if subcmd_key == f"{cmd_key}_{subcmd_name}" else False
#endregion validate_subcmd_key_with_name() function
# ---------------------------------------------------------------------------- +
#endregion CMD OBJECT functions
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region CMD_RESULT_OBJECT functions
# --------------------------------------------------------------------------- +
#region CMD_RESULT_OBJECT()
def CMD_RESULT_OBJECT(
    result_type: str = '',
    result_content: Any = None
) -> CMD_RESULT_TYPE:
    """Create a command result object."""
    cmd_result = {
        CMD_RESULT_TYPE_KEY: result_type,
        CMD_RESULT_CONTENT_KEY: result_content
    }
    return cmd_result.copy() 
# ---------------------------------------------------------------------------- +
#region is_CMD_RESULT() function
def is_CMD_RESULT(cmd_result: Any) -> bool:
    """Check if the cmd_result parameter is a valid command result."""
    if isinstance(cmd_result, dict):
        return CMD_RESULT_TYPE_KEY in cmd_result and CMD_RESULT_CONTENT_KEY  in cmd_result
    return False
#endregion is_CMD_RESULT() function
# ---------------------------------------------------------------------------- +
#region CMD_RESULT_OBJECT functions
# ---------------------------------------------------------------------------- +