# ---------------------------------------------------------------------------- +
#region budman_cli_view_datacontext.py module
""" budman_cli_view_datacontext.py implements BudgetManagerCLIViewDataContext class.

BudManCLIViewDataContext serves as a ViewModelCommandProcessor provider 
implementation for the BudManCLIView class. The CLIView is a
command line interpreter user interface for the BudMan application.
"""
#endregion bdm_view_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any, Callable
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
class BudManCLIViewDataContext():
    # ======================================================================== +
    #region BudManCLIViewDataContext class
    """A DataContext for the BudgetManagerCLIView.
    This Data Context (DC) is bound to a ViewModel of type 
    BudgetManagerViewModelInterface. The two concerns of the ViewModel are
    command processing and DC properties and methods needed by the View.
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Class Variables
    #endregion Class Variables
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self, view_model : object) -> None:
        super().__init__()
        self._initialized : bool = False
        self._view_model : object = view_model
        self._cp : Callable = None  # Command Processor
        self._dc : object = None    # Data Context
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region Properties
    @property
    def initialized(self) -> bool:
        """Return True if the Data Context is initialized."""
        return self._initialized
    
    @initialized.setter
    def initialized(self, value : bool) -> None:
        """Set the initialized property."""
        if not isinstance(value, bool):
            raise ValueError("initialized must be a boolean value.")
        self._initialized = value  
    @property
    def view_model(self) -> object:
        """Return the view model."""
        return self._view_model
    @view_model.setter
    def view_model(self, value : object) -> None:
        """Set the view model."""
        if not isinstance(value, object):
            raise ValueError("view_model must be an object.")
        self._view_model = value
    @property
    def command_processor(self) -> Callable:
        """Return the command processor."""
        return self._cp
    @command_processor.setter
    def command_processor(self, value : Callable) -> None:
        """Set the command processor."""
        if not callable(value):
            raise ValueError("command_processor must be a callable.")
        self._cp = value
    @property
    def data_context(self) -> object:
        """Return the data context."""
        return self._dc
    @data_context.setter
    def data_context(self, value : object) -> None:
        """Set the data context."""
        if not isinstance(value, object):
            raise ValueError("data_context must be an object.")
        self._dc = value
    @property
    def cp(self) -> Callable:
        """Return the command processor."""
        return self._cp
    @cp.setter
    def cp(self, value : Callable) -> None:
        """Set the command processor."""
        if not callable(value):
            raise ValueError("command_processor must be a callable.")
        self._cp = value
    @property
    def dc(self) -> object:
        """Return the data context."""
        return self._dc
    @dc.setter
    def dc(self, value : object) -> None:
        """Set the data context."""
        if not isinstance(value, object):
            raise ValueError("data_context must be an object.")
        self._dc = value
    #endregion Properties
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self, cp : Callable, dc : object) -> "BudManCLIViewDataContext":
        """Initialize the data context."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLIViewDataContext.")
            self.cp = cp
            self.dc = dc
            self.initialized = True
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #endregion BudManCLIViewDataContext class
    # ======================================================================== +

    # ======================================================================== +
    #region BudgetManagerViewModelInterface Interface client access methods    +
    """This Data Context the Budget Manager View Model for commands and data."""
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region execute_cmd() method
    def execute_cmd(self, cmd : Dict = None) -> Tuple[bool, Any]:
        """Execute a command with the Budget Model View Model.

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
            st = p3u.start_timer()
            logger.info(f"Start Command: {cmd}")
            if not self.initialized:
                m = f"{self.__class__.__name__} is not initialized."
                logger.error(m)
                return False, m
            # if the cp is not bound, return an error.
            if self.cp is None:
                m = f"{self.__class__.__name__} command processor is None."
                logger.error(m)
                return False, m
            return self.cp(cmd)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion execute_cmd() command method
    #                                                                          +
    #endregion BudgetManagerViewModelInterface Interface client access methods +
    # ======================================================================== +
