# ---------------------------------------------------------------------------- +
#region budget_domain_model_working_data.py
"""BDMWorkingData: The BDMWD object is the working state of the BudMan app.

A BDMWD object is intended to sit apart from the Model and ViewModel layers, serving
as a bridge. The BudMan design language is inherent to the BDMWD and DC
interface. A BDMWD object can be bound as a Data Context (DC) in the application
as it implements the BudManDataContext interface and translates it to the 
Budget Domain Model.
"""
#endregion budget_domain_model_working_data_base_interface.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from pathlib import Path
from typing import Any, TYPE_CHECKING
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages for necessary classes and functions
from budman_namespace import *
from budman_data_context import BudManDataContext
from budget_domain_model.budget_domain_model import BudgetDomainModel
from budget_domain_model.model_base_interface import BDMBaseInterface
from budget_domain_model.model_client_interface import BDMClientInterface
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
MODEL_OBJECT = BDMBaseInterface
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMWorkingData(BudManDataContext, BDMClientInterface):
    """Abstract base class for the Budget Domain Model Working Data (BDMWD). """
    def __init__(self, bdm : Any = None) -> None:
        super().__init__()
        self._budget_domain_model : MODEL_OBJECT = bdm
    # ------------------------------------------------------------------------ +

    # ======================================================================== +
    #region    BDMClientInterface concrete property implementation.
    @property
    def model(self) -> MODEL_OBJECT:
        """Return the model object reference."""
        return self._budget_domain_model
    @model.setter
    def model(self, bdm: MODEL_OBJECT) -> None:
        """Set the model object reference."""
        if not isinstance(bdm, MODEL_OBJECT):
            raise TypeError(f"model must be a {MODEL_OBJECT} instance")
        self._budget_domain_model = bdm
    #endregion BDMClientInterface concrete property implementation.
    # ======================================================================== +

    # ======================================================================== +
    #region    BudManDataContext(BudManDataContextBaseInterface) Method Overrides.
    # ------------------------------------------------------------------------ +
    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return self.bdmwd_FI_KEY_validate(fi_key)
    # ------------------------------------------------------------------------ +

    #endregion BudManDataContext Method Overrides.
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        # First end-to-end DC binding through the BDMClientInterface.
        return self.model.bdm_FI_KEY_validate(fi_key)
    #endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_FI_WORKBOOKS_load(self, 
                                fi_key: str, 
                                wf_key : str, 
                                wb_type : str) -> LOADED_WORKBOOK_LIST:
        """Load WORKBOOKS for the FI,WF, WBT."""
        # TODO: Add to dc_LOADED_WORKBOOKS, handle duplicate keys.
        lwbs = self.model.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
        self.dc_LOADED_WORKBOOKS = lwbs
        return 
    #endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ======================================================================== +



