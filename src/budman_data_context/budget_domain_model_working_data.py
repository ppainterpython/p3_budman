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
    # ======================================================================== +
    #region    BDMWorkingData class intrinsics
    # ------------------------------------------------------------------------ +
    #region __init__() method init during BDMWorkingData constructor.
    def __init__(self, bdm : Any = None) -> None:
        super().__init__()
        self._budget_domain_model : MODEL_OBJECT = bdm
    #endregion __init__() method init during BDMWorkingData constructor.
    # ------------------------------------------------------------------------ +
    #region initialize() method initializes the BDMWorkingData instance.
    def initialize(self) -> "BDMWorkingData":
        """Initialize the BDMWorkingData instance after construction.
        
        Apply any necessary initializations to the BDMWorkingData instance. 
        First, update the DC with BDM_CONFIG from model.bdm_config_object.
        Second, update the DC with appropriate values from BDMClientInterface 
        concerning the BDM Working Data (BDMWD).
        Returns:
            BDMWorkingData: The initialized BDMWorkingData instance.
        """
        try:
            # First, update the DC with BDM_CONFIG from model.bdm_config_object.
            bdm_config = getattr(self.model,BDM_CONFIG_OBJECT, None)
            if bdm_config is None:
                m = "The model does not have a bdm_config_object."
                logger.error(m)
                raise ValueError(m)
            # assume if the model has the bdm_config_object, it is a valid 
            # BDM_CONFIG dictionary.
            self.dc_BDM_STORE = bdm_config
            # Second, update the DC with appropriate values from BDMClientInterface.
            # self.dc_FI_KEY = self.model.bdm_FI_KEY
            # self.dc_WF_KEY = self.model.bdm_WF_KEY
            self.dc_WORKBOOKS = self.bdmwd_WORKBOOKS()
            self.dc_LOADED_WORKBOOKS = self.bdmwd_LOADED_WORKBOOKS()
            self.dc_INITIALIZED = True
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
        # 
    #endregion __init__() method initializes the BDMWorkingData instance.
    # ------------------------------------------------------------------------ +
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
    #endregion    BDMWorkingData class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    BudManDataContext Property/Method Overrides.
    # ------------------------------------------------------------------------ +
    @property
    def dc_WORKBOOKS(self) -> WORKBOOK_LIST:
        """Return the list of workbooks in the DC, pull from the BDMWD."""
        return self.bdmwd_WORKBOOKS()
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: WORKBOOK_LIST) -> None:
        """Set the list of workbooks in the DC."""
        logger.warning("Setting dc_WORKBOOKS directly is not supported.")

    @property
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_LIST:
        """Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available. Pull
        from the BDMWD."""
        return self.bdmwd_LOADED_WORKBOOKS()
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_LIST) -> None:
        """Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        logger.warning("Setting dc_LOADED_WORKBOOKS directly is not supported.")

    def dc_WORKBOOK_index(self, wb_name: str = None) -> int:
        """Return the index of a workbook based on wb_name.
        
        Args:
            wb_name (str): The name of the workbook to find.
        Returns:
            int: The index of the workbook in the WORKBOOK_LIST, or -1 if not found.
        """
        try:
            wbl = self.dc_WORKBOOKS
            for i, (wb_name_in_list, _) in enumerate(wbl):
                if wb_name_in_list == wb_name:
                    return i
            return -1
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        return self.bdmwd_FI_KEY_validate(fi_key)
    # ------------------------------------------------------------------------ +

    #endregion BudManDataContext Method Overrides.
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMWorkingDataBaseInterface BDMWD DC-aware Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_WORKBOOKS(self) -> WORKBOOK_LIST:
        """Return the WORKBOOK_LIST from the BDMWD."""
        # Ask the model for the bdmwd_WORKBOOKS.
        return self.model.bdmwd_WORKBOOKS_get()
    def bdmwd_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_LIST:
        """Return the LOADED_WORKBOOK_LIST from the BDMWD."""
        # Ask the model for the bdmwd_LOADED_WORKBOOKS.
        return self.model.bdmwd_LOADED_WORKBOOKS_get()

#endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingDataBaseInterface BDMWD (fi,wf,wb)-aware Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_FI_KEY_validate(self, fi_key: str) -> bool:
        """Validate the provided FI_KEY."""
        # First end-to-end DC binding through the BDMClientInterface.
        return self.model.bdm_FI_KEY_validate(fi_key)
    def bdmwd_FI_WORKBOOKS_load(self, 
                                fi_key: str, 
                                wf_key : str, 
                                wb_type : str) -> LOADED_WORKBOOK_LIST:
        """Load WORKBOOKS for the FI,WF, WBT."""
        lwbs = self.model.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
        self.dc_LOADED_WORKBOOKS = lwbs
        return 
    #endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ======================================================================== +



