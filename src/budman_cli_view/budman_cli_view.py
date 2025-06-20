# ---------------------------------------------------------------------------- +
#region budman_cli_view.py module
""" budman_cli_view.py cli-style view for Budget Manager.

A simple command line interface for the Budget Manager (BudMan) application. 
Using the cmd2 package which embeds the argparse package. Cmd2 handles the 
command structure and argparse handles the argument lists for each command. 
The BudManCLIView class is a subclass of cmd2.Cmd and implements the 
command line interface for the user.

This is an MVVM View object for BudMan. It binds to a an object providing
the ViewModelCommandProcessor interface. The command_processor object provides 
a defined interface supporting Command execution.

CLI Argument Parsing
--------------------

Argparse is very declarative. To separate the command line parsing from the 
code that executes commands, where the View Model methods are called, we use the
class BudgetModelCLIParser to manage all of the argparse setup work. It is
considered an inner class of the BudgetManagerCLIView class. But the argument
declarations are contained in that one class, separate from the View code.

"""
#endregion budman_cli_view.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any
# third-party modules and packages
from rich.console import Console
import p3_utils as p3u, pyjson5, p3logging as p3l
import cmd2, argparse
from cmd2 import (Cmd2ArgumentParser, with_argparser)
# local modules and packages
from budman_namespace.design_language_namespace import *
from budman_settings import *
from budman_cli_view import BudManCLIParser
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
console = Console(force_terminal=True,width=BUDMAN_WIDTH, highlight=True,
                  soft_wrap=False)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Configure the CLI parser
# Setup the command line argument parsers. This is required due to the
# cmd2.with_argparser decorator, which requires a callable to return a 
# Cmd2ArgumentParser object. If one fails during setup(), the goal is the
# whole app won't fail, and will display the error message for the
# particular command parser.
# TODO: how to get the app_name from settings prior to BudManCLIView instantiation?
cli_parser : BudManCLIParser = BudManCLIParser("p3_budget_manager")
def init_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    subcmd_parser = cli_parser.init_cmd if cli_parser else None
    return subcmd_parser
def show_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.show_cmd if cli_parser else None
def load_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.load_cmd if cli_parser else None
def save_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.save_cmd if cli_parser else None
def val_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.val_cmd if cli_parser else None
def workflow_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.workflow_cmd if cli_parser else None
def change_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.change_cmd if cli_parser else None
def app_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.app_cmd if cli_parser else None

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
def _show_args_only(cli_view : "BudManCLIView", opts) -> bool:
    oc = vars(opts).copy()
    oc.pop('cmd2_statement')
    oc.pop('cmd2_handler')
    cli_view.poutput(f"args: {str(oc)} parse_only: {cli_view.parse_only}")
    return cli_view.parse_only

BMCLI_SYSTEM_EXIT_WARNING = "Not exiting due to SystemExit"
PO_OFF_PROMPT = "p3budman> "
PO_ON_PROMPT = "po-p3budman> "
#endregion Configure the CLI parser 
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
class BudManCLIView(cmd2.Cmd):
    # ======================================================================== +
    #region BudManCLIView class intrinsics
    """An MVVM View class for BudMan implementing a command line interface.
    
    Operates under MVVM pattern, strictly. Instantiated with a blind 
    command_processor object providing the ViewModelCommandProcessor interface.
    Using cmd2 package which embeds the argparse package. Cmd2 handles the
    command structure and argparse handles the argument lists for each command.
    TODO: Use ABC for ViewModelCommandProcessor interface.
    """
    # ------------------------------------------------------------------------ +
    #region Class variables and methods
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    # Class Methods
    @classmethod
    def create_cmd(cls, opts : argparse.Namespace) -> Dict[str, Any]:
        """Create a command dictionary from the options."""
        return _filter_opts(opts)
    #endregion Class variables and methods
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self, 
                 command_processor : object | MockViewModel = None,
                 app_name : str = "budman_cli",
                 settings : BudManSettings = None) -> None:
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update({'wf': 'workflow'})
        self.app_name = app_name
        self._command_processor = MockViewModel() if command_processor is None else command_processor
        self._settings : BudManSettings = settings if settings else BudManSettings()
        self.parse_only = False
        self.terminal_width = 100 # TODO: add to settings.
        cmd2.Cmd.__init__(self, shortcuts=shortcuts)
        # super().__init__()
        BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
        self.initialized = True
    #endregion __init__() method
    # ------------------------------------------------------------------------ +
    #region    BudManCLIView Methods
    def initialize(self) -> None:
        """Initialize the BudManCLIView class."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLIView({self.app_name}).")
            # self.cli_parser.view_cmd = self
            self.initialized = True
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion BudManCLIView Methods
    #endregion BudManCLIView class  intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region ViewModelCommandProcessor interface implementation
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region ViewModelCommandProcessor Interface Properties
    @property
    def command_processor(self) -> object:
        """Get the command_processor property."""
        return self._command_processor
    
    @command_processor.setter
    def command_processor(self, value: object) -> None:
        """Set the command_processor property."""
        if not isinstance(value, (MockViewModel, object)):
            raise ValueError("command_processor must be a MockViewModel or object.")
        self._command_processor = value
    @property
    def CP(self) -> object:
        """Alias for the command_processor property."""
        return self._command_processor
    
    @CP.setter
    def CP(self, value: object) -> None:
        """Alias for the command_processor property."""
        if not isinstance(value, (MockViewModel, object)):
            raise ValueError("command_processor must be a MockViewModel or object.")
        self._command_processor = value
    #endregion ViewModelCommandProcessor Interface Properties
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region ViewModelCommandProcessor Interface Methods
    def cp_execute_cmd(self, opts : argparse.Namespace) -> Tuple[str, Any]:
        """Send a cmd through the command_processor.
         
        This view is a CommandProcessor_Binding, proxy-ing commands through
        a binding setup at setup time, Dependency Injection."""
        try:
            st = p3u.start_timer()
            if _log_cli_cmd_execute(self, opts): 
                console.print(f"Execute Command: {str(_filter_opts(opts))}")
                return True, "parse_only"
            cmd = BudManCLIView.create_cmd(opts)
            status, result = self.CP.execute_cmd(cmd)
            console.print(result)
            # if status:
            #     self.poutput(f"Result: {str(result)}")
            # else:
            #     self.poutput(f"Error: {str(result)}")
            _log_cli_cmd_complete(self, opts)
            return (status, result)
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    #endregion ViewModelCommandProcessor Interface methods
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region ViewModelCommandProcessor Interface Command Execution Methods
    # ------------------------------------------------------------------------ +
    #
    #region init command - initialize aspects of the BudgetModel application.
    @cmd2.with_argparser(init_cmd_parser()) # This decorator links cmd2 with argparse.
    def do_init(self, opts):
        """Initialize aspects of the Data Context for the Budget Manager application."""
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion init command - initialize aspects of the BudgetModel application.
    # ------------------------------------------------------------------------ +
    #region init command - initialize aspects of the BudgetModel application.
    @cmd2.with_argparser(change_cmd_parser()) # This decorator links cmd2 with argparse.
    def do_change(self, opts):
        """Change (ch) attributes of workbooks and other objects in the Data Context for the Budget Manager application."""
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion init command - initialize aspects of the BudgetModel application.
    # ------------------------------------------------------------------------ +
    #region Show command - workbooks, status, etc.
    @cmd2.with_argparser(show_cmd_parser())
    def do_show(self, opts):
        """Show information from the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion Show command
    # ------------------------------------------------------------------------ +
    #region Load command - load workbooks
    @cmd2.with_argparser(load_cmd_parser())
    def do_load(self, opts):
        """Load specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion Load command - load workbooks
    # ------------------------------------------------------------------------ +
    #region Save command - save workbooks
    @cmd2.with_argparser(save_cmd_parser())
    def do_save(self, opts):
        """Save specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion Save command - save workbooks
    # ------------------------------------------------------------------------ +    
    #region Val command - workbooks, status, etc.
    @cmd2.with_argparser(val_cmd_parser())
    def do_val(self, opts):
        """Val command to get and set values in Budget Manager application.
        
        The val cmd does various actions depending on the subcommand and options
        provided. The subcommands are:
            parse_only: toggle, on, off
            wf_key: <workflow key>
            wb_name: <workbook name>
            fi_key: <financial institution key>

        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            _ = _log_cli_cmd_execute(self, opts)
            self.val_subcommand(opts)
            _log_cli_cmd_complete(self, opts)
        except SystemExit:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    #endregion Val command
    # ------------------------------------------------------------------------ +
    #region val_subcommand() method
    def val_subcommand(self, opts) -> None:
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
                BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
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
    #endregion val_subcommand() method
    # ------------------------------------------------------------------------ +
    #region workflow command
    @with_argparser(workflow_cmd_parser())
    def do_workflow(self, opts):
        """Apply a workflow to Budget Manager data.
        
        Workflows are implemented by python code with configuration in the
        BDM_STORE file. In the DataContext (DC), there is a WF_KEY value
        identifying the workflow to use if not specified explicitly in the 
        cmd arguments.

        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.

        """
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion workflow command
    # ------------------------------------------------------------------------ +
    #region app command
    @with_argparser(app_cmd_parser())
    def do_app(self, opts):
        """View and adjust app settings and features.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.

        """
        try:
            status, result = self.cp_execute_cmd(opts)
        except Exception as e:
            self.pexcept(e)
    #endregion app command
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
    #endregion ViewModelCommandProcessor Command Execution Methods
    # ------------------------------------------------------------------------ +
    #
    #endregion ViewModelCommandProcessor interface implementation
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
