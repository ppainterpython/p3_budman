# ---------------------------------------------------------------------------- +
#region budmod_cli_parser.py module
""" budmod_cli_parser.py cli argument parsing for BudgetModelCLIView class.
"""
#endregion budmod_cli_parser.py module
# ---------------------------------------------------------------------------- +
#region Imports

# python standard library modules and packages
import logging

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

class BudgetModelCLIParser():
    """A class to parse command line arguments for the BudgetModelCLIView class.

    This class is used to parse command line arguments for the BudgetModelCLIView
    class. It uses the cmd2 library to create a command line interface for the
    BudgetModel application.
    """
    def __init__(self, view_cmd_input : cmd2.Cmd = None) -> None:
        """Initialize the BudgetModelCLIParser class."""
        self.view_cmd : cmd2.Cmd = view_cmd_input
        self.init_cmd_parser = Cmd2ArgumentParser()
        self.show_cmd_parser = Cmd2ArgumentParser()
        self.load_cmd_parser = Cmd2ArgumentParser()
        self.init_cmd_parser_setup()
        self.show_cmd_parser_setup()
        self.load_cmd_parser_setup()

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
            self.show_fi_subcmd_parser = self.show_cmd_subparsers.add_parser(
                "financial_institutions",
                aliases=["fi", "FI"], 
                help="Show Financial Institution information.")
            self.show_fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.") 
            self.show_wf_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workflows",
                aliases=["wf", "WF"], 
                help="Show Workflow information.")
            self.show_wf_subcmd_parser.add_argument(
                "wf_key", nargs="?", 
                action="store", 
                default=None,
                help="Workflow key value.")
            self.show_wb_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Show workbook information.")
            self.show_wb_subcmd_parser.add_argument(
                "wb_name", nargs="?", 
                action="store", 
                default=None,
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
    # ------------------------------------------------------------------------ +
