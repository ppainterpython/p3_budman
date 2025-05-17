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
from typing import List, Type, Generator, Dict, Tuple, Any, Callable

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
import budman_model as p3bm
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings[p3bm.APP_NAME])
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudgetManagerCommandViewModel():
    # ======================================================================== +
    #region BudgetManagerCommandViewModel class
    """A Budget Model View Model to support Commands and Data Context."""
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Class Variables
    #endregion Class Variables
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        super().__init__()
        self.intitialized : bool = False
        self.BUDMAN_STORE_loaded : bool = False
        self.budget_model : p3bm.BudgetModel = None
        self.FI_KEY : str = None
        self.WF_KEY : str = None
        self.WB_TYPE : str = None
        self.WB_NAME : str = None
        self.cmd_map : Dict[str, Callable] = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self, load_user_store : bool = False) -> "BudgetManagerCommandViewModel":
        """Initialize the command view_model."""
        try:
            st = p3u.start_timer()
            logger.info(f"Start: Configure Budget Manager: ...")
            # Check if the budget model is initialized.
            if (self.budget_model is None or 
                not isinstance(self.budget_model, p3bm.BudgetModel)):
                # There is no valid budget_model. Load a BM_STORE file?
                if load_user_store:
                    # Use BM_STORE file as a config_object 
                    config_object = self.BUDMAN_STORE_load_cmd()
                else:
                    # Use the builtin default template as a config_object.
                    config_object = p3bm.BudgetModelTemplate.get_budget_model_template()
                # Now to initialize the budget model.
                self.budget_model = p3bm.BudgetModel(config_object).bdm_initialize()
            if not self.budget_model.bm_initialized: 
                raise ValueError("BudgetModel is not initialized.")
            self.initialize_cmd_map()
            self.intitialized = True
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #region initialize_cmd_map() method
    def initialize_cmd_map(self) -> None:
        """Initialize the cmd_map dictionary."""
        try:
            # Use the following cmd_map to dispatch the command for execution.
            self.cmd_map = {
                "init_cmd_fin_inst": self.FI_init_cmd,
                "save_cmd_workbooks": self.FI_save_cmd,
                "load_cmd_BUDMAN_STORE": self.BUDMAN_STORE_load_cmd,
                "save_cmd_BUDMAN_STORE": self.BUDMAN_STORE_save,
            }
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #endregion BudgetManagerCommandViewModel class
    # ======================================================================== +

    # ======================================================================== +
    #region FICommandInterface Budget Manager View Model Command Interface
    """Budget Model View Model Command Interface Methods.
    
    In View Model form, these methods provide an Interface for executing
    Commands as a design pattern. Commands take actions for a command 
    initiated by an upstream View, or other client caller. Of course, 
    the upstream caller is mapping their specific domain of focus to the View Model
    interface. In general, there are a Command methods and other "Data Context"
    methods in a subsequent section.

    Throughout the BudgetModel (budmon) application, a design language is
    used as a convention for naming within the code-base. 

    Convention: <Domain_Model_Object_Name>_<action_verb>()
                <Domain_Model_Object_Name>_<action_verb>_<dc_item>()
                dc_item: a reference to data in the Data Context

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
    #region BMVM_execute_cmd() command method
    def BMVM_execute_cmd(self, cmd : Dict = None) -> Tuple[bool, Any]:
        """Execute a command for the Budget Model View Model.

        This method executes a command for the Budget Model View Model. 
        Commands and common argument values are validated. This method is the
        primary interface to the ViewModel, hence, it will return a result
        and not raise exceptions. When errors are caught, the result will 
        indicate an error occurred and have an error message.

        Arguments:
            cmd (Dict): The command to execute along with any arguments.
        
        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution.
        """
        try:
            st = p3u.start_timer()
            logger.info(f"Start Command: {cmd}")
            if not self.intitialized:
                m = f"{self.__class__.__name__} is not initialized."
                logger.error(m)
                return False, m
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                return False, m
            success, result = self.BMVM_validate_cmd(cmd)
            if not success: return success, result
            full_cmd_key = result
            func = self.cmd_map.get(full_cmd_key)
            function_name = func.__name__
            result = f"Executing command: {function_name}({str(cmd)})"
            logger.info(result)
            result = self.cmd_map.get(full_cmd_key)(cmd)
            return True, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion BMVM_execute_cmd() command method
    #region BMVM_validate_cmd() command method
    def BMVM_validate_cmd(self, cmd : Dict = None) -> Tuple[bool, str]:
        """Validate the cmd for the Budget Manager View Model.

        Extract a valid, known cmd_key to succeed.
        Consider values to common arguments which can be validated against
        the data context.

        returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the
                cmd and arguments are valid.
                True returns the full cmd_key value as a str.
                False, the message will contain an error message.
        """
        try:
            if not self.intitialized:
                m = f"{self.__class__.__name__} is not initialized."
                logger.error(m)
                return False, m
            pfx = f"{self.__class__.__name__}.{self.BMVM_execute_cmd.__name__}: "
            if cmd is None or not isinstance(cmd, dict) or len(cmd) == 0:
                m = f"cmd argument is None, no action taken."
                logger.error(m)
                return False, m
            # Check if the cmd contains a valid cmd_key.
            cmd_key = next((key for key in cmd.keys() if "_cmd" in key), None)
            if p3u.str_empty(cmd_key):
                m = f"No command key found in: {str(cmd)}"
                logger.error(m)
                return False, m
            # Acquire sub-command key if present.
            sub_cmd = cmd[cmd_key]
            full_cmd_key = cmd_key + '_' + sub_cmd if p3u.str_notempty(sub_cmd) else cmd_key
            # Check the cmd_key against the command map.
            if full_cmd_key not in self.cmd_map:
                m = f"Command key '{full_cmd_key}' not found in command map."
                logger.error(m)
                return False, m

            # Have a valid cmd_key, now check the arguments.
            for key, value in cmd.items():
                if key == cmd_key: continue
                elif key == "fi_key":
                    if value not in p3bm.VALID_FI_KEYS:
                        m = f"Invalid fi_key value: '{value}'."
                        logger.error(m)
                        return False, m
                    continue
                elif key == "wb_name": continue
                elif key == "wf_key":
                    if value not in p3bm.BM_VALID_WORKFLOWS:
                        m = f"Invalid fi_key value: '{value}'."
                        logger.error(m)
                        return False, m
                    continue
                else:
                    m = f"Unchedked argument key: '{key}': '{value}'."
                    logger.debug(m)
            return True, full_cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BMVM_validate_cmd() command method
    # ------------------------------------------------------------------------ +
    #region FI_init_command() command method
    def FI_init_cmd(self, cmd : Dict = None) -> Tuple[bool, str]: 
        """Execute FI_init command for one fi_key or 'all'.
        
        This command initializes the Data Context aspects of the View Model to
        contain workbooks and other information for the specified financial
        institution (FI) which may be 'all' or a specific FI key.

        Arguments:
            fi_key (str): The key for the financial institution. If None, 
                no action is taken. If 'all', all workbooks are loaded.
            wf_key (str): The key for the workflow.
            wb_type (str): The type of workbook, either input or output.
            wb_name (str): The name of the workbook. If None, all workbooks
                modified since open are saved. If 'all', all workbooks are saved.
        Raises:
            RuntimeError: If the fi_key is None or invalid.
        """
        try:
            st = p3u.start_timer()
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            fi_key = cmd.get("fi_key", None)
            wf_key = cmd.get("wf_key", p3bm.BM_WF_CATEGORIZATION)
            wb_type = cmd.get("wb_type", p3bm.WF_WORKBOOKS_IN)
            wb_name = cmd.get("wb_name", None)
            logger.info(f"Start Command: 'Init' fi_key: {fi_key}, "
                        f"wf_key: {wf_key}, wb_type: {wb_type}, wb_name: {wb_name}")
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
            logger.info(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_init_command() command method
    # ------------------------------------------------------------------------ +
    #region FI_save_cmd() command method
    def FI_save_cmd(self, cmd : Dict = None) -> None: 
        """Execute FI_save command for one fi_key or 'all'.
        
        This command saves the Data Context aspects of the View Model to
        contain workbooks and other information for the specified financial
        institution.

        FIs have associated financial documents (FD), for example workbooks,
        that are processed within workflows, typically moving through a 
        series of named workflows. A given FD is either of type input or output 
        with respect to the workflow (wb_type). Also, FDs are individually 
        named (wb_name). Specifying a wb_name is optional, but will indicate
        the command applies to just the named workbook.

        Arguments:
            fi_key (str): The key for the financial institution. If None, 
                no action is taken. If 'all', all workbooks are loaded.
            wf_key (str): The key for the workflow.
            wb_type (str): The type of workbook, either input or output.
            wb_name (str): The name of the workbook. If None, all workbooks
                modified since open are saved. If 'all', all workbooks are saved.
        Raises:
            RuntimeError: For excemptions.
        """
        try:
            st = p3u.start_timer()
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            fi_key = cmd.get("fi_key", None)
            wf_key = cmd.get("wf_key", p3bm.BM_WF_CATEGORIZATION)
            wb_type = cmd.get("wb_type", p3bm.WF_WORKBOOKS_IN)
            wb_name = cmd.get("wb_name", None)
            logger.info(f"Start Command: 'Save' fi_key: {fi_key}, "
                        f"wf_key: {wf_key}, wb_type: {wb_type}, wb_name: {wb_name}")
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
            # Save the workbooks for the specified FI, WF, and WB-type.
            ret = self.budget_model.bdwd_FI_WORKBOOKS_save(fi_key, wf_key, wb_type)
            # Set this fi_key as the latest or current FI key.
            self.FI_KEY = fi_key
            self.WF_KEY = wf_key
            self.WB_TYPE = wb_type
            logger.info(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_init_command() command method
    # ------------------------------------------------------------------------ +
    #region template() command methods
    #endregion template() method
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion FICommandInterface Budget Manager View Model Command Interface                                  +
    # ======================================================================== +

    # ======================================================================== +
    #region FIDataContextInterface view_model Data Context Interface                                +
    """BDM view_model Data Context Methods.

    These methods are to access the View Model as a Data Context from a View.
    Used by client packages up-stream in View-land, some are data requests and
    others perform work on the view_model Data Context state while owning
    the concern for syncing with the Model downstream.    

    This View Model leverages the BDWD (Budget Domain Working Data) feature 
    of the BudgetModel. All data is transient and not automatically saved to
    the BudgetModel store. 
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbooks_count() method
    def FI_get_loaded_workbooks_count(self) -> int: 
        """Return count of all loaded workbooks from Data Context."""
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            return self.budget_model.bdwd_LOADED_WORKBOOKS_count()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbooks_count() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbooks() method
    def FI_get_loaded_workbooks(self) -> List[str]: 
        """Return names of all loaded workbooks from Data Context."""
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            return self.budget_model.bdwd_LOADED_WORKBOOKS_get()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbook_names() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbook_names() method
    def FI_get_loaded_workbook_names(self) -> List[str]: 
        """Return names of all loaded workbooks from Data Context."""
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            bdwd_wb_list = self.budget_model.bdwd_LOADED_WORKBOOKS_get()
            wb_name_list = []
            for wb_name, _ in bdwd_wb_list:
                wb_name_list.append(wb_name)
            return wb_name_list
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbook_names() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbook_by_index() method
    def FI_get_loaded_workbook_by_index(self, i:int=0) -> Workbook: 
        """Reference loaded loaded workbooks by index, return Workbook object."""
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            bdwd_wb_list = self.budget_model.bdwd_LOADED_WORKBOOKS_get()
            if i < len(bdwd_wb_list):
                wb_name, wb = bdwd_wb_list[i]
                return wb
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbook_by_index() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbook_by_name() method
    def FI_get_loaded_workbook_by_name(self, name:str=None) -> Workbook: 
        """Reference loaded loaded workbooks by name, return Workbook object."""
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            bdwd_wb_list = self.budget_model.bdwd_LOADED_WORKBOOKS_get()
            for wb_name, wb in bdwd_wb_list:
                if wb_name == name:
                    return wb
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbook_by_name() method
    # ------------------------------------------------------------------------ +
    #endregion FIDataContextInterface view_model Data Context Methods                                +                             +
    # ======================================================================== +

    # ======================================================================== +
    #region BDM/BSM model Data Methods                                         +
    """BDM/BSM model Data Methods.

    These methods are to access the Model interfaces for BDM and BSM.

    In out MVVM design, the View has no knowledge of the Model, only the
    ViewModel invokes Model interfaces.  
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region BUDMAN_STORE_save() method
    def BUDMAN_STORE_save(self) -> None:
        """Save the Budget Manager store (BUDMAN_STORE) file with the BSM.

        Returns:
            None: for success.
        Raises:
            RuntimeError: If the BUDMAN_STORE file cannot be saved.
        """
        try:
            st = p3u.start_timer()
            logger.info(f"Start: ...")
            # Save the BUDMAN_STORE file with the BSM.
            # Use the BUDMAN_STORE info configured in BUDMAN_SETTINGS.
            budman_store_value = settings[p3bm.BUDMAN_STORE]
            budman_folder = settings[p3bm.BUDMAN_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_value
            # Update some values prior to saving.
            self.budget_model.bdm_url = budman_store_abs_path.as_uri()
            self.budget_model.bm_last_modified_date = p3u.now_iso_date_string()
            self.budget_model.bm_last_modified_by = getpass.getuser()
            # Get a Dict of the BudgetModel to store.
            budget_model_dict = self.budget_model.to_dict()
            # Save the BUDMAN_STORE file.
            p3bm.bsm_BUDMAN_STORE_save(budget_model_dict, budman_store_abs_path)
            logger.info(f"Saved BUDMAN_STORE file: {budman_store_abs_path}")
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BUDMAN_STORE_save() method
    # ------------------------------------------------------------------------ +
    #region BUDMAN_STORE_load_cmd() method
    def BUDMAN_STORE_load_cmd(self) -> Dict:
        """Load the Budget Manager store (BUDMAN_STORE) file from the BSM.

        A 

        Returns:
            Dict: The BudgetModel store as a dictionary.
        """
        try:
            st = p3u.start_timer()
            logger.info(f"Start: ...")
            # Load the BUDMAN_STORE file with the BSM.
            # Use the BUDMAN_STORE configured in BUDMAN_SETTINGS.
            budman_store_value = settings[p3bm.BUDMAN_STORE]
            budman_folder = settings[p3bm.BUDMAN_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_value
            # Load the BUDMAN_STORE file.
            budman_store_dict = p3bm.bsm_BUDMAN_STORE_load(budman_store_abs_path)
            self.BUDMAN_STORE_loaded = True
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return budman_store_dict
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BUDMAN_STORE_load_cmd() method
    # ------------------------------------------------------------------------ +
    #endregion BDM view_model Data Context Methods                             +
    # ======================================================================== +
