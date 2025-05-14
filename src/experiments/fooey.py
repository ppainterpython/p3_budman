#------------------------------------------------------------------------------+
# fooey.py - a place to fool around with experiments, not a dependent.
#------------------------------------------------------------------------------+
from config import settings

foo = settings.app_name
print(f"foo: {foo}")
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