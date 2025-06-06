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
            # First, update the DC with BDM_STORE from model.bdm_store_object.
            bdm_store = getattr(self.model,BDM_STORE_OBJECT, None)
            if bdm_store is None:
                m = "The model does not have a bdm_store_object."
                logger.error(m)
                raise ValueError(m)
            # assume if the model has the bdm_store_object, it is a valid 
            # BDM_STORE dictionary.
            self.dc_BDM_STORE = bdm_store
            # Second, update the DC with appropriate values from BDMClientInterface.
            bdm_store_dc = bdm_store.get(BDM_DATA_CONTEXT, {})
            self.dc_FI_KEY = bdm_store_dc.get(DC_FI_KEY, None)
            self.dc_WF_KEY = bdm_store_dc.get(DC_WF_KEY, None)
            self.dc_WB_TYPE = bdm_store_dc.get(DC_WB_TYPE, None)
            self.dc_WORKBOOKS = self.bdmwd_WORKBOOKS()
            self.dc_LOADED_WORKBOOKS = self.bdmwd_LOADED_WORKBOOKS()
            self.dc_INITIALIZED = True
            return self
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
    #region    BudManDataContext (Interface) Property/Method Overrides.
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
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Return the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available. Pull
        from the BDMWD."""
        return self.bdmwd_LOADED_WORKBOOKS()
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Set the list of workbooks currently loaded in the DC.
        Loaded means a file is loaded into memory and is available."""
        logger.warning("Setting dc_LOADED_WORKBOOKS directly is not supported.")

    def dc_FI_KEY_validate(self, fi_key: str) -> bool:
        """Model-aware: Validate the provided FI_KEY.
        
        Model-aware method to validate the provided fi_key.
        """
        # First end-to-end DC binding through the BDMClientInterface.
        return self.model.bdm_FI_KEY_validate(fi_key)

    def dc_WF_KEY_validate(self, wf_key: str) -> bool:
        """Model-aware: Validate the provided WF_KEY.
        
        Model-aware method to validate the provided wf_key.
        """
        return self.model.bdm_WF_KEY_validate(wf_key)
    
    def dc_WB_REF_validate(self, wb_ref : str) -> bool: 
        """Model-aware: Return True if the wb_ref is valid.
        
        Model-aware method to validate the provided workbook reference (wb_ref).
        """
        try:
            # Bind through the DC (data_context) object
            return self.model.bdmwd_WB_REF_validate(wb_ref)
        except Exception as e:
            return self.BMVM_cmd_exception(e)


    # ------------------------------------------------------------------------ +

    #endregion BudManDataContext (Interface) Property/Method Overrides.
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMWorkingDataBaseInterface BDMWD DC-aware Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_WORKBOOKS(self) -> WORKBOOK_LIST:
        """Return the WORKBOOK_LIST from the BDMWD."""
        # Ask the model for the bdmwd_WORKBOOKS.
        return self.model.bdmwd_WORKBOOKS_get()
    def bdmwd_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Return the LOADED_WORKBOOK_COLLECTION from the BDMWD."""
        # Ask the model for the bdmwd_LOADED_WORKBOOKS.
        return self.model.bdmwd_LOADED_WORKBOOKS_get()

#endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingDataBaseInterface BDMWD (fi,wf,wb)-aware Interface.
    # ------------------------------------------------------------------------ +
    # def bdmwd_FI_KEY_validate(self, fi_key: str) -> bool:
    #     """Validate the provided FI_KEY."""
    #     # First end-to-end DC binding through the BDMClientInterface.
    #     return self.model.bdm_FI_KEY_validate(fi_key)
    def bdmwd_WF_KEY_validate(self, wf_key: str) -> bool:
        """Validate the provided WF_KEY."""
        return self.model.bdm_WF_KEY_validate(wf_key)
    def bdmwd_FI_WORKBOOKS_load(self, 
                                fi_key: str, 
                                wf_key : str, 
                                wb_type : str) -> LOADED_WORKBOOK_COLLECTION:
        """Load WORKBOOKS for the FI,WF, WBT."""
        lwbs = self.model.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
        self.dc_LOADED_WORKBOOKS = lwbs
        return 
    #endregion BDMWorkingDataBaseInterface BDMWD Interface.
    # ======================================================================== +



