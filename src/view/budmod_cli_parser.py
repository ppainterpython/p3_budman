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
#region argparse declarations for the BudgetModelCLIView class commands.
# init command line arguments
try:
    init_cmd_parser = Cmd2ArgumentParser()
    init_cmd_subparsers = init_cmd_parser.add_subparsers(dest="init_cmd")
    init_wb_subcmd_parser  = init_cmd_subparsers.add_parser("workbook",
                            aliases=["wb", "WB"], 
                            help="Initialize the workbook.")
    init_wb_subcmd_parser.add_argument("wb_name", nargs="?", action="store", 
                                default=None,
                            help="Workbook name.")
    init_fi_subcmd_parser = init_cmd_subparsers.add_parser("financial_institution",
                            aliases=["fi", "FI"], 
                            help="Initialize Financial Institution.")
    init_fi_subcmd_parser.add_argument("fi_key", nargs="?", 
                            default= "all",
                            help="FI key value.")
except Exception as e:
    logger.exception(p3u.exc_err_msg(e))

# show command line arguments
try:
    show_cmd_parser = Cmd2ArgumentParser()
    show_cmd_subparsers = show_cmd_parser.add_subparsers(dest="show_cmd")
    show_wb_subcmd_parser  = show_cmd_subparsers.add_parser("workbook",
                            aliases=["wb", "WB"], 
                            help="Show workbook information.")
    show_wb_subcmd_parser.add_argument("wb_name", nargs="?", action="store", 
                            default=None,
                            help="Workbook name.")
    show_fi_subcmd_parser = show_cmd_subparsers.add_parser("financial_institution",
                            aliases=["fi", "FI"], 
                            help="Show Financial Institution information.")
    show_fi_subcmd_parser.add_argument("fi_key", nargs="?", 
                            default= "all",
                            help="FI key value.") 
except Exception as e:
    logger.exception(p3u.exc_err_msg(e))

# load command line arguments
load_cmd_parser = Cmd2ArgumentParser()
load_cmd_parser.add_argument("wb", nargs="?", action="store", default=True,
                    help="Load workbooks.")
load_cmd_parser.add_argument("-w", action="store", default = "categorization",
                    help="Workflow for workbooks to load.") 
#endregion argparse declarations for the BudgetModelCLIView class commands.
# ---------------------------------------------------------------------------- +
