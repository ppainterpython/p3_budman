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
from budman_namespace import *
from budman_data_context import BudManDataContext
from budget_domain_model.budget_domain_model import BudgetDomainModel
from budget_domain_model.model_base_interface import BDMBaseInterface
from budget_domain_model.model_client_interface import BDMClientInterface
from budget_storage_model.csv_data_collection import (
    csv_DATA_COLLECTION_get_url, verify_url_file_path
)

#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
MODEL_OBJECT = BDMBaseInterface
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMWorkingData(BudManDataContext, BDMClientInterface):
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
    def __init__(self, bdm : Any = None) -> None:
        super().__init__()
        self._budget_domain_model : MODEL_OBJECT = bdm
    #endregion __init__() method init during BDMWorkingData constructor.
    # ------------------------------------------------------------------------ +
    #region initialize() method initializes the BDMWorkingData instance.
    def initialize(self) -> "BDMWorkingData":
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
            # Update the DC with BDM_STORE from model.bdm_store_object.
            bdm_store = getattr(self.model,BDM_STORE_OBJECT, None)
            if bdm_store is None:
                m = "The model does not have a bdm_store_object."
                logger.error(m)
                raise ValueError(m)
            # The model should have a valid bdm_store_object, freshly loaded.
            self.dc_BDM_STORE = bdm_store
            # Next, update DC content persisted in BDM_STORE.BDM_DATA_CONTEXT.
            bdm_store_dc = bdm_store.get(BDM_DATA_CONTEXT, {})
            self.dc_FI_KEY = bdm_store_dc.get(DC_FI_KEY, None)
            self.dc_WF_KEY = bdm_store_dc.get(DC_WF_KEY, None)
            self.dc_WF_PURPOSE = bdm_store_dc.get(DC_WF_PURPOSE, None)
            self.dc_WB_TYPE = bdm_store_dc.get(DC_WB_TYPE, None)
            self.dc_WORKBOOKS = self.bdmwd_WORKBOOKS()
            self.dc_LOADED_WORKBOOKS = self.bdmwd_LOADED_WORKBOOKS()
            self.dc_CHECK_REGISTERS = bdm_store_dc.get(DC_CHECK_REGISTERS, {})
            self.dc_INITIALIZED = True
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
        # 
    #endregion __init__() method initializes the BDMWorkingData instance.
    # ------------------------------------------------------------------------ +
    #endregion    BDMWorkingData class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    BudManDataContext (Interface) Property/Method Overrides.
    #          Overrides are used when the DC must be Model-Aware
    # ------------------------------------------------------------------------ +
    @property
    def dc_WORKBOOK_COLLECTION(self) -> DATA_COLLECTION:
        """Model-Aware: Return model.bdm_FI_WORKBOOK_COLLECTION(self.dc_FI_KEY)"""
        try:
            fi_key = self.dc_FI_KEY
            if fi_key is None:
                m = "The dc_FI_KEY is not set. Cannot get WORKBOOK_COLLECTION."
                logger.error(m)
                raise ValueError(m)
            # Ask the model for the bdmwd_WORKBOOKS.
            return self.model.bdm_FI_WORKBOOK_COLLECTION(fi_key)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise ValueError(f"Failed: model.bdm_FI_WORKBOOK_COLLECTION({fi_key})")
    @dc_WORKBOOK_COLLECTION.setter
    def dc_WORKBOOK_COLLECTION(self, value: WORKBOOK_DATA_LIST) -> None:
        """Set the list of workbooks in the DC."""
        logger.warning("Setting dc_WORKBOOKS directly is not supported.")

    # @property
    # def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
    #     """Return the list of workbooks currently loaded in the DC.
    #     Loaded means a file is loaded into memory and is available. Pull
    #     from the BDMWD."""
    #     return self.bdmwd_LOADED_WORKBOOKS()
    # @dc_LOADED_WORKBOOKS.setter
    # def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
    #     """Set the list of workbooks currently loaded in the DC.
    #     Loaded means a file is loaded into memory and is available."""
    #     logger.warning("Setting dc_LOADED_WORKBOOKS directly is not supported.")

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
    
    # def dc_WB_REF_validate(self, wb_ref : str) -> bool: 
    #     """BDMWD-aware: Return True if the wb_ref is valid.
        
    #     Uses the BDMWD interface to validate the workbook reference (wb_ref).
    #     """
    #     try:
    #         # Bind through the DC (data_context) object
    #         wb_all, wb_index, wb_name = self.bdmwd_WB_REF_resolve(wb_ref)
    #         if wb_all or wb_index >= 0 or wb_name is not None:
    #             # If wb_all is True, or we have a valid index and name.
    #             return True
    #         return False
    #     except Exception as e:
    #         return self.BMVM_cmd_exception(e)

    # ------------------------------------------------------------------------ +

    #endregion BudManDataContext (Interface) Property/Method Overrides.
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
    #region    BDMWD Interface concrete implementation.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingDataBaseInterface BDMWD DC-aware Interface.
    #region bdmwd_WB_REF_resolve() method
    # def bdmwd_WB_REF_resolve(self, wb_ref:str|int) -> Tuple[bool,int]:
    #     """DC-BDMWD-Only: Resolve a wb_ref to valid wb_index, wb_name, or ALL_KEY.

    #     Args:
    #         wb_ref (str|int): The wb_ref to validate and resolve. Expecting
    #         a str with a digit, a wb_name, or the ALL_KEY constant.

    #     Returns:
    #         Tuple[wb_all:bool, wb_index:int, wb_name:str]: 
    #             (True, -1, ALL_KEY) if wb_ref is ALL_KEY. 
    #             (False, wb_index, wb_name) for a valid index, adds wb_name match.
    #             (False, -1, wb_name) no valid index, found a wb_name.
    #             (False, -1, None) if wb_ref is invalid index or name value.
        
    #     Raises:
    #         TypeError: if wb_ref is not a str or int.
    #     """
    #     try:
    #         if isinstance(wb_ref, str):
    #             if wb_ref == ALL_KEY:
    #                 return True, -1, ALL_KEY
    #             if wb_ref.isdigit() or isinstance(wb_ref, int):
    #                 # If the wb_ref is a digit, treat it as an index.
    #                 wb_index = int(wb_ref)
    #                 if wb_index < 0 or wb_index >= len(self.dc_WORKBOOKS):
    #                     m = f"Invalid wb_index: {wb_index} for wb_ref: '{wb_ref}'"
    #                     logger.error(m)
    #                     return False, -1, None
    #                 wb_name = self.dc_WORKBOOK_name(wb_index)
    #                 if wb_name is None:
    #                     return False, -1, None
    #                 return False, wb_index, wb_name
    #             else :
    #                 # Could be a wb_name or a wb_url
    #                 wb_url_path = verify_url_file_path(wb_ref, test=False)
    #                 wb_name = wb_ref.strip() # TODO: flesh this out
    #                 if wb_url_path is not None :
    #                     wb_name = wb_url_path.name # TODO: flesh this out
    #                 return False, -1, wb_name
    #         return False, -1, None
    #     except Exception as e:
    #         m = p3u.exc_err_msg(e)
    #         logger.error(m)
    #         raise
    #endregion bdmwd_WB_REF_resolve() method
    # ------------------------------------------------------------------------ +
    # #region bdmwd_LOADED_WORKBOOKS() methods
    def bdmwd_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Model-Aware: Return the LOADED_WORKBOOK_COLLECTION from the BDMWD."""
        # Ask the model for the bdmwd_LOADED_WORKBOOKS.
        return self.dc_LOADED_WORKBOOKS
    def bdmwd_LOADED_WORKBOOKS_count(self) -> int:
        """Return total count of BDMWD_LOADED_WORKBOOKS dictionary."""
        return len(self.dc_LOADED_WORKBOOKS)

    # def bdmwd_LOADED_WORKBOOKS_get(self) -> LOADED_WORKBOOK_COLLECTION | None:
    #     """Get the BDMWD_LOADED_WORKBOOKS from the BDM_WORKING_DATA.

    #     Returns:
    #         LOADED_WORKBOOK_COLLECTION(Dict[wb_name: Workbook object])
    #     """
    #     try:
    #         self.bdmwd_INITIALIZED()
    #         if self.bdm_working_data is None:
    #             m = f"BDM_WORKING_DATA is not set. "
    #             logger.error(m)
    #             raise ValueError(m)
    #         return self.get_BDM_WORKING_DATA(BDMWD_LOADED_WORKBOOKS)
    #     except Exception as e:
    #         m = p3u.exc_err_msg(e)
    #         logger.error(m)
    #         raise

    # def bdmwd_LOADED_WORKBOOKS_add(self,wb_name : str, wb : Workbook) -> None:
    #     """Add an entry to BDMWD_LOADED_WORKBOOKS in the BDM_WORKING_DATA.

    #     The BDMWD_LOADED_WORKBOOKS list holds tuples of workbook name and
    #     the loaded Workbook object. When adding an entry, if the wb_name is 
    #     already in the list, then do not add it again.

    #     Returns:
    #         None: on success.
    #     Raises:
    #         ValueError: if the BDM_WORKING_DATA is not set.
    #         TypeError: if wb_name is not a str.
    #         TypeError: if wb is not a Workbook object.
    #         ValueError: if wb_name is None or an empty str.
    #         ValueError: if wb is None.
    #     """
    #     try:
    #         self.bdmwd_INITIALIZED()
    #         p3u.is_str_or_none("wb_name",wb_name, raise_error = True)
    #         m = "Updated" if wb_name in self.dc_LOADED_WORKBOOKS else "Added"
    #         self.dc_LOADED_WORKBOOKS[wb_name] = wb  # Use dict-like access for easy updates.
    #         logger.debug(f"{m} ('{wb_name}', '{str(wb)}') "
    #                      f"to BDMWD_LOADED_WORKBOOKS.")
    #         return None
    #     except Exception as e:
    #         m = p3u.exc_err_msg(e)
    #         logger.error(m)
    #         raise
    # def bdwb_LOADED_WORKBOOKS_member(self, wb_name:str) -> bool: 
    #     """Return True if wb_name is a member of DC.LOADED_WORKBOOKS list."""
    #     try:
    #         _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
    #         # Reference the DC.LOADED_WORKBOOKS property. Dict(wb_name: Workbook).
    #         lwbl = self.bdmwd_LOADED_WORKBOOKS_get()
    #         return True if wb_name in lwbl else False
    #     except Exception as e:
    #         logger.error(p3u.exc_err_msg(e))
    #         raise
    #endregion bdmwd_LOADED_WORKBOOKS() methods
    # ------------------------------------------------------------------------ +
    
    #endregion BDMWorkingDataBaseInterface BDMWD DC-aware Interface.
    # ------------------------------------------------------------------------ +
    #region    BDMWorkingData Interface BDMWD Model-aware(fi,wf,wb) Interface.
    # ------------------------------------------------------------------------ +
    def bdmwd_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """Model-Aware: Return the WORKBOOK_DATA_LIST from the BDMWD."""
        # Ask the model for the bdmwd_WORKBOOKS.
        return self.model.bdmwd_WORKBOOKS_get()
    def bdmwd_WORKBOOKS_add(self, wb_name:str, wb_abs_path_str:str) -> None:
        """Model-Aware: Add an entry to BDMWD_WORKBOOKS in the BDM_WORKING_DATA.

        Args:
            wb_name (str): The name of the workbook to add.
            wb_abs_path_str (str): The absolute path of the workbook to add.    

        Returns:
            None: on success.
        Raises:
            ValueError: if the BDM_WORKING_DATA is not set.
            TypeError: if wb_name is not a str.
            TypeError: if wb_abs_path_str is not a str.
            ValueError: if wb_name is None or an empty str.
            ValueError: if wb_abs_path_str is None or empty string.
        """
        # Use the model binding.
        return self.model.bdmwd_WORKBOOKS_add(wb_name, wb_abs_path_str)
    def bdmwd_WF_KEY_validate(self, wf_key: str) -> bool:
        """Model-Aware: Validate the provided WF_KEY."""
        return self.model.bdm_WF_KEY_validate(wf_key)
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



