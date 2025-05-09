# ---------------------------------------------------------------------------- +
#region budmod_cli_view.py module
""" budmod_cli_view.py cli-style view for BudgetModel (budmod).
"""
#endregion budmod_cli_view.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any
import cmd, argparse

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l

# local modules and packages
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings.app_name)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region MockViewModel class
class MockViewModel():
    """Mock view_model object for the BudgetModel.
    
    Simulates an unknown view_model object for the BudgetModel.
    Supports dot notation for accessing attributes."""
    # TODO: Use ABC for view_model interface. 
    def __getattr__(self, item):
        return self[item] if item in self.__dict__ else None
    
    def __setattr__(self, item, value):
        self[item] = value

#endregion MockViewModel class
# ---------------------------------------------------------------------------- +
#region BudgetModelCLIView class
class BudgetModelCLIView(cmd.Cmd):
    """Command line interface for the BudgetModel.
    
    Operates under MVVM pattern, strictly. BudgetModelCLIView"""
    # https://pymotw.com/2/argparse/index.html#module-argparse
    #
    # Using cmd and argparse together, to integrate the help system, need to 
    # share the argparse parser between the two, for each command.
    prompt = "p3b> "
    intro = "Welcome to the BudgetModel CLI. Type help or ? to list commands.\n"

    def __init__(self, 
                 cmd_vm : object | MockViewModel = None) -> None:
        super().__init__()
        self.cmd_vm = MockViewModel() if cmd_vm is None else cmd_vm

    def do_init(self, line: str):
        """Initialize the BudgetModel."""
        try:
            if self.cmd_vm is None:
                print("BudgetModelCommandViewModel initialized.")
                return
            print(f"BudgetModelCommandViewModel already initialized.")
        except Exception as e:
            print(f"Error initializing BudgetModel: {e}")

    def _get_parser_show(self):
        """Get the parser for the show command."""
        parser = argparse.ArgumentParser(
            description="Show BugetModle properties and values.")
        parser.add_argument("wb", nargs="?", action="store", default=False,
                            help="Show workbooks.")
        parser.add_argument("-l", action="store", default = False,
                            help="Show loaded workbooks.") 
        return parser
    
    def help_show(self):
        """Show argarse-generated help for show command."""
        parser = self._get_parser_show()
        parser.print_help()

    def do_show(self, arg):
        """Show objects and properties from BudgetModel.
        
        Method self._get_parser_show() generates the parser for the show command.
        The second argument determines what to show, defaults to loaded workbooks.
        """
        try:
            parser = self._get_parser_show()
            # self.budget_model.bm_show()
            args = parser.parse_args(arg.split())
            # TODO: vm method to load the workflow workbooks.
            lwbs = self.cmd_vm.get_LOADED_WORKBOOKS()
        except argparse.ArgumentError as e:
            print(f"Error parsing arguments: {e}")
        except SystemExit:
            # Handle the case where argparse exits the program
            # print("Exiting due to SystemExit")
            pass
        except Exception as e:
            print(f"Error showing BudgetModel: {e}")
    def do_save(self, line: str):
        """Save the BudgetModel to a file."""
        try:
            # self.budget_model.bm_save()
            print("BudgetModel saved.")
        except Exception as e:
            print(f"Error saving BudgetModel: {e}")

    def do_load(self, line: str):
        """Load the BudgetModel from a file."""
        try:
            # self.budget_model.bm_load()
            print("BudgetModel loaded.")
        except Exception as e:
            print(f"Error loading BudgetModel: {e}")
    
    def do_exit(self, line: str):
        """Exit the BudgetModel CLI."""
        print("Exiting BudgetModel CLI.")
        return True
    
    def do_quit(self, line: str):
        """Quit the BudgetModel CLI."""
        print("Quitting BudgetModel CLI.")
        return True 
    
#endregion BudgetModelCLI class
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        from budmod import configure_logging
        import view_model.budmod_command_view_model as p3vm
        import data.p3_budget_model as p3b
        configure_logging(settings.app_name)
        logger.setLevel(logging.DEBUG)
        # Initalize the p3_budget_model package.
        bmt = p3b.BudgetModelTemplate()
        bm = p3b.BudgetModel().bdm_initialize(bmt) # use the template to init
        BudgetModelCLIView(bm).cmdloop() # Application Main()
    except Exception as e:
        m = p3u.exc_msg("__main__", e)
        logger.error(m)
    logger.info(f"Exiting {settings.app_name}...")
    exit(1)
#endregion Local __main__ stand-alone
# ---------------------------------------------------------------------------- +
