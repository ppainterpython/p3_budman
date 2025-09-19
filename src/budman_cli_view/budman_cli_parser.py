# ---------------------------------------------------------------------------- +
#region budman_cli_parser.py module
""" budman_cli_parser.py cli argument parsing for BudgetModelCLIView class.
"""
#endregion budman_cli_parser.py module
# ---------------------------------------------------------------------------- +
#region Imports

# python standard library modules and packages
from email import parser
import logging, shutil
from typing import List
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
import cmd2, argparse
from cmd2 import (Cmd2ArgumentParser, with_argparser)
from cmd2.argparse_custom import Cmd2HelpFormatter
# local modules and packages
from budman_settings import *
from budman_settings.budman_settings_constants import BUDMAN_CMD_HISTORY_FILENAME
import budman_command_processor.budman_cp_namespace as cp
import budman_namespace.design_language_namespace as bdm
                             
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class WideHelpFormatter(Cmd2HelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs['width'] = None  # Set desired width here
        kwargs['max_help_position'] = 60  # Set desired width here
        super().__init__(*args, **kwargs)
class UnwrappedPositionalHelpFormatter(Cmd2HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            # Positional argument — use full metavar without truncation
            metavar = self._metavar_formatter(action, action.dest)(1)[0]
            return metavar
        return super()._format_action_invocation(action)
class BudManCLIParser():
    #region class BudManCLIParser initialization
    """A class to parse command line arguments for the BudgetModelCLIView class.

    This class is used to parse command line arguments for the BudgetModelCLIView
    class. It uses the cmd2 library to create a command line interface for the
    BudgetModel application.
    """
    def __init__(self,settings: BudManSettings) -> None:
        """Initialize the BudManCLIParser class."""
        self.app_name = settings[APP_NAME]
        self.app_cmd = cmd2.Cmd2ArgumentParser()
        self.change_cmd = cmd2.Cmd2ArgumentParser()
        self.list_cmd = cmd2.Cmd2ArgumentParser()
        self.load_cmd = cmd2.Cmd2ArgumentParser()
        self.save_cmd = cmd2.Cmd2ArgumentParser()
        self.show_cmd = cmd2.Cmd2ArgumentParser()
        self.workflow_cmd = cmd2.Cmd2ArgumentParser(
            description="Workflow management commands.",
            formatter_class=UnwrappedPositionalHelpFormatter
        )
        self.app_cmd_parser_setup(self.app_name)
        self.change_cmd_parser_setup(self.app_name)
        self.list_cmd_parser_setup(self.app_name)
        self.load_cmd_parser_setup(self.app_name)
        self.save_cmd_parser_setup(self.app_name)
        self.show_cmd_parser_setup(self.app_name)
        self.workflow_cmd_parser_setup(self.app_name)
    #endregion class BudManCLIParser initialization
    # ------------------------------------------------------------------------ +
    #region Command Parser Setup Methods
    def app_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Application settings and feature controls."""
        try:
            parser = self.app_cmd
            parser.prog = app_name
            title = self.app_cmd_parser_setup.__doc__
            subparsers = parser.add_subparsers(title=title) #, dest="app_cmd")
            app_cmd_defaults = {
                p3m.CK_CMD_KEY: cp.CV_APP_CMD_KEY,
                p3m.CK_CMD_NAME: cp.CV_APP_CMD_NAME
            }
            parser.set_defaults(**app_cmd_defaults)

            # app exit subcommand
            exit_parser = subparsers.add_parser(
                cp.CV_EXIT_SUBCMD_NAME,
                aliases=["quit"],
                help="Exit the application.")
            exit_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_EXIT_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_EXIT_SUBCMD_KEY}
            exit_parser.set_defaults(**exit_parser_defaults)
            exit_parser.add_argument(
                f"--{cp.CK_NO_SAVE}",
                action="store_true",
                help="Do NOT save BDM_STORE on exit.")
            self.add_common_optional_args(exit_parser)

            # app delete subcommand
            delete_parser = subparsers.add_parser(
                p3m.CK_SUBCMD_NAME,
                aliases=["del"],
                help="Delete a module.")
            delete_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_DELETE_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_DELETE_SUBCMD_KEY}
            delete_parser.set_defaults(**delete_parser_defaults)
            delete_parser.add_argument(
                "delete_target", nargs="?",
                type=int, 
                default= -1,
                help="wb_index to delete.")
            self.add_common_optional_args(delete_parser)

            # app reload subcommand
            reload_parser = subparsers.add_parser(
                cp.CV_RELOAD_SUBCMD_NAME,
                aliases=["r"], 
                help="Reload objects like modules and data.")
            reload_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_RELOAD_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_RELOAD_SUBCMD_KEY}
            reload_parser.set_defaults(**reload_parser_defaults)
            reload_parser.add_argument(
                cp.CK_RELOAD_TARGET, 
                nargs="?",
                action="store", 
                choices=[cp.CV_CATEGORY_MAP, cp.CV_FI_WORKBOOK_DATA_COLLECTION,
                         cp.CV_WORKFLOWS_MODULE],
                default=cp.CV_CATEGORY_MAP,
                help="Name of object to reload, pick from choices.")
            self.add_common_optional_args(reload_parser)

            # app log [handler-name] [--list] [--level [level-value]] [--rollover]
            log_subcmd_parser = subparsers.add_parser(
                cp.CV_LOG_SUBCMD_NAME, 
                # aliases=["log"], 
                help="Workbook reference wb_name, wb_index, or 'all'.")
            log_subcmd_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_LOG_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_LOG_SUBCMD_KEY}
            log_subcmd_parser.set_defaults(**log_subcmd_parser_defaults)
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
            self.add_common_optional_args(log_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def change_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Change settings."""
        try:
            parser = self.change_cmd
            parser.prog = app_name
            subparsers = parser.add_subparsers()
            title = f"Change SubCommands"
            parser.set_defaults(cmd_key=cp.CV_CHANGE_CMD_KEY,
                                cmd_name=cp.CV_CHANGE_CMD_NAME)

            # change subcommands: workbook, wb_ref
            # change workbooks subcommand
            workbook_subcmd_parser  = subparsers.add_parser(
                cp.CV_WORKBOOKS_SUBCMD_NAME,
                aliases=["wb", "WB"], 
                help="Change workbook attributes.")
            workbook_subcmd_parser.set_defaults(
                subcmd_name=cp.CV_WORKBOOKS_SUBCMD_NAME,
                subcmd_key=cp.CV_CHANGE_WORKBOOKS_SUBCMD_KEY)
            self.add_wb_list_or_all_argument(workbook_subcmd_parser)
            wb_type_choices = bdm.VALID_WB_TYPE_VALUES
            workbook_subcmd_parser.add_argument(
                "-t", f"--{cp.CK_CMDLINE_WB_TYPE}",
                nargs="?", dest=cp.CK_CMDLINE_WB_TYPE, 
                default = None,
                choices=wb_type_choices,
                help="Specify the workbook type to apply.")
            self.add_workflow_optional_argument(workbook_subcmd_parser)
            self.add_purpose_optional_argument(workbook_subcmd_parser)
            self.add_common_optional_args(workbook_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def list_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Setup the command line argument parsers for the list command."""
        try:
            parser = self.list_cmd
            parser.prog = app_name
            list_cmd_defaults = {
                p3m.CK_CMD_KEY: cp.CV_LIST_CMD_KEY,
                p3m.CK_CMD_NAME: cp.CV_LIST_CMD_NAME
            }
            parser.set_defaults(**list_cmd_defaults)
            # List command subparsers
            list_subparsers = parser.add_subparsers()

            #region bdm_store_subcmd_parser
            # list BDM_STORE 
            bdm_store_subcmd_parser = list_subparsers.add_parser(
                cp.CV_BDM_STORE_SUBCMD_NAME,
                aliases=["bdm_store", "bms", "BMS", "budget_manager_store"], 
                help="List the Budget Manager Store file.")
            bdm_store_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_BDM_STORE_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_LIST_BDM_STORE_SUBCMD_KEY
            }
            bdm_store_subcmd_parser.set_defaults(**bdm_store_subcmd_defaults)
            self.add_common_optional_args(bdm_store_subcmd_parser)
            #endregion bdm_store_subcmd_parser

            # region wb_subcmd_parser
            # list workbooks  [-t] [wb_list | -all]
            wb_subcmd_parser  = list_subparsers.add_parser(
                cp.CV_WORKBOOKS_SUBCMD_NAME,
                aliases=["wb", "WB"], 
                help="Select workbooks to list.")
            wb_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_WORKBOOKS_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_LIST_WORKBOOKS_SUBCMD_KEY
            }
            wb_subcmd_parser.set_defaults(**wb_subcmd_defaults)
            wb_subcmd_parser.add_argument(
                "-t", f"--{cp.CK_BDM_TREE}", 
                action="store_true",
                help="Show the BDM tree hierarchy.")
            self.add_wb_list_or_all_argument(wb_subcmd_parser)
            self.add_common_optional_args(wb_subcmd_parser)
            # endregion wb_subcmd_parser

            #region files_subcmd_parser
            # list files  [--cmdline_wf_key | -w <wf_key>] [--cmdline_wf_purpose | [-p <wf_purpose> | -wi | -ww | -wo]]
            files_subcmd_parser  = list_subparsers.add_parser(
                cp.CV_FILES_SUBCMD_NAME,
                aliases=["files", "f"], 
                help="Select files to list.")
            files_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_FILES_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_LIST_FILES_SUBCMD_KEY
            }
            files_subcmd_parser.set_defaults(**files_subcmd_defaults)
            files_subcmd_subparsers = files_subcmd_parser.add_subparsers()

            # For files subcommand, next arg is either all_files or 
            # wf_folder specified as wf_key and wf_purpose values.
            self.add_all_files_subparser(files_subcmd_subparsers)
            self.add_src_wf_folder_subparser(files_subcmd_subparsers)
            #endregion files_subcmd_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def load_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Setup the command line argument parsers for the load command."""
        try:
            parser = self.load_cmd
            parser.prog = app_name
            # Load subcommands: BDM_STORE, workbooks
            subparsers = parser.add_subparsers()
            parser.set_defaults(cmd_key=cp.CV_LOAD_CMD_KEY,   # new way
                                cmd_name=cp.CV_LOAD_CMD_NAME)

            # bdm_store_subcmd_parser
            # load BDM_STORE 
            bdm_store_subcmd_parser = subparsers.add_parser(
                cp.CV_BDM_STORE_SUBCMD_NAME,
                aliases=["bdm_store", "bms", "BMS", "budget_manager_store"], 
                help="Load the Budget Manager Store file.")
            bdm_store_subcmd_parser.set_defaults(
                subcmd_name=cp.CV_BDM_STORE_SUBCMD_NAME,
                subcmd_key=cp.CV_LOAD_BDM_STORE_SUBCMD_KEY)
            self.add_common_optional_args(bdm_store_subcmd_parser)

            # wb_subcmd_parser
            # load workbooks [wb_index | -all | --all_wbs]
            wb_subcmd_parser  = subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Select workbooks for loading.")
            wb_subcmd_parser.set_defaults(
                subcmd_name=cp.CV_WORKBOOKS_SUBCMD_NAME,
                subcmd_key=cp.CV_LOAD_WORKBOOKS_SUBCMD_KEY)
            self.add_wb_list_or_all_argument(wb_subcmd_parser)
            self.add_common_optional_args(wb_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def save_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Save Command: parser setup"""
        try:
            # Save subcommands: BDM_STORE, workbooks
            parser = self.save_cmd
            parser.prog = app_name
            subparsers = parser.add_subparsers()
            parser.set_defaults(cmd_key=cp.CV_SAVE_CMD_KEY,   # new way
                                cmd_name=cp.CV_SAVE_CMD_NAME)

            # bdm_store_subcmd_parser
            # save BDM_STORE
            bdm_store_subcmd_parser = subparsers.add_parser(
                cp.CV_BDM_STORE_SUBCMD_NAME,
                aliases=["bdm_store", "bms", "BMS", "budget_manager_store"], 
                help="Save the Budget Manager Store file.")
            bdm_store_subcmd_parser.set_defaults(
                subcmd_name=cp.CV_BDM_STORE_SUBCMD_NAME,
                subcmd_key=cp.CV_SAVE_BDM_STORE_SUBCMD_KEY)
            self.add_common_optional_args(bdm_store_subcmd_parser)

            # wb_subcmd_parser
            # save workbooks [wb_index | -all | --all_wbs]
            wb_subcmd_parser  = subparsers.add_parser(
                cp.CV_WORKBOOKS_SUBCMD_NAME,
                aliases=["wb", "WB"], 
                help="Select workbooks to save.")
            wb_subcmd_parser.set_defaults(
                subcmd_name=cp.CV_WORKBOOKS_SUBCMD_NAME,
                subcmd_key=cp.CV_SAVE_WORKBOOKS_SUBCMD_KEY)
            self.add_wb_list_or_all_argument(wb_subcmd_parser)
            self.add_common_optional_args(wb_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def show_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Setup the command line argument parsers for the show command."""
        try:
            parser = self.show_cmd
            parser.prog = app_name
            subparsers = self.show_cmd.add_subparsers()
            show_cmd_defaults = {
                p3m.CK_CMD_KEY: cp.CV_SHOW_CMD_KEY,
                p3m.CK_CMD_NAME: cp.CV_SHOW_CMD_NAME
            }
            parser.set_defaults(**show_cmd_defaults)

            # show subcommands: 
            #     categories, datacontext, workbooks, fin_inst, workflows

            #region Show Budget Categories subcommand
            categories_subcmd_parser = subparsers.add_parser(
                cp.CV_BUDGET_CATEGORIES_SUBCMD_NAME,
                aliases=["cat", "budget_categories"],
                help="Show the Budget Categories.")
            categories_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_BUDGET_CATEGORIES_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_SHOW_BUDGET_CATEGORIES_SUBCMD_KEY
            }
            categories_subcmd_parser.set_defaults(**categories_subcmd_defaults)
            categories_subcmd_parser.add_argument(
                "cat_list", nargs="*",
                # "-i", "--include", nargs="*",
                action='extend', 
                default= [],
                help="List of categories to include, default is all.") 
            categories_subcmd_parser.add_argument(
                "-l", "--level",nargs="?",
                # "-i", "--include", nargs="*",
                action='store',
                type=int,
                default=2, 
                help="Level to display in category hierarchy, max 3.") 
            self.add_common_optional_args(categories_subcmd_parser)
            #endregion Show Categories subcommand

            #region show DataContext subcommand
            datacontext_subcmd_parser = subparsers.add_parser(
                cp.CV_DATA_CONTEXT_SUBCMD_NAME,
                aliases=["dc", "DC"],
                help="Show the data context information.")
            datacontext_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_DATA_CONTEXT_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_SHOW_DATA_CONTEXT_SUBCMD_KEY
            }
            datacontext_subcmd_parser.set_defaults(**datacontext_subcmd_defaults)
            self.add_common_optional_args(datacontext_subcmd_parser)
            #endregion show DataContext subcommand

            #region show Financial Institution subcommand [fi_key] [-wf [wf_key]] [-wb [wb_name]]
            fi_subcmd_parser = subparsers.add_parser(
                cp.CV_FIN_INST_SUBCMD_NAME,
                aliases=["fi", "FI", "financial_institutions"], 
                help="Show Financial Institution information.")
            fi_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_FIN_INST_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_SHOW_FIN_INST_SUBCMD_KEY
            }
            fi_subcmd_parser.set_defaults(**fi_subcmd_defaults)
            fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.") 
            self.add_common_optional_args(fi_subcmd_parser)
            #endregion show Financial Institution subcommand [fi_key] [-wf [wf_key]] [-wb [wb_name]]

            #region show workflows subcommand
            wf_subcmd_parser  = subparsers.add_parser(
                cp.CV_WORKFLOWS_SUBCMD_NAME,
                aliases=["wf", "WF", "workflows"], 
                help="Show Workflow information.")
            wf_subcmd_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_WORKFLOWS_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_SHOW_WORKFLOWS_SUBCMD_KEY
            }
            wf_subcmd_parser.set_defaults(**wf_subcmd_defaults)
            wf_subcmd_parser.add_argument(
                "wf_key", nargs="?", 
                action="store", 
                default = None,
                help="Workflow key value.")
            self.add_common_optional_args(wf_subcmd_parser)
            #endregion show workflows subcommand

        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def workflow_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """The workflow command is used to perform tasks supported by the
        different workflows configured in Budget Manager. Tasks are functional 
        behaviors working with the available workbooks."""
        try:
            parser = self.workflow_cmd
            # Add subparsers for workflow command parser
            d = "The workflow command is used to execute workflow tasks on "
            d += "available workbooks. Each task is associated with a "
            d += "subcommand used to present the arguments relevant for the task."
            subparsers = parser.add_subparsers()
            workflow_cmd_defaults = {
                p3m.CK_CMD_KEY: cp.CV_WORKFLOW_CMD_KEY,   # new way
                p3m.CK_CMD_NAME: cp.CV_WORKFLOW_CMD_NAME,
            }
            parser.set_defaults(**workflow_cmd_defaults)
            
            transfer_parser = self.add_transfer_subparser(subparsers)

            #region workflow categorization subcommand
            categorization_parser = subparsers.add_parser(
                cp.CV_CATEGORIZATION_SUBCMD_NAME,
                aliases=["cat", "CAT", "c"], 
                help="Apply Categorization workflow.")
            categorization_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_CATEGORIZATION_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_CATEGORIZATION_SUBCMD_KEY}
            categorization_parser.set_defaults(**categorization_parser_defaults)
            self.add_wb_list_or_all_argument(categorization_parser)
            categorization_parser.add_argument(
                f"--{cp.CK_LOAD_WORKBOOK}","-l", "-load", 
                action="store_true", 
                default=True,
                help="Load the workbook if not yet loaded.")
            categorization_parser.add_argument(
                f"--{cp.CK_LOG_ALL}", "-log_all", "-la", 
                action="store_true", 
                help="Log every catalog pattern match step.")
            categorization_parser.add_argument(
                f"--{cp.CK_CLEAR_OTHER}", "-c", 
                action="store_true", 
                help="Clear other category workbook at start of task run.")
            self.add_common_optional_args(categorization_parser)
            #endregion workflow categorization subcommand

            #region Workflow 'check' subcommand
            check_parser = subparsers.add_parser(
                cp.CV_CHECK_SUBCMD_NAME,
                aliases=["ch"], 
                help="Check some aspect of the workflow data or processing.")
            check_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_CHECK_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_CHECK_SUBCMD_KEY}
            check_parser.set_defaults(**check_parser_defaults)
            self.add_wb_list_or_all_argument(check_parser)
            self.add_load_workbook_argument(check_parser)
            self.add_fix_argument(check_parser)
            check_parser.add_argument(
                f"--{cp.CK_VALIDATE_CATEGORIES}", "-val", "-v", 
                action="store_true", 
                help="Validate the budget categories.")
            self.add_common_optional_args(check_parser)
            #endregion Workflow 'check' subcommand

            #region Workflow task sub-command: task
            task_parser = subparsers.add_parser(
                cp.CV_TASK_SUBCMD_NAME,
                aliases=["t"], 
                help="Task: Perform a specific workflow task on workbooks.")
            task_parser_defaults = {
                p3m.CK_SUBCMD_NAME: cp.CV_TASK_SUBCMD_NAME,
                p3m.CK_SUBCMD_KEY: cp.CV_TASK_SUBCMD_KEY}
            task_parser.set_defaults(**task_parser_defaults)
            task_name_choices = cp.VALID_TASK_NAMES
            task_parser.add_argument(
                cp.CK_TASK_NAME, nargs="?",
                choices=task_name_choices, 
                help=("Name of the task function to perform, e.g., 'sync' etc."))
            task_parser.add_argument(
                f"--{cp.CK_RECONCILE}", "-r",
                action="store_true", 
                help="Reconcile with the WORKBOOK_DATA_COLLECTION on sync."
            )
            # task_parser.add_argument(
            #     "task_args",
            #     nargs="*",
            #     default=None,
            #     help="List of arguments to pass to the workflow task."
            # )
            # self.add_wb_index_argument(task_parser)
            #endregion Workflow task sub-command: task

            #region workflow 'apply' subcommand
            apply_parser = subparsers.add_parser(
                cp.CV_APPLY_SUBCMD_NAME,
                aliases=["a"], 
                help="Task: Apply some operation with workbooks.")
            apply_parser.set_defaults(
                cmd_key=cp.CV_APPLY_SUBCMD_KEY,   # new way
                cmd_name=cp.CV_APPLY_SUBCMD_NAME, 
                subcmd_name=cp.CV_APPLY_SUBCMD_NAME,
                subcmd_key=cp.CV_APPLY_SUBCMD_KEY)
            apply_parser.add_argument(
                "-cm", "--category_map", nargs="?",
                action="store", 
                default=None,
                help="apply the category_map to update the txn_categories.")
            apply_parser.add_argument(
                "-cr", "--check_register", nargs="?",
                action="store", 
                default=None,
                help="a wb_ref to a check register(s). wb_index, wb_name or 'all'.")
            self.add_common_optional_args(apply_parser)
            #endregion workflow 'apply' subcommand
            set_parser = self.add_set_subparser(subparsers)
            intake_parser = self.add_intake_subparser(subparsers)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion Command Parser Setup Methods
    # ------------------------------------------------------------------------ +
    #region workflow set subcommand subparser
    def add_set_subparser(self, subparsers) -> None:
        """Add a set subparser to the provided subparsers."""
        try:
            # workflow set subcommand
            set_parser = subparsers.add_parser(
                cp.CV_SET_SUBCMD_NAME,
                aliases=["set"], 
                help="Set workflow task information.")
            set_parser.set_defaults(
                subcmd_name=cp.CV_SET_SUBCMD_NAME,
                subcmd_key=cp.CV_SET_SUBCMD_KEY)
            self.add_workflow_optional_argument(set_parser)
            self.add_purpose_optional_argument(set_parser)
            self.add_common_optional_args(set_parser)
            return set_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion workflow set subcommand subparser
    # ------------------------------------------------------------------------ +
    #region transfer subcommand subparser
    def add_transfer_subparser(self, subparsers) -> None:
        """Add a transfer subparser to the provided subparsers."""
        try:
            # workflow transfer subcommand
            transfer_subcmd_parser = subparsers.add_parser(
                cp.CV_TRANSFER_SUBCMD_NAME,
                aliases=["tr"], 
                help="Transfer files to a workflow with a specific purpose.")
            transfer_subcmd_parser.set_defaults(
                subcmd_name=cp.CV_TRANSFER_SUBCMD_NAME,
                subcmd_key=cp.CV_WORKFLOW_TRANSFER_SUBCMD_KEY)
            # transfer subcmd subparsers
            transfer_subparsers = transfer_subcmd_parser.add_subparsers()

            # workflow transfer files subcommand subparser
            files_parser = transfer_subparsers.add_parser(
                cp.CV_FILES_SUBCMD_NAME,
                aliases=["FILES"],
                help="Specifies transfer of files.")
            files_parser_defaults = {
                cp.CK_TRANSFER_FILES: True, 
                cp.CK_TRANSFER_WORKBOOKS: False,
                cp.CK_FILE_LIST: [],
                cp.CK_WF_KEY: None,
                cp.CK_WF_PURPOSE: None,
                cp.CK_WB_TYPE: None
            }
            files_parser.set_defaults(**files_parser_defaults)

            files_parser.add_argument(
                # selected files: file_list
                cp.CK_FILE_LIST, nargs='*',
                type=int, default=[], 
                help=("One or more file index values from file_list."))
            files_parser.add_argument(
                f"--{cp.CK_WF_KEY}", "-w",
                choices=bdm.VALID_BDM_WORKFLOWS,
                help="Specify the destination workflow key.")
            files_parser.add_argument(
                f"--{cp.CK_WF_PURPOSE}", "-p",
                choices=bdm.VALID_WF_PURPOSE_CHOICES,
                help="Specify the workflow purpose.")
            files_parser.add_argument(
                f"--{cp.CK_WB_TYPE}", "-t",
                choices=bdm.VALID_WB_TYPE_VALUES,
                help="Specify the destination workbook type.")
            self.add_common_optional_args(files_parser)

            # workflow transfer workbooks subcommand subparser
            workbooks_parser = transfer_subparsers.add_parser(
                cp.CV_WORKBOOKS_SUBCMD_NAME,
                aliases=["WORKBOOKS"],
                help="Specifies transfer of workbooks.")
            workbooks_parser_defaults = {
                cp.CK_TRANSFER_FILES: False,
                cp.CK_TRANSFER_WORKBOOKS: True,
                cp.CK_WB_LIST: [],
                cp.CK_WF_KEY: None,
                cp.CK_WF_PURPOSE: None,
                cp.CK_WB_TYPE: None
            }
            workbooks_parser.set_defaults(**workbooks_parser_defaults)
            workbooks_parser.add_argument(
                # selected workbooks: wb_list
                cp.CK_WB_LIST, nargs='*',
                type=int, default=[], 
                help=("One or more workbook index values from wb_list."))
            workbooks_parser.add_argument(
                f"--{cp.CK_WF_KEY}", "-w",
                choices=bdm.VALID_BDM_WORKFLOWS,
                help="Specify the destination workflow key.")
            workbooks_parser.add_argument(
                f"--{cp.CK_WF_PURPOSE}", "-p",
                choices=bdm.VALID_WF_PURPOSE_CHOICES,
                help="Specify the workflow purpose.")
            workbooks_parser.add_argument(
                f"--{cp.CK_WB_TYPE}", "-t",
                choices=bdm.VALID_WB_TYPE_VALUES,
                help="Specify the destination workbook type.")
            self.add_common_optional_args(workbooks_parser)

            return transfer_subcmd_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion transfer subcommand subparser
    # ------------------------------------------------------------------------ +
    #region intake subcommand subparser
    def add_intake_subparser(self, subparsers) -> None:
        """Add an intake subparser to the provided subparsers."""
        try:
            # workflow intake subcommand
            intake_parser = subparsers.add_parser(
                cp.CV_INTAKE_SUBCMD_NAME,
                aliases=["in", "i"], 
                help="Apply Intake workflow tasks.")
            intake_parser.set_defaults(
                cmd_key=cp.CV_WORKFLOW_CMD_KEY,   # new way
                cmd_name=cp.CV_WORKFLOW_CMD_NAME, 
                subcmd_name=cp.CV_INTAKE_SUBCMD_NAME,
                subcmd_key=cp.CV_WORKFLOW_INTAKE_SUBCMD_KEY)
            intake_subparsers = intake_parser.add_subparsers(
                dest=cp.CK_INTAKE_TASK, required=True)
            # workflow intake copy file_index
            copy_parser = intake_subparsers.add_parser( cp.CV_INTAKE_COPY_TASK, 
                        help=("Copy a file to process working folder."))
            copy_parser.add_argument(
                cp.CK_FILE_INDEX, nargs="?",
                action="store",
                type=int, 
                help=("Index of file to copy."))
            self.add_workflow_optional_argument(copy_parser)
            self.add_purpose_optional_argument(copy_parser)
            self.add_common_optional_args(copy_parser)
            return intake_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion intake subcommand subparser
    # ------------------------------------------------------------------------ +
    def add_workflow_optional_argument(self, parser) -> None:
        """Add a workflow optional argument to the provided parser."""
        try:
            wf_choices = bdm.VALID_BDM_WORKFLOWS
            parser.add_argument(
                "-w", f"--{cp.CK_CMDLINE_WF_KEY}", nargs="?", 
                dest=cp.CK_CMDLINE_WF_KEY, 
                choices=wf_choices,
                help="Specify the workflow key to apply.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_purpose_optional_argument(self, parser) -> None:
        """Add a workflow purpose optional argument to the provided parser."""
        try:
            purpose_choices = bdm.VALID_WF_PURPOSE_VALUES
            parser.add_argument(
                "-p", f"--{cp.CK_CMDLINE_WF_PURPOSE}", nargs="?",  
                choices=purpose_choices,
                help="Specify the workflow folder purpose.")
            parser.add_argument(
                "-wi", nargs="?",
                dest=cp.CK_CMDLINE_WF_PURPOSE,
                const=cp.CK_WF_INPUT,
                help="Use workflow folder purpose: wf_input.")
            parser.add_argument(
                "-ww", nargs="?",
                dest=cp.CK_CMDLINE_WF_PURPOSE,
                const=cp.CK_WF_WORKING,
                help="Use workflow folder purpose: wf_working.")
            parser.add_argument(
                "-wo", nargs="?",
                dest=cp.CK_CMDLINE_WF_PURPOSE,
                const=cp.CK_WF_OUTPUT,
                help="Use workflow folder purpose: wf_output.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_all_files_subparser(self, subparsers) -> None:
        """Add all_files subparser as a positional argument."""
        try:
            all_files_parser = subparsers.add_parser(
                cp.CK_ALL_FILES,
                aliases=["all"],
                help="Specify all files.")
            all_files_parser_defaults = { 
                cp.CK_ALL_FILES: True,
                cp.CK_SRC_WF_FOLDER: False,
                cp.CK_SRC_WF_KEY: None,
                cp.CK_SRC_WF_PURPOSE: None}
            all_files_parser.set_defaults(**all_files_parser_defaults)
            self.add_common_optional_args(all_files_parser)
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_src_wf_folder_subparser(self, subparsers) -> None:
        """Add a src_wf_folder subparser as a positional argument to capture 
        src_wf_key and src_wf_purpose."""
        try:
            src_wf_folder_parser = subparsers.add_parser(
                cp.CK_SRC_WF_FOLDER,
                aliases=["SRC_WF_FOLDER", "src"],
                help="Specify SRC_WF_FOLDER with SRC_WF_KEY SRC_WF_PURPOSE value.")
            src_wf_folder_parser_defaults = {
                cp.CK_ALL_FILES: False, 
                cp.CK_SRC_WF_FOLDER: True,
                cp.CK_SRC_WF_KEY: None,
                cp.CK_SRC_WF_PURPOSE: None
            }
            src_wf_folder_parser.set_defaults(**src_wf_folder_parser_defaults)
            self.add_src_wf_key_positional_arg(src_wf_folder_parser)
            self.add_src_wf_purpose_positional_arg(src_wf_folder_parser)
            self.add_common_optional_args(src_wf_folder_parser)
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_src_wf_key_positional_arg(self, parser) -> None:
        """Add a workflow positional argument to the provided parser."""
        try:
            parser.add_argument(
                cp.CK_SRC_WF_KEY,
                choices=bdm.VALID_BDM_WORKFLOWS,
                help="Specify the workflow key.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_src_wf_purpose_positional_arg(self, parser) -> None:
        """Add a workflow purpose positional argument to the provided parser."""
        try:
            parser.add_argument(
                cp.CK_SRC_WF_PURPOSE,
                choices=bdm.VALID_WF_PURPOSE_CHOICES,
                help="Specify the workflow purpose.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_wb_list_or_all_argument(self, parser) -> None:
        """Add a wb_list or all_wbs arguments."""
        try:
            group = parser.add_mutually_exclusive_group(required=False)
            group.add_argument(
                cp.CK_WB_LIST, nargs="*",
                action='extend',
                type=int, 
                default = [],
                help=f"Workbook index: one or more numbers (spaces, no commas) indexing from the workbook list, 0-based.")
            group.add_argument(
                f"--{cp.CK_ALL_WBS}", "-all", dest="all_wbs", 
                action="store_true",
                help="All workbooks switch.") 
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_file_list_argument(self, parser) -> None:
        """Add one or more file_index numbers from a file list.""" 
        try:
            parser.add_argument(
                cp.CK_FILE_LIST, nargs="*",
                action='extend',
                type=int, 
                default = [],
                help=f"File index: one or more numbers (spaces, no commas) indexing from a file list, 0-based.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_load_workbook_argument(self, parser) -> None:
        """Add a --load_workbook argument.""" 
        try:
            parser.add_argument(
                "--load_workbook","-l", "-load", 
                action="store_true", 
                help="Load the workbook if not yet loaded.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_fix_argument(self, parser) -> None:
        """Add a --fix_switch argument.""" 
        try:
            parser.add_argument(
                f"--{cp.CK_FIX_SWITCH}", "-fix", 
                action="store_true", 
                help="Fix the any fixable issues.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_common_optional_args(self, parser: cmd2.Cmd2ArgumentParser) -> object:
        """Add common arguments to the provided parser."""
        try:
            common_args = parser.add_argument_group(
                title="Common Command Options", 
                description="Add these to any command.")
            # Add common arguments to the parser (subparser)
            common_args.add_argument(
                "-po", f"--{cp.CK_PARSE_ONLY}",  
                action="store_true", 
                help="The command line is only parsed and displayed without executing.")
            common_args.add_argument(
                "-vo", f"--{cp.CK_VALIDATE_ONLY}",  
                action="store_true", 
                help="Command args are only validated with results returned, but no cmd execution.")
            common_args.add_argument(
                f"--{cp.CK_WHAT_IF}", 
                action="store_true", 
                help="Return details about what the command would do, but don't to any action.")
            return common_args
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion Common Sub-parsers for Commands
    # ------------------------------------------------------------------------ +
