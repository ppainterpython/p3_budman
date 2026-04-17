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
from budman_data_context import BudManAppDataContext_Base
from .mvvm_namespace import *
from .command_processor import *
from .cp_message_service import *
from .data_context_binding import DataContext_Binding
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
                 cp: CommandProcessor, 
                 cmd_name: str, 
                 cmd_exec_func: Callable, 
                 subcmd_name: Optional[str] = None,
                 required_parms: Optional[List[str]] = None) -> None:
        """Initialize a Command object with required and optional attributes."""
        self.cp : CommandProcessor = cp
        self.cmd_name: str = cmd_name
        self.cmd_key: str = f"{cmd_name}_cmd"
        self.cmd_exec_func: Callable = cmd_exec_func
        if subcmd_name :
            self.subcmd_name = subcmd_name
            self.subcmd_key = f"{self.cmd_key}_{subcmd_name}"
        self.async_id: str | None = None  
        self.cmd_parms: Dict[str, Any] = {} # Optional attribute for async command execution tracking
        # Add required_parms to cmd_parms if provided.
        if required_parms:
            for parm in required_parms:
                self.cmd_parms[parm] = None  # Initialize required parms with None or default values.
        self.add_common_cmd_parms()  # Add common command parameters to cmd_parms.
    #endregion Command __init__() method
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region Instance Methods
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
                raise CMDValidationException(cmd=self, msg=m)
            # Check it is a command of the type the caller expected.
            cmd_result : CMD_RESULT_TYPE = None
            # Should be indicated cmd_key.
            cmd_result = self.verify_cmd_key(expected_cmd_key)
            if not cmd_result[CK_CMD_RESULT_STATUS]: 
                raise CMDValidationException(cmd=self, 
                                             msg=cmd_result[CK_CMD_RESULT_CONTENT],
                                             cmd_result_error=cmd_result)
            # Should be indicated subcmd_key.
            cmd_result = self.verify_subcmd_key(expected_subcmd_key)
            if not cmd_result[CK_CMD_RESULT_STATUS]: 
                raise CMDValidationException(cmd=self, 
                                             msg=cmd_result[CK_CMD_RESULT_CONTENT],
                                             cmd_result_error=cmd_result)
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
                cmd_result = cp_CMD_RESULT_create(
                    status=False,
                    type=CV_CMD_ERROR_STRING_OUTPUT,
                    content=missing_arg_error_msg,
                    cmd=self
                    )
                raise CMDValidationException(cmd=self,
                                             msg=cmd_result[CK_CMD_RESULT_CONTENT],
                                             cmd_result_error=cmd_result)
            return cmd_args
        except CMDValidationException as ve:
            raise
        except Exception as e:
            logger.error(f"Error validating command components: {e}")
            return cp_CMD_RESULT_create(
                status=False,
                type=CV_CMD_ERROR_STRING_OUTPUT,
                content=str(e),
                cmd=self
            )
    #endregion validate_command() method
    # ------------------------------------------------------------------------ +
    #region verify_cmd_key()
    def verify_cmd_key(self, expected_cmd_key: str) -> CMD_RESULT_TYPE:
        """Verify the command key in the command object.

        Args:
            expected_cmd_key (str): The expected command key.

        Returns:
            CMD_RESULT_TYPE: True if the command key matches, False otherwise,
            with a returnable CMD_RESULT_TYPE.
        """
        cmd_result: CMD_RESULT_TYPE = cp_CMD_RESULT_create(
            status=True,
            type=CV_CMD_STRING_OUTPUT,
            content=f"Expected cmd_key: {expected_cmd_key} is valid.",
            cmd=self
        )
        if self.cmd_key != expected_cmd_key:
            # Invalid cmd_key
            m = (f"Invalid cmd_key: {self.cmd_key} "
                f"expected: {expected_cmd_key}")
            logger.error(m)
            cmd_result[CK_CMD_RESULT_STATUS] = False
            cmd_result[CK_CMD_RESULT_CONTENT] = m
            cmd_result[CK_CMD_RESULT_CONTENT_TYPE] = CV_CMD_ERROR_STRING_OUTPUT
        return cmd_result
    #endregion verify_cmd_key()
    # ------------------------------------------------------------------------ +
    #region verify_subcmd_key()
    def verify_subcmd_key( self,  
                            expected_subcmd_key: str) -> CMD_RESULT_TYPE:
        """Verify the subcommand key in the command object.

        Args:
            expected_subcmd_key (str): The expected subcommand key.

        Returns:
            CMD_RESULT_TYPE: True if the command key matches, False otherwise,
            with a returnable CMD_RESULT_TYPE.
        """
        cmd_result: CMD_RESULT_TYPE = cp_CMD_RESULT_create(
            status=True,
            type=CV_CMD_STRING_OUTPUT,
            content=f"Expected subcmd_key: {expected_subcmd_key} is valid.",
            cmd=self
        )
        actual_subcmd_key = self.get(CK_SUBCMD_KEY)
        if actual_subcmd_key != expected_subcmd_key:
            # Invalid subcmd_key
            m = (f"Invalid subcmd_key: {self.subcmd_key} "
                f"expected: {expected_subcmd_key}")
            logger.error(m)
            cmd_result[CK_CMD_RESULT_STATUS] = False
            cmd_result[CK_CMD_RESULT_CONTENT] = m
            cmd_result[CK_CMD_RESULT_CONTENT_TYPE] = CV_CMD_ERROR_STRING_OUTPUT
        return cmd_result
    #endregion verify_cmd_key()
    # ---------------------------------------------------------------------------- +

#endregion Command class
# ---------------------------------------------------------------------------- +
