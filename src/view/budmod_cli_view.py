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

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l
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

class BudgetModelCLIView(cmd2.Cmd):
    # ======================================================================== +
    #region BudgetModelCLIView class
    """A view for BudgetModel, a command line interface.
    
    Operates under MVVM pattern, strictly. Instantiated with a blind view_model.
    TODO: Use ABC for view_model interface.
    """
    # https://pymotw.com/2/argparse/index.html#module-argparse
    #
    # Using cmd and argparse together, to integrate the help system, need to 
    # share the argparse parser between the two, for each command.
    prompt = "p3b> "
    intro = "Welcome to the BudgetModel CLI. Type help or ? to list commands.\n"

    def __init__(self, 
                 data_context : object | MockViewModel = None) -> None:
        super().__init__()
        self._data_context = MockViewModel() if data_context is None else data_context
    
    @property
    def data_context(self) -> object:
        """Get the data_context property."""
        return self._data_context
    
    @data_context.setter
    def data_context(self, value: object) -> None:
        """Set the data_context property."""
        if not isinstance(value, (MockViewModel, object)):
            raise ValueError("data_context must be a MockViewModel or object.")
        self._data_context = value
    #endregion BudgetModelCLI class
    # ======================================================================== +

    # ======================================================================== +
    #region CLIViewModel Cmd methods
    # ======================================================================== +
    # ------------------------------------------------------------------------ +
    #region init command - initialize aspects of the BudgetModel application.
    # init command line arguments                                              +
    init_parser = Cmd2ArgumentParser()
    group = init_parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-fi", nargs="?", action="store", dest="fi", 
                    default=None,
                    const="all",
                    help="Initialize one or all of the financial institutions.")
    group.add_argument("-bsm", action="store_true", dest="bsm",
                    default = False,
                    help="Initialize the BSM.")     
    # init command implementation                                              +
    @with_argparser(init_parser)
    def do_init(self, opts):
        """Init BugetModel properties and values.."""
        try:
            self.poutput(f"args: {str(opts)}")
            if opts.fi:
                self.data_context.FI_init_cmd(opts.fi)
        except SystemExit:
            # Handle the case where argparse exits the program
            self.pwarning("Not exiting due to SystemExit")
            pass
        except Exception as e:
            self.pexcept(e)
    #endregion init command - initialize aspects of the BudgetModel application.
    # ------------------------------------------------------------------------ +
    #region Show command - workbooks, status, etc.
    # show command line arguments                                              +
    show_parser = Cmd2ArgumentParser()
    show_parser.add_argument("wb", nargs="?", action="store", default=False,
                        help="Show loaded workbooks.")
    show_parser.add_argument("vmwb", nargs="?", action="store", default=False,
                        help="Show workbooks.")
    show_parser.add_argument("-l", action="store_true", default = False,
                             dest="loaded_workbooks",
                        help="Show loaded workbooks.") 
    # show command implementation                                              +
    @with_argparser(show_parser)
    def do_show(self, opts):
        """Show BugetModel properties and values."""
        try:
            # TODO: vm method to load the workflow workbooks.
            if opts.loaded_workbooks:
                names = self.data_context.bdm_vm_BDWD_LOADED_WORKBOOKS_get_names()
                self.poutput(f"Loaded workbooks({len(names)}): {names}")
        # except Cmd2Arg as e:
        #     print(f"Error parsing arguments: {e}")
        except SystemExit as e:
            # Handle the case where argparse exits the program
            # print("Exiting due to SystemExit")
            pass
        except Exception as e:
            self.perror(f"Error showing BudgetModel: {e}")
    #endregion Show command
    # ------------------------------------------------------------------------ +
    #region Load command - load workbooks
    # load command line arguments                                              +
    load_parser = Cmd2ArgumentParser()
    load_parser.add_argument("wb", nargs="?", action="store", default=True,
                        help="Load workbooks.")
    load_parser.add_argument("-w", action="store", default = "categorization",
                        help="Workflow for workbooks to load.") 
    # load command implementation                                              +
    @with_argparser(load_parser)
    def do_load(self, opts):
        """Load BugetModel data items into app session."""
        try:
            # self.budget_model.bm_load()
            1 / 0  # TODO: remove this line
            print("BudgetModel loaded.")
        except Exception as e:
            self.pexcept(e)
    #endregion Load command - load workbooks
    # ------------------------------------------------------------------------ +
    def do_save(self, line: str):
        """Save the BudgetModel to a file."""
        try:
            # self.budget_model.bm_save()
            print("BudgetModel saved.")
        except Exception as e:
            self.perror(f"Error saving BudgetModel: {e}")

    
    def do_exit(self, line: str):
        """Exit the BudgetModel CLI."""
        print("Exiting BudgetModel CLI.")
        return True
    
    def do_quit(self, line: str):
        """Quit the BudgetModel CLI."""
        print("Quitting BudgetModel CLI.")
        return True 
    
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        from budmod import configure_logging
        import view_model.bdm_view_model as p3vm
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
