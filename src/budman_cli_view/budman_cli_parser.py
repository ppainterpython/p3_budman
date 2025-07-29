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
        self.init_cmd = cmd2.Cmd2ArgumentParser()
        self.show_cmd = cmd2.Cmd2ArgumentParser()
        self.load_cmd = cmd2.Cmd2ArgumentParser()
        self.save_cmd = cmd2.Cmd2ArgumentParser()
        self.val_cmd = cmd2.Cmd2ArgumentParser()
        self.workflow_cmd = cmd2.Cmd2ArgumentParser()
        self.change_cmd = cmd2.Cmd2ArgumentParser()
        self.app_cmd = cmd2.Cmd2ArgumentParser()
        self.init_cmd_parser_setup(self.app_name)
        self.show_cmd_parser_setup(self.app_name)
        self.load_cmd_parser_setup(self.app_name)
        self.save_cmd_parser_setup(self.app_name)
        self.val_cmd_parser_setup(self.app_name)
        self.workflow_cmd_parser_setup(self.app_name)
        self.change_cmd_parser_setup(self.app_name)
        self.app_cmd_parser_setup(self.app_name)
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

            # app exit subcommand
            exit_parser = subparsers.add_parser(
                cp.CV_EXIT_SUBCMD_NAME,
                aliases=["quit"],
                help="Exit the application.")
            exit_parser.set_defaults(cmd_key=cp.CV_APP_CMD_KEY,   # new way
                                       cmd_name=cp.CV_APP_CMD_NAME, 
                                       subcmd_name=cp.CV_EXIT_SUBCMD_NAME,
                                       subcmd_key=cp.CV_EXIT_SUBCMD_KEY)
            exit_parser.add_argument(
                f"--{cp.CK_NO_SAVE}",
                action="store_true",
                help="Do NOT save BDM_STORE on exit.")
            self.add_common_args(exit_parser)

            # app delete subcommand
            exit_parser = subparsers.add_parser(
                "delete",
                aliases=["del"],
                help="Delete a module.")
            exit_parser.set_defaults(cmd_key="app_cmd",   # new way
                                       cmd_name="app", 
                                       subcmd_name="delete",
                                       subcmd_key="app_cmd_delete")
            exit_parser.add_argument(
                "delete_target", nargs="?",
                type=int, 
                default= -1,
                help="wb_index to delete.")
            self.add_common_args(exit_parser)

            # app reload subcommand
            reload_parser = subparsers.add_parser(
                cp.CV_RELOAD_SUBCMD_NAME,
                aliases=["r"], 
                help="Reload objects like modules and data.")
            reload_parser.set_defaults(
                cmd_key=cp.CV_APP_CMD_KEY,   # new way
                cmd_name=cp.CV_APP_CMD_NAME, 
                subcmd_name=cp.CV_RELOAD_SUBCMD_NAME,
                subcmd_key=cp.CV_RELOAD_SUBCMD_KEY)
            reload_parser.add_argument(
                cp.CK_RELOAD_TARGET, 
                nargs="?",
                action="store", 
                choices=[cp.CV_CATEGORY_MAP, cp.CV_FI_WORKBOOK_DATA_COLLECTION,
                         cp.CV_WORKFLOWS_MODULE],
                default=bdm.CATEGORY_MAP,
                help="Name of object to reload, pick from choices.")
            self.add_common_args(reload_parser)

            # app log [handler-name] [--list] [--level [level-value]] [--rollover]
            log_subcmd_parser = subparsers.add_parser(
                "log", 
                # aliases=["log"], 
                help="Workbook reference wb_name, wb_index, or 'all'.")
            log_subcmd_parser.set_defaults(app_cmd="log",
                                       cmd_key="app_cmd",   # new way
                                       cmd_name="app", 
                                       subcmd_name="log",
                                       subcmd_key="app_cmd_log")
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
            subparsers = parser.add_subparsers()
            title = f"Change SubCommands"
            # change subcommands: workbook, wb_ref
            # change workbooks subcommand
            # workbook_subcmd_parser = self.add_WORKBOOKS_subparser(subparsers)
            workbook_subcmd_parser  = subparsers.add_parser(
                cp.CV_WORKBOOKS_SUBCMD_NAME,
                aliases=["wb", "WB"], 
                help="Change workbook attributes.")
            workbook_subcmd_parser.set_defaults(
                cmd_key=cp.CV_CHANGE_CMD_KEY,   # new way
                cmd_name=cp.CV_CHANGE_CMD_NAME,
                subcmd_name=cp.CV_WORKBOOKS_SUBCMD_NAME,
                subcmd_key=cp.CV_CHANGE_WORKBOOKS_SUBCMD_KEY)
            self.add_wb_index_argument(workbook_subcmd_parser)
            wb_type_choices = bdm.VALID_WB_TYPE_VALUES
            workbook_subcmd_parser.add_argument(
                "-t", f"--{cp.CK_CMDLINE_WB_TYPE}",
                nargs="?", dest=cp.CK_CMDLINE_WB_TYPE, 
                default = None,
                choices=wb_type_choices,
                help="Specify the workbook type to apply.")
            self.add_workflow_argument(workbook_subcmd_parser)
            self.add_purpose_argument(workbook_subcmd_parser)
            self.add_common_args(workbook_subcmd_parser)
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
            self.add_common_args(wb_subcmd_parser)

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
            self.add_common_args(fi_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def show_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Setup the command line argument parsers for the show command."""
        try:
            parser = self.show_cmd
            parser.prog = app_name
            subparsers = self.show_cmd.add_subparsers()
            # show subcommands: categories, datacontext, workbooks, fin_inst, 
            # workflows

            #region Show Categories subcommand
            categories_subcmd_parser = subparsers.add_parser(
                "BUDGET_CATEGORIES",
                aliases=["cat", "budget_categories"],
                help="Show the Budget Categories.")
            categories_subcmd_parser.set_defaults(
                show_cmd="BUDGET_CATEGORIES", # old way
                cmd_key="show_cmd",   # new way
                cmd_name="show", 
                subcmd_name="BUDGET_CATEGORIES",
                subcmd_key="show_cmd_BUDGET_CATEGORIES")
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
            self.add_common_args(categories_subcmd_parser)
            #endregion Show Categories subcommand

            #region show DataContext subcommand
            datacontext_subcmd_parser = subparsers.add_parser(
                "DATA_CONTEXT",
                aliases=["dc", "DC"],
                help="Show the data context information.")
            datacontext_subcmd_parser.set_defaults(
                show_cmd="DATA_CONTEXT", # old way
                cmd_key="show_cmd",   # new way
                cmd_name="show", 
                subcmd_name="DATA_CONTEXT",
                subcmd_key="show_cmd_DATA_CONTEXT")
            self.add_common_args(datacontext_subcmd_parser)
            #endregion show DataContext subcommand

            #region show Financial Institution subcommand [fi_key] [-wf [wf_key]] [-wb [wb_name]]
            fi_subcmd_parser = subparsers.add_parser(
                "fin_inst",
                aliases=["fi", "FI", "financial_institutions"], 
                help="Show Financial Institution information.")
            fi_subcmd_parser.set_defaults(
                show_cmd="fin_inst",
                cmd_key="show_cmd",   # new way
                cmd_name="show", 
                subcmd_name="fin_inst",
                subcmd_key="show_cmd_fin_inst")
            fi_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.") 
            self.add_common_args(fi_subcmd_parser)
            #endregion show Financial Institution subcommand [fi_key] [-wf [wf_key]] [-wb [wb_name]]

            #region show workflows subcommand
            wf_subcmd_parser  = subparsers.add_parser(
                "workflows",
                aliases=["wf", "WF"], 
                help="Show Workflow information.")
            wf_subcmd_parser.set_defaults(show_cmd="workflows")
            wf_subcmd_parser.add_argument(
                "wf_key", nargs="?", 
                action="store", 
                default = None,
                help="Workflow key value.")
            self.add_common_args(wf_subcmd_parser)
            #endregion show workflows subcommand

            #region show workbooks subcommand
            wb_subcmd_parser  = subparsers.add_parser(
                cp.CV_WORKBOOKS_SUBCMD_NAME,
                aliases=["wb", "WB"], 
                help="Show workbook information.")
            # wb_subcmd_parser = self.add_WORKBOOKS_subparser(subparsers)
            wb_subcmd_parser.set_defaults(
                cmd_key=cp.CV_SHOW_CMD_KEY,   # new way
                cmd_name=cp.CV_SHOW_CMD_NAME, 
                subcmd_name=cp.CV_WORKBOOKS_SUBCMD_NAME,
                subcmd_key=cp.CV_SHOW_WORKBOOKS_SUBCMD_KEY)
            self.add_wb_index_argument(wb_subcmd_parser)
            wb_subcmd_parser.add_argument(
                "-t", f"--{cp.CK_BDM_TREE}", 
                action="store_true",
                help="Show the BDM tree hierarchy.")
            self.add_common_args(wb_subcmd_parser)
            #endregion show workbooks subcommand

        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def load_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Setup the command line argument parsers for the load command."""
        try:
            parser = self.load_cmd
            parser.prog = app_name
            # Load subcommands: BDM_STORE, workbooks, check_register
            subparsers = parser.add_subparsers()

            # BDM_STORE subcommand
            bdm_store_subcmd_parser = subparsers.add_parser(
                "BDM_STORE",
                aliases=["store", "bms", "budget_manager_store","BDM_STORE"], 
                help="Load the Budget Manager Store file.")
            bdm_store_subcmd_parser.set_defaults(
                cmd_key=cp.CV_LOAD_CMD_KEY,   # new way
                cmd_name=cp.CV_LOAD_CMD_NAME, 
                subcmd_name=cp.CV_BDM_STORE_SUBCMD_NAME,
                subcmd_key=cp.CV_LOAD_BDM_STORE_SUBCMD_KEY)
            self.add_common_args(bdm_store_subcmd_parser)

            # WORKBOOK subcommand (wb_index | -all) [fi_key]
            wb_subcmd_parser  = subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Select workbooks for.")
            wb_subcmd_parser.set_defaults(load_cmd="workbooks",
                                        cmd_key="load_cmd",   # new way
                                        cmd_name="load", 
                                        subcmd_name="workbooks",
                                        subcmd_key="load_cmd_workbooks")
            self.add_wb_index_argument(wb_subcmd_parser)
            self.add_common_args(wb_subcmd_parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def save_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Save Command: parser setup"""
        try:
            # Save subcommands: BDM_STORE, workbooks
            parser = self.save_cmd
            parser.prog = app_name
            subparsers = parser.add_subparsers(
                dest="save_cmd")
            # subcommand save BDM_STORE
            self.save_bm_store_subcmd_parser = subparsers.add_parser(
                "BDM_STORE",
                aliases=["store", "bms", "BMS", "budget_manager_store","BDM_STORE"], 
                help="Save the Budget Manager Store file.")
            self.save_bm_store_subcmd_parser.set_defaults(
                save_cmd="BDM_STORE",
                cmd_key="save_cmd",   # new way
                cmd_name="save", 
                subcmd_name="BDM_STORE",
                subcmd_key="save_cmd_BDM_STORE")
            # subcommand save workbooks [wb_name] [fi_key]
            self.save_wb_subcmd_parser = self.add_WORKBOOKS_subparser(subparsers)
            self.save_wb_subcmd_parser.set_defaults(
                save_cmd="workbooks",
                cmd_key="save_cmd",   # new way
                cmd_name="save", 
                subcmd_name="workbooks",
                subcmd_key="save_cmd_workbooks")
            self.add_common_args(parser)
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def val_cmd_parser_setup(self,app_name : str = "not-set") -> None:
        """Examine or Set values in the application settings and data."""
        try:
            self.val_cmd_subparsers = self.val_cmd.add_subparsers(
                dest="val_cmd")
            self.val_cmd.prog = app_name
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
            
            #region workflow categorization subcommand
            categorization_parser = subparsers.add_parser(
                cp.CV_CATEGORIZATION_SUBCMD_NAME,
                aliases=["cat", "CAT", "c"], 
                help="Apply Categorization workflow.")
            categorization_parser.set_defaults(
                cmd_key=cp.CV_WORKFLOW_CMD_KEY,   # new way
                cmd_name=cp.CV_WORKFLOW_CMD_NAME, 
                subcmd_name=cp.CV_CATEGORIZATION_SUBCMD_NAME,
                subcmd_key=cp.CV_CATEGORIZATION_SUBCMD_KEY)
            self.add_wb_index_argument(categorization_parser)
            categorization_parser.add_argument(
                f"--{cp.CK_LOAD_WORKBOOK}","-l", "-load", 
                action="store_true", 
                default=True,
                help="Load the workbook if not yet loaded.")
            categorization_parser.add_argument(
                f"--{cp.CK_LOG_ALL}", "-log_all", "-la", 
                action="store_true", 
                help="Log every catalog pattern match step.")
            self.add_common_args(categorization_parser)
            #endregion workflow categorization subcommand

            #region workflow intake subcommand
            intake_parser = self.add_intake_subparser(subparsers)
            #endregion workflow intake subcommand
            
            #region Workflow 'check' subcommand
            check_parser = subparsers.add_parser(
                "check",
                aliases=["ch"], 
                help="Check some aspect of the workflow data or processing.")
            check_parser.set_defaults(
                cmd_key=cp.CV_WORKFLOW_CMD_KEY,   # new way
                cmd_name=cp.CV_WORKFLOW_CMD_NAME, 
                subcmd_name=cp.CV_CHECK_SUBCMD_NAME,
                subcmd_key=cp.CV_CHECK_SUBCMD_KEY)
            self.add_wb_index_argument(check_parser)
            self.add_load_workbook_argument(check_parser)
            self.add_fix_argument(check_parser)
            check_parser.add_argument(
                f"--{cp.CK_VALIDATE_CATEGORIES}", "-val", "-v", 
                action="store_true", 
                help="Validate the budget categories.")
            self.add_common_args(check_parser)
            #endregion Workflow 'check' subcommand

            #region Workflow task sub-command: task
            task_parser = subparsers.add_parser(
                "task",
                aliases=["t"], 
                help="Task: Perform a specific workflow task on workbooks.")
            task_parser.set_defaults(
                cmd_key="workflow_cmd",   # new way
                cmd_name="workflow", 
                subcmd_name="task",
                subcmd_key="workflow_cmd_task")
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
            self.add_wb_index_argument(task_parser)
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
            self.add_common_args(apply_parser)
            #endregion workflow 'apply' subcommand
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion Command Parser Setup Methods
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
                subcmd_key=cp.CV_INTAKE_SUBCMD_KEY)
            intake_subparsers = intake_parser.add_subparsers(
                dest=cp.CK_INTAKE_TASK, required=True)
            # workflow intake move file_index
            move_parser = intake_subparsers.add_parser( cp.CV_INTAKE_MOVE_TASK, 
                                                       help=("Move a file into intake process working folder."))
            move_parser.add_argument(
                cp.CK_FILE_INDEX, nargs="?",
                action="store",
                type=int, 
                help=("Index of file to move."))
            self.add_common_args(move_parser)
            # workflow intake list
            list_parser = intake_subparsers.add_parser( cp.CV_INTAKE_LIST_TASK, 
                                                       help=("List files in the intake process working folder."))
            self.add_workflow_argument(list_parser)
            self.add_purpose_argument(list_parser)
            self.add_common_args(list_parser)
            return intake_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    #endregion intake subcommand subparser
    # ------------------------------------------------------------------------ +
    #region Common Sub-parsers for Commands
    def add_WORKBOOKS_subparser(self, subparsers) -> None:
        """Add a WORKBOOKS subparser to the provided subparsers.""" 
        try:
            wb_subcmd_parser  = subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Select workbooks for.")
            self.add_wb_index_argument(wb_subcmd_parser)
            # # wb_subcmd_parser.set_defaults(load_cmd="workbooks")
            group = wb_subcmd_parser.add_mutually_exclusive_group(required=True)
            # group.add_argument(
            #     "wb_index", nargs="?",
            #     type=int, 
            #     default = -1,
            #     help=f"Workbook index: number associated in the workbook list, 0-based.")
            group.add_argument(
                "wb_list", nargs="*",
                action='extend',
                type=int, 
                default = [],
                help=f"Workbook index: one or more numbers (spaces, no commas) indexing from the workbook list, 0-based.")
            # group.add_argument(
            #     "-all", dest="all_wbs", 
            #     action = "store_true",
            #     help="All workbooks switch.") 
            return wb_subcmd_parser
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_workflow_argument(self, parser) -> None:
        """Add a workflow argument to the provided parser."""
        try:
            wf_choices = bdm.VALID_BDM_WORKFLOWS
            parser.add_argument(
                "-w", f"--{cp.CK_CMDLINE_WF_KEY}", nargs="?", dest=cp.CK_CMDLINE_WF_KEY, 
                default = None,
                choices=wf_choices,
                help="Specify the workflow key to apply.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_purpose_argument(self, parser) -> None:
        """Add a workflow purpose argument to the provided parser."""
        try:
            purpose_choices = bdm.VALID_WF_PURPOSE_VALUES
            parser.add_argument(
                "-p", f"--{cp.CK_CMDLINE_WF_PURPOSE}", nargs="?",  
                default = cp.CK_WF_INPUT,
                choices=purpose_choices,
                help="Specify the workflow purpose folder.")
            return
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def add_wb_index_argument(self, parser) -> None:
        """Add a wb_index or all_wbs arguments.""" 
        try:
            group = parser.add_mutually_exclusive_group(required=True)
            # group.add_argument(
            #     "wb_index", nargs="?",
            #     type=int, 
            #     default = -1,
            #     help=f"Workbook index: number associated in the workbook list, 0-based.")
            group.add_argument(
                "wb_list", nargs="*",
                action='extend',
                type=int, 
                default = [],
                help=f"Workbook index: one or more numbers (spaces, no commas) indexing from the workbook list, 0-based.")
            group.add_argument(
                "-all", dest="all_wbs", 
                action = "store_true",
                help="All workbooks switch.") 
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
                "--fix_switch", "-fix", 
                action="store_true", 
                help="Fix the any fixable issues.")
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
