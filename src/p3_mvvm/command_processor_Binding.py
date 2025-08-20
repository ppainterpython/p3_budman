# ---------------------------------------------------------------------------- +
#region budman_cli_view_command_processor_binding.py module
""" BudManCLICommandProcessor_Binding class implementation. 

BudManCLICommandProcessor_Binding serves as a CommandProcessor binding 
implementation for a View class.
"""
#endregion budman_cli_view_command_processor_binding.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging
from typing import List, Type, Generator, Dict, Tuple, Any, Callable, Optional
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
from .mvvm_namespace import *
from .command_processor_Base_ABC import CommandProcessor_Base
from .command_processor import create_CMD_RESULT_ERROR
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class CommandProcessor_Binding(CommandProcessor_Base):
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Binding class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Binding class doc string
    """Concrete Class for Command Processor Base."""
    #endregion CommandProcessor_Binding class doc string
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        super().__init__()
        self._initialized : bool = False
        self._cp : CommandProcessor_Base = None  # Command Processor
        self._cmd_map : Dict[str, Callable] = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #endregion CommandProcessor_Binding class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Binding Properties
    @property
    def CP(self) -> CommandProcessor_Base:
        """Return the command processor."""
        return self._cp
    @CP.setter
    def CP(self, value : CommandProcessor_Base) -> None:
        """Set the command processor."""
        self._cp = value
    #endregion CommandProcessor_BindingProperties
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Base Properties
    @property
    def cp_cmd_map(self) -> Dict[str, Callable]:
        """Return the command map for the command processor."""
        return self.CP.cp_cmd_map
    @cp_cmd_map.setter
    def cp_cmd_map(self, value : Dict[str, Callable]) -> None:
        """Set the command map for the command processor."""
        if not isinstance(value, dict):
            raise ValueError("cp_cmd_map must be a dictionary.")
        self.CP.cp_cmd_map = value

    #endregion CommandProcessor_BindingProperties
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Base Methods
    # ------------------------------------------------------------------------ +
    #region cp_initialize() method
    def cp_initialize(self) -> CommandProcessor_Base:
        """Initialize the CommandProcessor."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLICommandProcessor_Binding.")
            return self.CP.cp_initialize()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize() method
    # ------------------------------------------------------------------------ +
    #region cp_initialize_cmd_map() method
    def cp_initialize_cmd_map(self) -> None:
        """Application-specific: Initialize the cp_cmd_map."""
        try:
            self.initialized = True
            logger.debug(f"CommandProcessor cmd_map initialized.")
            return self.CP.cp_initialize_cmd_map()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #region execute_cmd() method
    def cp_execute_cmd(self, cmd : Dict = None,
                       raise_error : bool = False) -> CMD_RESULT_TYPE:
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
            return self.CP.cp_execute_cmd(cmd)
        except Exception as e:
            cmd_result = create_CMD_RESULT_ERROR(cmd, e)
            m = cmd_result[CMD_RESULT_CONTENT]
            if raise_error:
                raise RuntimeError(m)
            return False, m
    #endregion execute_cmd() command method
    # ------------------------------------------------------------------------ +
    #region cp_validate_cmd() method
    def cp_validate_cmd(self, 
                        cmd : Dict = None,
                        validate_all : bool = False) -> CMD_RESULT_TYPE:
        """CP-Binding: Validate the cmd object for cmd_key and parameters.

        """
        try:
            return self.CP.cp_validate_cmd(cmd, validate_all)
        except Exception as e:
            cmd_result = create_CMD_RESULT_ERROR(cmd, e)
            return cmd_result
    #endregion cp_validate_cmd() command method
    # ------------------------------------------------------------------------ +
    #region cp_validate_cmd_object() method
    def cp_validate_cmd_object(self, 
                               cmd : Dict = None,
                               raise_error : bool = False) -> bool:
        """CP-Binding: Validate the cmd object. """
        try:
            return self.CP.cp_validate_cmd_object(cmd, raise_error)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_validate_cmd_object() command method
    # ------------------------------------------------------------------------ +
    #region cp_exec_func_binding() method
    def cp_exec_func_binding(self, cmd_key : str, default:Callable) -> Callable:
        """Get the command function for a given command key."""
        try:
            return self.CP.cp_exec_func_binding(cmd_key, default)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_exec_func_binding() command method
    # ------------------------------------------------------------------------ +
    #region cp_cmd_attr_get() method
    def cp_cmd_attr_get(self, cmd: Dict,
                       key_name: str, default_value: Any = None) -> Any:
        """Use cmd attr key_name to get value or return default."""                  
        try:
            return self.CP.cp_cmd_attr_get(cmd, key_name, default_value)
        except Exception as e:
            raise
    #endregion cp_cmd_attr_get() command method
    # ------------------------------------------------------------------------ +
    #region cp_cmd_attr_set() method
    def cp_cmd_attr_set(self, cmd: Dict, arg_name: str, value: Any) -> None:
        """Set a command argument value in the cmd dictionary."""
        try:
            return self.CP.cp_cmd_attr_set(cmd, arg_name, value)
        except Exception as e:
            raise
    #endregion cp_cmd_attr_set() command method
    # ------------------------------------------------------------------------ +
    #endregion CommandProcessor_Base Methods                                   +
    # ------------------------------------------------------------------------ +
