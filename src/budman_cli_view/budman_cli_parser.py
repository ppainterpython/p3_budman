# ---------------------------------------------------------------------------- +
#region budman_cli_parser.py module
""" budman_cli_parser.py cli argument parsing for BudgetModelCLIView class.
"""
#endregion budman_cli_parser.py module
# ---------------------------------------------------------------------------- +
#region Imports

# python standard library modules and packages
import logging, shutil
from typing import List
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
import cmd2, argparse
from cmd2 import (Cmd2ArgumentParser, with_argparser)
# local modules and packages
from budman_namespace.design_language_namespace import (
    WB_TYPE_TRANSACTIONS, WB_TYPE_BUDGET, WB_TYPE_CHECK_REGISTER,
    WB_TYPE_BDM_STORE, WB_TYPE_BDM_CONFIG, VALID_WB_TYPE_VALUES)
                              
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManCLIParser():
    #region class BudManCLIParser initialization
    """A class to parse command line arguments for the BudgetModelCLIView class.

    This class is used to parse command line arguments for the BudgetModelCLIView
    class. It uses the cmd2 library to create a command line interface for the
    BudgetModel application.
    """
    def __init__(self,app_name : str = "not-set") -> None:
        """Initialize the BudManCLIParser class."""
        self.app_name = app_name
        self.init_cmd = cmd2.Cmd2ArgumentParser()
        self.show_cmd = cmd2.Cmd2ArgumentParser()
        self.load_cmd = cmd2.Cmd2ArgumentParser()
        self.save_cmd = cmd2.Cmd2ArgumentParser()
        self.val_cmd = cmd2.Cmd2ArgumentParser()
        self.workflow_cmd = cmd2.Cmd2ArgumentParser()
        self.change_cmd = cmd2.Cmd2ArgumentParser()
        self.app_cmd = cmd2.Cmd2ArgumentParser()
        self.init_cmd_parser_setup(app_name)
        self.show_cmd_parser_setup()
        self.load_cmd_parser_setup()
        self.save_cmd_parser_setup()
        self.val_cmd_parser_setup()
        self.workflow_cmd_parser_setup()
        self.change_cmd_parser_setup()
        self.app_cmd_parser_setup()
    #endregion class BudManCLIParser initialization
    # ------------------------------------------------------------------------ +
    #region Command Parser Setup Methods
    def app_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Application settings and feature controls."""
        try:
            parser = self.app_cmd
            parser.prog = app_name
            title = self.app_cmd_parser_setup.__doc__
            # app subcommands: logging
            subparsers = parser.add_subparsers(title=title, dest="app_cmd")
            # app log [handler-name] [--list] [--level [level-value]] [--rollover]
            log_subcmd_parser = subparsers.add_parser(
                "log", 
                # aliases=["log"], 
                help="Workbook reference wb_name, wb_index, or 'all'.")
            log_subcmd_parser.set_defaults(app_cmd="log_subcmd")
            log_subcmd_parser.add_argument(
                "handler_name", nargs="?", 
                default = None,
                help="Optional name of a logging handler.")
            log_subcmd_parser.add_argument(
                "--list", "-ls", dest="list_switch", 
                action = 'store_true',
                help="List information about the logging setup.")
            log_subcmd_parser.add_argument(
                "--level", "-l", nargs="?", dest="level_value", 
                action = 'store',
                default = None,
                help="Optional name or integer logging level designator.")
            log_subcmd_parser.add_argument(
                "--rollover", "-r", dest="rollover_switch", 
                action = 'store_true',
                help="Cause file loggers to rollover now.")
            self.add_common_args(log_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def change_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Change settings."""
        try:
            parser = self.change_cmd
            parser.prog = app_name
            title = f"Change SubCommands"
            # change subcommands: wb_type, wb_ref
            subparsers = parser.add_subparsers(title=title, dest="change_cmd")
            # subcommand init workbooks [wb_name] [-fi [fi_key] [-wf [wf_key]]
            wb_type_subcmd_parser = subparsers.add_parser(
                "wb_ref", 
                aliases=["wb", "workbooks"], 
                help="Workbook reference wb_name, wb_index, or 'all'.")
            wb_type_subcmd_parser.set_defaults(change_cmd="workbooks")
            wb_type_choices = VALID_WB_TYPE_VALUES
            wb_type_subcmd_parser.add_argument(
                "-t", "--wb_type",nargs="?", dest="wb_type", 
                default = None,
                choices=wb_type_choices,
                help="Specify the workbook type to apply.")
            self.add_common_args(wb_type_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def init_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Setup 'init' cmd argument parsers."""
        try:
            parser = self.init_cmd
            parser.prog = app_name
            title = f"Init SubCommands"
            # init subcommands: workbooks, and fin_inst
            subparsers = parser.add_subparsers(title=title, dest="init_cmd")
            # subcommand init workbooks [wb_name] [-fi [fi_key] [-wf [wf_key]]
            wb_subcmd_parser = subparsers.add_parser(
                "workbooks", 
                aliases=["wb", "WB"], 
                help="Initialize workbook(s).")
            wb_subcmd_parser.set_defaults(init_cmd="workbooks")
            wb_subcmd_parser.add_argument(
                "wb_name", nargs="?",
                action="store", 
                default=None,
                help="Workbook name.")
            wb_subcmd_parser.add_argument(
                "-fi", nargs="?", dest="fi_key", 
                default = None,
                help="FI key value.")
            wb_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                action="store", 
                default='all',
                help="Workflow key value.")
            # subcommand init fin_int [fi_key] [-wf [wf_key]] [-wb [wb_name]]
            fi_subcmd_parser = subparsers.add_parser(
                "fin_inst",
                aliases=["fi", "FI", "financial_institutions"], 
                help="Initialize Financial Institution(s).")
            fi_subcmd_parser.set_defaults(init_cmd="fin_inst")
            fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.")
            fi_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                action="store", 
                default = None,
                help="Workflow key value.")
            fi_subcmd_parser.add_argument(
                "-wn", nargs="?", dest="wb_name", 
                action="store", 
                default='all',
                help="Workbook name.")
            for subparser in [fi_subcmd_parser, wb_subcmd_parser]:
                self.add_common_args(subparser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def show_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the show command."""
        try:
            parser = self.show_cmd
            # show subcommands: datacontext, workbooks, fin_inst, workflows, and workbooks
            self.show_cmd_subparsers = self.show_cmd.add_subparsers(
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
                default = None,
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
                default = 'info',  # info | verbose
                help="Show additional information about the workbook.")

            for subparser in [self.show_wb_subcmd_parser, 
                              self.show_wf_subcmd_parser,
                              self.show_fi_subcmd_parser,
                              self.show_datacontext_subcmd_parser]:
                self.add_common_args(subparser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def load_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the load command."""
        try:
            parser = self.load_cmd
            # Load subcommands: BDM_STORE, workbooks, check_register
            subparsers = parser.add_subparsers(dest="load_cmd")

            # BDM_STORE subcommand
            bm_store_subcmd_parser = subparsers.add_parser(
                "BDM_STORE",
                aliases=["store", "bms", "budget_manager_store","BDM_STORE"], 
                help="Load the Budget Manager Store file.")
            bm_store_subcmd_parser.set_defaults(load_cmd="BDM_STORE")

            # WORKBOOK subcommand (wb_index | -all) [fi_key]
            wb_subcmd_parser  = subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Select workbooks for.")
            wb_subcmd_parser.set_defaults(load_cmd="workbooks")
            group = wb_subcmd_parser.add_mutually_exclusive_group(required=True)
            group.add_argument(
                "wb_index", nargs="?",
                type=int, 
                default = -1,
                help=f"Workbook index: number associated in the workbook list, 0-based.")
            group.add_argument(
                "-all", dest="all_wbs", 
                action = "store_true",
                help="All workbooks switch.") 
            wb_subcmd_parser.add_argument(
                "-fi", nargs="?", dest="fi_key", 
                default= None,
                help="FI key value.") 
            wb_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                default= None,
                help="WF key value.") 
            # subcommand load check_register [wb_url]
            check_register_subcmd_parser = subparsers.add_parser(
                "check_register",
                aliases=["checks", "register", "ch", "cr"],
                help="Load a check register csv file.")
            check_register_subcmd_parser.set_defaults(load_cmd="check_register")
            cr_url = "file:///C:/Users/ppain/OneDrive/budget/boa/data/new/CheckRegister_ToDate20250609.csv"
            check_register_subcmd_parser.add_argument(
                "wb_ref", nargs="?",
                action="store", 
                default=cr_url,
                help=f"Workbook url: a 'file://' to a check_register .csv or 'all'.")
            self.add_common_args(parser)
            for subparser in [ 
                              check_register_subcmd_parser,
                              wb_subcmd_parser,
                              bm_store_subcmd_parser]:
                self.add_common_args(subparser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def save_cmd_parser_setup(self) -> None:
        """Save Command: parser setup"""
        try:
            # Save subcommands: BDM_STORE, workbooks
            parser = self.save_cmd
            subparsers = parser.add_subparsers(
                dest="save_cmd")
            # subcommand save BDM_STORE
            self.save_bm_store_subcmd_parser = subparsers.add_parser(
                "BDM_STORE",
                aliases=["store", "bms", "BMS", "budget_manager_store","BDM_STORE"], 
                help="Save the Budget Manager Store file.")
            self.save_bm_store_subcmd_parser.set_defaults(save_cmd="BDM_STORE")
            # subcommand save workbooks [wb_name] [fi_key]
            self.save_wb_subcmd_parser = self.add_WORKBOOKS_subparser(subparsers)
            self.save_wb_subcmd_parser.set_defaults(save_cmd="workbooks")
            self.add_common_args(parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def val_cmd_parser_setup(self) -> None:
        """Examine or Set values in the application settings and data."""
        try:
            self.val_cmd_subparsers = self.val_cmd.add_subparsers(
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
                default = None,
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
                default = None,
                help="fi_key value for valid Fin. Inst. or 'all'.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def workflow_cmd_parser_setup(self) -> None:
        """The workflow command is used to perform tasks supported by the
        different workflows configured in Budget Manager. Tasks are functional 
        behaviors working with the available workbooks."""
        try:
            parser = self.workflow_cmd
            # Add subparsers for workflow command parser
            d = "The workflow command is used to execute workflow tasks on "
            d += "available workbooks. Each task is associated with a "
            d += "subcommand used to present the arguments relevant for the task."
            subparsers = parser.add_subparsers(
                dest="workflow_cmd", title="Workflow Task Commands",
                description=d)
            
            # workflow categorization subcommand
            categorization_parser = subparsers.add_parser(
                "categorization",
                aliases=["cat", "CAT", "c"], 
                help="Apply Categorization workflow.")
            categorization_parser.set_defaults(workflow_cmd="categorization")

            self.add_wb_index_argument(categorization_parser)

            categorization_parser.add_argument(
                "--load_workbook","-l", "-load", 
                action="store_true", 
                help="Load the workbook if not yet loaded.")
            
            categorization_parser.add_argument(
                "--check-register","-cr",  
                action="store_true", 
                help="Specified workbook is type: Check Register.")
            
            # Workflow task sub-command: task
            task_parser = subparsers.add_parser(
                "task",
                aliases=["t"], 
                help="Task: Perform a specific workflow task on workbooks.")
            task_parser.set_defaults(workflow_cmd="wf_task")
            task_parser.add_argument(
                "task_name", nargs="?",
                action="store", 
                default=None,
                help=("Name of the task function to perform, e.g., 'discover'. "
                       "Or, 'list' to display a list of valid task names."))
            task_parser.add_argument(
                "task_args",
                nargs="*",
                default=None,
                help="List of arguments to pass to the workflow task."
            )
            # Workflow specific task subcmds: map-category, apply, reload, check
            # task 'check' subcommand
            check_parser = subparsers.add_parser(
                "check",
                aliases=["ch"], 
                help="Check some aspect of the workflow data or processing.")
            check_parser.set_defaults(workflow_cmd="check")
            check_parser.add_argument(
                "wb_ref", nargs="?",
                action="store", 
                default='all',
                help="Workbook reference, name or number of a loaded workbook.")
            check_parser.add_argument(
                "-f", dest="fix", action="store_true",
                help="switch to fix issues found by check cmd.") 

            # workflow 'apply' subcommand
            apply_parser = subparsers.add_parser(
                "apply",
                aliases=["a"], 
                help="Task: Apply some operation to workbooks.")
            apply_parser.set_defaults(workflow_cmd="apply")
            apply_parser.add_argument(
                "-wr","--wb_ref", nargs="?",
                action="store", dest='wb_ref', 
                default=None,
                help="Workbook reference, wb_index, wb_name or 'all' workbooks.")
            apply_parser.add_argument(
                "-cr", "--check_register", nargs="?",
                action="store", 
                default=None,
                help="a wb_ref to a check register(s). wb_index, wb_name or 'all'.")
            
            # Workflow subcommand: reload
            reload_parser = subparsers.add_parser(
                "reload",
                aliases=["r"], 
                help="(move to App cmd) Reload modules.")
            reload_parser.set_defaults(workflow_cmd="reload")
            reload_parser.add_argument(
                "reload_target", nargs="?",
                action="store", 
                default='category_map',
                help="Name of module to reload, or 'all' re-loadable.")

            # self.add_common_args(parser)
            # Instead of propagating, just add common args directly to each subparser:
            for subparser in [apply_parser, check_parser, reload_parser, categorization_parser]:
                self.add_common_args(subparser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion Command Parser Setup Methods
    # ------------------------------------------------------------------------ +
    #region Common Sub-parsers for Commands
    def add_WORKBOOKS_subparser(self, subparsers) -> None:
        """Add a WORKBOOKS subparser to the provided subparsers.""" 
        try:
            wb_subcmd_parser  = subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Select workbooks for.")
            wb_subcmd_parser.set_defaults(load_cmd="workbooks")
            group = wb_subcmd_parser.add_mutually_exclusive_group(required=True)
            group.add_argument(
                "wb_index", nargs="?",
                type=int, 
                default = -1,
                help=f"Workbook index: number associated in the workbook list, 0-based.")
            group.add_argument(
                "-all", dest="all_wbs", 
                action = "store_true",
                help="All workbooks switch.") 
            wb_subcmd_parser.add_argument(
                "-fi", nargs="?", dest="fi_key", 
                default= None,
                help="FI key value.") 
            wb_subcmd_parser.add_argument(
                "-wf", nargs="?", dest="wf_key", 
                default= None,
                help="WF key value.") 
            return wb_subcmd_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_wb_index_argument(self, parser) -> None:
        """Add a wb_index or all_wbs arguments.""" 
        try:
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument(
                "wb_index", nargs="?",
                type=int, 
                default = -1,
                help=f"Workbook index: number associated in the workbook list, 0-based.")
            # group.add_argument(
            #     "wb_list", nargs="*",
            #     action='extend',
            #     type=int, 
            #     default = [],
            #     help=f"Workbook index: one or more numbers (spaces, no commas) indexing from the workbook list, 0-based.")
            group.add_argument(
                "-all", dest="all_wbs", 
                action = "store_true",
                help="All workbooks switch.") 
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_common_args(self, parser: cmd2.Cmd2ArgumentParser) -> object:
        """Add common arguments to the provided parser."""
        try:
            common_args = parser.add_argument_group(
                title="Common Options", 
                description="Add these to any command.")
            # Add common arguments to the parser
            # common_args.add_argument(
            #     "wb_ref", nargs="?", 
            #     action="store", 
            #     default='all',
            #     help="Workbook reference, name or number from show workbooks.")
            common_args.add_argument(
                "-po", "--parse-only",  
                action="store_true", 
                help="The command line is only parsed and displayed without executing.")
            common_args.add_argument(
                "-vo", "--validate-only",  
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
    #endregion Common Sub-parsers for Commands
    # ------------------------------------------------------------------------ +
