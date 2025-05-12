# ---------------------------------------------------------------------------- +
#region budmod_cli_view.py module
""" budmod_cli_view.py cli-style view for BudgetModel (budmod).

A simple command line interface for the BudgetModel application. Using the cmd2
package which embeds the argparse package. Cmd2 handles the command structure and
argparse handles the argument lists for each command. The BudgetModelCLIView
class is a subclass of cmd2.Cmd and implements the command line interface for the
user.

This is an MVVM View class for the BudgetModel. It uses a DataContext object to
interact with the BudgetModel. The DataContext object is a View Model and 
provides a defined interface supporting Commands and other DC-related methods
needed to let a user View interact.

CLI Argument Parsing
--------------------

Argparse is very declarative. To separate the command line parsing from the 
code that executes commands, where the View Model methods are called, we use the
class BudgetModelCLIParser to manage all of the argparse setup work. It is
considered an inner class of the BudgetModelCLIView class. But the argument
declarations are contained in that one class, separate from the View code.

"""
#endregion budmod_cli_view.py module
# ---------------------------------------------------------------------------- +
#region Imports

# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l
import cmd2
from cmd2 import (Cmd2ArgumentParser, with_argparser)
from  .budmod_cli_parser import BudgetModelCLIParser

# local modules and packages

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings.app_name)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region MockViewModel class
class MockViewModel():
    """Mock view_model object for the BudgetModel.
    
    Simulates an unknown view_model object for the BudgetModel.
    Supports dot notation for accessing attributes."""
    # TODO: Use ABC for view_model interface. 
    def __getattr__(self, item):
        return self[item] if item in self.__dict__ else None
    
    def __setattr__(self, item, value):
        self[item] = value

#endregion MockViewModel class
# ---------------------------------------------------------------------------- +
# Setup the command line argument parsers. This is required due to the
# cmd2.with_argparser decorator, which requires a callable to return a 
# Cmd2ArgumentParser object. If one fails during setup(), the goal is the
# whole app won't fail, and will display the error message for the
# particular command parser.
cli_parser : BudgetModelCLIParser = BudgetModelCLIParser()
def init_cmd_parser() -> Cmd2ArgumentParser:
    return cli_parser.init_cmd_parser if cli_parser else None
def show_cmd_parser() -> Cmd2ArgumentParser:
    return cli_parser.show_cmd_parser if cli_parser else None
def load_cmd_parser() -> Cmd2ArgumentParser:
    return cli_parser.load_cmd_parser if cli_parser else None

class BudgetModelCLIView(cmd2.Cmd):
    # ======================================================================== +
    #region BudgetModelCLIView class
    """An MVVM View class for BudgetModel implementing a command line interface.
    
    Operates under MVVM pattern, strictly. Instantiated with a blind view_model.
    Using cmd2 package which embeds the argparse package. Cmd2 handles the
    command structure and argpars handles the argument lists for each command.
    TODO: Use ABC for view_model interface.
    """
    prompt = "p3b> "
    intro = "Welcome to the BudgetModel CLI. Type help or ? to list commands.\n"

    def __init__(self, data_context : object | MockViewModel = None) -> None:
        super().__init__()
        self.initialized = False
        self.cli_parser : BudgetModelCLIParser = cli_parser
        self._data_context = MockViewModel() if data_context is None else data_context
    
    @property
    def data_context(self) -> object:
        """Get the data_context property."""
        return self._data_context
    
    @data_context.setter
    def data_context(self, value: object) -> None:
        """Set the data_context property."""
        if not isinstance(value, (MockViewModel, object)):
            raise ValueError("data_context must be a MockViewModel or object.")
        self._data_context = value
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self) -> None:
        """Initialize the BudgetModelCLIView class."""
        try:
            self.cli_parser.view_cmd = self
            self.initialized = True
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #endregion BudgetModelCLI class
    # ======================================================================== +

    # ======================================================================== +
    #region CLIViewModel Cmd methods
    # ======================================================================== +
    # ------------------------------------------------------------------------ +
    #region init command - initialize aspects of the BudgetModel application.
    @with_argparser(init_cmd_parser())
    def do_init(self, opts):
        """Init BugetModel properties and values.."""
        try:
            self.poutput(f"args: {str(opts)}")
            if opts.init_cmd in ["financial_institution", "fi", "FI"]:
                fi_key = opts.fi_key if opts.fi_key else None
                self.data_context.FI_init_cmd(opts.fi_key)
                self.poutput(f"Initialized financial institution: {fi_key}")
        except SystemExit:
            # Handle the case where argparse exits the program
            self.pwarning("Not exiting due to SystemExit")
        except Exception as e:
            self.pexcept(e)
    #endregion init command - initialize aspects of the BudgetModel application.
    # ------------------------------------------------------------------------ +
    #region Show command - workbooks, status, etc.
    @with_argparser(show_cmd_parser())
    def do_show(self, opts):
        """Show BugetModel domain information."""
        try:
            self.poutput(f"args: {str(opts)}")
            if opts.show_cmd in ["workbook", "wb", "WB"]:
                wb_name = opts.wb_name if opts.wb_name else None
                c = self.data_context.FI_get_loaded_workbooks_count()
                self.poutput(f"Loaded workbooks: {c}")
                if c > 0:
                    names = self.data_context.FI_get_loaded_workbook_names()
                    [self.poutput(f"  {i}: {n}") for i, n in enumerate(names)]
                else:
                    self.poutput("No loaded workbooks.")
            elif opts.show_cmd in ["financial_institution", "fi", "FI"]:
                fi_key = opts.fi_key if opts.fi_key else None
                c = self.data_context.FI_get_loaded_workbooks_count()
                self.poutput(f"Loaded workbooks: {c}")
                if c > 0:
                    names = self.data_context.FI_get_loaded_workbook_names()
                    [self.poutput(f"  {i}: {n}") for i, n in enumerate(names)]
                else:
                    self.poutput("No loaded workbooks.")
        # except Cmd2Arg as e:
        #     print(f"Error parsing arguments: {e}")
        except SystemExit as e:
            # Handle the case where argparse exits the program
            # print("Exiting due to SystemExit")
            pass
        except Exception as e:
            self.perror(f"Error showing BudgetModel: {e}")
    #endregion Show command
    # ------------------------------------------------------------------------ +
    #region Load command - load workbooks
    @with_argparser(load_cmd_parser())
    def do_load(self, opts):
        """Load BugetModel data items into app session."""
        try:
            # self.budget_model.bm_load()
            self.poutput(f"args: {str(opts)}")
            print("BudgetModel loaded.")
        except Exception as e:
            self.pexcept(e)
    #endregion Load command - load workbooks
    # ------------------------------------------------------------------------ +
    #region Save command - save workbooks
    def do_save(self, line: str):
        """Save the BudgetModel to a file."""
        try:
            # self.budget_model.bm_save()
            print("BudgetModel saved.")
        except Exception as e:
            self.perror(f"Error saving BudgetModel: {e}")
    #endregion Save command - save workbooks
    # ------------------------------------------------------------------------ +    
    #region exit and quit commands
    def do_exit(self, line: str):
        """Exit the BudgetModel CLI."""
        print("Exiting BudgetModel CLI.")
        return True
    
    def do_quit(self, line: str):
        """Quit the BudgetModel CLI."""
        print("Quitting BudgetModel CLI.")
        return True 
    #endregion exit and quit commands
    # ------------------------------------------------------------------------ +    
    #endregion CLIViewModel Cmd methods
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
