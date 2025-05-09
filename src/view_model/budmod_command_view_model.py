# ---------------------------------------------------------------------------- +
#region budmod_command_view_model.py module
""" budmod_command_view_model.py command-style view_model for BudgetModel (budmod).
"""
#endregion budmod_command_view.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l

# local modules and packages
from p3_excel_budget_constants import  *
import data.p3_budget_model as p3bm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings.app_name)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
class BudgetModelCommandViewModel():
    """Command action view_model for the BudgetModel."""
    def __init__(self,bm : p3bm.BudgetModel = None) -> None:
        super().__init__()
        self.intitialized = False
        self.budget_model : p3bm.BudgetModel = bm
    
    def initialize(self) -> None:
        """Initialize the command view_model."""
        try:
            if (self.budget_model is None or 
                not isinstance(self.budget_model, p3bm.BudgetModel)):
                self.budget_model = p3bm.BudgetModel().bdm_initialize()
            if not self.budget_model.bm_initialized: 
                raise ValueError("BudgetModel is not initialized.")
            self.intitialized = True
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def get_LOADED_WORKBOOKS(self) -> List[Tuple[str, object]]:
        """Get the loaded workbooks."""
        return self.budget_model.bdwd_LOADED_WORKBOOKS()