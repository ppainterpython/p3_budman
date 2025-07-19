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
from budman_namespace import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class CommandProcessor_Base(ABC):
    """Abstract Base Class for Command Processor Binding."""
    #region CommandProcessor_Base Properties
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
    #endregion CommandProcessor_Base Properties
    # ------------------------------------------------------------------------ +
    #region CommandProcessor_Base methods
    @abstractmethod
    def cp_execute_cmd(self, cmd : Dict = None, raise_error:bool=False) -> Tuple[bool, Any]:
        """Execute a command.

        The command processor is a callable object.

        Arguments:
            cmd (Dict): The command to execute along with any arguments.
        
        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution.
        """
        pass

    # @abstractmethod
    # def cp_validate_cmd(self, cmd : Dict = None,
    #                     validate_all : bool = False) -> BUDMAN_RESULT:
    #     """Validate a command."""
    #     pass



    #endregion CommandProcessor_Base methods
