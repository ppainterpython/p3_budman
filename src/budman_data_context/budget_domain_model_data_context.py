# ---------------------------------------------------------------------------- +
#region budget_domain_model_data_context.py
"""BDMDataContext: The BDMDataContext object is the working state of the BudMan app.

A BDMDataContext object is intended to sit apart from the Model and ViewModel layers, serving
as a bridge. The BudMan design language is inherent to the BDMDataContext and DC
interface. A BDMDataContext object can be bound as a Data Context (DC) in the application
as it implements the BudManDataContext interface and translates it to the
Budget Domain Model.
"""
#endregion budget_domain_model_data_context.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
from pathlib import Path
from typing import Any, Tuple, Dict, List, Optional
# third-party modules and packages
from openpyxl import Workbook
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages for necessary classes and functions
from budman_namespace.design_language_namespace import *
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_data_context import BudManAppDataContext
from p3_mvvm import Model_Base, Model_Binding
from budget_storage_model import (bsm_BDM_WORKBOOK_load, bsm_BDM_WORKBOOK_save)
from budman_workflows.txn_category import BDMTXNCategoryManager
from budget_domain_model import BudgetDomainModel
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
MODEL_OBJECT = Model_Base
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMDataContext(BudManAppDataContext, Model_Binding):
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
    def __init__(self,  model : Model_Base = None, *args, dc_id : str = None) -> None:
        dc_id = args[0] if len(args) > 0 else None
        super().__init__(*args, dc_id=dc_id)
        self._model : MODEL_OBJECT = model
        self._dc_id = self.__class__.__name__ if not self._dc_id else None
        self._WF_CATEGORY_MANAGER : Optional[object] = None
    #endregion __init__() method init during BDMWorkingData constructor.
    # ------------------------------------------------------------------------ +
    #endregion    BDMWorkingData class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    Model_Binding concrete implementation.
    # ------------------------------------------------------------------------ +
    #region    Model_Binding Interface Properties
    @property
    def model(self) -> MODEL_OBJECT:
        """Return the model object reference."""
        return self._model
    @model.setter
    def model(self, bdm: MODEL_OBJECT) -> None:
        """Set the model object reference."""
        if not isinstance(bdm, MODEL_OBJECT):
            raise TypeError(f"model must be a {MODEL_OBJECT} instance")
        self._model = bdm
    #endregion Model_Binding Interface Properties
    # ------------------------------------------------------------------------ +
    #endregion BDMClientInterface concrete implementation.
    # ======================================================================== +

    # ======================================================================== +
    #region    BudManDataContext(BudManDataContext_Base) Model-Aware Overrides.
    #          These method overrides implement Model-Aware behavior.
    # ------------------------------------------------------------------------ +
    #region    BudManDataContext(BudManDataContext_Base) Model-Aware Property Overrides.
    # @property
    # def dc_FI_OBJECT(self) -> str:
    #     """DC-Only: Return the FI_OBJECT of the current Financial Institution. 
    #     """
    #     return self._dc_FI_OBJECT if self.dc_VALID else None
    # @dc_FI_OBJECT.setter
    # def dc_FI_OBJECT(self, value: str) -> None:
    #     """Model-Aware: Set the current FI_OBJ for the DC.
    #     Validate the FI_OBJECT before assigning.
    #     DC-Only: Set the FI_OBJECT of the current Financial Institution."""
    #     if not self.dc_VALID: return None
    #     self._dc_FI_OBJECT = value

    # @property
    # def dc_FI_KEY(self) -> str:
    #     """DC-Only: Return the FI_KEY of the current Financial Institution.
    #     Depends on the value of dc_BDM_STORE.
    #     Current means that the other data in the DC is for this FI.
    #     """
    #     if self.dc_BDM_STORE is None and not self._initialization_in_progress:
    #         m = "dc_BDM_STORE is None. Cannot get fi_key."
    #         logger.warning(m)
    #         return None
    #     return self._dc_FI_KEY
    # @dc_FI_KEY.setter
    # def dc_FI_KEY(self, value: str) -> None:
    #     """DC-Only: Set the FI_KEY of the current Financial Institution.
    #     Depends on the value of dc_BDM_STORE.
    #     """
    #     if self.dc_BDM_STORE is None and not self._initialization_in_progress:
    #         m = "dc_BDM_STORE is None. Cannot set fi_key."
    #         logger.warning(m)
    #         return None
    #     self._dc_FI_KEY = value


    @property
    def WF_CATEGORY_MANAGER(self) -> Optional[object]:
        """Return the current category manager in the DC.

        This is a property to register and share a reference to
        the WORKFLOW CATEGORY MANAGER service, which is needed
        by some workflow command processor implementations. It does not 
        impact the DC state but will reference values in the DC.
        """
        return self._WF_CATEGORY_MANAGER
    @WF_CATEGORY_MANAGER.setter
    def WF_CATEGORY_MANAGER(self, value: Optional[object]) -> None:
        """Set the current category manager in the DC."""
        self._WF_CATEGORY_MANAGER = value

    #endregion BudManDataContext(BudManDataContext_Base) Property Overrides.
    # ------------------------------------------------------------------------ +
    #region    BudManDataContext(BudManDataContext_Base) Method Model-Aware Overrides.
    def dc_initialize(self) -> "BudManAppDataContext":
        """Model-Aware: Initialize the BDMWorkingData instance after construction.
        
        Apply any necessary initializations to the BDMWorkingData instance. 
        First, update the DC with BDM_CONFIG from model.bdm_config_object.
        Second, update the DC with appropriate values from BDMClientInterface 
        concerning the BDM Working Data (BDMWD).
        Returns:
            BDMWorkingData: The initialized BDMWorkingData instance.
        """
        try:
            # We are Model-Aware, so we can access the model.
            if self.model is None:
                m = "There is no model binding. Cannot dc_initialize BDMWorkingData."
                logger.error(m)
                raise ValueError(m)
            # With the model available, obtain the BDM_STORE_OBJECT from the 
            # model, used to initialize it. The DC initialize chain uses it.
            # The model's BDM_STORE_OBJECT was used to initialize the model.
            bdm_store = getattr(self.model, BDM_STORE_OBJECT, None)
            if bdm_store is None:
                m = "The model binding does not have a bdm_store_object."
                logger.error(m)
                raise ValueError(m)
            # Place a reference to the bdm_store in the DC, for super().dc_initialize().
            self.dc_BDM_STORE = bdm_store
            # Perform BudManDataContext.dc_initialize() to set up the DC-Only parts.
            super().dc_initialize()
            # Model-Aware DC property initialization.
            try:
                if not self.dc_FI_KEY:
                    m = "dc_FI_KEY is None. Cannot initialize dc_WORKBOOK_DATA_COLLECTION."
                    logger.warning(m)
                else:
                    if self.model.bdm_initialized:
                        # The fi_object and FI_WORKBOOK_DATA_COLLECTION are the
                        # key bindings between the BDMDataContext and the Model.
                        fi_object = self.model.bdm_FI_OBJECT(self.dc_FI_KEY)
                        wdc = self.model.bdm_FI_WORKBOOK_DATA_COLLECTION(self.dc_FI_KEY)
                        # self.dc_WORKBOOK_DATA_COLLECTION = wdc
                        self.dc_FI_OBJECT = fi_object
                        if self.WF_CATEGORY_MANAGER is not None:
                            # Load the WB_TYPE_TXN_CATEGORIES for the FI.
                            wfm : BDMTXNCategoryManager = self.WF_CATEGORY_MANAGER
                            wfm.FI_TXN_CATEGORIES_WORKBOOK_load(self.dc_FI_KEY)
            except Exception as e:
                m = f"{p3u.exc_err_msg(e)}"
                logger.error(m)
            self.dc_INITIALIZED = True
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def dc_WF_PURPOSE_FOLDER_MAP(self, wf_key: str, wf_purpose:str) -> bool:
        """Model-Aware: Return the wf_folder_id from the provided WF_KEY & WF_PURPOSE.
        """
        return self.model.bdm_WF_PURPOSE_FOLDER_MAP(wf_key, wf_purpose)

    def dc_WORKBOOK_validate(self, bdm_wb : WORKBOOK_OBJECT) -> bool:
        """Model-Aware: Validate the type of WORKBOOK_OBJECT.
        Abstract: sub-class hook to test specialized WORKBOOK_OBJECT types.
        DC-ONLY: check builtin type: 'object'.
        Model-Aware: validate type: BDMWorkbook class.
        """
        try:
            if bdm_wb is None:
                return False
            if not isinstance(bdm_wb, BDMWorkbook):
                m = (f"bdm_wb must be type: 'BDMWorkbook', "
                     f"not type: {type(bdm_wb).__name__}.")
                logger.error(m)
                return False
            if not self.dc_WB_ID_validate(bdm_wb.wb_id):
                m = f"Invalid workbook ID: {bdm_wb.wb_id}"
                logger.error(m)
                return False
            return True
        except Exception as e:
            m = f"Error validating workbook: {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False
        
    def dc_WORKBOOK_content_get(self, wb : BDMWorkbook, load:bool = True) -> BUDMAN_RESULT:
        """Model-Aware: Get the workbook content from dc_LOADED_WORKBOOKS 
        property if present. To be simple and consistent, use the 
        WORKBOOK_OBJECT to access the workbook meta-data.

        Args:
            wb (WORKBOOK_OBJECT): The workbook object to retrieve content for.
            load (bool): If True, attempt to load the workbook content fresh
                from storage. Else, return what is already in the
                dc_LOADED_WORKBOOKS property or error.
        Returns:
            Optional[WORKBOOK_CONTENT]: The content of the workbook if available,
            otherwise None.
        """
        try:
            # Model-Aware World
            success : bool = False
            result : BDMWorkbook | str = None
            if not self.dc_WORKBOOK_validate(wb):
                m = f"Invalid workbook object: {wb!r}"
                logger.error(m)
                return False, m
            # Check if the workbook is loaded in dc_LOADED_WORKBOOKS.
            wb_content = None
            wb.wb_loaded = wb.wb_id in self.dc_LOADED_WORKBOOKS
            if not load:
                # Retrieve the workbook content from dc_LOADED_WORKBOOKS.
                wb_content = self.dc_LOADED_WORKBOOKS[wb.wb_id]
                if wb_content is None:
                    m = f"Workbook content for '{wb.wb_id}' is not loaded."
                    logger.error(m)
                    wb.wb_loaded = False
                    return False, m
                wb.wb_loaded = True
                return True, wb_content
            # load is True, so we need to load the workbook content.
            return self.dc_WORKBOOK_load(wb)
        except Exception as e:
            m = f"Error loading workbook '{wb.wb_id}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m

    def dc_WORKBOOK_content_put(self,wb_content:WORKBOOK_CONTENT, bdm_wb : BDMWorkbook) -> BUDMAN_RESULT:
        """Model-Aware: Put the workbook content into dc_LOADED_WORKBOOKS,
        replacing previous content if present. Then, save the content. 

        Args:
            wb_content (WORKBOOK_CONTENT): The content to put into the 
                dc_LOADED_WORKBOOKS property and save.
            wb (WORKBOOK_OBJECT): The workbook object to retrieve content for.
        Returns:
            BUDMAN_RESULT: Tuple[success:bool, result: Optional[msg:str]
        """
        try:
            # Model-Aware World
            success : bool = False
            result : BDMWorkbook | str = None
            if not self.dc_WORKBOOK_validate(bdm_wb):
                m = f"Invalid workbook object: {bdm_wb!r}"
                logger.error(m)
                return False, m
            # Check if the workbook is loaded in dc_LOADED_WORKBOOKS.
            if wb_content is None:
                m = f"Workbook content for '{bdm_wb.wb_id}' is None."
                logger.error(m)
                return False, m
            success, result = self.dc_WORKBOOK_save(wb_content, bdm_wb)
            bdm_wb.wb_loaded = bdm_wb.wb_id in self.dc_LOADED_WORKBOOKS
            if bdm_wb.wb_loaded :
                # Retrieve the workbook content from dc_LOADED_WORKBOOKS.
                wb_content = self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id]
                if wb_content is None:
                    m = f"Workbook content for '{bdm_wb.wb_id}' is not loaded."
                    logger.error(m)
                    return False, m
                return True, result
            else:
                m = f"Workbook '{bdm_wb.wb_id}' is not loaded after saving."
                logger.error(m)
                return False, m
        except Exception as e:
            m = f"Error loading workbook '{bdm_wb.wb_id}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m

    def dc_WORKBOOK_load(self, bdm_wb : BDMWorkbook) -> BUDMAN_RESULT:
        """Model-aware: Load the workbook bdm_wb with BSM service."""
        try:
            # Model-Aware World
            success : bool = False
            result : BDMWorkbook | str = None
            if not self.dc_WORKBOOK_validate(bdm_wb):
                m = f"Invalid workbook object: {bdm_wb!r}"
                logger.error(m)
                return False, m
            # Model-aware: Load the bdm_wb WORKBOOK_CONTENT object with the BSM.
            bsm_BDM_WORKBOOK_load(bdm_wb)
            # Add/update to the loaded workbooks collection.
            self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id] = bdm_wb.wb_content
            self.dc_WORKBOOK = bdm_wb  # Update workbook-related DC info.
            logger.info(f"Loaded workbook '{bdm_wb.wb_id}' "
                        f"from url '{bdm_wb.wb_url}'.")
            return True, bdm_wb.wb_content
        except Exception as e:
            m = f"Error loading wb_id '{bdm_wb.wb_id}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m
        
    def dc_WORKBOOK_save(self, bdm_wb : BDMWorkbook) -> BUDMAN_RESULT:
        """Model-Aware: Save the workbook content to storage.

        Args:
            wb_content (WORKBOOK_CONTENT): The content to save.
            bdm_wb (BDMWorkbook): The workbook object to save content for.
        Returns:
            BUDMAN_RESULT: Tuple[success:bool, result: Optional[msg:str]]
        """
        try:
            # Model-Aware World
            success : bool = False
            result : BDMWorkbook | str = None
            if not self.dc_WORKBOOK_validate(bdm_wb):
                m = f"Invalid workbook object: {bdm_wb!r}"
                logger.error(m)
                return False, m
            # Save the workbook content using the BSM.
            bsm_BDM_WORKBOOK_save(bdm_wb)
            # Update the dc_LOADED_WORKBOOKS with the saved content.
            self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id] = bdm_wb.wb_content
            bdm_wb.wb_loaded = True
            return True, f"Workbook '{bdm_wb.wb_id}' saved successfully."
        except Exception as e:
            m = f"Error saving workbook '{bdm_wb.wb_id}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m
    #endregion BudManDataContext Method Overrides.
    # ------------------------------------------------------------------------ +
    #endregion BudManDataContext (Interface) Property/Method Overrides.
    # ======================================================================== +
