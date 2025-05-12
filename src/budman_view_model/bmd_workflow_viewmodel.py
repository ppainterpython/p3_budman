#region bdm_workflow_viewmodel.py module
""" bdm_workflow_viewmodel and BDMWorkflowViewModel class
implements the workflow concerns for the Budget Domain Model, providing 
an API to upstream actors such as User Interfaces and other system packages.

Following a rough MVVM pattern, the BDMWorkflowViewModel class is  
the ViewModel. 

At present, the BudgetModel class is a singleton class that manages the 
mapping of excel "workbooks" stored in the filesystem to the budget model.
The BudgetModel class presents properties and methods to the outside world.
Methods are separated into ViewModel-ish methods for the Budget Domain 
and Model-ish methods for the Storage Domain, which is the filesystem.

In the Budget Domain Model, a data pipeline pattern is used, anticipating 
"raw data" will be introduced from finanancial institutions (FI) and and 
proceed through a series of transformations to a "finalized", although
updatable budget model. Raw data is a "workbook", often an excel file, 
or a .cvs file.

A "folder" concept is aligned with the stages of transformation as a 
series of "workflows" applied to the data. Roughly, workflow stage works 
on data in its associated folder and then may process data inplace locally 
or as modifications or output to workbooks to another stage folder.

[raw_data] -> [incoming] -> [categorized] -> [finalized]

Workflows are functional units of work with clearly defined concerns applied
to input data and producing outout data. 

Key Concepts:
-------------
- Folders: containers of workbooks associated with a workflow stage.
- Workflows: a defined set of process functions applied to data.
- Workbooks: a container of financial transaction data, e.g., excel file.
- Raw Data: original data from a financial institution (FI), read-only.
- Financial Budget: the finalized output, composed of workbooks,
    representing time-series transactions categorized by payments and
    deposits (debits and credits).
- Financial Institution (FI): a bank or brokerage financial institution.
    
Perhaps the primary domain should be "Financial Budget" instead of
"Budget Model". The FB Domain and the "Storage Domain" or Sub-Domain. 

The Budget Domain Model has the concern of presenting an API that is 
independent of where the workbook data is sourced and stored. The 
Budget Storage Model has the concern of managing sourcing and storing 
workbooks in the filesystem. It maps the Budget Domain structure to 
filesystem folders and files.

Assumptions:
- The FI transactions are in a folder specified in the budget_config.
- Banking transaction files are typical excel spreadsheets. 
- Data content starts in cell A1.
- Row 1 contains column headers. All subsequent rows are data.
"""
#endregion budget_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from ..budman_model.budget_model_constants import *
from ..budman_model.budget_domain_model import BudgetModel
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class SingletonMeta(type):
    """Metaclass for implementing the Singleton pattern for subclasses."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
# ---------------------------------------------------------------------------- +
class BDMWorkflowViewModel(metaclass=SingletonMeta):
    
    def __init__(self, budget_model: BudgetModel = None) -> None:
        """Initialize the BDMWorkflowViewModel class.

        Args:
            budget_model (BudgetModel): The BudgetModel instance.
        """
        self._budget_model = budget_model if budget_model else BudgetModel()
        self._initialized = False
        self._created_date = time.time()
        self._last_modified_date = self._created_date
        self._last_modified_by = getpass.getuser()
        self._options = None

        