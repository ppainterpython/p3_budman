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
            self.cp_cmd_map = {
                CV_P3_UNKNOWN_CMD_KEY: self.UNKNOWN_cmd
            }
            logger.debug(f"CommandProcessor cmd_map initialized.")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #region cp_execute_cmd() method
    def cp_execute_cmd(self, cmd : CMD_OBJECT_TYPE = None,
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
            cmd_result: CMD_RESULT_TYPE = self.cp_validate_cmd(cmd)
            if not cmd_result[CMD_RESULT_STATUS]: return cmd_result
            # if cp_validate_cmd() is good, continue.
            exec_func: Callable = cmd[CK_CMD_EXEC_FUNC]
            function_name = exec_func.__name__
            validate_only: bool = self.cp_cmd_attr_get(cmd, CK_VALIDATE_ONLY)
            if validate_only:
                result = f"vo-command: {function_name}({str(cmd)})"
                logger.info(result)
                return True, result
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
    #region cp_validate_cmd() method
    def cp_validate_cmd(self, 
                        cmd : CMD_OBJECT_TYPE = None,
                        validate_all : bool = False) -> CMD_RESULT_TYPE:
        """Validate the CMD_OBJECT for cmd_key and parameters.

        Override this method to provide application-specific validation logic.
        This base implementation checks if the CMD_OBJECT is valid and
        returns a CMD_RESULT_TYPE indicating the validation result.

        Arguments:
            cmd (Dict): A candidate Command object to validate.
            validate_all (bool): If True, validate all attributes in the cmd.

        Returns:
            CMD_RESULT_TYPE: The result of the validation.
        """
        try:
            if not self.cp_validate_cmd_object(cmd, raise_error=False):
                return create_CMD_RESULT_ERROR(cmd, "Invalid command object.")
            # Additional validation logic can be added here.
            return create_CMD_RESULT_OBJECT(cmd_result_status=True,
                                            result_content_type="validation",
                                            result_content="Command is valid.",
                                            cmd_object=cmd)
        except Exception as e:
            return create_CMD_RESULT_ERROR(cmd, e)
    #endregion cp_validate_cmd() method
    #region    cp_validate_cmd_object() Command Processor method
    def cp_validate_cmd_object(self, 
                               cmd : CMD_OBJECT_TYPE = None,
                               raise_error:bool=False) -> bool:
        """Validate Command Processor is initialized and the CMD_OBJECT is valid.

        Validation rules are:
          1. CommandProcessor is initialized, i.e., self.initialized is True.
          2. cmd is a CMD_OBJECT_TYPE, not None and not empty.
          3. cmd contains mandatory CK_CMD_KEY. There may be an 
             optional CK_SUBCMD_KEY, but it is not required.

        Arguments:
            cmd (CMD_OBJECT_TYPE): A candidate CMD_OBJECT to validate.
            raise_error (bool): If True, raise any errors encountered. 

        returns:
            bool: True if validation rules are satisfied, False otherwise.

        Raise:
            RuntimeError: If raise_error is True, a RunTimeError is raised 
            with an error message.
        """
        # Primary Concern: Validate the CMD_OBJECT is ready for parameter
        # validation. See doc string for validation rules.
        try:
            pfx = f"{self.__class__.__name__}.{self.cp_validate_cmd_object.__name__}: "
            logger.debug(f"Before Validating CMD_OBJECT: {str(cmd)}")
            if not self.initialized:
                m = f"Command Processor is not initialized."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                cmd_type = type(cmd).__name__
                m = f"Invalid CMD_OBJECT type: '{cmd_type}', no action taken."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if not is_CMD_OBJECT(cmd):
                m = f"No action taken, invalid CMD_OBJECT[{str(cmd)}]."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if len(cmd) == 0:
                m = f"CMD_OBJECT is empty, no action taken."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            # Examine the CMD_OBJECT for the required cmd values.
            success : bool = False
            cmd_exec_func : Callable = None
            # Check for the current cmd keys.
            cmd_key:str = cmd.get(CK_CMD_KEY, None)
            if not p3u.str_notempty(cmd_key):
                m = f"CMD_OBJECT is missing required key '{CK_CMD_KEY}'."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            cmd_name:str = cmd.get(CK_CMD_NAME, None)
            subcmd_name:str = cmd.get(CK_SUBCMD_NAME, None)
            subcmd_key:str = cmd.get(CK_SUBCMD_KEY, None)
            # Bind the command execution function, using subcmd_key first,
            # then cmd_key, then the UNKNOWN_cmd function.
            if subcmd_key:
                cmd_exec_func = self.cp_exec_func_binding(subcmd_key, None)
            if cmd_key and cmd_exec_func is None:
                cmd_exec_func = self.cp_exec_func_binding(cmd_key, self.UNKNOWN_cmd)
            # Set the command key CK_CMD_EXEC_FUNC in the CMD_OBJECT.
            cmd[CK_CMD_EXEC_FUNC] = cmd_exec_func
            logger.debug(f"Success validating CMD_OBJECT: {str(cmd)}")
            return True
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_validate_cmd_object() Command Processor method
    #region    cp_exec_func_binding() Command Processor method
    def cp_exec_func_binding(self, cmd_key : str, default:Callable) -> Callable:
        """Get the command function for a given command key.

        This method retrieves the CMD_EXEC_FUNC from the CommandProcessor's
        command map (cp_cmd_map) using the provided command key. If the command
        key is not found, and a default function is provided, it returns that
        function. Otherwise, it returns None.

        Arguments:
            cmd_key (str): The command key to look up in the command map.

        Returns:
            Callable: The function associated with the command key, or a 
            provided default function if the key is not found.
        """
        if not p3u.str_notempty(cmd_key):
            raise ValueError("cmd_key must be a non-empty string.")
        if self.cp_cmd_map is None:
            raise ValueError("cp_cmd_map must be initialized.")
        exec_func : Callable = self.cp_cmd_map.get(cmd_key, None)
        if exec_func is None:
            # If no exec_func found, use the provided default function or None.
            exec_func = default if default else None
        return exec_func
    #endregion cp_exec_func_binding() Command Processor method
    #region    cp_cmd_attr_get() Command Processor method
    def cp_cmd_attr_get(self, cmd: Dict,
                       key_name: str, default_value: Any = None) -> Any:
        """Use cmd attr key_name to get value or return default."""                  
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")    
        if not isinstance(key_name, str):
            raise TypeError("arg_name must be a string.")
        if key_name not in cmd:
            return default_value
        value = cmd.get(key_name, default_value)
        if value is None:
            return default_value
        return value
    #endregion cp_cmd_attr_get() Command Processor method
    #region    cp_cmd_attr_set() Command Processor method
    def cp_cmd_attr_set(self, cmd: Dict,
                       arg_name: str, value: Any) -> None:
        """Set a command argument value in the cmd dictionary."""
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")
        if not isinstance(arg_name, str):
            raise TypeError("arg_name must be a string.")
        # if arg_name not in cp.BUDMAN_VALID_CK_ATTRS:
        #     raise ValueError(f"Command argument '{arg_name}' is not a valid "
        #                      f"BudMan command argument. Valid arguments are: "
        #                      f"{cp.BUDMAN_VALID_CK_ATTRS}")
        if not isinstance(value, (str, int, float, bool, type(None))):
            raise TypeError(f"Command argument '{arg_name}' must be a string, "
                            f"int, float, or bool, not {type(value)}.")
        # Set the value in the cmd dictionary.
        cmd[arg_name] = value
    #endregion cp_cmd_attr_set() Command Processor method
    #endregion Command_Processor_Base Methods
    # ------------------------------------------------------------------------ +
    #region UNKNOWN_cmd() 
    def UNKNOWN_cmd(self, cmd : Dict) -> CMD_RESULT_TYPE:
        """A cmd received that is not found in the current cmd map.

        This is an error handling command to fall back too when
        the CommandProcessor cannot find a valid EXEC_FUNC for a cmd_key in the 
        cmd_map.

        Arguments:
            cmd (Dict): A CMD_OBJECT object. 

        Returns:
            CMD_RESULT_TYPE: 
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.info(f"Start: ...")
            func_name = self.UNKNOWN_cmd.__name__
            result = f"{func_name}(): Received unknown CMD_OBJECT: {str(cmd)})"
            logger.warning(result)
            return create_CMD_RESULT_OBJECT(False, 
                                           result_content_type=CMD_ERROR_STRING_OUTPUT,
                                           result_content=result,
                                           cmd_object=cmd)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion UNKNOWN_cmd() method
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
    cmd_exec_func: Callable = None,
    subcmd_name: str = None,
    subcmd_key: str = None,
    other_attrs: Optional[Dict[str, Any]] = None
) -> CMD_OBJECT_TYPE:
    """Create a command object."""
    cmd_obj = {
        CK_CMD_NAME: cmd_name,
        CK_CMD_KEY: cmd_key,
        CK_CMD_EXEC_FUNC: cmd_exec_func,
        CK_SUBCMD_NAME: subcmd_name,
        CK_SUBCMD_KEY: subcmd_key
    }
    if other_attrs:
        # Perform non-destructive merge, adding keys from other_attrs not present
        # in cmd_obj.
        cmd_obj.update({k: v for k, v in other_attrs.items() if k not in cmd_obj})
    return cmd_obj.copy()
#endregion create_CMD_OBJECT()
# ---------------------------------------------------------------------------- +
#region is_CMD_OBJECT() function
def is_CMD_OBJECT(cmd_object: Any) -> bool:
    """Check if the cmd_object parameter is a valid command object."""
    if (isinstance(cmd_object, dict) and
        all(k in cmd_object for k in REQUIRED_CMD_OBJECT_KEYS)):
        return True
    return False
#endregion is_CMD_RESULT() function
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
    if (isinstance(cmd_result, dict) and
        all(k in cmd_result for k in REQUIRED_CMD_RESULT_KEYS)):
        return True
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