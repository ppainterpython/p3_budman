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
import logging, os, sys, getpass, time, copy, threading
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any, Optional, Union, Callable
# third-party modules and packages
from rich import print
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree as RichTree
from rich.console import Console
from rich.table import Table
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
import cmd2, argparse
from cmd2 import with_argparser
# local modules and packages
import budman_settings as bdms
from budman_settings.budman_settings_constants import BUDMAN_CMD_HISTORY_FILENAME
from budman_data_context import BudManAppDataContext_Binding
import budman_namespace as bdm
import budman_command_services as cp
from budman_cli_view import BudManCLIParser
from p3_mvvm.cp_message_service import cp_user_error_message
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
console = Console(force_terminal=True,width=bdm.BUDMAN_WIDTH, highlight=True,
                  soft_wrap=False)

BMCLI_SYSTEM_EXIT_WARNING = "Not exiting due to SystemExit"
# PO_OFF_PROMPT = "p3budman> "
# PO_ON_PROMPT = "po-p3budman> "
PO_OFF_PROMPT = "> "
PO_ON_PROMPT = "> "
TERM_TITLE = "Budget Manager CLI"
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Configure the CLI parser
# Setup the command line argument parsers. Parsers are now initialized
# as a class variable in BudManCLIView for better encapsulation.
# settings = bdms.BudManSettings()
#endregion Configure the CLI parser 
# ---------------------------------------------------------------------------- +
#region    cli_view_cp_user_output()
@p3m.cp_user_message_callback
def cli_view_cp_user_output(m: p3m.CPUserOutputMessage) -> None:
    """Output callback for async user messages from the Command Processor to the CLI View.
       Runs in the PubSub-Worker thread."""
    try:
        tag = m.tag.upper()
        msg = m.message
        budman_cli_view.view_user_message(msg, tag)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))        

#endregion cli_view_cp_user_output()
# ---------------------------------------------------------------------------- +
#region    cli_cmd_result_output() method
@p3m.cp_cmd_result_message_callback
def cli_cmd_result_output(cmd_result: p3m.CMD_RESULT_TYPE) -> None:
    """Output async command results to the CLI View.
       Runs in the PubSub-Worker thread."""
    try:
        if budman_cli_view:
            if budman_cli_view.cp_verbose_log:
                p3m.cp_user_debug_message(f"cli_cmd_result_output: "
                                          f"cmd_result={p3m.cp_CMD_RESULT_summary(cmd_result)}")
            budman_cli_view.output_cmd_result( cmd_result)
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
#endregion cli_cmd_result_output() method
# ---------------------------------------------------------------------------- +

# ============================================================================ +
#region BudManCLIView class
class BudManCLIView(cmd2.Cmd, 
                    p3m.View_Base,
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
    # Initialize the CLI parser as a class variable
    cli_parser: BudManCLIParser | None = None
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    #endregion Class variables
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self, 
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 data_context : Optional[BudManAppDataContext_Binding] = None,
                 app_name : str = "budman_cli",
                 settings : Optional[bdms.BudManSettings] = None) -> None:
        # Internal attributes for this View
        global budman_cli_view
        budman_cli_view = self
        BudManCLIView.cli_parser = BudManCLIParser(settings if settings else bdms.BudManSettings())
        self._app_name = app_name
        self._settings : bdms.BudManSettings = settings if settings else bdms.BudManSettings()
        self._current_cmd :Optional[str] = None
        self._save_on_exit : bool = True

        # Setup CommandProcessor_Binding 
        p3m.CommandProcessor_Binding.__init__(self, command_processor)
        # Bind with the CommandProcessor.
        self.CP.view = self

        # Setup BudManAppDataContext_Binding
        BudManAppDataContext_Binding.__init__(self, data_context)

        # Setup CP Msg Svc bindings
        p3m.cp_msg_svc.subscribe_user_message(cli_view_cp_user_output)
        p3m.cp_msg_svc.subscribe_cmd_result_message(cli_cmd_result_output)

        # Setup and initialize cmd2.cmd cli parser
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update({'wf': 'workflow'})
        hfn = self._settings[BUDMAN_CMD_HISTORY_FILENAME]
        cmd2.Cmd.__init__(self, 
                          shortcuts=shortcuts,
                          allow_cli_args=False, 
                          include_ipy=True,
                          persistent_history_file=hfn)
        # self.allow_style = ansi.AllowStyle.TERMINAL
        self.register_precmd_hook(self.precmd_hook)
        self.register_postcmd_hook(self.postcmd_hook)
        self.register_postparsing_hook(self.postparsing_hook)
        # Configure set cmd parameters
        self.parse_only = False
        self.add_settable(
            cmd2.Settable(cp.CK_PARSE_ONLY, str, 'parse_only mode: on|off|toggle',
                          self, onchange_cb=self._onchange_parse_only)
        )
        self.verbose = False
        self.add_settable(
            cmd2.Settable(cp.CK_VERBOSE, str, 'verbose mode: on|off|toggle',
                          self, onchange_cb=self._onchange_verbose)
        )
        self.set_prompt()
        self.user_info_message("BudManCLIView initialized.")
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
            self.CP.view = self
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
        cwl: str = f"[bold green]{fi_key}[/bold green]:"
        cwl += f"[bold cyan]{wf_key}[/bold cyan]:"
        cwl += f"[bold yellow]{wf_purpose}[/bold yellow]"
        with console.capture() as capture:
            console.print(cwl)
        return capture.get()
    def set_prompt(self) -> None:
        """Set the prompt for the CLI."""
        try:
            # update the dynamic prompt and window title
            BudManCLIView.prompt = PO_ON_PROMPT if self.cp_parse_only else PO_OFF_PROMPT
            if self.cp_initialized:
                # cwl = self.current_working_location()
                # self.prompt = f"{cwl}{BudManCLIView.prompt}"
                self.prompt = f"{BudManCLIView.prompt}"
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
            self.current_cmd = data.statement.raw
            # self.terminal_lock.acquire()
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
            # self.terminal_lock.release()
            # update the dynamic prompt and window title
            self.set_prompt()
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
    @classmethod
    def create_app_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the app command parser."""
        try:
            return cls.cli_parser.app_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @with_argparser(lambda: BudManCLIView.create_app_cmd_parser())
    def do_app(self, opts):
        """View and adjust app settings and features.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.

        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
            # If app exit cmd, handle here.
            if cmd[p3m.CK_SUBCMD_KEY] == cp.CV_EXIT_SUBCMD_KEY:
                # Handle the --no_save switch
                self.save_on_exit = not cmd[cp.CK_NO_SAVE]
                console.print("Exiting Budget Manager CLI.")
                return True
            # Submit the command to the command processor.
            _ = self.cp_execute_cmd(cmd)
        except Exception as e:
            self.pexcept(e)
    #endregion do_app command
    # ------------------------------------------------------------------------ +
    #region do_change command - change attributes of workbooks and other objects.
    @classmethod
    def create_change_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the change command parser."""
        try:
            return cls.cli_parser.change_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_change_cmd_parser()) # This decorator links cmd2 with argparse.
    def do_change(self, opts):
        """Change (ch) attributes of workbooks and other objects in the Data Context for the Budget Manager application."""
        try:
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            _ = self.cp_execute_cmd(cmd)
        except Exception as e:
            self.pexcept(e)
    #endregion do_change command - change attributes of workbooks and other objects.
    # ------------------------------------------------------------------------ +
    #region do_list command - workbooks, status, etc.
    @classmethod
    def create_list_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the list command parser."""
        try:
            return cls.cli_parser.list_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_list_cmd_parser())
    def do_list(self, opts):
        """List information from the Budget Manager application.

        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # list_parser = self._command_parsers.get(self.do_list)
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.Command = self.construct_command_from_argparse(opts)
            # Submit the command to the command processor.
            _ = self.cp_execute_cmd(cmd)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.pexcept(m)
    #endregion do_show command
    # ------------------------------------------------------------------------ +
    #region do_load command - load workbooks
    @classmethod
    def create_load_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the load command parser."""
        try:
            return cls.cli_parser.load_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_load_cmd_parser())
    def do_load(self, opts):
        """Load specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            _ = self.cp_execute_cmd(cmd)
        except Exception as e:
            self.pexcept(e)
    #endregion do_load command - load workbooks
    # ------------------------------------------------------------------------ +
    #region restart command - restart the application.
    @classmethod
    def create_restart_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the restart command parser."""
        try:
            return cls.cli_parser.restart_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

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
    @classmethod
    def create_show_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the show command parser."""
        try:
            return cls.cli_parser.show_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_show_cmd_parser())
    def do_show(self, opts):
        """Show information from the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
            # _  = self.cp_execute_cmd(cmd)
            cr : p3m.CMD_RESULT_TYPE  = self.cp_execute_cmd_async(
                cmd,
                async_result_subscriber=cli_cmd_result_output
                )
            ...
        except Exception as e:
            self.pexcept(e)
    #endregion do_show command
    # ------------------------------------------------------------------------ +
    #region do_save command - save workbooks
    @classmethod
    def create_save_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the save command parser."""
        try:
            return cls.cli_parser.save_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_save_cmd_parser())
    def do_save(self, opts):
        """Save specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
           # Submit the command to the command processor.
            _ = self.cp_execute_cmd(cmd)
        except Exception as e:
            self.pexcept(e)
    #endregion do_save command - save workbooks
    # ------------------------------------------------------------------------ +
    #region do_close command - close workbooks
    @classmethod
    def create_close_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the close command parser."""
        try:
            return cls.cli_parser.close_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_close_cmd_parser())
    def do_close(self, opts):
        """Close specified data objects in the Budget Manager application.
        
        Arguments:
            opts (argparse.Namespace): The command line options after parsing
            the arguments with argparse. The opts dict becomes the command
            object for the command processor.
        """
        try:
            # Construct the command object from cmd2's argparse Namespace.
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
           # Submit the command to the command processor.
            _ = self.cp_execute_cmd(cmd)
        except Exception as e:
            self.pexcept(e)
    #endregion do_close command - close workbooks
    # ------------------------------------------------------------------------ +
    #region do_workflow command
    @classmethod
    def create_workflow_cmd_parser(cls) -> cmd2.Cmd2ArgumentParser:
        """Create the workflow command parser."""
        try:
            return cls.cli_parser.workflow_cmd if cls.cli_parser else None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @cmd2.with_argparser(lambda: BudManCLIView.create_workflow_cmd_parser())
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
            cmd: p3m.CMD_OBJECT_TYPE = self.cp_construct_cmd_from_argparse(opts)
            # Submit the command to the command processor.
            _  = self.cp_execute_cmd(cmd)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            self.pexcept(e)
    #endregion do_workflow command
    # ------------------------------------------------------------------------ +
    #region cmd_result_output() method
    def output_cmd_result(self, cmd_result: p3m.CMD_RESULT_TYPE):
        """Output command results to the CLI View."""
        try:
            if (cmd_result is None or 
                not p3m.cp_is_CMD_RESULT(cmd_result)):
                self.cp_cmd_result_output_error(f"Invalid command result: {str(cmd_result)}")
                return
            if not cmd_result.get(p3m.CK_CMD_RESULT_STATUS, False):
                # If the command result status is False, output the error message.
                self.cp_cmd_result_output_error(cmd_result)
                return
            result_type = cmd_result.get(p3m.CK_CMD_RESULT_CONTENT_TYPE, None)
            result_content: Any = cmd_result.get(p3m.CK_CMD_RESULT_CONTENT, "")
            # CMD_STRING_OUTPUT
            if result_type == p3m.CV_CMD_STRING_OUTPUT:
                # OUTPUT_STRING input is a simple string.
                self.view_user_message(result_content, p3m.CP_INFO)
            # CMD_LIST_OUTPUT
            elif result_type == cp.CV_CMD_LIST_OUTPUT:
                # Python list (list) input object.
                self.view_user_message(result_content, p3m.CP_INFO)
            # CMD_DICT_OUTPUT
            elif result_type == cp.CV_CMD_DICT_OUTPUT:
                # Python dictionary (dict) input object.
                output_str: str = p3u.first_n(str(result_content), 100)
                self.view_user_message(output_str, p3m.CP_INFO)
            # CV_CMD_JSON_OUTPUT
            elif result_type == cp.CV_CMD_JSON_OUTPUT:
                # CV_CMD_JSON_OUTPUT input is a JSON string.
                console.print_json(result_content)
            # CV_CMD_TREE_OBJECT
            elif result_type == cp.CV_CMD_TREE_OBJECT:
                # CMD_RESULT content is a treelib.Tree.
                formatted_tree = p3u.format_tree_view(result_content)
                console.print(formatted_tree)
            elif result_type == cp.CV_CMD_RICHTREE_OBJECT:
                # CMD_RESULT content is a RichTree.
                self.view_user_message(result_content, p3m.CP_NONE)
            # CV_CMD_FILE_TREE_OBJECT
            elif result_type == cp.CV_CMD_FILE_TREE_OBJECT:
                # CMD_RESULT content is a treelib.Tree with file information.
                formatted_tree = p3u.format_tree_view(result_content)
                console.print(formatted_tree)
            # CV_CMD_WORKBOOK_TREE_OBJECT
            elif result_type == cp.CV_CMD_WORKBOOK_TREE_OBJECT:
                # CV_CMD_WORKBOOK_TREE_OBJECT input is a treelib.Tree with workbook information.
                formatted_tree = p3u.format_tree_view(result_content)
                console.print(formatted_tree)
            # CV_CMD_WORKBOOK_INFO_TABLE
            elif result_type == cp.CV_CMD_WORKBOOK_INFO_TABLE:
                # INFO_TABLE input is an array dictionaries.
                hdr = list(result_content[0].keys()) if result_content else []
                table = Table(*hdr, show_header=True, header_style="bold green")
                for row in result_content:
                    table.add_row(*[str(cell) for cell in row.values()])
                console.print(table)
            else:
                logger.warning(f"Unknown command result type: {result_type}")
                self.view_user_message(result_content, p3m.CP_WARNING)
        except Exception as e:
            self.cp_cmd_result_output_error(f"Error processing command result: {e}") 
    
    def cp_cmd_result_output_error(self, error_msg: str) -> None:
        """Output command result error messages to the CLI View."""
        try:
            console.print(f"[bold red]ERROR:[/bold red] {error_msg}")
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
    #endregion cmd_result_output() method
    # ------------------------------------------------------------------------ +
    #
    #endregion BudManCLIView do_ommand Execution Methods
    # ======================================================================== +

    # ======================================================================== +
    #region BudManCLIView direct user output methods
    # ------------------------------------------------------------------------ +
    #
    # ------------------------------------------------------------------------ +
    #region view_user_message()
    def view_user_message(self, msg: Optional[str], tag: Optional[str]) -> None:
        """Output user messages from the Command Processor to the CLI View."""
        try:
            if not self.is_valid_user_message_type(msg):
                return
            if p3u.str_empty(tag):
                tag = p3m.CP_INFO
            prefix: str = ""
            with self.terminal_lock:
                if tag == p3m.CP_NONE:
                    # When CP_NONE, just output the message with no prefix.
                    console.print(msg)
                    return
                for n, line in enumerate(msg.splitlines(), start=1):
                    if tag == p3m.CP_INFO:
                        prefix = f"[bold green]{p3m.CP_INFO:>7}:[/bold green] "
                    elif tag == p3m.CP_WARNING:
                        prefix = f"[bold orange]{p3m.CP_WARNING:>7}:[/bold orange] "
                    elif tag == p3m.CP_ERROR:
                        prefix = f"[bold red]{p3m.CP_ERROR:>7}:[/bold red] "
                    elif tag == p3m.CP_DEBUG:
                        prefix = f"[bold blue]{p3m.CP_DEBUG:>7}:[/bold blue] "
                    elif tag == p3m.CP_VERBOSE:
                        prefix = f"[bold light blue]{p3m.CP_VERBOSE:>7}:[/bold light blue] "
                    elif tag == p3m.CP_CRITICAL:
                        prefix = f"[bold dark red]{p3m.CP_CRITICAL:>7}:[/bold dark red] "
                    else:
                        prefix = ""
                    self.poutput(f"{prefix}{line}", markup=True)
                    # console.print(f"{prefix}{line}")
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
    #endregion view_user_message()
    # ------------------------------------------------------------------------ +    
    #region is_valid_user_message_type()
    def is_valid_user_message_type(self, msg: Any|None) -> bool:
        """Check if the provided msg is a valid user message type."""
        if msg is not None and isinstance(msg, (str, RichTree)):
            return True
        return False
    #endregion is_valid_user_message_type()
    # ------------------------------------------------------------------------ +    
    #region BudManCLIView user message methods
    def user_info_message(self, message: str, log: bool = True) -> None:
        """Publish a user INFO message."""
        self.view_user_message(message, p3m.CP_INFO)
        if log:
            logger.info(message)

    def user_warning_message(self, message: str, log: bool = True) -> None:
        """Publish a user WARNING message."""
        self.view_user_message(message, p3m.CP_WARNING)
        if log:
            logger.warning(message)
            
    def user_error_message(self, message: str, log: bool = True) -> None:
        """Publish a user ERROR message."""
        self.view_user_message(message, p3m.CP_ERROR)
        if log:
            logger.error(message)

    def user_debug_message(self, message: str, log: bool = True) -> None:
        """Publish a user DEBUG message."""
        self.view_user_message(message, p3m.CP_DEBUG)
        if log:
            logger.debug(message)

    def user_verbose_message(self, message: str, log: bool = True) -> None:
        """Publish a user VERBOSE message."""
        if self.verbose_log:    
            self.view_user_message(message, p3m.CP_VERBOSE)
        if log:
            logger.debug(message)
    def user_none_message(self, message: str, log: bool = True) -> None:
        """Publish a user message with no prefix."""
        self.view_user_message(message, p3m.CP_NONE)
        if log:
            logger.debug(message)
    def user_message(self, message: str, log: bool = True) -> None:
        """Publish a user message with no prefix."""
        self.user_none_message(message)
    #region BudManCLIView user message methods
    # ------------------------------------------------------------------------ +    
    #
    # ------------------------------------------------------------------------ +    
    #
    #endregion BudManCLIView direct user output methods
    # ======================================================================== +

    # ======================================================================== +
    #region BudManCLIView Helper Methods
    # ------------------------------------------------------------------------ +
    #
    # ------------------------------------------------------------------------ +
    #region _onchange_parse_only
    def _onchange_parse_only(self, _param_name, _old, new: str) -> None:
        """parse_only settalbe attribute was changed."""
        new = new.lower()
        if new == "toggle":
            self.parse_only = not self.cp_parse_only
        elif new == "on" or new == 'true':
            self.parse_only = True
        elif new == "off" or new == 'false':
            self.parse_only = False
    #endregion _onchange_parse_only
    # ------------------------------------------------------------------------ +    
    #region _onchange_verbose
    def _onchange_verbose(self, _param_name, _old, new: str) -> None:
        """verbose settalbe attribute was changed."""
        new = new.lower()
        if new == "toggle":
            self.verbose = not self.verbose
        elif new == "on" or new == 'true':
            self.verbose = True
        elif new == "off" or new == 'false':
            self.verbose = False 
        self.cp_verbose_log = self.verbose
    #endregion _onchange_verbose
    # ------------------------------------------------------------------------ +    
    #
    #endregion BudManCLIView Helper Methods
    # ======================================================================== +

    # ------------------------------------------------------------------------ +    
#endregion BudManCLIView class
    # ------------------------------------------------------------------------ +    
    #endregion BudManCLIView direct user output methods
    # ------------------------------------------------------------------------ +    

    # ------------------------------------------------------------------------ +    
    #region    construct_command_from_argparse
    def construct_command_from_argparse(self, opts : argparse.Namespace) -> p3m.Command:
        """Construct a valid p3m.Command (cmd) object from cmd2/argparse 
           arguments or raise error."""
        try:
            # Process cmd object core values, either return a valid command 
            # object or raise an error.
            cmd: p3m.Command = self.extract_command_from_argparse_namespace(opts)
            if not cmd:
                raise ValueError("Failed to construct command object from cmd2/argparse arguments.")
            # Process parameters affecting possible cmd.
            # parse_only flag can be set in the view or added to any cmd.
            self.parse_only = cmd.cmd_parms.get(p3m.CK_PARSE_ONLY, False)
            # validate_only flag 
            self.validate_only = cmd.cmd_parms.get(p3m.CK_VALIDATE_ONLY,False)
            # what_if flag 
            self.what_if = cmd.cmd_parms.get(p3m.CK_WHAT_IF, False)
            return cmd
        except SystemExit as e:
            # Handle the case where argparse exits the program
            self.pwarning(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            cp_user_error_message(m)
            raise
    #endregion construct_command_from_argparse
    # ------------------------------------------------------------------------ +
    #region    extract_command_from_argparse_namespace
    def extract_command_from_argparse_namespace(self, opts : argparse.Namespace) -> p3m.Command:
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

            # Convert to p3m.Command instance, remove two common cmd2 attributes, if present.
            # see bottom of https://cmd2.readthedocs.io/en/latest/features/argument_processing/#decorator-order
            opts_dict = vars(opts).copy()
            cmd2_statement: cmd2.Statement = opts_dict.pop('cmd2_statement', None).get()
            cmd2_handler = opts_dict.pop('cmd2_handler', None).get()
            if cmd2_statement is not None:
                # A valid cmd2.cmd will provide a cmd_name, at a minimum.
                # see https://cmd2.readthedocs.io/en/latest/features/commands/#statements
                cmd2_cmd_name = cmd2_statement.command
            # Remove cmd_name, cmd_key, subcmd_name, subcmd_key, cmd_exec_func if present in opts_dict to avoid conflicts with cmd2 attributes.
            # Collect the command attributes present (or not) in the opts_dict.
            cmd_name = opts_dict.pop(p3m.CK_CMD_NAME, cmd2_cmd_name) 
            if p3u.str_empty(cmd_name):
                # Must have cmd_name
                raise ValueError("Invalid: No command name provided.")
            cmd_key = opts_dict.pop(p3m.CK_CMD_KEY, f"{cmd_name}{p3m.CK_CMD_KEY_SUFFIX}")
            subcmd_name = opts_dict.pop(p3m.CK_SUBCMD_NAME, None)
            subcmd_key = opts_dict.pop(p3m.CK_SUBCMD_KEY, 
                    f"{cmd_key}_{subcmd_name}" if subcmd_name else None)
            cmd_exec_func = opts_dict.pop(p3m.CK_CMD_EXEC_FUNC, None)
            # Validate CMD_OBJECT requirements.
            if not p3m.cp_validate_cmd_key_with_name(cmd_name, cmd_key):
                raise ValueError(f"Invalid: cmd_key '{cmd_key}' does not match cmd_name '{cmd_name}'.")
            if (p3u.str_notempty(subcmd_name) and 
                not p3m.cp_validate_subcmd_key_with_name(subcmd_name, cmd_key, subcmd_key)):
                raise ValueError(f"Invalid: subcmd_key '{subcmd_key}' does not "
                                f"match subcmd_name '{subcmd_name}'.")
            cmd: p3m.Command = self.cp_find_command(cmd_key, subcmd_key)
            if cmd:
                cmd.cmd_parms.update(opts_dict)
            return cmd
        except Exception as e:
            cp_user_error_message(p3u.exc_err_msg(e))
            raise ValueError(f"Failed to create command object from cmd2:opts: {e}")
    #endregion extract_command_from_argparse_namespace
    # ------------------------------------------------------------------------ +
# ============================================================================ +

# ---------------------------------------------------------------------------- +
budman_cli_view: BudManCLIView = None