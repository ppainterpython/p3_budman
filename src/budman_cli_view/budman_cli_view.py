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
import cmd
import logging, os, sys, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any, Optional, Union, Callable
# third-party modules and packages
from rich.console import Console
import p3_utils as p3u, pyjson5, p3logging as p3l
import cmd2, argparse
from cmd2 import (Cmd2ArgumentParser, with_argparser)
from cmd2 import (Bg,Fg, style, ansi)
# local modules and packages
from budman_cli_view.budman_cli_output import cli_view_cmd_output
from budman_settings import *
from budman_settings.budman_settings_constants import BUDMAN_CMD_HISTORY_FILENAME
from p3_mvvm import DataContext_Binding
import budman_namespace as bdm
from budman_cli_view import BudManCLIParser
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
console = Console(force_terminal=True,width=bdm.BUDMAN_WIDTH, highlight=True,
                  soft_wrap=False)

BMCLI_SYSTEM_EXIT_WARNING = "Not exiting due to SystemExit"
PO_OFF_PROMPT = "p3budman> "
PO_ON_PROMPT = "po-p3budman> "
CMD_PARSE_ONLY = "parse_only"
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
settings = BudManSettings()
cli_parser : BudManCLIParser = BudManCLIParser(settings)
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

#endregion Configure the CLI parser 
# ---------------------------------------------------------------------------- +
class BudManCLIView(cmd2.Cmd): # , DataContext_Binding):
    # ======================================================================== +
    #region BudManCLIView class intrinsics
    """An MVVM View class for BudMan implementing a command line interface.
    
    Operates under MVVM pattern, as a View concerned with all users interaction. 
    This View implements a command line interface (CLI) for the Budget Manager
    application. So, user's are typing in commands, which are parsed, validated
    and then executed either locally in the View or downstream in the View_Model.

    A Command Processor pattern is utilized to execute the commands. The View's
    responsibility is to accept, validate and parse the cli input into
    well-formed "command" objects to be executed downstream. 
    
    This view has is based on the cmd2.Cmd class, which runs a cmd loop to
    accept user input, and parse the input into commands with valid argument
    lists. Part of the cmd2.Cmd design is to execute the commands it parses by 
    calling a function named do_<command_name>(). Our design utilizes this 
    feature to initiate command execution. 

    If a command is very local, and can be executed completely in the View
    object, then the code for that command will reside in its "do_<command_name>()" 
    method. Most often, the Command Processor pattern is used to encode the 
    Command Object and submit it for execution to a Command Processor, which
    is linked to the View through binding.

    A Command Processor has a defined interface to accept the command objects 
    and is responsible for executing them in the appropriate context. This 
    View implements the ViewModelCommandProcessor_Base interface, which is a
    contract for command processing in the application. Command Processor 
    interface methods are prefixed with "cp_".

    At app-setup time (Dependency Injection), the view is bound to objects
    providing the ViewModelCommandProcessor_Base and ViewModelDataContext_Base
    interfaces (abstract base class - ABC). There are two techniques available.
    First, a concrete implementation of the DCorCP_Base interface can be applied
    directly in a class. Second, a class providing such a concrete 
    implementation could be subclassed (inherited). Or third, a class 
    implementing a client _Binding to a concrete class can be used. This view
    adopts the third technique, using implementations of the
    ViewModelCommandProcessor_Binding and ViewModelDataContext_Binding 
    interfaces. The _Binding implementations are concrete, either inline or  
    subclassing concrete classes serving as the client-sdk to the concrete 
    service objects.
    TODO: Use ABC for ViewModelCommandProcessor interface.
    """
    # ------------------------------------------------------------------------ +
    #region Class variables and methods
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    # Class Methods
    @classmethod
    def create_cmd_from_cmd2_argparse(cls, opts : argparse.Namespace) -> Dict[str, Any]:
        """Create a CommandProcessor cmd dictionary from argparse.Namespace.
        
        This method is specific to BudManCLIView which utilizes argparse for 
        command line argument parsing integrated with cmd2.cmd for command help
        and execution. It converts the argparse.Namespace object into a
        dictionary suitable for the command processor to execute, but 
        independent of the cmd2.cmd structure and argparse specifics.

        A ViewModelCommandProcessor_Binding implementation must provide valid
        ViewModelCommandProcessor cmd dictionaries to the
        ViewModelCommandProcessor interface. This method is used to convert
        the cmd2.cmd arguments into a dictionary that can be used by the
        ViewModelCommandProcessor_Binding implementation.
        """
        if not isinstance(opts, argparse.Namespace):
            raise TypeError("opts must be an instance of argparse.Namespace.")
        # Convert to dict, remove two common cmd2 attributes, if present.
        cmd = vars(opts).copy()
        cmd.pop('cmd2_statement')
        cmd.pop('cmd2_handler')
        # TODO: validate cmd_key, cmd_name attributes in cmd dict.

        return cmd
    #endregion Class variables and methods
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self, 
                 command_processor : Optional[Callable] = None,
                 app_name : str = "budman_cli",
                 settings : Optional[BudManSettings] = None) -> None:
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update({'wf': 'workflow'})
        self._app_name = app_name
        self._command_processor = command_processor
        self._settings : BudManSettings = settings if settings else BudManSettings()
        self._parse_only :bool = False
        self._current_cmd :Optional[str] = None
        # cmd2.Cmd initialization
        hfn = settings[BUDMAN_CMD_HISTORY_FILENAME]
        cmd2.Cmd.__init__(self, 
                          shortcuts=shortcuts,
                          allow_cli_args=False, 
                         include_ipy=True,
                         persistent_history_file=hfn)
        self.allow_style = ansi.AllowStyle.TERMINAL
        self.register_precmd_hook(self.precmd_hook)
        self.register_postcmd_hook(self.postcmd_hook)
        BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
        self.initialized : bool = True
    #endregion __init__() method
    # ------------------------------------------------------------------------ +
    #region   BudManCLIView class properties
    @property
    def app_name(self) -> str:
        """Get the app_name property."""
        return self._app_name
    @app_name.setter
    def app_name(self, value: str) -> None:
        """Set the app_name property."""
        if not isinstance(value, str):
            raise TypeError("app_name must be a string.")
        self._app_name = value
        BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT

    @property
    def parse_only(self) -> bool:
        """Get the parse_only property."""
        return self._parse_only
    @parse_only.setter
    def parse_only(self, value: bool) -> None:
        """Set the parse_only property."""
        if not isinstance(value, bool):
            raise TypeError("parse_only must be a boolean.")
        self._parse_only = value
        BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT

    @property
    def current_cmd(self) -> Optional[str]:
        """Get the current_cmd property."""
        return self._current_cmd
    @current_cmd.setter
    def current_cmd(self, value: Optional[str]) -> None:
        """Set the current_cmd property."""
        if value is not None and not isinstance(value, str):
            raise TypeError("current_cmd must be a string or None.")
        self._current_cmd = value
        if value:
            logger.debug(f"Current command set to: {value}")
        else:
            logger.debug("Current command cleared.")

    @property
    def settings(self) -> BudManSettings:
        """Get the settings property."""
        return self._settings
    @settings.setter
    def settings(self, value: BudManSettings) -> None:
        """Set the settings property."""
        if not isinstance(value, BudManSettings):
            raise TypeError("settings must be a BudManSettings instance.")
        self._settings = value
        logger.debug(f"Settings updated: {self._settings}")
    #endregion BudManCLIView class properties
    # ------------------------------------------------------------------------ +
    #region    BudManCLIView Methods
    def initialize(self) -> None:
        """Initialize the BudManCLIView class."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLIView({self._app_name}).")
            # self.cli_parser.view_cmd = self
            self.initialized = True
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion BudManCLIView Methods
    # ------------------------------------------------------------------------ +
    #region   precmd_hook() Methods
    def precmd_hook(self, data: cmd2.plugin.PrecommandData) -> cmd2.plugin.PrecommandData:
        """Tweak the cmd args before cp_execute_cmd()."""
        try:
            logger.debug(f"Start:")
            # self.cli_parser.view_cmd = self
            self.current_cmd = data.statement.command
            logger.debug(f"Complete:")
            return data
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion precmd_hook Methods
    # ------------------------------------------------------------------------ +
    #region   postcmd_hook() Methods
    def postcmd_hook(self, data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        """Clean after cmd execution."""
        try:
            logger.debug(f"Start:")
            self.current_cmd = None
            logger.debug(f"Complete:")
            return data
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion postcmd_hook Methods
    # ------------------------------------------------------------------------ +
    #endregion BudManCLIView class  intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region ViewModelCommandProcessor_Binding implementation
    # TODO: Create ViewModelCommandProcessor_Binding class so BudManCLIView
    # can inherit it.
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region ViewModelCommandProcessor_Binding Properties
    @property
    def command_processor(self) -> Callable:
        """Get the command_processor property."""
        return self._command_processor    
    @command_processor.setter
    def command_processor(self, value: Callable) -> None:
        """Set the command_processor property."""
        self._command_processor = value

    @property
    def CP(self) -> Callable:
        """Alias for the command_processor property."""
        return self._command_processor
    
    @CP.setter
    def CP(self, value: Callable) -> None:
        """Alias for the command_processor property."""
        self._command_processor = value
    #endregion ViewModelCommandProcessor_Binding Properties
    # ------------------------------------------------------------------------ +
    #region ViewModelCommandProcessor_Binding Methods
    def cp_execute_cmd(self, cmd : Dict) -> Tuple[bool, Any]:
        """Send a cmd through the command_processor.
         
        This view is a CommandProcessor_Binding, proxy-ing commands through
        a binding setup at setup time, Dependency Injection."""
        try:
            st = p3u.start_timer()
            logger.debug(f"Execute Command: {cmd}")
            status, result = self.CP.cp_execute_cmd(cmd)
            logger.debug(f"Complete Command: {str(cmd)} {p3u.stop_timer(st)}")
            return (status, result)
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    #endregion ViewModelCommandProcessor_Binding methods
    # ------------------------------------------------------------------------ +
    #
    #endregion ViewModelCommandProcessor interface implementation
    # ======================================================================== +

    # ======================================================================== +
    #region BudManCLIView Command Execution Methods
    # ------------------------------------------------------------------------ +
    #
    # ------------------------------------------------------------------------ +
    #region restart command - restart the application.
    def do_restart(self, args):
        """Restart the Budget Manager CLI application."""
        try:
            logger.info(f"BizEVENT: Restarting the application.")
            # Restart the application.
            python = sys.executable
            os.execl(python, python, *sys.argv)
            return 
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion restart command - restart the application.
    # ------------------------------------------------------------------------ +
    #region do_init command - initialize aspects of the BudgetModel application.
    @cmd2.with_argparser(init_cmd_parser()) # This decorator links cmd2 with argparse.
    def do_init(self, opts):
        """Initialize aspects of the Data Context for the Budget Manager application."""
        try:
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                console.print(result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_init command - initialize aspects of the BudgetModel application.
    # ------------------------------------------------------------------------ +
    #region do_change command - change attributes of workbooks and other objects.
    @cmd2.with_argparser(change_cmd_parser()) # This decorator links cmd2 with argparse.
    def do_change(self, opts):
        """Change (ch) attributes of workbooks and other objects in the Data Context for the Budget Manager application."""
        try:
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                console.print(result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_change command - change attributes of workbooks and other objects.
    # ------------------------------------------------------------------------ +
    #region do_show command - workbooks, status, etc.
    @cmd2.with_argparser(show_cmd_parser())
    def do_show(self, opts):
        """Show information from the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                cli_view_cmd_output(cmd, result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_show command
    # ------------------------------------------------------------------------ +
    #region do_load command - load workbooks
    @cmd2.with_argparser(load_cmd_parser())
    def do_load(self, opts):
        """Load specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                console.print(result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_load command - load workbooks
    # ------------------------------------------------------------------------ +
    #region do_save command - save workbooks
    @cmd2.with_argparser(save_cmd_parser())
    def do_save(self, opts):
        """Save specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                console.print(result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_save command - save workbooks
    # ------------------------------------------------------------------------ +
    #region do_val command - workbooks, status, etc.
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
            self.val_subcommand(opts)
        except SystemExit:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    #endregion do_val command
    # ------------------------------------------------------------------------ +
    #region val_subcommand() method
    def val_subcommand(self, opts) -> None:
        """Examine or set values in Budget Manager."""
        try:
            cmd = BudManCLIView.create_cmd_from_cmd2_argparse(opts)
            self.poutput(f"args: {str(cmd)} parse_only: {self.parse_only}")
            if cmd.val_cmd == CMD_PARSE_ONLY:
                if cmd.po_value == "toggle":
                    self.parse_only = not self.parse_only
                elif cmd.po_value == "on":
                    self.parse_only = True
                elif cmd.po_value == "off":
                    self.parse_only = False
                else:
                    self.poutput("Invalid value for parse_only. "
                                 "Use on|off|toggle.")
                BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
                self.poutput(f"parse_only: {self.parse_only}")
            elif cmd.val_cmd == "wf_key":
                _ = cmd.wf_ref
            elif cmd.val_cmd == "wb_name":
                _ = cmd.wb.ref
            elif cmd.val_cmd == "fi_key":
                _ = cmd.fi_ref
            else:
                self.poutput(f"Nothing to do here: {str(cmd)}.")
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion val_subcommand() method
    # ------------------------------------------------------------------------ +
    #region do_workflow command
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
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                console.print(result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_workflow command
    # ------------------------------------------------------------------------ +
    #region do_app command
    @with_argparser(app_cmd_parser())
    def do_app(self, opts):
        """View and adjust app settings and features.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.

        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            status, cmd = self.construct_cmd(opts)
            if not status:
                return
            # Submit the command to the command processor.
            status, result = self.cp_execute_cmd(cmd)
            # Render the result.
            if status:
                console.print(result)
            else:
                console.print(f"[red]Error:[/red] {result}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_app command
    # ------------------------------------------------------------------------ +
    #region do_exit and quit commands
    def do_exit(self, args):
        """Exit the Budget Manager CLI."""
        self.poutput("Exiting Budget Manager CLI.")
        return True 
    def do_quit(self, args):
        """Quit the BudgetModel CLI."""
        self.poutput("Quitting BudgetModel CLI.")
        return True 
    #endregion do_exit and quit commands
    # ------------------------------------------------------------------------ +    
    #region cmd_
    def construct_cmd(self, opts : argparse.Namespace) -> Tuple[bool, Any]:
        """Construct a command object from cmd2/argparse arguments. 
        """
        try:
            cmd = BudManCLIView.create_cmd_from_cmd2_argparse(opts)
            parse_only : bool = self.parse_only or getattr(opts,CMD_PARSE_ONLY, False)
            cmd_line = f"{self.current_cmd} {opts.cmd2_statement.get()}"
            if parse_only: 
                console.print(f"parse-only: '{cmd_line}' {str(cmd)}")
                return False, CMD_PARSE_ONLY
            return True, cmd
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            self.pexcept(e)
    # ------------------------------------------------------------------------ +    
    #
    #endregion BudManCLIView Command Execution Methods
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
