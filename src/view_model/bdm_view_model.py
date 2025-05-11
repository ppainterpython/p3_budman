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
    
    In View Model form, these methods execute the actions for a command 
    initiated by an upstream View, or other client caller. Of course, 
    the upstream caller is mapping their specific domain of focus to the View Model
    interface. In general, there are a command methods and other "Data Context"
    methods in a subsequent section.

    Throughout the BudgetModel (budmon) application, a design language is
    used as a convention for naming within the code-base. 

    Budget Model Domain Design Language 
    -----------------------------------

    Budget Domain Concepts
    ---------------------
        
    - Budget - a means of tracking financial transactions over time.

    - Budget Model (BM) - a functional model of budget processes. It is composed
    of worflows that process transactions from financial institutions, income 
    and expenses. Transactions are categorized by scanning input data and
    producing output data.

    - Budget Domain (BD) and Budget Domain Model (BDM) - the conceptual model 
    of the budget top-level concept.

    Budget Domain Objects
    ---------------------

    Objects are considered things, pieces of data that commands do something to.
    An app will executve commands to take action on an object. Object names are 
    nouns of the design language.

    - Workbook - typically an excel workbook, stored in a file on the user's
    file system. It contains data in worksheets, and is often received from a 
    bank or brokerage firm

    - Financial Institution (FI) - a bank or brokerage firm that provides
    financial services to the user. The FI is the source of transactions for the
    budget model.

    - Loaded Workbook - a workbook that has been loaded into the budget model
    for processing. It is a workbook that has been opened by the app and is in 
    the current session context, available to have commands executed on it.

    - Workflow (WF) - a sequence of steps to process data. A Budget Model workflow 
    has a purpose, and applies to workbooks. As workflows are executed,
    the workbooks are processed and the data is transformed. Workflows have 
    folders in the filesystem where workbooks are accessed. In general, a 
    workflow has both an input and output folder. The input folder is where the
    workbooks are loaded from, and the output folder is where the processed, or 
    changed workbooks are saved.

    - Commands - a command is an action to be taken on an object. Commands are
    typically implemented as methods in the code. A command is named, has a
    source and a target, and in MVVM packages, a binding to configure how
    Views bind to the commands of a ViewModel.

    For the sake of the BudgetModel design language, the command source is 
    some class serving as a View. The command target is a workbook (WB), 
    a loaded workbook, a financial institution (FI), or a workflow (WF). The
    command method name will include a noun (probably abbreviated) from the
    design language for objects and one of the a verb for the action: init, load, 
    save, show, delet, add, etc., suffixed by '_cmd'. Additional method 
    naming conventions are described below.

    MVVM Design Pattern
    -------------------

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

    Command Methods: To be a clean ViewModel, command methods are provided to
    enable the View to call the command methods in a consistent and 
    loosely-coupled manner. The command methods are typically implemented as a
    single method. A naming convention reveals the verb and noun. In the MVVM
    pattern, a DataContext is used to bind the ViewModel to the View. For 
    the view, Commands are methods on the DataContext, without actually knowing
    the type of the DataContext. Since python is dynamically typed, we just
    use it to dispatch the command to the appropriate method.
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region bdm_vm_BDWD_LOAD_WORKBOOKS() command methods
    #endregion bdm_vm_BDWD_LOAD_WORKBOOKS() method
    # ------------------------------------------------------------------------ +
    #region FI_init_command() command method
    def FI_init_cmd(self, fi_key : str = None) -> None: 
        """Execute FI_init command for one fi_key or 'all'."""
        try:
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if not p3u.is_non_empty_str("fi_key",fi_key,pfx):
                m = f"fi_key is None, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            # Check for 'all'
            if fi_key == "all":
                raise NotImplementedError(f"{pfx}fi_key 'all' not implemented.")
            # Check if valid fi_key            
            try:
                _ = self.budget_model.bdm_FI_KEY_validate(fi_key)
            except ValueError as e:
                m = f"ValueError({str(e)})"
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
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
    #endregion FI_init_command() command method
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
