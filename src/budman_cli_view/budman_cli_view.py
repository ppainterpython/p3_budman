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
#region    cli_view_cp_user_output()
@p3m.cp_user_message_callback
def cli_view_cp_user_output(m: p3m.CPUserOutputMessage) -> None:
    """Output user messages from the Command Processor to the CLI View."""
    try:
        tag = m.tag.upper()
        msg = m.message
        if tag == p3m.CP_INFO:
            console.print(f"[bold green]{p3m.CP_INFO:>7}:[/bold green] {msg}")
        elif tag == p3m.CP_WARNING:
            console.print(f"[bold orange]{p3m.CP_WARNING:>7}:[/bold orange] {msg}")
        elif tag == p3m.CP_ERROR:
            console.print(f"[bold red]{p3m.CP_ERROR:>7}:[/bold red] {msg}")
        elif tag == p3m.CP_DEBUG:
            console.print(f"[bold blue]{p3m.CP_DEBUG:>7}:[/bold blue] {msg}")
        elif tag == p3m.CP_VERBOSE:
            console.print(f"[bold light blue]{p3m.CP_VERBOSE:>7}:[/bold light blue] {msg}")
        elif tag == p3m.CP_CRITICAL:
            console.print(f"[bold dark red]{p3m.CP_CRITICAL:>7}:[/bold dark red] {msg}")
        else:
            console.print(f"[bold blue]{tag}:[/bold blue] {msg}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))        
#endregion cli_view_cp_user_output()
# ---------------------------------------------------------------------------- +
class BudManCLIView(cmd2.Cmd, 
                    BudManAppDataContext_Binding,
                    p3m.CommandProcessor_Binding): 
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
    #region    Class variables
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    #endregion Class variables
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self, 
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 app_name : str = "budman_cli",
                 settings : Optional[bdms.BudManSettings] = None) -> None:
        # Internal attributes for this View
        self._app_name = app_name
        self._settings : bdms.BudManSettings = settings if settings else bdms.BudManSettings()
        self._current_cmd :Optional[str] = None
        self._save_on_exit : bool = True

        # Setup CommandProcessor_Binding 
        p3m.CommandProcessor_Binding.__init__(self, command_processor)
        self.cp_initialized : bool = False

        # Setup CP Msg Svc bindings
        p3m.cp_msg_svc.subscribe_user_message(cli_view_cp_user_output)

        # Setup and initialize cmd2.cmd cli parser
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update({'wf': 'workflow'})
        hfn = self._settings[BUDMAN_CMD_HISTORY_FILENAME]
        cmd2.Cmd.__init__(self, 
                          shortcuts=shortcuts,
                          allow_cli_args=False, 
                          include_ipy=True,
                          persistent_history_file=hfn)
        self.allow_style = ansi.AllowStyle.TERMINAL
        self.register_precmd_hook(self.precmd_hook)
        self.register_postcmd_hook(self.postcmd_hook)
        self.register_postparsing_hook(self.postparsing_hook)
        # Configure set cmd parameters
        self.add_settable(
            cmd2.Settable(cp.CK_PARSE_ONLY, str, 'parse_only mode: on|off|toggle',
                          self, onchange_cb=self._onchange_parse_only)
        )
        self.set_prompt()
        p3m.cp_msg_svc.user_info_message("BudManCLIView initialized.")
    #endregion __init__() method
    # ------------------------------------------------------------------------ +
    #region    BudManCLIView class properties
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
        BudManCLIView.prompt = PO_ON_PROMPT if self.cp_parse_only else PO_OFF_PROMPT

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
    #region    BudManCLIView Methods
    def initialize(self) -> None:
        """Initialize the BudManCLIView class."""
        try:
            logger.info(f"BizEVENT: View setup for BudManCLIView({self._app_name}).")
            # Initialize CommandProcessor.
            self.cp_initialize()    
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
            BudManCLIView.prompt = PO_ON_PROMPT if self.cp_parse_only else PO_OFF_PROMPT
            if self.cp_initialized:
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
    #region    postparsing_hook() Methods
    def postparsing_hook(self, data: cmd2.plugin.PostparsingData) -> cmd2.plugin.PostparsingData:
        """Tweak the cmd args after parsing complete()."""
        try:
            logger.debug(f"Start:")
            # self.cli_parser.view_cmd = self
            self.current_cmd = data.statement.raw
            logger.debug(f"Complete:")
            return data
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion postparsing_hook Methods
    # ------------------------------------------------------------------------ +
    #region    precmd_hook() Methods
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
    #region    postcmd_hook() Methods
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
            # If app exit cmd, handle here.
            if cmd[p3m.CK_SUBCMD_KEY] == cp.CV_EXIT_SUBCMD_KEY:
                # Handle the --no_save switch
                self.save_on_exit = not cmd[cp.CK_NO_SAVE]
                console.print("Exiting Budget Manager CLI.")
                return True
            # Submit the command to the command processor.
            cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
            # Render the result.
            self.cp_output_cmd_result(cmd, cmd_result)
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
            # Render the result.
            self.cp_output_cmd_result(cmd, cmd_result)
        except Exception as e:
            self.pexcept(e)
    #endregion do_change command - change attributes of workbooks and other objects.
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
            # Render the result.
            self.cp_output_cmd_result(cmd, cmd_result)
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
            # Render the result.
            self.cp_output_cmd_result(cmd, cmd_result)
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
            cmd_result: p3m.CMD_RESULT_TYPE  = self.cp_execute_cmd(cmd)
            # Render the result.
            self.cp_output_cmd_result(cmd, cmd_result)
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
           # Submit the command to the command processor.
            cmd_result: p3m.CMD_RESULT_TYPE = self.cp_execute_cmd(cmd)
            # Render the result.
            self.cp_output_cmd_result(cmd, cmd_result)
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
            cmd: p3m.CMD_OBJECT_TYPE = self.construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            cmd_result: p3m.CMD_RESULT_TYPE  = self.cp_execute_cmd(cmd)
            # Output the result.
            self.cp_output_cmd_result(cmd, cmd_result)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
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
    #region _onchange_parse_only
    def _onchange_parse_only(self, _param_name, _old, new: str) -> None:
        """parse_only settalbe attribute was changed."""
        if new == "toggle":
            self.cp_parse_only = not self.cp_parse_only
        elif new == "on":
            self.cp_parse_only = True
        elif new == "off":
            self.cp_parse_only = False
    # ------------------------------------------------------------------------ +    
    #
    #endregion BudManCLIView Helper Methods
    # ------------------------------------------------------------------------ +    
    #endregion BudManCLIView class
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
