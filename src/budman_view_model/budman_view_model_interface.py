# ---------------------------------------------------------------------------- +
#region budman_view_model_interface.py module
""" budman_view_model_interface.py implements the BudgetManagerViewModelInterface
class, serving as the ViewModel for the Budget Manager application.
"""
#endregion budman_view_model_interface.py module
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
from budman_model import P2, P4, P6, P8, P10
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(settings[p3bm.APP_NAME])
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudgetManagerViewModelInterface():
    # ======================================================================== +
    #region BudgetManagerViewModelInterface class
    """A Budget Model View Model to support Commands and Data Context.
    
    This ViewModel support two primary interfaces: Command processing to the 
    Model (from upstream Views and other clients) and Data Context properties
    and methods. The Data Context (DC) is the main medium of exchange of
    data between the ViewModel and the View. Commands are sent from the 
    View, to be processed by the ViewModel in the context of the DC. Command
    implementation methods access the APIs of the Model to perform the
    requested actions.
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Class Variables
    #endregion Class Variables
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        super().__init__()
        self._initialized : bool = False
        self.BUDMAN_STORE_loaded : bool = False
        self._budget_model : p3bm.BudgetModel = None
        self._data_context : Dict = {}
        self._cmd_map : Dict[str, Callable] = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region Properties
    @property
    def initialized(self) -> bool:
        """Return True if the ViewModel is initialized."""
        return self._initialized
    @initialized.setter
    def initialized(self, value: bool) -> None:
        """Set the initialized property."""
        if not isinstance(value, bool):
            raise ValueError("initialized must be a boolean value.")
        self._initialized = value
    @property
    def budget_model(self) -> p3bm.BudgetModel:
        """Return the BudgetModel instance."""
        return self._budget_model
    @budget_model.setter
    def budget_model(self, value: p3bm.BudgetModel) -> None:
        """Set the BudgetModel instance."""
        if not isinstance(value, p3bm.BudgetModel):
            raise ValueError("budget_model must be a BudgetModel instance.")
        self._budget_model = value
    @property
    def data_context(self) -> Dict:
        """Return the data context dictionary."""
        return self._data_context
    @data_context.setter
    def data_context(self, value: Dict) -> None:
        """Set the data context dictionary."""
        if not isinstance(value, dict):
            raise ValueError("data_context must be a dictionary.")
        self._data_context = value
    @property
    def cmd_map(self) -> Dict[str, Callable]:
        """Return the command map dictionary."""
        return self._cmd_map
    @cmd_map.setter
    def cmd_map(self, value: Dict[str, Callable]) -> None:
        """Set the command map dictionary."""
        if not isinstance(value, dict):
            raise ValueError("cmd_map must be a dictionary.")
        self._cmd_map = value
    #endregion Properties
    # ------------------------------------------------------------------------ +
    #region initialize() method
    def initialize(self, load_user_store : bool = False) -> "BudgetManagerViewModelInterface":
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
                    config_object = p3bm.bsm_BUDMAN_STORE_load()
                    self.BUDMAN_STORE_loaded = True
                else:
                    # Use the builtin default template as a config_object.
                    config_object = p3bm.BudgetModelTemplate.get_budget_model_template()
                # Now to initialize the budget model.
                self.budget_model = p3bm.BudgetModel(config_object).bdm_initialize()
            if not self.budget_model.bm_initialized: 
                raise ValueError("BudgetModel is not initialized.")
            # Initialize the data context. This View Model uses a DC object from
            # the Model which places data in it.
            self.data_context = self.budget_model.data_context
            # Initialize the command map.
            self.initialize_cmd_map()
            self.initialized = True
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
                "save_cmd_workbooks": self.FI_LOADED_WORKBOOKS_save_cmd,
                "load_cmd_BUDMAN_STORE": self.BUDMAN_STORE_load_cmd,
                "save_cmd_BUDMAN_STORE": self.BUDMAN_STORE_save,
                "show_cmd_DATA_CONTEXT": self.DATA_CONTEXT_show_cmd,
            }
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #endregion BudgetManagerViewModelInterface class
    # ======================================================================== +

    # ======================================================================== +
    #region BudgetManagerViewModelInterface implementation                     +
    """BudgetModelViewModelInterface provides two interfaces:
       1. BudgetManagerViewModelCommandInterface.
       2. BudgetManagerViewModelDataContextInterface.
    
    BudgetManagerViewModelCommandInterface
    --------------------------------------

    - Provides Command Processing for the command pattern, used by Views and
      other upstream clients to submit commands to the ViewModel. The command
    - Provides the Command Binding Implementations. The cmd_map property 
      holds a map from the supported command_keys to the methods that
      implement them. This map binds the commands to the code that implements
      each Command.

    BudgetManagerViewModelDataContextInterface
    ------------------------------------------

    - Provides Data Context access to the ViewModel. This interface is
      functional, not requiring the upstream caller to know much about the
      data apart from attribute names. It uses dict objects to represent
      objects.

    In View Model form, these methods provide an Interface for executing
    Commands as a design pattern. Commands take actions for a command 
    initiated by an upstream View, or other client caller. Of course, 
    the upstream caller is mapping their specific domain of focus to the View Model
    interface. In general, there are a Command methods and other "Data Context"
    methods in a subsequent section.

    Throughout the BudgetModel (budman) application, a design language is
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
    of worklows that process transactions from financial institutions, income 
    and expenses. Transactions are categorized by scanning input data and
    producing output data.

    - Budget Domain (BD) and Budget Domain Model (BDM) - the conceptual model 
    of the budget top-level concept.

    Budget Domain Objects
    ---------------------

    Objects are considered things, pieces of data that commands do something to.
    An app will execute commands to take action on an object. Object names are 
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
    save, show, delete, add, etc., suffixed by '_cmd'. Additional method 
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
    and supporting parameter arguments. The verb is the action to be taken,
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
    a constant defined in the module or class and used to represent a single
    value or a list of values both in the design language and the code.

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

    Also, adopting the practice of documenting the design language in the code
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
    # ======================================================================== +
    #region BudgetManagerViewModelCommandInterface implementation              +
    """ BudgetManagerViewModelCommandInterface Design Notes

    A Command Pattern supports a means to represent a command as an object,
    in out case, a dictionary. The command is a request to perform an action
    and includes arguments. Both the command and the arguments are validated
    before executing the command. The command is a dictionary with a
    command key and a an optional sub-command value. The command key includes
    the name of the requested action, a verb, e.g., init, show, save, etc. 
    The characters '_cmd' are appended to the command key. The sub-command 
    value is optional, but most common. It is a noun indicating the type
    of object to be acted upon. The command key is combined with the subcommand
    value to form a full command key. The full command key is used to look
    up the command method in the command map. The command map is a dictionary
    with the full command key as the key and the command method as the value.

    An example command object content is:

    {'init_cmd': 'fin_inst', 'fi_key': 'boa', 'wf_key': None, 'wb_name': 'all'}

    The command key is 'init_cmd' and the sub-command value is 'fin_inst'. The 
    resulting full command key is 'init_cmd_fin_inst'. 

    The other key/values are arguments: fi_key = 'boa', wf_key = None, and
    wb_name = 'all'. Some arguments are included with default values and will
    raise an error if their value is None.

    - fi_key: The key for the financial institution, cannot be None. The 
      reserved fi_key = 'all' indicates to apply the action to all FIs.
    - wf_key: The key for the workflow, cannot be None. The reserved 
      wf_key = 'all' indicates to apply the action to all workflows.
    - wb_name: The name of a workbook, None or the reserved name of 'all'
      which indicates to apply the action to all workbooks in the scope.
    
    """
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Command Processing methods
    # ------------------------------------------------------------------------ +
    #region BMVM_execute_cmd() Command Processing method
    def BMVM_execute_cmd(self, 
                         cmd : Dict = None,
                         raise_errors : bool = False) -> Tuple[bool, Any]:
        """Execute a command for the Budget Model View Model.

        This method executes a command for the Budget Model View Model. 
        Commands and common argument values are validated. This method is the
        primary interface to the ViewModel, hence, it will return a result
        and not raise exceptions. When errors are caught, the result will 
        indicate an error occurred and have an error message.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object.
            raise_errors (bool): If True, raise any errors encountered.
        
        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.

        Raises:
            If raise-errors is True, RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            st = p3u.start_timer()
            logger.info(f"Start Command: {cmd}")
            if not self.initialized:
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
            logger.info(f"Executing command: {function_name}({str(cmd)})")
            status, result = self.cmd_map.get(full_cmd_key)(cmd)
            return status, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            if raise_errors:
                raise RuntimeError(m)
            return False, m
    #endregion BMVM_execute_cmd() Command Processing method
    #region BMVM_validate_cmd() Command Processing method
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
            # Extract a valid, full cmd key from the cmd, or error out.
            success, result = self.BMVM_full_cmd_key(cmd)
            if not success: return False, result
            full_cmd_key = result
            # Have a valid full_cmd_key, now check the arguments.
            success, result = self.BMVM_cmd_key(cmd)
            if not success: return False, result
            cmd_key = result
            for key, value in cmd.items():
                if key == cmd_key: continue
                elif key == "fi_key":
                    if not self.dc_FI_KEY_validate(value):
                        m = f"Invalid fi_key value: '{value}'."
                        logger.error(m)
                        return False, m
                    continue
                elif key == "wb_name": continue
                elif key == "wf_key":
                    if not self.dc_WF_KEY_validate(value):
                        m = f"Invalid wf_key value: '{value}'."
                        logger.error(m)
                        return False, m
                    if value == p3bm.ALL_KEY:
                        logger.warning(f"wf_key: '{p3bm.ALL_KEY}' not implemented."
                                    f" Defaulting to {p3bm.BM_WF_CATEGORIZATION}.")
                        cmd[key] = p3bm.BM_WF_CATEGORIZATION
                    continue
                else:
                    m = f"Unchecked argument key: '{key}': '{value}'."
                    logger.debug(m)
            logger.debug(f"Full command key: '{full_cmd_key}' cmd: {str(cmd)}")
            return True, full_cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BMVM_validate_cmd() Command Processing method
    #region BMVM_cmd_key() Command Processing method
    def BMVM_cmd_key(self, cmd : Dict = None) -> Tuple[bool, str]:
        """Extract and return the cmd key from cmd."""
        try:
            if not self.initialized:
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
            return True, cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BMVM_cmd_key() Command Processing method
    #region BMVM_full_cmd_key() Command Processing method
    def BMVM_full_cmd_key(self, cmd : Dict = None) -> Tuple[bool, str]:
        """Extract and return full cmd key from cmd, if subcommand given."""
        try:
            # Extract a cmd key from the cmd, or error out.
            success, result = self.BMVM_cmd_key(cmd)
            if not success: return False, result
            cmd_key = result
            # Acquire sub-command key if present.
            sub_cmd = cmd[cmd_key]
            full_cmd_key = cmd_key + '_' + sub_cmd if p3u.str_notempty(sub_cmd) else cmd_key
            # Check the cmd_key against the command map.
            if full_cmd_key not in self.cmd_map:
                m = f"Command key '{full_cmd_key}' not found in command map."
                logger.error(m)
                return False, m
            return True, full_cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BMVM_full_cmd_key() Command Processing method
    # ------------------------------------------------------------------------ +
    #endregion Command Processing methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Command Binding Implementations
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region FI_init_command() command method
    def FI_init_cmd(self, cmd : Dict = None) -> Tuple[bool, str]: 
        """Execute FI_init command for one fi_key or 'all'.
        
        This command initializes the Data Context aspects of the View Model to
        contain the current information for the specified financial
        institution (FI) which may be 'all' or a specific FI key. When completed 
        successfully, returns a string representation of the following FI data 
        for each applicable financial institution:
        - fi_key: The key for the financial institution.
        - wf_key: The key for the workflow.
        - wb_type: The type of workbooks, either input or output.
        - wb_name: The name of the workbooks within each type.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
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
            logger.info(f"Start: {str(cmd)}")
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
            # Load the workbooks for the specified FI and workflow.
            lwbl = self.budget_model.bdwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
            # Set last values of FI_init_cmd in the DC.
            self.dc_FI_KEY = fi_key
            self.dc_WF_KEY = wf_key
            self.dc_WB_TYPE = wb_type
            self.dc_WB_NAME = wb_name
            # Create result
            lwbl_names = self.FI_get_loaded_workbook_names()
            result = f"Loaded {len(lwbl_names)} Workbooks: {str(lwbl_names)}"
            logger.info(f"Complete Command: 'Init' {p3u.stop_timer(st)}")   
            return True, result
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise RuntimeError(m) from e
    #endregion FI_init_command() command method
    # ------------------------------------------------------------------------ +
    #region FI_LOADED_WORKBOOKS_save_cmd() command method
    def FI_LOADED_WORKBOOKS_save_cmd(self, cmd : Dict = None) -> None: 
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
            RuntimeError: For exceptions.
        """
        try:
            st = p3u.start_timer()
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            # Get the command arguments.
            fi_key = cmd.get("fi_key", None)
            wf_key = cmd.get("wf_key", p3bm.BM_WF_CATEGORIZATION)
            wb_type = cmd.get("wb_type", p3bm.WF_WORKBOOKS_IN)
            wb_name = cmd.get("wb_name", None)
            # Resolve with current DC values.
            if fi_key != self.dc_FI_KEY:
                logger.warning(f"fi_key: arg '{fi_key}' differs from "
                                f" current value '{self.dc_FI_KEY}'")
                fi_key = self.dc_FI_KEY
                logger.warning(f"fi_key: using current value '{self.dc_FI_KEY}'")
            if wf_key != self.dc_WF_KEY:
                logger.warning(f"wf_key: arg '{wf_key}' differs from "
                                f" current value '{self.dc_WF_KEY}'")
                wf_key = self.dc_WF_KEY
                logger.warning(f"wf_key: using current value '{self.dc_WF_KEY}'")
            if wb_name != self.dc_WB_NAME:
                logger.warning(f"wb_name: arg '{wb_name}' differs from "
                                f" current value '{self.dc_WB_NAME}'")
            if wb_type != self.dc_WB_TYPE:
                logger.warning(f"wb_type: arg '{wb_type}' differs from "
                                f" current value '{self.dc_WB_TYPE}'")
                wb_type = self.dc_WB_TYPE
                logger.warning(f"wb_type: using current value '{self.dc_WB_TYPE}'")
            logger.info(f"Start: {str(cmd)}")
            # Check if valid fi_key            
            try:
                _ = self.budget_model.bdm_FI_KEY_validate(fi_key)
            except ValueError as e:
                m = f"ValueError({str(e)})"
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            # Get the WORKBOOK_LIST from the BDM.
            # wbl = self.bdm_FI_WF_WORKBOOK_LIST(fi_key, wf_key, wb_type)
            # Get the LOADED_WORKBOOKS_LIST from the BDM_WORKING_DATA.
            lwbl = self.dc_LOADED_WORKBOOKS
            # For each loaded workbook, save it to its the path .
            for wb_name, wb in lwbl:
                self.budget_model.bsm_FI_WF_WORKBOOK_save(wb, wb_name,
                                                          fi_key, wf_key, wb_type)
            # Save the workbooks for the specified FI, WF, and WB-type.
            # ret = self.budget_model.bdwd_FI_WORKBOOKS_save(fi_key, wf_key, wb_type)
            logger.info(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_LOADED_WORKBOOKS_save_cmd() command method
    # ------------------------------------------------------------------------ +
    #region BUDMAN_STORE_save() method
    def BUDMAN_STORE_save(self, cmd : Dict) -> None:
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
    def BUDMAN_STORE_load_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Load the Budget Manager store (BUDMAN_STORE) file from the BSM.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain load_cmd = 'BUDMAN_STORE' resulting in
            a full command key of 'load_cmd_BUDMAN_STORE'.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            st = p3u.start_timer()
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            logger.info(f"Start: ...")
            # Load the BUDMAN_STORE file with the BSM.
            # Use the BUDMAN_STORE configured in BUDMAN_SETTINGS.
            budman_store_value = settings[p3bm.BUDMAN_STORE]
            budman_folder = settings[p3bm.BUDMAN_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_value
            # Load the BUDMAN_STORE file.
            budman_store_dict = p3bm.bsm_BUDMAN_STORE_load(budman_store_abs_path)
            self.dc_BUDMAN_STORE = budman_store_dict
            self.BUDMAN_STORE_loaded = True
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, budman_store_dict
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BUDMAN_STORE_load_cmd() method
    # ------------------------------------------------------------------------ +
    #region DATA_CONTEXT_show_cmd() method
    def DATA_CONTEXT_show_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Show information in the Budget Manager Data Context.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain show_cmd = 'DATA_CONTEXT' resulting in
            a full command key of 'show_cmd_DATA_CONTEXT'.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            st = p3u.start_timer()
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            logger.info(f"Start: ...")
            # Return the current content of the DATA_CONTEXT.
            bs = self.dc_BUDMAN_STORE
            bs_str = p3u.first_n(str(bs))
            bs_msg = p3u.first_n(bs_str)
            lwbl = self.dc_LOADED_WORKBOOKS
            lwbl_count = len(lwbl) if lwbl else 0
            result = f"Budget Manager Data Context:\n"
            result += f"{P2}{p3bm.DC_INITIALIZED}: {self.dc_INITIALIZED}\n"
            result += f"{P2}{p3bm.FI_KEY}: {self.dc_FI_KEY}\n"
            result += f"{P2}{p3bm.WF_KEY}: {self.dc_WF_KEY}\n"
            result += f"{P2}{p3bm.WB_TYPE}: {self.dc_WB_TYPE}\n"
            result += f"{P2}{p3bm.WB_NAME}: {self.dc_WB_NAME}\n"
            result += f"{P2}{p3bm.DC_BUDMAN_STORE}: {bs_msg}\n"
            result += f"{P2}{p3bm.DC_LOADED_WORKBOOKS}: {lwbl_count}\n"
            if lwbl_count > 0:
                for wb_name, wb in lwbl:
                    result += f"{P4}{wb_name}: {str(wb)}\n"
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, result
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion DATA_CONTEXT_show_cmd() method
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion Command Binding Implementations
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion BudgetManagerViewModelCommandInterface implementation           +
    # ======================================================================== +
    #                                                                          +
    # ======================================================================== +
    #region BudgetManagerViewModelDataContextInterface implementation          +
    """BDM view_model Data Context Methods.

    Budget Manager is designed around the MVVM (Model View ViewModel) design
    pattern. In MVVM implementations, a View binds to a ViewModel through an
    abstract Data Context (DC) object interface. Also, there is often a Command
    Processing pattern to map command actions from a user interface View to 
    data actions in the DC. 
    
    Herein, the design is to have the DC support Commands as well as DC
    properties and methods. To keep the details of the View Model limited in
    the design of commands, all understanding of the structure of the data in 
    in the DC, the ViewModel and beyond it, the Model, the DC properties and
    methods are where downstream APIs are used, not in the Command Binding
    Implementation methods.
    
    These DC methods are used by Commands to access DC data values.
    As an API, the DC methods are an abstraction to support a View trying to
    interact with a user. Some are data requests and
    others perform work on the view_model Data Context state while owning
    the concern for syncing with the Model downstream.    

    This View Model leverages the DC leverages BudgetManager Domain Model (BDM)
    "library" to reference actual data for the application, in memory. 
    When storage actions are required, the BudgetManager Storage Model (BSM)
    library.
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Data Context Interface methods
    # ------------------------------------------------------------------------ +
    #region get_DC() method
    def get_DC(self) -> Dict:
        """Return the Data Context for the ViewModel.

        This method returns the Data Context for the ViewModel. The Data
        Context is a dictionary that contains all of the data for the
        ViewModel. It is used to bind the ViewModel to the View.
        """
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            return self.budget_model.bdwd_LOADED_WORKBOOKS_get()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion get_DC() method
    # ------------------------------------------------------------------------ +
    #region set_DC() method
    def set_DC(self, dc : Dict) -> None:
        """Set the Data Context for the ViewModel.

        This method sets the Data Context for the ViewModel. The Data
        Context is a dictionary that contains all of the data for the
        ViewModel. It is used to bind the ViewModel to the View.
        """
        try:
            # Reference the BDWD_LOADED_WORKBOOKS.
            self.budget_model.bdwd_LOADED_WORKBOOKS_set(dc)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion set_DC() method
    # ------------------------------------------------------------------------ +
    #endregion Data Context Interface methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Data Context Properties                                            +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    def _valid_DC(self) -> Dict:
        """Init self._data_context if it is None."""
        try:
            self._data_context = self._data_context if self._data_context else {}
            return self._data_context
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    @property
    def dc_INITIALIZED(self) -> bool:
        """Return the value of the DC_INITIALIZED attribute."""
        dc = self._valid_DC()
        if p3bm.DC_INITIALIZED not in dc:
            self.data_context[p3bm.DC_INITIALIZED] = False
        return self.data_context[p3bm.DC_INITIALIZED]
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """Set the value of the DC_INITIALIZED attribute."""
        dc = self._valid_DC()
        self.data_context[p3bm.DC_INITIALIZED] = value
    @property
    def dc_FI_KEY(self) -> str:
        """Return the current financial institution key value in DC."""
        dc = self._valid_DC()
        if p3bm.FI_KEY not in dc:
            self.data_context[p3bm.FI_KEY] = None
        return self.data_context[p3bm.FI_KEY]
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """Set the current financial institution key value in DC."""
        dc = self._valid_DC()
        self.data_context[p3bm.FI_KEY] = value
    @property
    def dc_WF_KEY(self) -> str:
        """Return the current workflow key value in DC."""
        dc = self._valid_DC()
        if p3bm.WF_KEY not in dc:
            self.data_context[p3bm.WF_KEY] = None
        return self.data_context[p3bm.WF_KEY]
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """Set the current workflow key value in DC."""
        dc = self._valid_DC()
        self.data_context[p3bm.WF_KEY] = value
    @property
    def dc_WB_TYPE(self) -> str:
        """Return the current workbook type value in DC."""
        dc = self._valid_DC()
        if p3bm.WB_TYPE not in dc:
            self.data_context[p3bm.WB_TYPE] = None
        return self.data_context[p3bm.WB_TYPE]
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the current workbook type value in DC."""
        dc = self._valid_DC()
        self.data_context[p3bm.WB_TYPE] = value
    @property
    def dc_WB_NAME(self) -> str:
        """Return the current workbook name value in DC."""
        dc = self._valid_DC()
        if p3bm.WB_NAME not in dc:
            self.data_context[p3bm.WB_NAME] = None
        return self.data_context[p3bm.WB_NAME]
    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
        """Set the current workbook name value in DC."""
        dc = self._valid_DC()
        self.data_context[p3bm.WB_NAME] = value
    @property
    def dc_BUDMAN_STORE(self) -> str:
        """Return the current BUDMAN_STORE value in DC."""
        dc = self._valid_DC()
        if p3bm.DC_BUDMAN_STORE not in dc:
            self.data_context[p3bm.DC_BUDMAN_STORE] = None
        return self.data_context[p3bm.DC_BUDMAN_STORE]
    @dc_BUDMAN_STORE.setter
    def dc_BUDMAN_STORE(self, value: str) -> None:
        """Set the current BUDMAN_STORE value in DC."""
        dc = self._valid_DC()
        self.data_context[p3bm.DC_BUDMAN_STORE] = value
    @property 
    def dc_LOADED_WORKBOOKS(self) -> p3bm.LOADED_WORKBOOKS_LIST:
        """Return the current loaded workbooks value in DC."""
        dc = self._valid_DC()
        if p3bm.DC_LOADED_WORKBOOKS not in dc:
            self.data_context[p3bm.DC_LOADED_WORKBOOKS] = None
        return self.data_context[p3bm.DC_LOADED_WORKBOOKS]
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: p3bm.LOADED_WORKBOOKS_LIST) -> None:
        """Set the current loaded workbooks value in DC."""
        dc = self._valid_DC()
        self.data_context[p3bm.DC_LOADED_WORKBOOKS] = value
    # ------------------------------------------------------------------------ +
    #endregion Data Context Properties
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Data Context Methods
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region dc_WF_KEY_validate() method
    def dc_WF_KEY_validate(self, wf_key : str) -> bool: 
        """Return True if the wf_key is valid."""
        try:
            # Ask the Budget Domain Model to validate the wf_key.
            return self.budget_model.bdm_WF_KEY_validate(wf_key)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion dc_WF_KEY_validate() method
    # ------------------------------------------------------------------------ +
    #region dc_FI_KEY_validate() method
    def dc_FI_KEY_validate(self, fi_key : str) -> int: 
        """Return True if the fi_key is valid."""
        try:
            # Ask the Budget Domain Model to validate the fi_key.
            return self.budget_model.bdm_FI_KEY_validate(fi_key)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion dc_FI_KEY_validate() method
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
    #endregion Data Context Methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion BudgetManagerViewModelDataContextInterface implementation       +
    # ======================================================================== +
    #                                                                          +
    #endregion BudgetManagerViewModelInterface implementation
    # ======================================================================== +
