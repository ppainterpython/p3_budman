# ---------------------------------------------------------------------------- +
#region budmod_cli_view.py module
""" budmod_cli_view.py cli-style view for BudgetModel (budmod).

A simple command line interface for the BudgetModel application. Using the cmd2
package which embeds the argparse package. Cmd2 handles the command structure and
argparse handles the argument lists for each command. The BudgetManagerCLIView
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
considered an inner class of the BudgetManagerCLIView class. But the argument
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
import cmd2, argparse
from cmd2 import (Cmd2ArgumentParser, with_argparser)
from  .budman_cli_parser import BudgetManagerCLIParser, BudManCmd2ArgumentParser

# local modules and packages

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings.app_name)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Module Variables and Functions
# Setup the command line argument parsers. This is required due to the
# cmd2.with_argparser decorator, which requires a callable to return a 
# Cmd2ArgumentParser object. If one fails during setup(), the goal is the
# whole app won't fail, and will display the error message for the
# particular command parser.
cli_parser : BudgetManagerCLIParser = BudgetManagerCLIParser()
def init_cmd_parser() -> BudManCmd2ArgumentParser:
    subcmd_parser = cli_parser.init_cmd_parser if cli_parser else None
    return subcmd_parser
def show_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.show_cmd_parser if cli_parser else None
def load_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.load_cmd_parser if cli_parser else None
def save_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.save_cmd_parser if cli_parser else None
def val_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.val_cmd_parser if cli_parser else None

def _filter_opts(opts) -> Dict[str, Any]:
    if opts is None: return {}
    oc = vars(opts).copy()
    oc.pop('cmd2_statement')
    oc.pop('cmd2_handler')
    return oc
def _log_cli_cmd_execute(self, opts):
    """Log the command and options. Return True if parse_only."""
    logger.info(f"Execute Command: {str(_filter_opts(opts))}")
    return self.parse_only if not "val_cmd" in opts else False
def _log_cli_cmd_complete(self, opts, st = None):
    m = p3u.stop_timer(st) if st else None
    logger.info(f"Complete Command: {str(_filter_opts(opts))} {m}")
def _show_args_only(cli_view : "BudgetManagerCLIView", opts) -> bool:
    oc = vars(opts).copy()
    oc.pop('cmd2_statement')
    oc.pop('cmd2_handler')
    cli_view.poutput(f"args: {str(oc)} parse_only: {cli_view.parse_only}")
    return cli_view.parse_only

BMCLI_SYSTEM_EXIT_WARNING = "Not exiting due to SystemExit"
PO_OFF_PROMPT = "p3budman> "
PO_ON_PROMPT = "po-p3budman> "
#endregion Module Variables and Functions 
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
class BudgetManagerCLIView(cmd2.Cmd):
    # ======================================================================== +
    #region BudgetManagerCLIView class
    """An MVVM View class for BudgetModel implementing a command line interface.
    
    Operates under MVVM pattern, strictly. Instantiated with a blind view_model.
    Using cmd2 package which embeds the argparse package. Cmd2 handles the
    command structure and argparse handles the argument lists for each command.
    TODO: Use ABC for view_model interface.
    """
    # ------------------------------------------------------------------------ +
    # Class variables
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    # Class Methods
    @classmethod
    def create_cmd(cls, opts : argparse.Namespace) -> Dict[str, Any]:
        """Create a command dictionary from the options."""
        return _filter_opts(opts)
    # ------------------------------------------------------------------------ +
    # Constructor
    def __init__(self, data_context : object | MockViewModel = None) -> None:
        super().__init__()
        self._data_context = MockViewModel() if data_context is None else data_context
        self.initialized = False
        self.parse_only = False
        self.terminal_width = 100 # TODO: add to settings.
        # self.cli_parser : BudgetManagerCLIParser = cli_parser
        BudgetManagerCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
    # ------------------------------------------------------------------------ +
    # Properties
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
        """Initialize the BudgetManagerCLIView class."""
        try:
            # self.cli_parser.view_cmd = self
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
    #region CLIViewModel Cmd2 Interface methods
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region execute_cmd method.
    def execute_cmd(self, opts : argparse.Namespace) -> Dict[str, Any]:
        """Send a cmd through the data_context using 
        BudgetManagerCommandInterface implementation."""
        try:
            st = p3u.start_timer()
            if _log_cli_cmd_execute(self, opts): return True, "parse_only"
            cmd = BudgetManagerCLIView.create_cmd(opts)
            status, result = self.data_context.execute_cmd(cmd)
            if status:
                # TODO: cleanup output when 
                self.poutput(f"Result: {str(result)}")
            else:
                self.poutput(f"Error: {str(result)}")
            _log_cli_cmd_complete(self, opts)
            return (status, result)
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    #endregion execute_cmd method.
    # ------------------------------------------------------------------------ +
    #region init command - initialize aspects of the BudgetModel application.
    @with_argparser(init_cmd_parser())
    def do_init(self, opts):
        """Init the data context in the Budget Manager application."""
        try:
            status, result = self.execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion init command - initialize aspects of the BudgetModel application.
    # ------------------------------------------------------------------------ +
    #region Show command - workbooks, status, etc.
    @with_argparser(show_cmd_parser())
    def do_show(self, opts):
        """Show information in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            status, result = self.execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion Show command
    # ------------------------------------------------------------------------ +
    #region Load command - load workbooks
    @with_argparser(load_cmd_parser())
    def do_load(self, opts):
        """Load data in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            status, result = self.execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion Load command - load workbooks
    # ------------------------------------------------------------------------ +
    #region Save command - save workbooks
    @with_argparser(save_cmd_parser())
    def do_save(self, opts):
        """Save data in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            status, result = self.execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion Save command - save workbooks
    # ------------------------------------------------------------------------ +    
    #region Val command - workbooks, status, etc.
    @with_argparser(val_cmd_parser())
    def do_val(self, opts):
        """Val command to examine and set values in Budget Manager application.
        
        The val cmd does various actions depending on the subcommand and options
        provided. The subcommands are:
            parse_only: toggle, on, off
            wf_key: <workflow key>
            wb_name: <workbook name>
            fi_key: <financial institution key>

        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. 
        """
        try:
            _ = _log_cli_cmd_execute(self, opts)
            self.val_command(opts)
            _log_cli_cmd_complete(self, opts)
        except SystemExit:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    #endregion Val command
    # ------------------------------------------------------------------------ +
    #region exit and quit commands
    def do_exit(self, args):
        """Exit the Budget Manager CLI."""
        # if _log_cli_cmd_execute(self, args): return
        self.poutput("Exiting Budget Manager CLI.")
        # _log_cli_cmd_complete(self, args)
        return True 
    def do_quit(self, args):
        """Quit the BudgetModel CLI."""
        # if _log_cli_cmd_execute(self, args): return
        self.poutput("Quitting BudgetModel CLI.")
        # _log_cli_cmd_complete(self, args)
        return True 
    #endregion exit and quit commands
    # ------------------------------------------------------------------------ +    
    #endregion CLIViewModel Cmd methods
    # ======================================================================== +

    # ======================================================================== +
    #region Command and Subcommand Execution methods
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region val_command() method
    def val_command(self, opts) -> None:
        """Examine or set values in Budget Manager."""
        try:
            _ = _show_args_only(self, opts)
            if opts.val_cmd == "parse_only":
                if opts.po_value == "toggle":
                    self.parse_only = not self.parse_only
                elif opts.po_value == "on":
                    self.parse_only = True
                elif opts.po_value == "off":
                    self.parse_only = False
                else:
                    self.poutput("Invalid value for parse_only. "
                                 "Use on|off|toggle.")
                BudgetManagerCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
                self.poutput(f"parse_only: {self.parse_only}")
            elif opts.val_cmd == "wf_key":
                _ = opts.wf_ref
            elif opts.val_cmd == "wb_name":
                _ = opts.wb.ref
            elif opts.val_cmd == "fi_key":
                _ = opts.fi_ref
            else:
                self.poutput(f"Nothing to do here: {str(opts)}.")
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion val_command() method
    # ------------------------------------------------------------------------ +
    #endregion Command and Subcommand Execution methods
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
