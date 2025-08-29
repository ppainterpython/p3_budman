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
from abc import ABC, abstractmethod
import logging, os, getpass, time, copy
from typing import List, Type, Generator, Dict, Tuple, Any, Callable, Optional
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
from .mvvm_namespace import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class CommandProcessor_Base(ABC):
    # ------------------------------------------------------------------------ +
    #region CommandProcessor class doc string
    """Abstract Base Class for Command Processor."""
    #endregion CommandProcessor class doc string
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Base Properties
    @property
    @abstractmethod
    def cp_initialized(self) -> bool:
        """Return True if the command processor is initialized."""
        pass
    @cp_initialized.setter
    def cp_initialized(self, value: bool) -> None:
        """Set the initialized state of the command processor."""
        pass

    @property
    @abstractmethod
    def cp_cmd_map(self) -> Dict[str, Callable]:
        """Return the command map for the command processor."""
        pass
    @cp_cmd_map.setter
    @abstractmethod
    def cp_cmd_map(self, value : Dict[str, Callable]) -> None:
        """Set the command map for the command processor."""
        pass

    @property
    @abstractmethod
    def cp_parse_only(self) -> bool:
        """Return the parse_only state of the command processor."""
        pass
    @cp_parse_only.setter
    @abstractmethod
    def cp_parse_only(self, value: bool) -> None:
        """Set the parse_only state of the command processor."""
        pass

    @property
    @abstractmethod
    def cp_validate_only(self) -> bool:
        """Return the validate_only state of the command processor."""
        pass
    @cp_validate_only.setter
    @abstractmethod
    def cp_validate_only(self, value: bool) -> None:
        """Set the validate_only state of the command processor."""
        pass

    @property
    @abstractmethod
    def cp_what_if(self) -> bool:
        """Return the what_if state of the command processor."""
        pass
    @cp_what_if.setter
    @abstractmethod
    def cp_what_if(self, value: bool) -> None:
        """Set the what_if state of the command processor."""
        pass

    #endregion CommandProcessor_Base Properties
    # ------------------------------------------------------------------------ +
    #region CommandProcessor methods
    @abstractmethod
    def cp_initialize(self, cp : Optional[Callable]) -> "CommandProcessor_Base":
        """Initialize the CommandProcessor."""
        pass

    @abstractmethod
    def cp_initialize_cmd_map(self) -> None:
        """Application-specific: Initialize the cp_cmd_map."""
        pass

    @abstractmethod
    def cp_execute_cmd(self, cmd : CMD_OBJECT_TYPE = None, raise_error:bool=False) -> CMD_RESULT_TYPE:
        """Execute a command.

        The command processor is a callable object.

        Arguments:
            cmd (Dict): The command to execute along with any arguments.
        
        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution.
        """
        pass

    @abstractmethod
    def cp_validate_cmd(self, cmd : CMD_OBJECT_TYPE = None,
                        validate_all : bool = False) -> CMD_RESULT_TYPE:
        """Validate a command."""
        pass

    @abstractmethod
    def cp_validate_cmd_object(self, 
                               cmd : CMD_OBJECT_TYPE = None,
                               raise_error:bool=False) -> bool:
        """Validate Command Processor is initialized and the cmd object is valid.

        Test self.initialized property, must be True to proceed.

        Verify the cmd object is a dictionary, not None and not 0 length.

        Arguments:
            cmd (Dict): A candidate Command object to validate.
            raise_error (bool): If True, raise any errors encountered. 

        returns:
            bool: True if Command Processor is initialized, and cmd object is 
            a dictionary, False otherwise.

        Raise:
            RuntimeError: If raise_error is True, a RunTimeError is raised 
            with an error message.
        """
        pass

    @abstractmethod
    def cp_exec_func_binding(self, cmd_key : str, default:Callable) -> Callable:
        """Get the command function for a given command key.

        This method retrieves the command function from the command map
        using the provided command key. If the command key is not found,
        it returns a function that handles unknown command cmd objects.

        Arguments:
            cmd_key (str): The command key to look up in the command map.

        Returns:
            Callable: The function associated with the command key, or an 
            UNKNOWN_cmd function if the key is not found.
        """
        pass

    @abstractmethod
    def cp_cmd_attr_get(self, cmd: CMD_OBJECT_TYPE,
                    key_name: str, default_value: Any = None) -> Any:
        """Use cmd attr key_name to get value or return default."""
        pass
    
    @abstractmethod
    def cp_cmd_attr_set(self, cmd: CMD_OBJECT_TYPE, key_name: str, value: Any) -> None:
        """Set the cmd attribute key_name to value."""
        pass

    #endregion CommandProcessor_Base methods
