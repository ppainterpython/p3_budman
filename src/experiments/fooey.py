#------------------------------------------------------------------------------+
# fooey.py - a place to fool around with experiments, not a dependent.
#------------------------------------------------------------------------------+
import logging, shutil, argparse
from typing import Dict, Any
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

class BudgetManagerCLIParser(BudManCmd2ArgumentParser):
    """A class to parse command line arguments for the BudgetModelCLIView class.

    This class is used to parse command line arguments for the BudgetModelCLIView
    class. It uses the cmd2 library to create a command line interface for the
    BudgetModel application.
    """
    def __init__(self) -> None:
        """Initialize the BudgetModelCLIParser class."""
        self.subparsers = None
        self.init_cmd_parser = None #BudManCmd2ArgumentParser()
        self.show_cmd_parser = None
        self.load_cmd_parser = None
        self.save_cmd_parser = None
        self.val_cmd_parser = None
        # self.show_cmd_parser = BudManCmd2ArgumentParser()
        # self.load_cmd_parser = BudManCmd2ArgumentParser()
        # self.save_cmd_parser = BudManCmd2ArgumentParser()
        # self.val_cmd_parser = BudManCmd2ArgumentParser()
        # self.show_cmd_parser_setup()
        # self.load_cmd_parser_setup()
        # self.save_cmd_parser_setup()
        # self.val_cmd_parser_setup()
    def initialize(self,tsp) -> None:
        """Initialize the BudgetManagerCLIParser class."""
        try:
            # Initialize the command line argument parsers
            self.subparsers = tsp
            self.init_cmd_parser_setup()
            # self.show_cmd_parser = BudManCmd2ArgumentParser()
            # self.load_cmd_parser = BudManCmd2ArgumentParser()
            # self.save_cmd_parser = BudManCmd2ArgumentParser()
            # self.val_cmd_parser = BudManCmd2ArgumentParser()
        except Exception as e:
            # logger.exception(p3u.exc_err_msg(e))
            print(p3u.exc_err_msg(e))
            raise

    def init_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the init command."""
        try:
            # init subcommands: workbooks, and fin_inst
            # self.init_cmd_subparser = self.subparsers.add_subparsers(
            #     dest="init_cmd")
            self.init_cmd_parser = self.subparsers.add_parser(
                "init", help="Initialize the Budget Manager application.")
            self.init_cmd_parser.add_argument(
                "fi_key", nargs="?", action="store", dest="fi_key", 
                default=None,
                const="all",
                help="Initialize one or all of the financial institutions.")
            self.init_cmd_parser.add_argument(
                "wf_key", nargs="?", dest="wf_key", 
                action="store", 
                default='all',
                help="Workflow key value.")
            # init workbooks subcommand
            # self.init_wb_subcmd_parser = self.init_cmd_subparsers.add_parser(
            #     "workbooks", 
            #     aliases=["wb", "WB"], 
            #     help="Initialize workbook(s).")
            # self.init_wb_subcmd_parser.set_defaults(init_cmd="workbooks")
            # self.init_wb_subcmd_parser.add_argument(
            #     "wb_name", nargs="?",
            #     action="store", 
            #     default=None,
            #     help="Workbook name.")
            # # init fin_int subcommand
            # self.init_fi_subcmd_parser = self.init_cmd_subparsers.add_parser(
            #     "fin_inst",
            #     aliases=["fi", "FI", "financial_institutions"], 
            #     help="Initialize Financial Institution(s).")
            # self.init_fi_subcmd_parser.set_defaults(init_cmd="fin_inst")
            # self.init_fi_subcmd_parser.add_argument(
            #     "fi_key", nargs="?", 
            #     default= "all",
            #     help="FI key value.")
            # self.init_fi_subcmd_parser.add_argument(
            #     "wf_key", nargs="?", 
            #     action="store", 
            #     default='all',
            #     help="Workflow key value.")
            # self.init_fi_subcmd_parser.add_argument(
            #     "wb_name", nargs="?", 
            #     action="store", 
            #     default='all',
            #     help="Workbook name.")
        except Exception as e:
            # logger.exception(p3u.exc_err_msg(e))
            print(p3u.exc_err_msg(e))
            raise

    def show_cmd_parser_setup(self) -> None:
        """Setup the command line argument parsers for the show command."""
        try:
            # show subcommands: workbooks, fin_inst, workflows, and workbooks
            self.show_cmd_subparsers = self.show_cmd_parser.add_subparsers(
                dest="show_cmd")
            # subcommand show fi_inst [fi_key] [wf_key] [wb_name]
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
                default='all',
                help="Workflow key value.")
            # show workbooks subcommand
            self.show_wb_subcmd_parser  = self.show_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Show workbook information.")
            self.show_wb_subcmd_parser.set_defaults(show_cmd="workbooks")
            self.show_wb_subcmd_parser.add_argument(
                "wb_name", nargs="?", 
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
            # Save subcommands: BUDMAN_STORE, workbooks
            self.save_cmd_subparsers = self.save_cmd_parser.add_subparsers(
                dest="save_cmd")
            # subcommand save BUDMAN_STORE
            self.save_bm_store_subcmd_parser = self.save_cmd_subparsers.add_parser(
                "BUDMAN_STORE",
                aliases=["store", "BMS", "budget_manager_store","BUDMAN_STORE"], 
                help="Save the Budget Manager Store file.")
            self.save_bm_store_subcmd_parser.set_defaults(save_cmd="BUDMAN_STORE")
            # subcommand save workbooks [wb_name] [fi_key]
            self.save_wb_subcmd_parser  = self.save_cmd_subparsers.add_parser(
                "workbooks",
                aliases=["wb", "WB"], 
                help="Save workbook information.")
            self.save_wb_subcmd_parser.set_defaults(save_cmd="workbooks")
            self.save_wb_subcmd_parser.add_argument(
                "wb_name", nargs="?", 
                action="store", 
                default='all',
                help="Workbook reference, name or number from show workbooks.")
            self.save_wb_subcmd_parser.add_argument(
                "fi_key", nargs="?", 
                default= "all",
                help="FI key value.") 
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
                default='all',
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
                default='all',
                help="fi_key value for valid Fin. Inst. or 'all'.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    # ------------------------------------------------------------------------ +
cli_parser : BudgetManagerCLIParser = BudgetManagerCLIParser()
def init_cmd_parser() -> BudManCmd2ArgumentParser:
    subcmd_parser = cli_parser.init_cmd_parser if cli_parser else None
    return subcmd_parser
def show_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.show_cmd_parser if cli_parser else None
def load_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.load_cmd_parser if cli_parser else None
def save_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.save_cmd_parser if cli_parser else None
def val_cmd_parser() -> BudManCmd2ArgumentParser:
    return cli_parser.val_cmd_parser if cli_parser else None

def _filter_opts(opts) -> Dict[str, Any]:
    if opts is None: return {}
    oc = vars(opts).copy()
    oc.pop('cmd2_statement')
    oc.pop('cmd2_handler')
    return oc
def _log_cli_cmd_execute(self, opts):
    """Log the command and options. Retrun True if parse_only."""
    logger.info(f"Execute Command: {str(_filter_opts(opts))}")
    return self.parse_only
def _log_cli_cmd_complete(self, opts):
    logger.info(f"Complete Command: {str(_filter_opts(opts))}")
def _show_args_only(cli_view : "BudgetManagerCLIView", opts) -> bool:
    oc = vars(opts).copy()
    oc.pop('cmd2_statement')
    oc.pop('cmd2_handler')
    cli_view.poutput(f"args: {str(oc)} parse_only: {cli_view.parse_only}")
    return cli_view.parse_only

BMCLI_SYSTEM_EXIT_WARNING = "Not exiting due to SystemExit"
PO_OFF_PROMPT = "p3budman> "
PO_ON_PROMPT = "po-p3budman> "
class testapp(cmd2.Cmd):
    """Test application for the BudgetManager CLI."""
    prompt = "budman> "
    intro = "\nWelcome to the Budget Manager CLI. Type help or ? to list commands.\n"
    def __init__(self):
        super().__init__()
        self.parse_only = False
        self.prompt = PO_OFF_PROMPT
        self.intro = "Welcome to the BudgetManager CLI. Type help or ? to list commands.\n"
        self.budget_model = None  # Placeholder for the budget model instance
        self.cli_parser = cli_parser

    def initialize(self):   
        self.cli_parser.initialize()

    def do_quit(self, line: str):
        """Quit the BudgetManager CLI."""
        print("Quitting BudgetManager CLI.")
        return True

    def do_parse_only(self, opts):
        """Set parse-only mode on|off|toggle."""
        if opts.po_value == "on":
            self.parse_only = True
            self.prompt = PO_ON_PROMPT
        elif opts.po_value == "off":
            self.parse_only = False
            self.prompt = PO_OFF_PROMPT
        elif opts.po_value == "toggle":
            self.parse_only = not self.parse_only
            self.prompt = PO_ON_PROMPT if self.parse_only else PO_OFF_PROMPT
        else:
            print(f"Invalid parse-only value: {opts.po_value}")
            return False
        print(f"Parse-only mode set to: {self.parse_only}")
        return True 
    @with_argparser(init_cmd_parser())
    def do_init(self, opts):
        """Init the data context in the Budget Manager application."""
        try:
            print(f"args: {str(_filter_opts(opts))}")
            _ = opts
        except SystemExit:
            # Handle the case where argparse exits the program
            print(BMCLI_SYSTEM_EXIT_WARNING)
        except Exception as e:
            print(str(e))
if __name__ == "__main__":
    # tp = BudgetManagerCLIParser()
    # tsp = tp.add_subparsers(title="subcommands",help="commands")
    # tp.initialize(tsp)
    # ta = testapp()
    # ta.initialize()
    # ta.cmdloop() # Application Main()
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='commands')

    # A list command
    list_parser = subparsers.add_parser('list', help='List contents')
    list_parser.add_argument('dirname', action='store', help='Directory to list')

    # A create command
    create_parser = subparsers.add_parser('create', help='Create a directory')
    create_parser.add_argument('dirname', action='store', help='New directory to create')
    create_parser.add_argument('--read-only', default=False, action='store_true',
                            help='Set permissions to prevent writing to the directory',
                            )

    # A delete command
    delete_parser = subparsers.add_parser('delete', help='Remove a directory')
    delete_parser.add_argument('dirname', action='store', help='The directory to remove')
    delete_parser.add_argument('--recursive', '-r', default=False, action='store_true',
                            help='Remove the contents of the directory, too',
                            )

    print (parser.parse_args())
exit(0)

# class BudgetModelCLIView(cmd2.Cmd):
#     prompt = "p3b> "
#     intro = "Welcome to the BudgetModel CLI. Type help or ? to list commands.\n"

#     init_parser = Cmd2ArgumentParser()
#     try:
#         group = init_parser.add_mutually_exclusive_group(required=False)
#         group.add_argument("-fi", nargs="?", action="store", dest="fi", 
#                         default=None,
#                         const="all",
#                         help="Initialize one or all of the financial institutions.")
#         group.add_argument("-bsm", action="store_true", dest="bsm",
#                         default = False,
#                         help="Initialize the BSM.")     
#     except Exception as e:
#         print(f"Error initializing parser: {e}")
#     # init command implementation                                              +
#     @with_argparser(init_parser)
#     def do_init(self, opts):
#         """Init BugetModel properties and values.."""
#         try:
#             self.poutput(f"args: {str(opts)}")
#         except SystemExit:
#             # Handle the case where argparse exits the program
#             self.pwarning("Not exiting due to SystemExit")
#             pass
#         except Exception as e:
#             self.pexcept(e)

#     # show command line arguments                                              +
#     show_parser = Cmd2ArgumentParser()
#     show_subparsers = show_parser.add_subparsers(dest="show_cmd")
#     try:
#         wb_parser  = show_subparsers.add_parser("workbook",
#                                 aliases=["wb", "WB"], 
#                                 help="Show workbook information.")
#         wb_parser.add_argument("wb_name", nargs="?", action="store", 
#                                  default=None,
#                                 help="Workbook name.")
#         fi_parser = show_subparsers.add_parser("financial_institution",
#                                 aliases=["fi", "FI"], 
#                                 help="Show Financial Institution information.")
#         fi_parser.add_argument("fi_key", nargs="?", 
#                                 default= "all",
#                                 help="FI key value.") 
#     except Exception as e:
#         print(f"Error initializing parser: {e}")

#     # show command implementation                                              +
#     @with_argparser(show_parser)
#     def do_show(self, opts):
#         """Show BugetModel properties and values."""
#         try:
#             self.poutput(f"args: {str(opts)}")
#         except SystemExit as e:
#             # Handle the case where argparse exits the program
#             # print("Exiting due to SystemExit")
#             pass
#         except Exception as e:
#             self.perror(f"Error showing BudgetModel: {e}")

#     # load command line arguments                                              +
#     load_parser = Cmd2ArgumentParser()
#     load_parser.add_argument("wb", nargs="?", action="store", default=True,
#                         help="Load workbooks.")
#     load_parser.add_argument("-w", action="store", default = "categorization",
#                         help="Workflow for workbooks to load.") 
#     # load command implementation                                              +
#     @with_argparser(load_parser)
#     def do_load(self, opts):
#         """Load BugetModel data items into app session."""
#         try:
#             # self.budget_model.bm_load()
#             1 / 0  # TODO: remove this line
#             print("BudgetModel loaded.")
#         except Exception as e:
#             self.pexcept(e)
#     def do_quit(self, line: str):
#         """Quit the BudgetModel CLI."""
#         print("Quitting BudgetModel CLI.")
#         return True 

# #region Local __main__ stand-alone
# if __name__ == "__main__":
#     BudgetModelCLIView().cmdloop() # Application Main()
#     exit(1)
# #endregion Local __main__ stand-alone







# import re

# sample = [
#     "Bank of America - Bank - Primary Checking Acct",
#     "Bank of America - Credit Card - Visa Signature",
#     "Bank of America - Bank - Primary Checking Acct",
#     "Bank of America - Credit Card - Visa Signature",
#     "Bank of America - Credit Card - Visa Signature"
# ]

# modified_sample = []

# # Regular expression to extract the third part
# pattern = r'^[^-]+-\s*[^-]+-\s*(.+)$'

# # Iterate through the sample array and apply the regex replacement
# for item in sample:
#     modified_value = re.sub(pattern, r'\1', item)  # Replace with the third part
#     modified_sample.append(modified_value)

# print(modified_sample)