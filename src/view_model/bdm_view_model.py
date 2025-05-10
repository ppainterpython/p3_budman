# ---------------------------------------------------------------------------- +
#region bdm_view_model.py module
""" bdm_view_model.py command-style view_model for Budget Domain Model (budmod).
"""
#endregion bdm_view_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l

# local modules and packages
from p3_excel_budget_constants import  *
import data.p3_budget_model as p3bm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings.app_name)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudgetModelCommandViewModel():
    # ======================================================================== +
    #region BudgetModelCommandViewModel class
    """Command action view_model for the BudgetModel."""
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self,bm : p3bm.BudgetModel = None) -> None:
        super().__init__()
        self.intitialized : bool = False
        self.budget_model : p3bm.BudgetModel = bm
        self.FI_KEY : str = None
        self.WF_KEY : str = None
        self.WB_TYPE : str = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self) -> None:
        """Initialize the command view_model."""
        try:
            if (self.budget_model is None or 
                not isinstance(self.budget_model, p3bm.BudgetModel)):
                self.budget_model = p3bm.BudgetModel().bdm_initialize()
            if not self.budget_model.bm_initialized: 
                raise ValueError("BudgetModel is not initialized.")
            self.intitialized = True
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #endregion BudgetModelCommandViewModel class
    # ======================================================================== +

    # ======================================================================== +
    #region BDM view_model Command Methods                                     +
    """BDM view_model Command Methods.
    
    In View Model form, these methods provide the action for a command initiated
    by an upstream View, or other client caller. Of course, the upstream
    caller is mapping their specific domain of focus to the View Model
    interface. In general, there are a command methods and other "service"
    methods in a subsequent section.

    Throughout the BudgetModel (budmon) application, a design language is
    used as a convention for naming within the code-base. 

    Budget Model Domain Design Language:

    Budget - a means of tracking financial transactions over time.

    Budget Model (BM) - a functional model of budget processes. It is composed
    of worflows that process transactions from financial institutions, income 
    and expenses. Transactions are categorized by scanning input data and
    producing output data.

    Budget Domain (BD) and Budget Domain Model (BDM) - the conceptual model 
    of the budget top-level concept.

    MVVM - Model View ViewModel - a design pattern applied throughout for 
    separation of concerns in the Budget Domain.

    View (v) - code implementing access to a View Model, either by a 
    user-facing experience (UX) or an API interface.

    View Model (vm) - code implementing the domain interface to the Model. 
    View Models separate the concerns of the Model from those anticipated
    by the View.

    Model (m) - code implementing the domain model data. The Model is caboose
    in terms of the application data models, persistence, etc.
    
    These View Model commands have a verb, an noun (object reference), 
    and supporting parameter arguements. The verb is the action to be taken,
    the noun is the object to be acted upon, and the parameters are the
    supporting data for the action. The command methods are typically
    implemented as a single method. A naming convention reveals the verb and
    noun. The method name is a concatenation of the verb and noun, with an  
    underscore between them.

    Character case convention:
    - Class names are in CamelCase.
    - Method names are in prefix_snake_Camel_UPPER_lower_case.
    - Constants are in UPPER_SNAKE_CASE.
    - Seeing UPPER case in a mixed name implies the UPPER case part is also
    a contant defined in the module or class and used to represent a single
    value or a list of values both in the design langauge and the code.

    Method Naming convention: <scope>_<noun>_<verb>()
    where scope is the domain or sub-domain of the method (function), verb is the action to be taken, 
    and noun is the object to be acted upon. The noun is broken into two parts:

    <noun>: <object>[_<property>]
    <object>: <class_name> | <class_abbrev> | <pseudo_class_abbrev>
    <class_abbrev>: "bm" | "bmt" | "bdm" | "bdwd" | "bdvm"
    "bm" - BudgetModel class name
    "bmt" - BudgetModelTemplate class name
    "bdm" - Budget Domain Model
    "bsm" - Budget Storage Model

    bdm_vm - scope is the concern of the Budget Domain Model View Model
    BDWD - scope is the concern of the Budget Domain Working Data

    The term "Design Language" is abbreviated as "DL" or "dl" in the code. All
    constants are defined in a design_language.py module for the intended scope. 
    A package will have a design_language.py module for the package. If deemed
    helpful, a specific module will have a module_name_dl.py module for the
    design language for that module. Names mean something, and acronyms are used
    prolifically in code, as are fully descriptive names. 

    Maintaining consistency with the design language is critical for good
    design and keeping cohesion continuous. Here, python constants are used
    heavily to represent the design language. Think of constants as "tags" 
    from the design language word cloud. Searching the code-base for a constant
    will reveal the design language and the code that implements it. The best
    API design with high cohesion and low coupling reflect a consistent design
    language, and ruthless refactoring to keep it consistent and documented.

    Also, adopting the practice of documenting the design langague in the code
    is proving to be beneficial for GPT coding assistance. In this case, 
    GitHub Copilot is mind-blowingly adept at applying the design language in
    all parts of a large application, not just the neighboring code. Thank
    God for code-folding though.
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region bdm_vm_BDWD_LOAD_WORKBOOKS() command methods
    def bdm_vm_BDWD_LOADED_WORKBOOKS_get(self) -> List[Tuple[str, object]]: 
        """Get the loaded workbooks from BMWD_LOADED_WORKBOOKS working data."""
        return self.budget_model.bdwd_LOADED_WORKBOOKS_get()
    #endregion bdm_vm_BDWD_LOAD_WORKBOOKS() method
    # ------------------------------------------------------------------------ +
    #region bdm_vm_BDWD_FI() command methods
    def bdm_vm_BDWD_FI_initialize(self, fi_key : str = None) -> None: 
        """Initialize for a specific FI or 'all'."""
        try:
            if fi_key is None:
                logger.info("fi_key is None, no action taken.")
            wf_key = p3bm.BM_WF_CATEGORIZATION
            wb_type = p3bm.WF_WORKBOOKS_IN
            # Load the workbooks for the specified FI and workflow.
            ret = self.budget_model.bdwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
            # Set this fi_key as the latest or current FI key.
            self.FI_KEY = fi_key
            self.WF_KEY = wf_key
            self.WB_TYPE = wb_type

            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion bdm_vm_BDWD_FI() methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion BDM view_model Command Methods                                  +
    # ======================================================================== +

    # ======================================================================== +
    #region BDM view_model Service Methods                                     +
    """BDM view_model Service Methods.
    These methods are the service methods for the BDM view_model. Used by
    client packages up-stream in View-land, some are data requests and
    others perform work on the view_model state.    
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region 
    def bdm_vm_BDWD_LOADED_WORKBOOKS_get_names(self) -> List[str]: 
        """Return names of all loaded workbooks from BMWD_LOADED_WORKBOOKS."""
        try:
            # Retrieve the BDWD_LOADED_WORKBOOKS.
            bdwd_wb_list = self.budget_model.bdwd_LOADED_WORKBOOKS_get()
            wb_name_list = []
            for wb_name, _ in bdwd_wb_list:
                wb_name_list.append(wb_name)
            return wb_name_list
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
        return self.budget_model.bdwd_LOADED_WORKBOOKS_get()
    #endregion BDM view_model Service Methods                                  +
    # ======================================================================== +
