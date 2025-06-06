# ---------------------------------------------------------------------------- +
#region budman_cli_parser.py module
""" budman_cli_parser.py cli argument parsing for BudgetModelCLIView class.
"""
#endregion budman_cli_parser.py module
# ---------------------------------------------------------------------------- +
#region Imports

# python standard library modules and packages
import logging, shutil, argparse
from typing import List
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
import cmd2
from cmd2 import (Cmd2ArgumentParser, with_argparser)
# local modules and packages
from budman_namespace import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManCLIParser():
    """A class to parse command line arguments for the BudgetModelCLIView class.

    This class is used to parse command line arguments for the BudgetModelCLIView
    class. It uses the cmd2 library to create a command line interface for the
    BudgetModel application.
    """
    def __init__(self) -> None:
        """Initialize the BudgetModelCLIParser class."""
        self.init_cmd_parser = cmd2.Cmd2ArgumentParser()
        self.show_cmd_parser = cmd2.Cmd2ArgumentParser()
        self.load_cmd_parser = cmd2.Cmd2ArgumentParser()
        self.save_cmd_parser = cmd2.Cmd2ArgumentParser()
        self.val_cmd_parser = cmd2.Cmd2ArgumentParser()
        self.workflow_cmd_parser = cmd2.Cmd2ArgumentParser()
        self.init_cmd_parser_setup()
        self.show_cmd_parser_setup()
        self.load_cmd_parser_setup()
        self.save_cmd_parser_setup()
        self.val_cmd_parser_setup()
        self.workflow_cmd_parser_setup()

    def init_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the init command."""
        try:
            # init subcommands: workbooks, and fin_inst
            self.init_cmd_subparsers = self.init_cmd_parser.add_subparsers(
                dest="init_cmd")
            # subcommand init workbooks [wb_name] [-fi [fi_key] [-wf [wf_key]]
            self.init_wb_subcmd_parser = self.init_cmd_subparsers.add_parser(
                "workbooks", 
                aliases=["wb", "WB"], 
                help="Initialize workbook(s).")
            self.init_wb_subcmd_parser.set_defaults(init_cmd="workbooks")
            self.init_wb_subcmd_parser.add_argument(
                "wb_name", nargs="?",
                action="store", 
                default=None,
                help="Workbook name.")
            self.init_wb_subcmd_parser.add_argument(
                "-fi", nargs="?", dest="fi_key", 
                default = "all",
                help="FI key value.")
            self.init_wb_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                action="store", 
                default='all',
                help="Workflow key value.")
            # subcommand init fin_int [fi_key] [-wf [wf_key]] [-wb [wb_name]]
            self.init_fi_subcmd_parser = self.init_cmd_subparsers.add_parser(
                "fin_inst",
                aliases=["fi", "FI", "financial_institutions"], 
                help="Initialize Financial Institution(s).")
            self.init_fi_subcmd_parser.set_defaults(init_cmd="fin_inst")
            self.init_fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.")
            self.init_fi_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                action="store", 
                default = 'all',
                help="Workflow key value.")
            self.init_fi_subcmd_parser.add_argument(
                "-wb", nargs="?", dest="wb_name", 
                action="store", 
                default='all',
                help="Workbook name.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def show_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the show command."""
        try:
            # show subcommands: datacontext, workbooks, fin_inst, workflows, and workbooks
            self.show_cmd_subparsers = self.show_cmd_parser.add_subparsers(
                dest="show_cmd")
            self.show_datacontext_subcmd_parser = self.show_cmd_subparsers.add_parser(
                "DATA_CONTEXT",
                aliases=["dc", "DC"],
                help="Show the data context information.")
            self.show_datacontext_subcmd_parser.set_defaults(show_cmd="DATA_CONTEXT")

            # subcommand show fi_inst [fi_key] [-wf [wf_key]] [-wb [wb_name]]
            self.show_fi_subcmd_parser = self.show_cmd_subparsers.add_parser(
                "fin_inst",
                aliases=["fi", "FI", "financial_institutions"], 
                help="Show Financial Institution information.")
            self.show_fi_subcmd_parser.set_defaults(show_cmd="fin_inst")
            self.show_fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.") 
            # show workflows subcommand
            self.show_wf_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workflows",
                aliases=["wf", "WF"], 
                help="Show Workflow information.")
            self.show_wf_subcmd_parser.set_defaults(show_cmd="workflows")
            self.show_wf_subcmd_parser.add_argument(
                "wf_key", nargs="?", 
                action="store", 
                default = 'all',
                help="Workflow key value.")
            # show workbooks subcommand
            self.show_wb_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Show workbook information.")
            self.show_wb_subcmd_parser.set_defaults(show_cmd="workbooks")
            self.show_wb_subcmd_parser.add_argument(
                "wb_ref", nargs="?", 
                action="store", 
                default='all',
                help="Workbook reference, name or number from show workbooks.")
            self.show_wb_subcmd_parser.add_argument(
                "-i", "--info", 
                nargs="?", 
                required=False, 
                dest="wb_info",
                action="store",
                const = 'info', 
                default = None,  # info | verbose
                help="Show additional information about the workbook.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def load_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the load command."""
        try:
            # Load subcommands: BDM_STORE, workbooks
            self.load_cmd_subparsers = self.load_cmd_parser.add_subparsers(
                dest="load_cmd")
            # subcommand load BDM_STORE
            self.load_bm_store_subcmd_parser = self.load_cmd_subparsers.add_parser(
                "BDM_STORE",
                aliases=["store", "bms", "BMS", "budget_manager_store","BDM_STORE"], 
                help="Load the Budget Manager Store file.")
            self.load_bm_store_subcmd_parser.set_defaults(load_cmd="BDM_STORE")
            # subcommand load workbooks [wb_name] [fi_key]
            self.load_wb_subcmd_parser  = self.load_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Load workbook information.")
            self.load_wb_subcmd_parser.set_defaults(load_cmd="workbooks")
            self.load_wb_subcmd_parser.add_argument(
                "wb_ref", nargs="?",
                action="store", 
                default='all',
                help="Workbook reference, name or number from show workbooks.")
            self.load_wb_subcmd_parser.add_argument(
                "-fi", nargs="?", dest="fi_key", 
                default= "all",
                help="FI key value.") 
            self.load_wb_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                default= "all",
                help="WF key value.") 
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def save_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the save command."""
        try:
            # Save subcommands: BDM_STORE, workbooks
            self.save_cmd_subparsers = self.save_cmd_parser.add_subparsers(
                dest="save_cmd")
            # subcommand save BDM_STORE
            self.save_bm_store_subcmd_parser = self.save_cmd_subparsers.add_parser(
                "BDM_STORE",
                aliases=["store", "bms", "BMS", "budget_manager_store","BDM_STORE"], 
                help="Save the Budget Manager Store file.")
            self.save_bm_store_subcmd_parser.set_defaults(save_cmd="BDM_STORE")
            # subcommand save workbooks [wb_name] [fi_key]
            self.save_wb_subcmd_parser  = self.save_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Save workbook information.")
            self.save_wb_subcmd_parser.set_defaults(save_cmd="workbooks")
            self.save_wb_subcmd_parser.add_argument(
                "-wb", nargs="?", dest="wb_ref",
                action="store", 
                default='all',
                help="Workbook reference, name or number from show workbooks.")
            self.save_wb_subcmd_parser.add_argument(
                "-fi", nargs="?", dest="fi_key", 
                default= "all",
                help="FI key value.") 
            self.save_wb_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                default= "all",
                help="WF key value.") 
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def val_cmd_parser_setup(self) -> None:
        """Examine or Set values in the application settings and data."""
        try:
            self.val_cmd_subparsers = self.val_cmd_parser.add_subparsers(
                dest="val_cmd")
            # val parse_only subcommand
            self.val_po_subcmd_parser = self.val_cmd_subparsers.add_parser(
                "parse_only",
                aliases=["po", "PO"], 
                help="Set cli parse-only mode to on|off|toggle, default is toggle.")
            self.val_po_subcmd_parser.set_defaults(val_cmd="parse_only")
            self.val_po_subcmd_parser.add_argument(
                "po_value", nargs="?", 
                default= "toggle",
                help="parse-only value: on | off | toggle. Default is toggle.")
            # val wf_key subcommand
            self.val_wf_key_subcmd_parser = self.val_cmd_subparsers.add_parser(
                "wf_key",
                aliases=["wf", "WF"], 
                help="Set current wf_key value.")
            self.val_wf_key_subcmd_parser.set_defaults(val_cmd="wf_key")
            self.val_wf_key_subcmd_parser.add_argument(
                "wf_ref", nargs="?", 
                action="store", 
                default = 'all',
                help="wf_key value for valid workflow or 'all'.")
            # val wb_name subcommand
            self.val_wb_name_subcmd_parser = self.val_cmd_subparsers.add_parser(
                "wb_name",
                aliases=["wb", "WB"], 
                help="Set current wb_name value.")
            self.val_wb_name_subcmd_parser.set_defaults(val_cmd="wb_name")
            self.val_wb_name_subcmd_parser.add_argument(
                "wb_ref", nargs="?", 
                action="store", 
                default=None,
                help="wb_ref is a name for a workbook.")
            # val fi_key subcommand
            self.val_fi_key_subcmd_parser  = self.val_cmd_subparsers.add_parser(
                "fi_key",
                aliases=["fi", "FI"], 
                help="Set current fi_key.")
            self.val_fi_key_subcmd_parser.set_defaults(val_cmd="fi_key")
            self.val_fi_key_subcmd_parser.add_argument(
                "fi_ref", nargs="?", 
                action="store", 
                default = 'all',
                help="fi_key value for valid Fin. Inst. or 'all'.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def workflow_cmd_parser_setup(self) -> None:
        """Apply workflows to data in Budget Manager."""
        try:
            parser = self.workflow_cmd_parser
            # Add common arguments to the workflow command parser
            common_args = self.add_common_args(parser)
            # Add subparsers for workflow command parser
            self.workflow_cmd_subparsers = parser.add_subparsers(
                dest="workflow_cmd")
            subparsers = self.workflow_cmd_subparsers
            # Workflow subcommands: categorization, reload, check
            # workflow check subcommand
            check_subcmd_parser = subparsers.add_parser(
                "check",
                aliases=["ch"], 
                help="Check some aspect of the workflow data or processing.")
            check_subcmd_parser.set_defaults(
                workflow_cmd="check")
            check_subcmd_parser.add_argument(
                "wb_ref", nargs="?",
                action="store", 
                default='all',
                help="Workbook reference, name or number of a loaded workbook.")
            check_subcmd_parser.add_argument(
                "-f", dest="fix", action="store_true",
                help="switch to fix issues found by check cmd.") 
            # Workflow subcommand: reload
            reload_subcmd_parser = subparsers.add_parser(
                "reload",
                aliases=["r"], 
                help="Reload modules.")
            reload_subcmd_parser.set_defaults(
                workflow_cmd="reload")
            reload_subcmd_parser.add_argument(
                "reload_target", nargs="?",
                action="store", 
                default='category_map',
                help="Name of module to reload, or 'all' re-loadable.")
            # workflow categorization subcommand
            categorization_subcmd_parser = self.workflow_cmd_subparsers.add_parser(
                "categorization",
                aliases=["cat", "CAT", "c"], 
                help="Apply Categorization workflow.")
            categorization_subcmd_parser.set_defaults(
                workflow_cmd="categorization")
            categorization_subcmd_parser.add_argument(
                "wb_ref", nargs="?",
                action="store", 
                default='all',
                help="Workbook reference, name or number of a loaded workbook.")

            # Instead of propagating, just add common args directly to each subparser:
            for subparser in [check_subcmd_parser, reload_subcmd_parser, categorization_subcmd_parser]:
                self.add_common_args(subparser)

        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    def add_common_args(self, parser: cmd2.Cmd2ArgumentParser) -> object:
        """Add common arguments to the provided parser."""
        try:
            common_args = parser.add_argument_group(
                "Common Arguments", 
                "Arguments common to all commands.")
            # Add common arguments to the parser
            common_args.add_argument(
                "--parse-only","-po",  
                action="store_true", 
                help="Command is only parsed with results returned.")
            common_args.add_argument(
                "--validate-only", "-vo", 
                action="store_true", 
                help="Command args are only validated with results returned, but no cmd execution.")
            common_args.add_argument(
                "-wi", "--what-if", 
                action="store_true", 
                help="Return details about what the command would do, but don't to any action.")
            return common_args
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    def propagate_common_args(self, 
                              parser: cmd2.Cmd2ArgumentParser,
                              subparsers: List[cmd2.Cmd2ArgumentParser],
                              common_args: object) -> None:
        """Propagate common arguments to all subparsers."""
        try:
            # Propagate the common arguments to all subparsers
            # It took 4 iterations with Copilot to get this right. On the
            # 4th iteration, I determined its last recommendation was incorrect
            # and I figured it out.
            for subparser in subparsers:
                for action in common_args._group_actions:
                    # kwargs = {key: getattr(action, key) for key in ["help", "default", "type", "choices", "action"] 
                    #           if hasattr(action, key) and isinstance(getattr(action, key), (str, int, bool))}
                    kwargs = {key: getattr(action, key) for key in ["help", "default", "type", "choices", "action"] if hasattr(action, key)}
                    subparser.add_argument(*action.option_strings, **kwargs)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    # ------------------------------------------------------------------------ +
