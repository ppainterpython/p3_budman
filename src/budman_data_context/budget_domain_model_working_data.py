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
from typing import Any, Tuple, Dict, List
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages for necessary classes and functions
from budman_namespace.design_language_namespace import *
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_data_context import BudManDataContext
from p3_mvvm import Model_Base, Model_Binding
from budget_storage_model import bsm_WORKBOOK_url_get

#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
MODEL_OBJECT = Model_Base
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMWorkingData(BudManDataContext, Model_Binding):
    """DC and Model-Aware: BDMWD -Budget Domain Model Working Data. 
    
        BDMWorkingData sits between the ViewModel and the Model. Its role is
        to serve as the Data Context provider to the ViewModel, so it provides
        the BudManDataContext interface. Some of the concrete properties and
        methods from BudManDataContext are overridden to specialize the access
        to the Model.

        Assess to the Model is through binding to model property required by
        the BDMClientInterface. With that, BDMWorkingData can access the the 
        whole Model.

        A ViewModel considers the BDMWD properties and methods as an extension
        of the DataContext (DC) object binding. A client such as the ViewModel
        is intended to use the BudManDataContext Interface on the DC. The hope
        is that these properties and methods will satisfy most needs. However,
        if the need arises, the ViewModel can access the BDMWD Interface
        also provided. But the design encourages that to happen in the concrete
        overrides provided in BDMWD DC functions.
    """
    # ======================================================================== +
    #region    BDMWorkingData class intrinsics
    # ------------------------------------------------------------------------ +
    #region __init__() method init during BDMWorkingData constructor.
    def __init__(self,  bdm : Any = None, *args, dc_id : str = None) -> None:
        dc_id = args[0] if len(args) > 0 else None
        super().__init__(*args, dc_id=dc_id)
        self._budget_domain_model : MODEL_OBJECT = bdm
        self._dc_id = self.__class__.__name__ if not self._dc_id else None
    #endregion __init__() method init during BDMWorkingData constructor.
    # ------------------------------------------------------------------------ +
    #endregion    BDMWorkingData class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMClientInterface concrete implementation.
    # ------------------------------------------------------------------------ +
    #region    BDMClientInterface Interface Properties
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
    #endregion BDMClientInterface Interface Properties
    # ------------------------------------------------------------------------ +
    #endregion BDMClientInterface concrete implementation.
    # ======================================================================== +

    # ======================================================================== +
    #region    BudManDataContext(BudManDataContextBaseInterface) Overrides.
    #          These method overrides are Model-Aware behavior.
    # ------------------------------------------------------------------------ +
    #region BudManDataContext Property Overrides.
    #endregion BudManDataContext Interface Property Overrides.
    # ------------------------------------------------------------------------ +
    #region    BudManDataContext Method Overrides.
    def dc_initialize(self) -> "BudManDataContext":
        """Model-Aware: Initialize the BDMWorkingData instance after construction.
        
        Apply any necessary initializations to the BDMWorkingData instance. 
        First, update the DC with BDM_CONFIG from model.bdm_config_object.
        Second, update the DC with appropriate values from BDMClientInterface 
        concerning the BDM Working Data (BDMWD).
        Returns:
            BDMWorkingData: The initialized BDMWorkingData instance.
        """
        try:
            # Perform BudManDataContext.dc_initialize() to set up the DC.
            super().dc_initialize()
            # The model's BDM_STORE_OBJECT was used to initialize the model.
            bdm_store = getattr(self.model, BDM_STORE_OBJECT, None)
            if bdm_store is None:
                m = "The model does not have a bdm_store_object."
                logger.error(m)
                raise ValueError(m)
            # Place a reference to the bdm_store in the DC.
            self.dc_BDM_STORE = bdm_store
            # Update DC values save in BDM_STORE.BDM_DATA_CONTEXT.
            bdm_store_dc = bdm_store.get(BDM_DATA_CONTEXT, {})
            self.dc_FI_KEY = bdm_store_dc.get(DC_FI_KEY, None)
            self.dc_WF_KEY = bdm_store_dc.get(DC_WF_KEY, None)
            self.dc_WF_PURPOSE = bdm_store_dc.get(DC_WF_PURPOSE, None)
            self.dc_WB_TYPE = bdm_store_dc.get(DC_WB_TYPE, None)
            # Set the model-aware properties.
            try:
                if not self.dc_FI_KEY:
                    m = "dc_FI_KEY is None. Cannot initialize dc_WORKBOOK_DATA_COLLECTION."
                    logger.warning(m)
                else:
                    if self.model.bdm_initialized:
                        fi_object = self.model.bdm_FI_OBJECT(self.dc_FI_KEY)
                        wbc = self.model.bdm_FI_WORKBOOK_DATA_COLLECTION(self.dc_FI_KEY)
                        self.dc_WORKBOOK_DATA_COLLECTION = wbc
                        self.dc_FI_OBJECT = fi_object
            except Exception as e:
                m = f"{p3u.exc_err_msg(e)}"
                logger.error(m)
            self.dc_CHECK_REGISTERS = bdm_store_dc.get(DC_CHECK_REGISTERS, {})
            self.dc_INITIALIZED = True
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def dc_WORKBOOK_url_get(self, wb_url: str) -> Tuple[bool, str]:
        """Model-aware: Get the workbook at wb_url."""
        try:
            wb_obj : BDMWorkbook = self.dc_WORKBOOK_DATA_COLLECTION.get(wb_url, None)
            if wb_obj is None:
                m = f"dc_WORKBOOK_DATA_COLLECTION does not have a workbook with wb_url '{wb_url}'."
                logger.error(m)
                return False, m
        except Exception as e:
            m = f"Error loading workbook url '{wb_url}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m

    def dc_WORKBOOK_file_load(self, wb_index: str) -> Tuple[bool, str]:
        """Model-aware: Load the workbook indicated by wb_index."""
        try:
            if not isinstance(wb_index, str):
                raise TypeError(f"wb_index must be a string, got {type(wb_index)}")
            wdc = self.dc_WORKBOOK_DATA_COLLECTION
            wb : BDMWorkbook= self.dc_WORKBOOK_by_index(wb_index)
            if wb is None:
                m = f"dc_WORKBOOK_DATA_COLLECTION does not have a workbook with index '{wb_index}'."
                logger.error(m)
                return False, m
            content = bsm_WORKBOOK_url_get(wb.wb_url)
            if content is None:
                m = f"Failed to load Workbook data for '{wb.wb_name}'."
                logger.error(m)
                return False, m
            wb_index = self.dc_WORKBOOK_wb_index(wb.wb_id, wdc)
            r = f"{P2}wb_index: {wb_index:>2} wb_name: '{wb.wb_name:<40}'\n"
            self.dc_WB_REF = str(wb_index)  # Set the wb_ref in the DC.
            self._dc_WB_NAME = wb.wb_name  # Set the wb_name in the DC.
            # Add to the loaded workbooks collection.
            self.dc_LOADED_WORKBOOKS[wb.wb_id] = content
            wb.loaded = True
            logger.info(f"Loaded workbook '{wb.wb_id}' "
                        f"from url '{wb.wb_url}'.")
            return True, r
        except Exception as e:
            m = f"Error loading workbook with index '{wb_index}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m
    #endregion BudManDataContext Method Overrides.
    # ------------------------------------------------------------------------ +
    #endregion BudManDataContext (Interface) Property/Method Overrides.
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMWD Interface concrete implementation.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingDataBaseInterface BDMWD DC-aware Interface.
    def bdmwd_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Model-Aware: Return the LOADED_WORKBOOK_COLLECTION from the BDMWD."""
        # Ask the model for the bdmwd_LOADED_WORKBOOKS.
        return self.dc_LOADED_WORKBOOKS
    def bdmwd_LOADED_WORKBOOKS_count(self) -> int:
        """Return total count of BDMWD_LOADED_WORKBOOKS dictionary."""
        return len(self.dc_LOADED_WORKBOOKS)
    #endregion BDMWorkingDataBaseInterface BDMWD DC-aware Interface.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingData Interface BDMWD Model-aware(fi,wf,wb) Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """Model-Aware: Return the WORKBOOK_DATA_LIST from the BDMWD."""
        # Ask the model for the bdmwd_WORKBOOKS.
        return self.model.bdmwd_WORKBOOKS_get()
    def bdmwd_FI_WORKBOOKS_load(self, 
                                fi_key: str, 
                                wf_key : str, 
                                wb_type : str) -> LOADED_WORKBOOK_COLLECTION:
        """Model-Aware: Load WORKBOOKS for the FI,WF,WB."""
        lwbs = self.model.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
        self.dc_LOADED_WORKBOOKS = lwbs
        return 
    #endregion BDMWorkingData Interface BDMWD Interface.
    # ------------------------------------------------------------------------ +
    #endregion BDMWD Interface concrete implementation.
    # ======================================================================== +



