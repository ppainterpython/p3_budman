# ---------------------------------------------------------------------------- +
#region budget_domain_model_working_data_base_interface.py
"""BDMWorkingDataBaseInterface: An abstract base class interface for BDMWD objects.
This class defines the interface for Budget Domain Model Working Data (BDMWD) objects
in terms of properties and methods, as an extension to the BudManDataContextBaseInterface
class. Therefore, subclasses must implement the methods and properties
defined herein AND in the BudManDataContextBaseInterface class.

A BDMWD object is intended to sit apart from the Model and ViewModel layers, serving
as a bridge. The BudMan design language is inherent to the BDMWD and DC
interface. A BDMWD object can be bound as a Data Context (DC) in the application.
"""
#endregion budget_domain_model_working_data_base_interface.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from abc import ABC, abstractmethod
from pathlib import Path
# third-party modules and packages
from openpyxl import Workbook

# local modules and packages
from src.budget_manager_domain_model import design_language_namespace as bdmns
from budman_data_context_interface import BudManDataContext
import budman_model as p3bm
from budman_model import P2, P4, P6, P8, P10

# local libraries
import logging, p3_utils as p3u, p3logging as p3l
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(bdmns.THIS_APP_NAME)
#endregion Globals
# ---------------------------------------------------------------------------- +
class BDMWorkingDataBaseInterface(BudManDataContext):
    """Abstract base class for the Budget Domain Model Working Data (BDMWD). """

    # ======================================================================== +
    #region    BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +

    #endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ======================================================================== +
    def __init__(self, bdm : p3bm.BudgetDomainModel = None) -> None:
        super().__init__()
        self._budget_domain_model : p3bm.BudgetDomainModel = bdm



