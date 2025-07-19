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
from .command_processor_Base_ABC import CommandProcessor_Base
from .data_context_base_ABC import DataContext_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class CommandProcessor(CommandProcessor_Base):
    """Concrete Class for Command Processor Base."""
    #region __init__() constructor method
    def __init__(self) -> None:
        super().__init__()
        self._initialized : bool = False
        self._cp : Callable = None  # Command Processor
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

    @property
    def data_context(self) -> DataContext_Base:
        """Return the command processor."""
        pass
    @data_context.setter
    def data_context(self, value : DataContext_Base) -> None:
        """Set the command processor."""
        pass

    #endregion CommandProcessor_BindingProperties
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self, cp : Optional[Callable]) -> "BudManCLICommandProcessor_Binding":
        """Initialize the data context."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLICommandProcessor_Binding.")
            self.CP = cp
            self.initialized = True
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #endregion BudManCLICommandProcessor_Binding class
    # ======================================================================== +

    # ======================================================================== +
    #region BudgetManagerViewModelInterface Interface client access methods    +
    """This Data Context the Budget Manager View Model for commands and data."""
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region execute_cmd() method
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
    #endregion execute_cmd() command method
    #                                                                          +
    #endregion BudgetManagerViewModelInterface Interface client access methods +
    # ======================================================================== +
