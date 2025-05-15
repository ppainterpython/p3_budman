# ---------------------------------------------------------------------------- +
#region budmod_cli_parser.py module
""" budmod_cli_parser.py cli argument parsing for BudgetModelCLIView class.
"""
#endregion budmod_cli_parser.py module
# ---------------------------------------------------------------------------- +
#region Imports

# python standard library modules and packages
import logging, shutil, argparse

# third-party modules and packages
from config import settings
import p3_utils as p3u, p3logging as p3l
import cmd2
from cmd2 import (Cmd2ArgumentParser, with_argparser)

# local modules and packages

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings.app_name)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManCmd2ArgumentParser(cmd2.Cmd2ArgumentParser):
    def __init__(self, *args, **kwargs):
        """Initialize the BudManCmd2ArgumentParser class."""
        terminal_width = shutil.get_terminal_size().columns
        kwargs["formatter_class"] = lambda prog: argparse.HelpFormatter(
            prog, max_help_position=terminal_width - 2,
            width=terminal_width - 2)
        super().__init__(*args, **kwargs)
    def format_help(self):
        """Dynamically adjust width before printing help text."""
        terminal_width = shutil.get_terminal_size().columns  # Get current terminal width
        self.formatter_class = lambda prog: argparse.HelpFormatter(prog, width=terminal_width)
        return super().format_help()  # Call parent method

class BudgetModelCLIParser():
    """A class to parse command line arguments for the BudgetModelCLIView class.

    This class is used to parse command line arguments for the BudgetModelCLIView
    class. It uses the cmd2 library to create a command line interface for the
    BudgetModel application.
    """
    def __init__(self, view_cmd_input : cmd2.Cmd = None) -> None:
        """Initialize the BudgetModelCLIParser class."""
        self.view_cmd : cmd2.Cmd = view_cmd_input
        self.init_cmd_parser = BudManCmd2ArgumentParser()
        self.show_cmd_parser = BudManCmd2ArgumentParser()
        self.load_cmd_parser = BudManCmd2ArgumentParser()
        self.save_cmd_parser = BudManCmd2ArgumentParser()
        self.val_cmd_parser = BudManCmd2ArgumentParser()
        self.init_cmd_parser_setup()
        self.show_cmd_parser_setup()
        self.load_cmd_parser_setup()
        self.save_cmd_parser_setup()
        self.val_cmd_parser_setup()

    def setup(self) -> None:
        """Setup the command line argument parsers."""
        try:
            if self.view_cmd is None or not isinstance(self.view_cmd, cmd2.Cmd):
                m = "BudgetModelCLIParser: Error with configuration. "
                m += "view_cmd is None or not a cmd2.Cmd object."
                raise RuntimeError(m)
            # Initialize the command line argument parsers.
            self.init_cmd_parser_setup()
            self.show_cmd_parser_setup()
            self.load_cmd_parser_setup()
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def init_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the init command."""
        try:
            self.init_cmd_subparsers = self.init_cmd_parser.add_subparsers(
                dest="init_cmd")
            self.init_wb_subcmd_parser = self.init_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Initialize workbook(s).")
            self.init_wb_subcmd_parser.add_argument(
                "wb_name", nargs="?", 
                action="store", 
                default=None,
                help="Workbook name.")
            self.init_fi_subcmd_parser = self.init_cmd_subparsers.add_parser(
                "financial_institutions",
                aliases=["fi", "FI"], 
                help="Initialize Financial Institution(s).")
            self.init_fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def show_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the show command."""
        try:
            self.show_cmd_subparsers = self.show_cmd_parser.add_subparsers(
                dest="show_cmd")
            # show FI subcommand
            self.show_fi_subcmd_parser = self.show_cmd_subparsers.add_parser(
                "financial_institutions",
                aliases=["fi", "FI"], 
                help="Show Financial Institution information.")
            self.show_fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.") 
            # show WF subcommand
            self.show_wf_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workflows",
                aliases=["wf", "WF"], 
                help="Show Workflow information.")
            self.show_wf_subcmd_parser.add_argument(
                "wf_key", nargs="?", 
                action="store", 
                default='all',
                help="Workflow key value.")
            # show WB subcommand
            self.show_wb_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Show workbook information.")
            self.show_wb_subcmd_parser.add_argument(
                "wb_ref", nargs="?", 
                action="store", 
                default='all',
                help="Workbook name.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def load_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the load command."""
        try:
            self.load_cmd_parser.add_argument(
                "wb", 
                nargs="?", 
                action="store", 
                default=True,
                help="Load workbooks.")
            self.load_cmd_parser.add_argument(
                "-w", 
                action="store", 
                default = "categorization",
                help="Workflow for workbooks to load.") 
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def save_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the save command."""
        try:
            # Save budget_manager_store subcommand
            self.save_cmd_subparsers = self.save_cmd_parser.add_subparsers(
                dest="save_cmd")
            self.save_bm_store_subcmd_parser = self.save_cmd_subparsers.add_parser(
                "budget_manager_store",
                aliases=["store", "BMS"], 
                help="Save the Budget Manager Store file.")
            # save workbooks subcommand
            self.save_wb_subcmd_parser  = self.save_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Save workbook information.")
            self.save_wb_subcmd_parser.add_argument(
                "wb_ref", nargs="?", 
                action="store", 
                default='all',
                help="Workbook reference, name or number from show workbooks.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    def val_cmd_parser_setup(self) -> None:
        """Examine or Set values in the application settings and data."""
        try:
            self.val_cmd_subparsers = self.val_cmd_parser.add_subparsers(
                dest="val_cmd")
            # set parse_only subcommand
            self.val_po_subcmd_parser = self.val_cmd_subparsers.add_parser(
                "parse_only",
                aliases=["po", "PO"], 
                help="Set cli to parse-only mode to on|off|toggle ")
            self.val_po_subcmd_parser.add_argument(
                "po_value", nargs="?", 
                default= "toggle",
                help="parse-only value: on | off | toggle.")
            # set wf_key subcommand
            self.val_wf_key_subcmd_parser = self.val_cmd_subparsers.add_parser(
                "current_wf_key",
                aliases=["wf", "WF"], 
                help="Set current wf_key value.")
            self.val_wf_key_subcmd_parser.add_argument(
                "wf_key", nargs="?", 
                action="store", 
                default='all',
                help="wf_key value for valid workflow or 'all'.")
            # show fi_key subcommand
            self.val_fi_key_subcmd_parser  = self.val_cmd_subparsers.add_parser(
                "current_fi_key",
                aliases=["fi", "FI"], 
                help="Set current fi_key.")
            self.val_fi_key_subcmd_parser.add_argument(
                "fi_ref", nargs="?", 
                action="store", 
                default='all',
                help="fi_key value for valid Fin. Inst. or 'all'.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    # ------------------------------------------------------------------------ +
