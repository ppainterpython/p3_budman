# ---------------------------------------------------------------------------- +
#region command_class.py module
""" Command class concrete implementation. 

    This module implements the Command class, which is a concrete
    implementation. A Command contains information to execute functionality in
    the mvvm application. The Command Processor pattern depends on executing
    Commands and is independent of the view, view_model and model abstractions.

    A Command object (CMD_OBJECT or CMD) contains the key attributes of a 
    p3_mvvm command. A valid CMD_OBJECT may have a variable number of attributes, 
    based on the need of the command. But, there are some required attributes 
    and several common attributes which may be in any valid CMD_OBJECT. 
    Constants are defined for these attribute keys and values, as appropriate. 
    Note, these are the basic requirements used in the Command Processor for 
    functional operation and are not specific to any application.

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
import logging, threading, queue, uuid, time
from typing import List, Type, Union, Dict, Tuple, Any, Callable, Optional
# third-party modules and packages
from git import cmd
import p3_utils as p3u 
import p3logging as p3l
# local modules and packages
import budman_namespace.design_language_namespace as bdm
from .mvvm_namespace import *
from .cp_message_service import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region Command class
class Command:
    # ------------------------------------------------------------------------ +
    #region    Command class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +
    #region Command class docstring
    """Command: A class representing a command in the Command Processor pattern.
    
    This class is a concrete implementation of a command. It contains the key
    attributes of a command, such as cmd_name, cmd_key, cmd_exec_func, and
    optional attributes such as subcmd_name and subcmd_exec_func. The Command
    class is used to create command objects that can be executed by the Command
    Processor. The Command class is independent of the view, view_model and
    model abstractions in the mvvm design pattern.
    """
    #endregion Command class docstring
    # ------------------------------------------------------------------------ +
    #region Class Methods

    #endregion Class Methods
    # ------------------------------------------------------------------------ +
    #region Command __init__() method

    def __init__(self,
                 cp: object, 
                 cmd_name: str, 
                 cmd_exec_func: Callable, 
                 subcmd_name: Optional[str] = None,
                 required_parms: Optional[List[str]] = None) -> None:
        """Initialize a Command object with required and optional attributes."""
        if not cp:
            raise ValueError("Command Processor (cp) is required to create a Command.")
        self.cp : object = cp
        self.cmd_name: str = cmd_name
        self.cmd_key: str = f"{cmd_name}_cmd"
        if subcmd_name :
            self.subcmd_name = subcmd_name
            self.subcmd_key = f"{self.cmd_key}_{subcmd_name}"
        if not cmd_exec_func or not callable(cmd_exec_func):
            raise ValueError("cmd_exec_func is required and must be callable to create a Command.")
        self.cmd_exec_func: Callable = cmd_exec_func
        self.async_id: str | None = None  
        self.cmd_async_result_subscriber: Callable | None = None
        self.cmd_parms: Dict[str, Any] = {} # Optional attribute for async command execution tracking
        # Add required_parms to cmd_parms if provided.
        if required_parms:
            for parm in required_parms:
                self.cmd_parms[parm] = None  # Initialize required parms with None or default values.
        self.add_common_cmd_parms()  # Add common command parameters to cmd_parms.
        self.add_command_to_cp()  # Add the command to the Command Processor's command dictionary.
    #endregion Command __init__() method
    # ------------------------------------------------------------------------ +
    #region __str__() method
    def __str__(self) -> str:
        """Return a string representation of the Command object."""
        return (f"Command(cmd_name='{self.cmd_name}', cmd_key='{self.cmd_key}', "
                f"subcmd_name='{getattr(self, 'subcmd_name', None)}', "
                f"subcmd_key='{getattr(self, 'subcmd_key', None)}', "
                f"cmd_exec_func='{self.cmd_exec_func.__name__}', "
                f"cmd_parms={self.cmd_parms})")
    #endregion __str__() method
    # ------------------------------------------------------------------------ +
    #region    Command class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region Instance Methods
    # ------------------------------------------------------------------------ +
    #region add_command_to_cp() method
    def add_command_to_cp(self) -> None:
        """Add the command to the Command Processor's command dictionary."""
        if self.subcmd_name:
            self.cp.cp_commands[self.subcmd_key] = self
        else:
            self.cp.cp_commands[self.cmd_key] = self
    #endregion add_command_to_cp() method
    # ------------------------------------------------------------------------ +
    #region validate_command() method
    def validate_command(self,
                         expected_cmd_key: str,
                         expected_subcmd_key: str) -> CMD_ARGS_TYPE:
        """Validate the components of the command object.

        Args:
            expected_cmd_key (str): The expected command key to validate.
            expected_subcmd_key (str): The expected sub-command key to validate.

        Returns:
            cmd_args: CMD_ARGS_TYPE: The resulting cmd arg from the validation.
        """
        try:
            # Check the cmd_key or subcmd_key have a binding in the command processor.
            key: str = self.subcmd_key if self.subcmd_key else self.cmd_key
            command_def: Command = self.cp.cp_commands.get(key, None)
            if not command_def:
                m = f"Command definition not found for key: {key}"
                logger.error(m)
                raise ValueError(msg=m)
            # Check it is a command of the type the caller expected.
            cmd_result : CMD_RESULT_TYPE = None
            # Should be indicated cmd_key.
            if not self.verify_cmd_key(expected_cmd_key): 
                raise ValueError(msg=f"cmd_key: '{self.cmd_key}' does not match expected_cmd_key: '{expected_cmd_key}'")
            # Should be indicated subcmd_key.
            if not self.verify_subcmd_key(expected_subcmd_key): 
                raise ValueError(msg=f"subcmd_key: '{self.subcmd_key}' does not match expected_subcmd_key: '{expected_subcmd_key}'")    
            # Check for required command key arguments (CK_) in the command object
            cmd_args: CMD_ARGS_TYPE = {}
            cmd_args[CK_CMD_KEY] = self.cmd_key
            cmd_args[CK_SUBCMD_KEY] = self.subcmd_key
            missing_arg_error_msg: str = "Required arguments validation:"
            missing_arg_list = []
            missing_arg_count = 0
            for key in command_def.cmd_parms.keys():
                if key not in self.cmd_parms:
                    m = f"Missing required command argument key: {key}"
                    logger.error(m)
                    missing_arg_error_msg += f"{m}\n"
                    missing_arg_count += 1
                    missing_arg_list.append(key)
                else:
                    cmd_args[key] = self.cmd_parms[key]
            if missing_arg_count > 0:
                m = (f"Missing {missing_arg_count} required arguments: "
                    f"{missing_arg_list}")
                logger.error(m)
                raise ValueError(msg=m)
            return cmd_args
        except Exception as e:
            logger.error(f"Error validating command components: {e}")
            raise
    #endregion validate_command() method
    # ------------------------------------------------------------------------ +
    #region add_common_cmd_parms() method
    def add_common_cmd_parms(self) -> None:
        """Add common command parameters to the cmd_parms dictionary."""
        self.cmd_parms[CK_PARSE_ONLY] = False
        self.cmd_parms[CK_VALIDATE_ONLY] = False
        self.cmd_parms[CK_WHAT_IF] = False
        self.cmd_parms[CK_VERBOSE] = False
    #endregion add_common_cmd_parms() method
    # ------------------------------------------------------------------------ +
    #region verify_cmd_key()
    def verify_cmd_key(self, expected_cmd_key: str) -> bool:
        """Verify the command key in the command object.

        Args:
            expected_cmd_key (str): The expected command key.

        Returns:
            bool: True if the command key matches, False otherwise.
        """
        if self.cmd_key != expected_cmd_key:
            # Invalid cmd_key
            m = (f"Invalid cmd_key: {self.cmd_key} "
                f"expected: {expected_cmd_key}")
            logger.debug(m)
            return False
        return True
    #endregion verify_cmd_key()
    # ------------------------------------------------------------------------ +
    #region verify_subcmd_key()
    def verify_subcmd_key( self,  
                            expected_subcmd_key: str) -> bool:
        """Verify the subcommand key in the command object.

        Args:
            expected_subcmd_key (str): The expected subcommand key.

        Returns:
            bool: True if the subcommand key matches, False otherwise.
        """
        if self.subcmd_key != expected_subcmd_key:
            # Invalid subcmd_key
            m = (f"Invalid subcmd_key: {self.subcmd_key} "
                f"expected: {expected_subcmd_key}")
            logger.debug(m)
            return False
        return True     
    #endregion verify_cmd_key()
    # ---------------------------------------------------------------------------- +

#endregion Command class
# ---------------------------------------------------------------------------- +
