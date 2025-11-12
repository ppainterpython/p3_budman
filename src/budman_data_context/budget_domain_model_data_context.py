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
from treelib import Tree, Node
import logging, p3_utils as p3u, p3logging as p3l
# local modules and packages for necessary classes and functions
from budman_namespace import *
from budman_data_context import BudManAppDataContext
from p3_mvvm import Model_Base, Model_Binding
import budget_storage_model as bsm
from budman_workflows.txn_category import BDMTXNCategoryManager
from budget_domain_model import BudgetDomainModel
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
MODEL_OBJECT = BudgetDomainModel
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMDataContext(BudManAppDataContext, Model_Binding):
    """DC and Model-Aware: BDMWD -Budget Domain Model Working Data. 
    
        BDMDataContext sits between the ViewModel and the Model. Its role is
        to serve as the Data Context provider to the ViewModel, so it provides
        the BudManAppDataContext interface. Some of the concrete properties and
        methods from BudManDataContext are overridden to specialize the 
        access to the Model, referred to as "Model-Aware".

        Access to the Model is through binding to model property required by
        the BDMClientInterface. With that, BDMDataContext can access the the
        whole Model.

        A client such as the ViewModel is intended to use the 
        BudManAppDataContext Interface on the DC. The hope
        is that these properties and methods will satisfy most needs. 

        At present, some DC properities are also saved in the Model so they may
        be set at application startup as part of the DC initialization:
        - dc_FI_KEY: The key of the current Financial Institution.
        - dc_WF_KEY: The key of the current Workflow.
        - dc_WF_PURPOSE: The purpose of the current Workflow folder.
    """
    # ======================================================================== +
    #region    BDMDataContext class intrinsics
    # ------------------------------------------------------------------------ +
    #region __init__() method init during BDMDataContext constructor.
    def __init__(self,  model : Model_Base = None, *args, dc_id : str = None) -> None:
        dc_id = args[0] if len(args) > 0 else None
        super().__init__(*args, dc_id=dc_id)
        self._model : MODEL_OBJECT = model
        self._dc_id = self.__class__.__name__ if not self._dc_id else None
        self._WF_CATEGORY_MANAGER : Optional[object] = None
    #endregion __init__() method init during BDMDataContext constructor.
    # ------------------------------------------------------------------------ +
    #endregion    BDMDataContext class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    Model_Binding concrete implementation.
    # ------------------------------------------------------------------------ +
    #region    Model_Binding Interface Properties
    @property
    def model(self) -> BudgetDomainModel:
        """Return the model object reference."""
        return self._model
    @model.setter
    def model(self, bdm: BudgetDomainModel) -> None:
        """Set the model object reference."""
        if not isinstance(bdm, BudgetDomainModel):
            raise TypeError(f"model must be a BudgetDomainModel instance")
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
    @property
    def dc_FI_OBJECT(self) -> Optional[FI_OBJECT_TYPE]:
        """DC-Only: Return the FI_OBJECT of the current Financial Institution. """
        return self._dc_FI_OBJECT if self.dc_VALID else None
    @dc_FI_OBJECT.setter
    def dc_FI_OBJECT(self, value: Optional[FI_OBJECT_TYPE]) -> None:
        """Model-Aware: Set the current FI_OBJECT value.
        
        Can be None. Valid value must be a valid FI_OBJECT from the model.
        """
        if not self.dc_VALID: return None
        # The value must be a valid FI_OBJECT.
        if not isinstance(value, dict):
            raise TypeError(f"dc_FI_OBJECT must be an FI_OBJECT, "
                            f"not {type(value).__name__}.")
        # The value's FI_KEY must match dc_FI_KEY.
        if value[FI_KEY] != self.dc_FI_KEY:
            raise ValueError(f"FI_OBJECT key mismatch: "
                             f"value[{FI_KEY}]('{value[FI_KEY]}') != "
                             f"dc_FI_KEY('{self.dc_FI_KEY}')")
        # The new FI_OBJECT value must be the same object from model.
        if value != self.model.bdm_FI_COLLECTION.get(self.dc_FI_KEY, None):
            raise ValueError(f"dc_FI_OBJECT must be the same object from "
                             f"model.bdm_FI_COLLECTION for key "
                             f"dc_FI_KEY'{self.dc_FI_KEY}').")
        self._dc_FI_OBJECT = value

    @property
    def dc_FI_KEY(self) -> Optional[str]:
        """DC-Only: Return the FI_KEY of the current Financial Institution.
        Depends on the value of dc_FI_OBJECT.
        Current means that the other data in the DC is for this FI.
        """
        self.not_dc_INITIALIZED()
        return self.dc_FI_OBJECT[FI_KEY] if self.dc_VALID else None
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: Optional[str]) -> None:
        """
        Model-Aware: Set the current FI_KEY value to None or validated value.
        Setting FI_KEY is accomplished by setting the dc_FI_OBJECT to the 
        FI_OBJECT associated with that FI_KEY in the model. Before assigning, 
        validate the FI_KEY from the model. The dc_FI_KEY property is 
        derived from the dc_FI_OBJECT property.
        """
        self.not_dc_INITIALIZED()
        if not self.model.bdm_FI_KEY_validate(value):
            raise ValueError(f"Invalid FI_KEY: {value}")
        self.dc_FI_OBJECT = self.dc_BDM_STORE[BDM_FI_COLLECTION].get(value, None)
        # One of the model-saved DC properties.
        self.model.bdm_data_context[DC_FI_KEY] = value

    @property
    def dc_WF_KEY(self) -> Optional[str]:
        """DC-Only: Return the WF_KEY for the current workflow of interest.
        Current means that the other data in the DC is for this workflow.
        """
        return self._dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: Optional[str]) -> None:
        """Model-Aware: Set the WF_KEY for the workflow."""
        self._dc_WF_KEY = value if self.dc_WF_KEY_validate(value) else None
        # One of the model-saved DC properties.
        self.model.bdm_data_context[DC_WF_KEY] = value

    @property
    def dc_WF_PURPOSE(self) -> Optional[str]:
        """DC-Only: Return the current WF_PURPOSE (workbook type) .
        Current means that the other data in the DC is for this workbook type. 
        This indicates the type of data in the workflow being processed,
        e.g., 'input', 'output', 'working', etc.
        """
        return self._dc_WF_PURPOSE
    @dc_WF_PURPOSE.setter
    def dc_WF_PURPOSE(self, value: Optional[str]) -> None:
        """Model-Aware: Set the WF_PURPOSE workbook type."""
        self._dc_WF_PURPOSE = value
        # One of the model-saved DC properties.
        self.model.bdm_data_context[DC_WF_PURPOSE] = value

    @property
    def WF_CATEGORY_MANAGER(self) -> Optional[object]:
        """Return the current category manager in the DC.
           Currently not part of BudManApppDataContext or _Base.

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
        """Model-Aware: Initialize the BDMDataContext instance after construction.
        
        Apply any necessary initializations to the BDMDataContext instance. 
        First, update the DC with BDM_CONFIG from model.bdm_config_object.
        Second, update the DC with appropriate values from BDMClientInterface 
        concerning the BDM Working Data (BDMWD).
        Returns:
            BDMDataContext: The initialized BDMDataContext instance.
        """
        try:
            # We are Model-Aware, so we can access the model.
            if self.model is None:
                m = "There is no model binding. Cannot dc_initialize BDMDataContext."
                logger.error(m)
                raise ValueError(m)
            # There is a model binding, obtain the BDM_STORE_OBJECT from the 
            # model, used to initialize it. 
            bdm_store = getattr(self.model, BDM_STORE_OBJECT, None)
            if bdm_store is None:
                m = "The model binding does not have a bdm_store_object."
                logger.error(m)
                raise ValueError(m)
            # Place a reference to the bdm_store in the DC, for super().dc_initialize().
            self.dc_BDM_STORE = bdm_store
            # Perform super().dc_initialize() to set up the DC-Only parts.
            super().dc_initialize()
            # Model-Aware DC property initialization. To proceed, must have 
            # a valid, initialized model.
            try:
                if not self.model.bdm_initialized:
                    m = "Model is not initialized. Cannot initialize BDMDataContext."
                    logger.error(m)
                    raise ValueError(m)
                # After super().dc_initialize(), the value dc_FI_KEY is set to
                # the value from the last model save to storage. If it is None,
                # then further initialization is not possible.
                if not self._dc_FI_KEY:
                    m = "dc_FI_KEY is None. Cannot continue to initialize BDMDataContext."
                    logger.error(m)
                    raise ValueError(m)
                # Set the dc_FILE_TREE binding.
                self._dc_FILE_TREE = self.model.bsm_file_tree.file_tree
                # The fi_key/fi_object binding to the model is the critical link
                # between the BDMDataContext and the Model.
                fi_object = self.model.bdm_FI_OBJECT(self._dc_FI_KEY)
                wdc = self.model.bdm_FI_WORKBOOK_DATA_COLLECTION(self._dc_FI_KEY)
                self._dc_FI_OBJECT = fi_object
                # This is not DC business, but setup the WF_CATEGORY_MANAGER here.
                if self.WF_CATEGORY_MANAGER is not None:
                    # Load the WB_TYPE_TXN_CATEGORIES for the FI.
                    wfm : BDMTXNCategoryManager = self.WF_CATEGORY_MANAGER
                    wfm.FI_TXN_CATEGORIES_WORKBOOK_load(self._dc_FI_KEY)
            except Exception as e:
                m = f"{p3u.exc_err_msg(e)}"
                logger.error(m)
            self.dc_INITIALIZED = True # Completes the full DC init process.
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    
    def not_dc_INITIALIZED(self) -> bool:
        """Model-Aware: Unforgiving check if the BDMDataContext is not initialized."""
        if not self.dc_INITIALIZED:
            m = "BDMDataContext is not initialized. Cannot proceed."
            logger.error(m)
            raise ValueError(m)
        return False

    def dc_WORKBOOK_validate(self, bdm_wb : WORKBOOK_OBJECT_TYPE) -> bool:
        """Model-Aware: Validate the type of WORKBOOK_OBJECT.
        Abstract: sub-class hook to test specialized WORKBOOK_OBJECT types.
        DC-ONLY: check builtin type: 'object'.
        Model-Aware: validate type: BDMWorkbook class.
        """
        self.not_dc_INITIALIZED()
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
        
    def dc_WORKBOOK_content_get(self, wb : BDMWorkbook, load:bool = True) -> BUDMAN_RESULT_TYPE:
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
        self.not_dc_INITIALIZED()
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

    def dc_WORKBOOK_content_put(self, wb_content:WORKBOOK_CONTENT_TYPE, bdm_wb : BDMWorkbook) -> BUDMAN_RESULT_TYPE:
        """Model-Aware: Put the workbook content into dc_LOADED_WORKBOOKS,
        replacing previous content if present. Then, save the content. 

        Args:
            wb_content (WORKBOOK_CONTENT): The content to put into the 
                dc_LOADED_WORKBOOKS property and save.
            wb (WORKBOOK_OBJECT): The workbook object to retrieve content for.
        Returns:
            BUDMAN_RESULT: Tuple[success:bool, result: Optional[msg:str]
        """
        self.not_dc_INITIALIZED()
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

    def dc_WORKBOOK_load(self, bdm_wb : BDMWorkbook) -> BUDMAN_RESULT_TYPE:
        """Model-aware: Load the workbook bdm_wb with BSM service."""
        self.not_dc_INITIALIZED()
        try:
            # Model-Aware World
            success : bool = False
            result : BDMWorkbook | str = None
            if not self.dc_WORKBOOK_validate(bdm_wb):
                m = f"Invalid workbook object: {bdm_wb!r}"
                logger.error(m)
                return False, m
            # Model-aware: Load the bdm_wb WORKBOOK_CONTENT object with the BSM.
            bsm.bsm_BDMWorkbook_load(bdm_wb)
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

    def dc_WORKBOOK_save(self, bdm_wb : BDMWorkbook) -> BUDMAN_RESULT_TYPE:
        """Model-Aware: Save the workbook content to storage.

        Args:
            wb_content (WORKBOOK_CONTENT): The content to save.
            bdm_wb (BDMWorkbook): The workbook object to save content for.
        Returns:
            BUDMAN_RESULT: Tuple[success:bool, result: Optional[msg:str]]
        """
        self.not_dc_INITIALIZED()
        try:
            # Model-Aware World
            success : bool = False
            result : BDMWorkbook | str = None
            if not self.dc_WORKBOOK_validate(bdm_wb):
                m = f"Invalid workbook object: {bdm_wb!r}"
                logger.error(m)
                return False, m
            # Save the workbook content using the BSM.
            bsm.bsm_BDMWorkbook_save(bdm_wb)
            # Update the dc_LOADED_WORKBOOKS with the saved content.
            self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id] = bdm_wb.wb_content
            bdm_wb.wb_loaded = True
            return True, f"Workbook '{bdm_wb.wb_id}' saved successfully."
        except Exception as e:
            m = f"Error saving workbook '{bdm_wb.wb_id}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m

    def dc_FILE_TREE_node_info(self, node: Node) -> Dict[str,str]:
        """Model-Aware: Return info about the specified file tree node."""
        if not self.dc_VALID:
            logger.error("Data context is not valid.")
            return {}
        if self.dc_FILE_TREE is None:
            logger.error("Data context FILE_TREE is not set.")
            return {}
        if node is None:
            logger.error("Node is None.")
            return {}
        bsm_file: bsm.BSMFile = node.data
        if bsm_file.type == bsm.BSMFile.BSM_FILE:
            info = {
                "identifier": str(node.identifier),
                "tag": str(node.tag),
                "data": str(node.data),
                "is_leaf": str(node.is_leaf),
                "depth": str(node.depth),
                "num_children": str(len(node.children)),
                "filename": str(bsm_file.filename),
                "extension": str(bsm_file.extension),
                "prefix": str(bsm_file.prefix),
                "wb_type": str(bsm_file.wb_type),
                "in_bdm": str(bsm_file.in_bdm),
            }
            return info
        elif bsm_file.type == bsm.BSMFile.BSM_FOLDER:
            info = {
                "identifier": str(node.identifier),
                "tag": str(node.tag),
                "data": str(node.data),
                "is_leaf": str(node.is_leaf),
                "depth": str(node.depth),
                "num_children": str(len(node.children)),
                "folder_name": str(bsm_file.folder_name),
                "in_bdm": str(bsm_file.in_bdm),
            }
            return info
        else:
            raise ValueError(f"Unknown BSMFile type: {bsm_file.type}")

    #endregion BudManDataContext Method Overrides.
    # ------------------------------------------------------------------------ +
    #endregion BudManDataContext (Interface) Property/Method Overrides.
    # ======================================================================== +
