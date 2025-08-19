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
    - 'cmd_exec_func': Callable  A callable function to execute the sub-command.

    Command_Processor provides a general purpost CMD_RESULT dictionary returned
    by a command or sub-command EXEC_FUNC. The CMD_RESULT dictionary
    contains the following keys:
    - 'cmd_result_status': bool  The status of the command execution, True if
        successful, False if an error occurred.
    - 'cmd_result_content_type': str A symbol reflecting the type of the result
      returned by the command. This will be application function specific for
      each command implemented.
    - 'cmd_result_content': Any  The content returned by the command execution. 
      If cmd_result_success is True, this can be any type of object. If False,
      this is typically a string error message.
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
from .mvvm_namespace import *
from .command_processor_Base_ABC import CommandProcessor_Base
from .data_context_binding import DataContext_Binding
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals
# ---------------------------------------------------------------------------- +
#region CommandProcessor class
class CommandProcessor(CommandProcessor_Base, DataContext_Binding):
    # ------------------------------------------------------------------------ +
    #region CommandProcessor class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +
    #region CommandProcessor class doc string
    """Concrete Class for CommandProcessor_Base."""
    #endregion CommandProcessor class doc string
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        self._initialized : bool = False
        self._cmd_map : Dict[str, Callable] = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #endregion CommandProcessor class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Base Properties
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
    #endregion CommandProcessor_Base Properties
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Base Methods
    # ------------------------------------------------------------------------ +
    #region cp_initialize() method
    def cp_initialize(self) -> "CommandProcessor":
        """Initialize the CommandProcessor."""
        try:
            self.cp_initialize_cmd_map()
            self.initialized = True
            logger.debug(f"CommandProcessor initialized.")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize() method
    # ------------------------------------------------------------------------ +
    #region cp_initialize_cmd_map() method
    def cp_initialize_cmd_map(self) -> None:
        """Application-specific: Initialize the cp_cmd_map."""
        try:
            self.cp_cmd_map = {}
            logger.debug(f"CommandProcessor cmd_map initialized.")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #region cp_execute_cmd() method
    def cp_execute_cmd(self, cmd : Dict = None,
                       raise_error : bool = False) -> CMD_RESULT_TYPE:
        """Execute a command within the command processor.

        Pass the command request through to the command processor for
        execution. 

        Arguments:
            cmd (Dict): The command to execute along with any arguments.
        
        Returns:
            CMD_RESULT_TYPE: The outcome of the command 
            execution.
        """
        try:
            st = p3u.start_timer()
            logger.info(f"Start Command: {cmd}")
            success, result = self.cp_validate_cmd(cmd)
            if not success: return success, result
            # if cp_validate_cmd() is good, continue.
            exec_func: Callable = cmd[CK_CMD_EXEC_FUNC]
            function_name = exec_func.__name__
            # validate_only: bool = self.cp_cmd_attr_get(cmd, cp.CK_VALIDATE_ONLY)
            # if validate_only:
            #     result = f"vo-command: {function_name}({str(cmd)})"
            #     logger.info(result)
            #     return True, result
            logger.info(f"Executing command: {function_name}({str(cmd)})")
            # Execute a cmd with its associated exec_func from the cmd_map.
            cmd_result: CMD_RESULT_TYPE = exec_func(cmd)
            # status, result = self.cp_cmd_map.get(full_cmd_key)(cmd)
            logger.info(f"Complete Command: [{p3u.stop_timer(st)}] "
                        f"{(cmd_result[CMD_RESULT_STATUS])}")
            return cmd_result
        except Exception as e:
            cmd_result = create_CMD_RESULT_ERROR(cmd, e)
            if raise_error:
                raise RuntimeError(cmd_result[CMD_RESULT_CONTENT]) from e
            return cmd_result
    #endregion cp_execute_cmd() method
    # ------------------------------------------------------------------------ +
    #endregion Command_Processor_Base Methods
    # ------------------------------------------------------------------------ +
#endregion CommandProcessor class
# ---------------------------------------------------------------------------- +

# --------------------------------------------------------------------------- +
#region CMD_OBJECT functions
# ---------------------------------------------------------------------------- +
#region create_CMD_OBJECT()
def create_CMD_OBJECT(
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
#endregion create_CMD_OBJECT()
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
#endregion CMD_OBJECT functions
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region CMD_RESULT_OBJECT functions
# --------------------------------------------------------------------------- +
#region create_CMD_RESULT_OBJECT()
def create_CMD_RESULT_OBJECT(
    cmd_result_status: bool = False,
    result_content_type: str = '',
    result_content: Optional[Any] = None,
    cmd_object: Optional[CMD_OBJECT_TYPE] = None
) -> CMD_RESULT_TYPE:
    """Construct a CMD_RESULT_OBJECT from input parameters."""
    cmd_result = {
        CMD_RESULT_STATUS: cmd_result_status,
        CMD_RESULT_CONTENT_TYPE: result_content_type,
        CMD_RESULT_CONTENT: result_content,
        CMD_OBJECT_VALUE: cmd_object
    }
    return cmd_result.copy() 
#endregion create_CMD_RESULT_OBJECT()
# ---------------------------------------------------------------------------- +
#region is_CMD_RESULT() function
def is_CMD_RESULT(cmd_result: Any) -> bool:
    """Check if the cmd_result parameter is a valid command result."""
    if isinstance(cmd_result, dict):
        return (CMD_RESULT_CONTENT_TYPE in cmd_result and  
                CMD_RESULT_CONTENT in cmd_result and 
                CMD_RESULT_STATUS in cmd_result)
    return False
#endregion is_CMD_RESULT() function
# ---------------------------------------------------------------------------- +
#region create_CMD_RESULT_ERROR() function
def create_CMD_RESULT_ERROR(cmd: CMD_OBJECT_TYPE, e: Exception) -> CMD_RESULT_TYPE:
    """Construct a CMD_RESULT_ERROR from input parameters."""
    m = p3u.exc_err_msg(e)
    logger.error(m)
    cmd_result = {
        CMD_RESULT_STATUS: False,
        CMD_RESULT_CONTENT_TYPE: CMD_ERROR_STRING_OUTPUT,
        CMD_RESULT_CONTENT: m,
        CMD_OBJECT_VALUE: cmd
    }
    return cmd_result.copy()
#endregion create_CMD_RESULT_ERROR() function
# ---------------------------------------------------------------------------- +
#endregion CMD_RESULT_OBJECT functions
# ---------------------------------------------------------------------------- +