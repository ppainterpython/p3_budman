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

    Command_Processor supports builtin parameter flags which can be added to any
    cmd string or possibly set as flags affecting all cmds.
    - parse_only: bool - If True, the command will only be parsed, the resulting
    attributes are displayed, but the cmd is not executed. WHen parse_only 
    is used, the cp_execute_cmd() method will construct a CMD_RESULT_TYPE object
    with a simple string out showing the content of the CMD_OBJECT_TYPE object
    and return it prior to any other actions in the Command_Processor
    pipeline interface.
    - validate_only : bool - If True, the command will be fully validated, but 
    not executed. The cmd parameters with possible validation messages is 
    displayed. Command_Processor pipeline stops after calling the 
    cp_validate_cmd_object() method in the Command_Processor pipeline interface.
    - what_if : bool - If True, the command will be executed in a "what if"
    mode, where the effects of the command are simulated but not applied. Output
    about possible impact of the cmd is displayed. Not supported by all cmds.

    Command_Processor includes optional support for building CMD_OBJECTs from
    command lines parsed by cmd2, arparse for convenience.
"""
#endregion command_processor.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging
from typing import List, Type, Generator, Dict, Tuple, Any, Callable, Optional
# third-party modules and packages
from h11 import Data
import cmd2, argparse
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
from .mvvm_namespace import *
from .command_processor_Base_ABC import CommandProcessor_Base
from .data_context_binding import DataContext_Binding
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
BMCLI_SYSTEM_EXIT_WARNING = "Not exiting due to SystemExit"
# ---------------------------------------------------------------------------- +
#endregion Globals
# ---------------------------------------------------------------------------- +
#region    CommandProcessor class
class CommandProcessor(CommandProcessor_Base, DataContext_Binding):
    # ------------------------------------------------------------------------ +
    #region    CommandProcessor class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +
    #region CommandProcessor class doc string
    """Concrete Class for CommandProcessor_Base."""
    #endregion CommandProcessor class doc string
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        self._initialized : bool = False
        self._cmd_map : Dict[str, Callable] = None
        self._parse_only : bool = False
        self._validate_only : bool = False
        self._what_if : bool = False
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #endregion CommandProcessor class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region    CommandProcessor_Base Properties
    @property
    def cp_initialized(self) -> bool:
        """Return True if the command processor is initialized."""
        return self._initialized

    @cp_initialized.setter
    def cp_initialized(self, value: bool) -> None:
        """Set the initialized state of the command processor."""
        self._initialized = value

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

    @property
    def cp_parse_only(self) -> bool:
        """Return the parse_only state of the command processor."""
        return self._parse_only

    @cp_parse_only.setter
    def cp_parse_only(self, value: bool) -> None:
        """Set the parse_only state of the command processor."""
        self._parse_only = value

    @property
    def cp_validate_only(self) -> bool:
        """Return the validate_only state of the command processor."""
        return self._validate_only

    @cp_validate_only.setter
    def cp_validate_only(self, value: bool) -> None:
        """Set the validate_only state of the command processor."""
        self._validate_only = value

    @property
    def cp_what_if(self) -> bool:
        """Return the what_if state of the command processor."""
        return self._what_if

    @cp_what_if.setter
    def cp_what_if(self, value: bool) -> None:
        """Set the what_if state of the command processor."""
        self._what_if = value
    #endregion CommandProcessor_Base Properties
    # ------------------------------------------------------------------------ +
    #region    CommandProcessor_Base Methods
    # ------------------------------------------------------------------------ +
    #region    cp_initialize() method
    def cp_initialize(self) -> "CommandProcessor":
        """Initialize the CommandProcessor."""
        try:
            self.cp_initialize_cmd_map()
            self.cp_initialized = True
            logger.debug(f"CommandProcessor initialized.")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize() method
    # ------------------------------------------------------------------------ +
    #region    cp_initialize_cmd_map() method
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
    #region    cp_execute_cmd() method
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
            parse_only: bool = self.cp_cmd_attr_get(cmd, CK_PARSE_ONLY, self.cp_parse_only)
            if parse_only:
                cmd_string: str = f"{CK_PARSE_ONLY}: {str(cmd)}"
                logger.info(cmd_string)
                return create_CMD_RESULT_OBJECT(cmd_result_status=True,
                                                 result_content_type=CMD_STRING_OUTPUT,
                                                 result_content=cmd_string,
                                                 cmd_object=cmd)
            cmd_result: CMD_RESULT_TYPE = self.cp_validate_cmd(cmd)
            if not cmd_result[CMD_RESULT_STATUS]: return cmd_result
            # if cp_validate_cmd() is good, continue.
            exec_func: Callable = cmd[CK_CMD_EXEC_FUNC]
            function_name = exec_func.__name__
            validate_only: bool = self.cp_cmd_attr_get(cmd, CK_VALIDATE_ONLY, self.cp_validate_only)
            if validate_only:
                cmd_string: str = f"{CK_VALIDATE_ONLY}: {function_name}({str(cmd)})"
                logger.info(cmd_string)
                return create_CMD_RESULT_OBJECT(cmd_result_status=True,
                                                 result_content_type=CMD_STRING_OUTPUT,
                                                 result_content=cmd_string,
                                                 cmd_object=cmd)
            logger.info(f"Executing command: {function_name}({str(cmd)})")
            # Execute a cmd with its associated exec_func from the cmd_map.
            cmd_result: CMD_RESULT_TYPE = exec_func(cmd)
            # status, result = self.cp_cmd_map.get(full_cmd_key)(cmd)
            logger.info(f"Complete Command: [{p3u.stop_timer(st)}] "
                        f"{(cmd_result[CMD_RESULT_STATUS])}")
            return cmd_result
        except Exception as e:
            cmd_result = create_CMD_RESULT_EXCEPTION(cmd, e)
            if raise_error:
                raise RuntimeError(cmd_result[CMD_RESULT_CONTENT]) from e
            return cmd_result
    #endregion cp_execute_cmd() method
    # ------------------------------------------------------------------------ +
    #region    cp_validate_cmd() method
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
                return create_CMD_RESULT_EXCEPTION(cmd, "Invalid command object.")
            # Additional validation logic can be added here.
            return create_CMD_RESULT_OBJECT(cmd_result_status=True,
                                            result_content_type="validation",
                                            result_content="Command is valid.",
                                            cmd_object=cmd)
        except Exception as e:
            return create_CMD_RESULT_EXCEPTION(cmd, e)
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
            if not self.cp_initialized:
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
    # ------------------------------------------------------------------------ +
    #region    UNKNOWN_cmd() 
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
    #endregion Command_Processor_Base Methods
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region CommandProcessor argparse support methods
    # ------------------------------------------------------------------------ +
    #region construct_cmd_from_argparse
    def construct_cmd_from_argparse(self, opts : argparse.Namespace) -> CMD_OBJECT_TYPE:
        """Construct a valid cmd object from cmd2/argparse arguments or raise error."""
        try:
            # Process cmd object core values, either return a valid command 
            # object or raise an error.
            cmd: CMD_OBJECT_TYPE = self.extract_CMD_OBJECT_from_argparse_Namespace(opts)
            # Process parameters affecting possible cmd.
            # parse_only flag can be set in the view or added to any cmd.
            parse_only:bool = self.cp_cmd_attr_get(cmd, CK_PARSE_ONLY, self.cp_parse_only)
            self.cp_cmd_attr_set(cmd, CK_PARSE_ONLY, parse_only)
            # validate_only flag 
            validate_only:bool = self.cp_cmd_attr_get(cmd, CK_VALIDATE_ONLY, self.cp_validate_only)
            self.cp_cmd_attr_set(cmd, CK_VALIDATE_ONLY, validate_only)
            # what_if flag 
            what_if:bool = self.cp_cmd_attr_get(cmd, CK_WHAT_IF, self.cp_what_if)
            self.cp_cmd_attr_set(cmd, CK_WHAT_IF, what_if)
            return cmd
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion construct_cmd_from_argparse
    # ------------------------------------------------------------------------ +
    #region extract_CMD_OBJECT_from_argparse_Namespace
    def extract_CMD_OBJECT_from_argparse_Namespace(self, opts : argparse.Namespace) -> CMD_OBJECT_TYPE:
        """Create a CommandProcessor cmd dictionary from argparse.Namespace.
        
        This method is specific to BudManCLIView which utilizes argparse for 
        command line argument parsing integrated with cmd2.cmd for command help
        and execution. It converts the argparse.Namespace object into a
        dictionary suitable for the command processor to execute, but 
        independent of the cmd2.cmd structure and argparse specifics.

        A ViewModelCommandProcessor_Binding implementation must provide valid
        ViewModelCommandProcessor cmd dictionaries to the
        ViewModelCommandProcessor interface. This method is used to convert
        the cmd2.cmd arguments into a dictionary that can be used by the
        ViewModelCommandProcessor_Binding implementation.
        """
        try:
            if not isinstance(opts, argparse.Namespace):
                raise TypeError("opts must be an instance of argparse.Namespace.")
            cmd2_cmd_name: str = ''
            cmd_name: str = ''
            cmd_key: str = ''
            subcmd_name: str = ''
            subcmd_key: str = ''
            cmd_exec_func: Optional[Callable] = None

            # Convert to dict, remove two common cmd2 attributes, if present.
            # see bottom of https://cmd2.readthedocs.io/en/latest/features/argument_processing/#decorator-order
            opts_dict = vars(opts).copy()
            cmd2_statement: cmd2.Statement = opts_dict.pop('cmd2_statement', None).get()
            cmd2_handler = opts_dict.pop('cmd2_handler', None).get()
            if cmd2_statement is not None:
                # A valid cmd2.cmd will provide a cmd_name, at a minimum.
                # see https://cmd2.readthedocs.io/en/latest/features/commands/#statements
                cmd2_cmd_name = cmd2_statement.command
            # Collect the command attributes present (or not) in the opts_dict.
            cmd_name = opts_dict.get(CK_CMD_NAME, cmd2_cmd_name) 
            if p3u.str_empty(cmd_name):
                # Must have cmd_name
                raise ValueError("Invalid: No command name provided.")
            cmd_key = opts_dict.get(CK_CMD_KEY, f"{cmd_name}{CMD_KEY_SUFFIX}")
            subcmd_name = opts_dict.get(CK_SUBCMD_NAME, None)
            subcmd_key = opts_dict.get(CK_SUBCMD_KEY, 
                    f"{cmd_key}_{subcmd_name}" if subcmd_name else None)
            cmd_exec_func = opts_dict.get(CK_CMD_EXEC_FUNC, None)
            # Validate CMD_OBJECT requirements.
            if not validate_cmd_key_with_name(cmd_name, cmd_key):
                raise ValueError(f"Invalid: cmd_key '{cmd_key}' does not match cmd_name '{cmd_name}'.")
            if (p3u.str_notempty(subcmd_name) and 
                not validate_subcmd_key_with_name(subcmd_name, cmd_key, subcmd_key)):
                raise ValueError(f"Invalid: subcmd_key '{subcmd_key}' does not "
                                f"match subcmd_name '{subcmd_name}'.")
            cmd = create_CMD_OBJECT(
                cmd_name=cmd_name,
                cmd_key=cmd_key,
                subcmd_name=subcmd_name,
                subcmd_key=subcmd_key,
                cmd_exec_func=cmd_exec_func,
                other_attrs=opts_dict)
            return cmd
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise ValueError(f"Failed to create command object from cmd2:opts: {e}")
    #endregion extract_CMD_OBJECT_from_argparse_Namespace

    # ------------------------------------------------------------------------ +
    #endregion CommandProcessor argparse support methods
    # ------------------------------------------------------------------------ +

#endregion CommandProcessor class
# ---------------------------------------------------------------------------- +
#region CMDValidationException class
class CMDValidationException(Exception):
    """Exception raised for errors in the command validation process."""
    def __init__(self, message: str, cmd_result_error: CMD_RESULT_TYPE = None):
        self.message = message
        self.cmd_result_error = cmd_result_error
        super().__init__(self.message)
#endregion CMDValidationException class
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
    result_content_type: str = CMD_STRING_OUTPUT,
    result_content: Optional[Any] = "No result content.",
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
def create_CMD_RESULT_ERROR(cmd: CMD_OBJECT_TYPE, msg: str) -> CMD_RESULT_TYPE:
        """Return a CMD_RESULT based on an Error msg.

        Executing the cmd resulted in Error. Wrap the error message
        and return it in a CMD_RESULT suitable to return as an error.

        Arguments:
            cmd (Dict): A valid CMD_OBJECT_TYPE.

        Returns:
            CMD_RESULT_TYPE with error information and status of False.
            
        """
        m = (f"Error executing cmd: {cmd.get(CK_CMD_KEY,"Unknown cmd_key")} "
             f"{cmd.get(CK_SUBCMD_KEY, "Unknown subcmd_key")}: {msg}")
        logger.error(m)
        return create_CMD_OBJECT(
            cmd_result_status = False,
            result_content = m,
            result_content_type=CMD_ERROR_STRING_OUTPUT,
            cmd_object=cmd
        )
#endregion create_CMD_RESULT_ERROR() function
# ---------------------------------------------------------------------------- +
#region create_CMD_RESULT_EXCEPTION() function
def create_CMD_RESULT_EXCEPTION(cmd: CMD_OBJECT_TYPE, e: Exception) -> CMD_RESULT_TYPE:
        """Return a CMD_RESULT based on an Exception e for the CMD_OBJECT execution.

        Executing the cmd resulted in Exception e. Format an error message
        and return it in a CMD_RESULT suitable to return as an error.

        Arguments:
            cmd (Dict): A valid CMD_OBJECT_TYPE.
            e (Exception): The exception that occurred.

        Returns:
            CMD_RESULT_TYPE with error information and status of False.
            
        """
        m = (f"Exception executing cmd: {cmd.get(CK_CMD_KEY,"Unknown cmd_key")} "
             f"{cmd.get(CK_SUBCMD_KEY, "Unknown subcmd_key")}: "
             f"{p3u.exc_err_msg(e)}")
        logger.error(m)
        return create_CMD_RESULT_ERROR(cmd, m)
#endregion create_CMD_RESULT_EXCEPTION() function
# ---------------------------------------------------------------------------- +
#region create_CMD_RESULT_ERROR() function
def unknown_CMD_RESULT_ERROR(cmd: CMD_OBJECT_TYPE) -> CMD_RESULT_TYPE:
        """Return a CMD_RESULT based on unknown CK_CMD_KEY and CK_SUBCMD_KEY.

        Arguments:
            cmd (Dict): A valid CMD_OBJECT_TYPE.

        Returns:
            CMD_RESULT_TYPE with error information and status of False.
            
        """
        m = (f"Error unknown {CK_CMD_KEY}: '{cmd.get(CK_CMD_KEY,None)}' "
             f"{CK_SUBCMD_KEY}: '{cmd.get(CK_SUBCMD_KEY, None)}' ")
        logger.error(m)
        return create_CMD_RESULT_OBJECT(
            cmd_result_status = False,
            result_content = m,
            result_content_type=CMD_ERROR_STRING_OUTPUT,
            cmd_object=cmd
        )
#endregion create_CMD_RESULT_ERROR() function
# ---------------------------------------------------------------------------- +
#endregion CMD_RESULT_OBJECT functions
# ---------------------------------------------------------------------------- +