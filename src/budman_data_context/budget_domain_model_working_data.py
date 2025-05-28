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
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages
from budman_namespace import (
    FI_KEY, WF_KEY, WB_NAME, WB_TYPE,
    WB_REF, WB_INFO, WB_INFO_LEVEL_INFO, WB_INFO_LEVEL_VERBOSE,
    WB_INFO_VALID_LEVELS, RELOAD_TARGET, CATEGORY_MAP,
    ALL_KEY, P2, P4, P6, P8, P10, MODEL_OBJECT, THIS_APP_NAME
    )
from budman_data_context import BudManDataContext
import budman_model as p3bm
from budman_model import P2, P4, P6, P8, P10
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# MODEL_OBJECT = p3bm.BudgetDomainModel
logger = logging.getLogger(THIS_APP_NAME)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMWorkingData(BudManDataContext):
    """Abstract base class for the Budget Domain Model Working Data (BDMWD). """
    def __init__(self, bdm : MODEL_OBJECT = None) -> None:
        super().__init__()
        self._budget_domain_model : MODEL_OBJECT = bdm
    # ------------------------------------------------------------------------ +
    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return self.bdmwd_FI_KEY_validate(fi_key)
    # ------------------------------------------------------------------------ +
    @property
    def model(self) -> MODEL_OBJECT:
        """Return the model object reference."""
        return self._budget_domain_model
    @model.setter
    def model(self, bdm: MODEL_OBJECT) -> None:
        """Set the model object reference."""
        if not isinstance(bdm, MODEL_OBJECT):
            raise TypeError("model must be a BudgetDomainModel instance")
        self._budget_domain_model = bdm
    # ======================================================================== +
    #region    BudManDataContext Method Overrides.
    # ------------------------------------------------------------------------ +

    #endregion BudManDataContext Method Overrides.
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return self.model.bdm_FI_KEY_validate(fi_key)

    #endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ======================================================================== +



