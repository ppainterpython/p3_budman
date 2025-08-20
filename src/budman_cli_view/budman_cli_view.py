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
from rich import print
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree
from rich.console import Console
from rich.table import Table
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
import cmd2, argparse
from cmd2 import (Cmd2ArgumentParser, with_argparser, with_argument_list)
from cmd2 import (Bg,Fg, style, ansi)
# local modules and packages
from budman_cli_view.budman_cli_output import cli_view_cmd_output
import budman_settings as bdms
from budman_settings.budman_settings_constants import BUDMAN_CMD_HISTORY_FILENAME
from budman_data_context import BudManAppDataContext_Binding
import budman_namespace as bdm
import budman_command_processor as cp
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
TERM_TITLE = "Budget Manager CLI"
red = str(Fg.RED)
green = str(Fg.GREEN)
yellow = str(Fg.YELLOW)
blue = str(Fg.BLUE)
magenta = str(Fg.MAGENTA)
cyan = str(Fg.CYAN)
fg_reset = str(Fg.RESET)
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
settings = bdms.BudManSettings()
cli_parser : BudManCLIParser = BudManCLIParser(settings)
def app_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.app_cmd if cli_parser else None
def change_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.change_cmd if cli_parser else None
def init_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    subcmd_parser = cli_parser.init_cmd if cli_parser else None
    return subcmd_parser
def list_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.list_cmd if cli_parser else None
def load_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.load_cmd if cli_parser else None
def save_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.save_cmd if cli_parser else None
def show_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.show_cmd if cli_parser else None
def workflow_cmd_parser() -> cmd2.Cmd2ArgumentParser:
    return cli_parser.workflow_cmd if cli_parser else None

#endregion Configure the CLI parser 
# ---------------------------------------------------------------------------- +
class BudManCLIView(cmd2.Cmd, BudManAppDataContext_Binding,
                    p3m.CommandProcessor_Binding): # , DataContext_Binding 
    # ======================================================================== +
    #region BudManCLIView class intrinsics
    # ------------------------------------------------------------------------ +
    #region doc string
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
    interfaces (abstract base class - ABC). There are three techniques available.
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
    #endregion doc string
    # ------------------------------------------------------------------------ +
    #region Class variables
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    #endregion Class variables
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self, 
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 app_name : str = "budman_cli",
                 settings : Optional[bdms.BudManSettings] = None) -> None:
        # Initialize super() CommandProcessor_Binding.
        p3m.CommandProcessor_Binding.__init__(self)
        self.initialized : bool = False
        self._app_name = app_name
        self._cp = command_processor
        self._settings : bdms.BudManSettings = settings if settings else bdms.BudManSettings()
        self._current_cmd :Optional[str] = None
        self._save_on_exit : bool = True
        # Setup and do cmd2.cmd initialization.
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update({'wf': 'workflow'})
        hfn = self._settings[BUDMAN_CMD_HISTORY_FILENAME]
        cmd2.Cmd.__init__(self, 
                          shortcuts=shortcuts,
                          allow_cli_args=False, 
                         include_ipy=True,
                         persistent_history_file=hfn)
        self.parse_only : bool = False
        self.allow_style = ansi.AllowStyle.TERMINAL
        self.register_precmd_hook(self.precmd_hook)
        self.register_postcmd_hook(self.postcmd_hook)
        self.add_settable(
            cmd2.Settable(cp.CK_PARSE_ONLY, str, 'parse_only mode: on|off|toggle',
                          self, onchange_cb=self._onchange_parse_only)
        )
        self.set_prompt()
        # BudManCLIView.update_terminal_title(f"{TERM_TITLE}")
    #endregion __init__() method
    # ------------------------------------------------------------------------ +
    #region    BudManCLIView Methods
    def initialize(self) -> None:
        """Initialize the BudManCLIView class."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLIView({self._app_name}).")
            self.initialized = True
            self.set_prompt()
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    def current_working_location(self) -> str:
        """Get the current working location."""
        fi_key = self.dc_FI_KEY if self.DC else "unknown"
        wf_key = self.dc_WF_KEY if self.DC else "unknown"
        wf_purpose = self.dc_WF_PURPOSE if self.DC else "unknown"
        cwl: str = f"{fg_reset}({green}{fi_key}:{cyan}{wf_key}:{yellow}{wf_purpose}{fg_reset})"
        return cwl
    def set_prompt(self) -> None:
        """Set the prompt for the CLI."""
        try:
            # update the dynamic prompt and window title
            BudManCLIView.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
            if self.initialized:
                cwl = self.current_working_location()
                # cmd2.Cmd.set_window_title(f"Budget Manager CLI - {cwl}")
                self.prompt = f"{cwl}\n{BudManCLIView.prompt}"
            else:
                self.prompt = f"{BudManCLIView.prompt}"
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
            self.current_cmd = data.statement.raw
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
            # update the dynamic prompt and window title
            self.set_prompt()
            cwl = self.current_working_location()
            # BudManCLIView.update_terminal_title(f"Budget Manager CLI - {cwl}")
            logger.debug(f"Complete:")
            return data
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion postcmd_hook Methods
    # ------------------------------------------------------------------------ +
    #region   BudManCLIView class properties
    
    @property
    def save_on_exit(self) -> bool:
        """Get the save_on_exit property."""
        return self._save_on_exit
    @save_on_exit.setter
    def save_on_exit(self, value: bool) -> None:
        """Set the save_on_exit property."""
        if not isinstance(value, bool):
            raise TypeError("save_on_exit must be a boolean.")
        self._save_on_exit = value

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
    def settings(self) -> bdms.BudManSettings:
        """Get the settings property."""
        return self._settings
    @settings.setter
    def settings(self, value: bdms.BudManSettings) -> None:
        """Set the settings property."""
        if not isinstance(value, bdms.BudManSettings):
            raise TypeError("settings must be a BudManSettings instance.")
        self._settings = value
        logger.debug(f"Settings updated: {self._settings}")
    #endregion BudManCLIView class properties
    # ------------------------------------------------------------------------ +
    #endregion BudManCLIView class  intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region BudManCLIView do_command Execution Methods
    # ------------------------------------------------------------------------ +
    #
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
            # If app exit cmd, handle here.
            if cmd[cp.p3m.CK_SUBCMD_KEY] == cp.CV_EXIT_SUBCMD_KEY:
                # Handle the --no_save switch
                self.save_on_exit = not cmd[cp.CK_NO_SAVE]
                console.print("Exiting Budget Manager CLI.")
                return True
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
    #region do_list command - workbooks, status, etc.
    @cmd2.with_argparser(list_cmd_parser())
    def do_list(self, opts):
        """List information from the Budget Manager application.

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
            cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
            # Render the result.
            if cmd_result[p3m.CMD_RESULT_STATUS]:
                cli_view_cmd_output(cmd, cmd_result)
            else:
                console.print(f"[red]Error:[/red] {cmd_result[p3m.CMD_RESULT_CONTENT]}")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.pexcept(m)
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
            cmd_result: p3m.CMD_RESULT_TYPE  = self.cp_execute_cmd(cmd)
            # Render the result.
            if cmd_result[p3m.CMD_RESULT_STATUS]:
                cli_view_cmd_output(cmd, cmd_result[p3m.CMD_RESULT_DATA])
            else:
                console.print(f"[red]Error:[/red] {cmd_result[p3m.CMD_RESULT_ERROR]}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_show command
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
            cmd_result: p3m.CMD_RESULT_TYPE  = self.cp_execute_cmd(cmd)
            # Render the result.
            if cmd_result[p3m.CMD_RESULT_STATUS]:
                cli_view_cmd_output(cmd, cmd_result[p3m.CMD_RESULT_DATA])
            else:
                console.print(f"[red]Error:[/red] {cmd_result[p3m.CMD_RESULT_ERROR]}")
        except Exception as e:
            self.pexcept(e)
    #endregion do_workflow command
    # ------------------------------------------------------------------------ +
    #
    #endregion BudManCLIView do_ommand Execution Methods
    # ======================================================================== +

    # ======================================================================== +
    #region BudManCLIView Helper Methods
    # ------------------------------------------------------------------------ +
    #
    # ------------------------------------------------------------------------ +
    #region construct_cmd
    def construct_cmd(self, opts : argparse.Namespace) -> Tuple[bool, Any]:
        """Construct a command object from cmd2/argparse arguments."""
        try:
            cmd = self.extract_CMD_OBJECT_from_argparse_Namespace(opts)
            parse_only:bool = self.CP.cp_cmd_attr_get(cmd, p3m.CK_PARSE_ONLY, False)
            if parse_only: 
                console.print(f"parse-only: '{self.current_cmd}' {str(cmd)}")
                return False, cp.CK_PARSE_ONLY
            return True, cmd
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.pexcept(m)
    #endregion construct_cmd
    # ------------------------------------------------------------------------ +
    #region extract_CMD_OBJECT_from_argparse_Namespace
    def extract_CMD_OBJECT_from_argparse_Namespace(self, opts : argparse.Namespace) -> Dict[str, Any]:
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
        try:
            if not isinstance(opts, argparse.Namespace):
                raise TypeError("opts must be an instance of argparse.Namespace.")
            cmd2_cmd_name: str = ''
            cmd_name: str = ''
            cmd_key: str = ''
            subcmd_name: str = ''
            subcmd_key: str = ''
            cmd_exec_func: Optional[Callable] = None

            # Convert to dict, remove two common cmd2 attributes, if present.
            # see bottom of https://cmd2.readthedocs.io/en/latest/features/argument_processing/#decorator-order
            opts_dict = vars(opts).copy()
            cmd2_statement: cmd2.Statement = opts_dict.pop('cmd2_statement', None).get()
            cmd2_handler = opts_dict.pop('cmd2_handler', None).get()
            if cmd2_statement is not None:
                # A valid cmd2.cmd will provide a cmd_name, at a minimum.
                # see https://cmd2.readthedocs.io/en/latest/features/commands/#statements
                cmd2_cmd_name = cmd2_statement.command
            # Collect the command attributes present (or not) in the opts_dict.
            cmd_name = opts_dict.get(p3m.CK_CMD_NAME, cmd2_cmd_name) 
            if p3u.str_empty(cmd_name):
                # Must have cmd_name
                raise ValueError("Invalid: No command name provided.")
            cmd_key = opts_dict.get(p3m.CK_CMD_KEY, f"{cmd_name}{p3m.CMD_KEY_SUFFIX}")
            subcmd_name = opts_dict.get(p3m.CK_SUBCMD_NAME, None)
            subcmd_key = opts_dict.get(p3m.CK_SUBCMD_KEY, 
                    f"{cmd_key}_{subcmd_name}" if subcmd_name else None)
            cmd_exec_func = opts_dict.get(p3m.CK_CMD_EXEC_FUNC, None)
            # Validate CMD_OBJECT requirements.
            if not p3m.validate_cmd_key_with_name(cmd_name, cmd_key):
                raise ValueError(f"Invalid: cmd_key '{cmd_key}' does not match cmd_name '{cmd_name}'.")
            if (p3u.str_notempty(subcmd_name) and 
                not p3m.validate_subcmd_key_with_name(subcmd_name, cmd_key, subcmd_key)):
                raise ValueError(f"Invalid: subcmd_key '{subcmd_key}' does not "
                                f"match subcmd_name '{subcmd_name}'.")
            cmd = p3m.create_CMD_OBJECT(
                cmd_name=cmd_name,
                cmd_key=cmd_key,
                subcmd_name=subcmd_name,
                subcmd_key=subcmd_key,
                cmd_exec_func=cmd_exec_func,
                other_attrs=opts_dict)
            return cmd
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise ValueError(f"Failed to create command object from cmd2:opts: {e}")
    #endregion extract_CMD_OBJECT_from_argparse_Namespace
    # ------------------------------------------------------------------------ +    
    #region _onchange_parse_only
    def _onchange_parse_only(self, _param_name, _old, new: str) -> None:
        """parse_only settalbe attribute was changed."""
        if new == "toggle":
            self.parse_only = not self.parse_only
        elif new == "on":
            self.parse_only = True
        elif new == "off":
            self.parse_only = False
    # ------------------------------------------------------------------------ +    
    #
    #endregion BudManCLIView Helper Methods
    # ------------------------------------------------------------------------ +    
    #endregion BudManCLIView class
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
