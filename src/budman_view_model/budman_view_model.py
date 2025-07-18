# ---------------------------------------------------------------------------- +
#region budman_view_model.py module
""" budman_view_model.py implements the BudManViewModel class.

    In MVVM, the ViewModel is the interface between the View and the Model. As
    such, it must provide the inherent View Model behavior, a Command Pattern,
    and a Data Context Pattern for the View. Also, it requires the services
    from one or more Model objects, in this case, the Budget Domain Model.

    Provided Interfaces:
    --------------------
       1. ViewModel - the behavior of a View Model in MVVM.
       2. ViewModelCommandProcessor - the Command Pattern.
       3. ViewModelDataContext - the Data Context Pattern.

    Required Interfaces:
    --------------------
        1. BDMClient - the Budget Domain Model provider.

    ViewModelCommandProcessor
    -------------------------

    - Provides Command Processor for the command pattern, used by Views and
      other upstream clients to submit commands to the ViewModel. The command
    - Provides the Command Binding Implementations. The cmd_map property 
      holds a map from the supported command_keys to the methods that
      implement them. This map binds the commands to the code that implements
      each Command.

    ViewModelDataContext
    --------------------

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

    Budget Domain Model Design Language (namespace) 
    -----------------------------------------------

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
    <class_abbrev>: "bdm" | "bmc" |"bdmwd" | "bdm_vm"
    "bdm" - Budget Domain Model (BudgetDomainModel class, budget_domain_model pkg)
    "bmc" - Budget Domain Model Config (BDMConfig class, budget_domain_model pkg)
    "bsm" - Budget Storage Model (budget_storage_model package)

    bdm_vm - scope is the concern of the Budget Domain Model View Model
    bdmwd - scope is the concern of the Budget Domain Model Working Data

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
#endregion budman_view_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, sys, getpass, time, copy, importlib
from pathlib import Path
from typing import List, Type, Optional, Dict, Tuple, Any, Callable

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_mvvm import (Model_Base, Model_Binding)
import budman_command_processor.budman_cp_namespace as cp
from budman_settings import *
from budman_namespace.design_language_namespace import *
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_workflows import (
    BDMTXNCategoryManager, TXNCategoryCatalog,
    category_map_count, get_category_map, clear_category_map, 
    compile_category_map, set_compiled_category_map, clear_compiled_category_map,
    check_sheet_schema, check_sheet_columns, 
    validate_budget_categories, process_budget_category,
    apply_check_register, output_category_tree, output_bdm_tree,
    process_txn_intake
    )
from budman_workflows import budget_category_mapping

from budget_domain_model import (
    BudgetDomainModel, 
    BDMConfig
    )
from budget_storage_model import *
from budman_data_context.budman_data_context_binding_class import BudManDataContext_Binding
from budman_data_context.budget_domain_model_working_data import BDMWorkingData
from budman_cli_view import budman_cli_parser, budman_cli_view
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManViewModel(BudManDataContext_Binding, Model_Binding): # future ABC for DC, CP, VM interfaces
    #region BudManViewModel class doc string                                   +
    """BudManViewModel - A Budget Manager View Model providing 
    CommandProcessor & Data Context.
    
    This ViewModel, BudManViewModel, depends on some primary MVVM design 
    pattern abstract behaviors:
        1. ViewModel_Base - the behavior of a View Model in MVVM.
        2. ViewModelCommandProcessor_Base (CP), Command Processor behavior,
        3. ViewModelDataContext_Base (DC), Data Context behavior, and
        4. Model_Base - the Model behavior.
         
    BudManViewModel is a concrete implementation of the ViewModel_Base and
    ViewModelCommandProcessor_Base. It applies the ViewModelDataContext_Binding
    and Model_Binding to access concrete Model and Data Context implementations.

    Each pattern is backed by defined interfaces for properties and methods. 
    CP is the means for a View to take actions performing commands against data 
    in the DC. From an MVVM pattern perspective, DC is the only medium of data 
    exchange between the View and the ViewModel using properties, methods and
    eventing. Commands are sent from the View, to be processed by the ViewModel 
    in the "context" of the data state in the DC. Command implementation methods 
    access the DC properties and invoke methods on the View Model DC interface 
    to perform the requested actions. A View Model may publish events as well, 
    which a View may subscribe to.
    """
    #endregion BudManViewModel class doc string                                +

    # ======================================================================== +
    #region BudManViewModel_Base class intrinsics                              +
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region    BudManViewModel Class __init__() constructor method             +
    def __init__(self, bdms_url : str = None, settings : BudManSettings = None) -> None:
        super().__init__()
        self._bdm_store_url : str = bdms_url
        self._settings = settings
        self._initialized : bool = False
        self._BDM_STORE_loaded : bool = False
        self._budget_domain_model : BudgetDomainModel = None
        self._cmd_map : Dict[str, Callable] = None
        self._shutdown : bool = False
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region    BudManViewModel Class Properties     
    @property
    def app_name(self) -> str:
        """Return the application name."""
        if self._settings is None:
            raise ValueError("Settings not configured.")
        return self._settings.get(APP_NAME, "BudManViewModel")      

    @property
    def bdms_url(self) -> str:
        """Return the BDM_STORE URL."""
        return self._bdm_store_url
    @bdms_url.setter
    def bdms_url(self, url: str) -> None:
        """Set the BDM_STORE URL."""
        if not isinstance(url, str):
            raise TypeError("bdms_url must be a string")
        if not url.startswith("file://") and not url.startswith("http://"):
            raise ValueError("bdms_url must be a valid file or http URL")
        self._bdm_store_url = url

    @property
    def settings(self) -> BudManSettings:
        """Return the application settings."""
        return self._settings
    @settings.setter
    def settings(self, settings: BudManSettings) -> None:
        """Set the application settings."""
        if not isinstance(settings, BudManSettings):
            raise TypeError("settings must be a BudManSettings instance")
        self._settings = settings

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

    # def _valid_DC(self) -> BDMWorkingData:
    #     """Init self._data_context if it is None."""
    #     try:
    #         if (self._data_context is None or 
    #             not isinstance(self._data_context, BDMWorkingData)):
    #             m = f"data_context property is not a BDMWorkingData instance, " 
    #             m += f"it is {type(self._data_context)}."
    #             logger.error(m)
    #             raise TypeError(m)
    #         return self._data_context
    #     except Exception as e:
    #         logger.error(p3u.exc_err_msg(e))
    #         raise
    #endregion BudManViewModel Class Properties                                +
    # ------------------------------------------------------------------------ +
    #region    BudManViewModel Class initialize() method                       +
    def initialize(self) -> "BudManViewModel":
        """Initialize the command view_model."""
        try:
            st = p3u.start_timer()
            logger.info(f"BizEVENT: View Model setup for '{self.app_name}'")
            # Check if the budget domain model is initialized.
            # bdm = self.initialize_model(load_user_store=load_user_store)
            # Create/initialize a BDMWorkingData data_context 
            # self.data_context = BDMWorkingData(self.model)
            # self.dc_initialize()
            # Initialize the command map.
            # TODO: binding for BudManCommandProcessor in the future,
            #       for now it is built in to the View Model.
            self.cp_initialize_cmd_map()  # TODO: move to DataContext class
            self.initialized = True
            logger.debug(f"Complete: {p3u.stop_timer(st)}")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BudManViewModel Class initialize() method                       +
    # ------------------------------------------------------------------------ +
    #region    BudManViewModel Class shutdown() method                          +
    def shutdown(self) -> None:
        """Shutdown the command view_model."""
        try:
            st = p3u.start_timer()
            logger.info(f"Shutdown Start: ...")
            if self._shutdown:
                logger.debug(f"shutdown already complete.")
                return None
            # Save the BDM_STORE file with the BSM.
            # Get a Dict of the BudgetModel to store.
            bdm_dict = BDMConfig.BDM_STORE_dehydrate(self.budget_domain_model)
            # budget_model_dict = self.budget_domain_model.to_dict()
            # Save the BDM_STORE file.
            bdm_url = self.dc_BDM_STORE[BDM_URL]
            bsm_BDM_STORE_url_put(bdm_dict, bdm_url)
            logger.info(f"Saved BDM_STORE url: {bdm_url}")
            logger.info(f"Shutdown Complete: {p3u.stop_timer(st)}")
            self._shutdown = True
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BudManViewModel Class shutdown() method                       +
    # ------------------------------------------------------------------------ +
    #region    BudManViewModel Class initialize_model() method                   +
    def initialize_model(self, bdms_url : str) -> BudgetDomainModel:
        """Create a model using the bdms_url location for a valid BDM_STORE.
            The BDM_STORE object provides the model configuration and state.
        """
        try:
            st = p3u.start_timer()
            logger.debug(f"Start: ...")
            # if a bdms_url is provided, load the BDM_STORE file.
            if p3u.str_notempty(self.bdms_url):
                # Load the BDM_STORE file from the URL.
                bdmc : BDMConfig= BDMConfig.BDM_STORE_url_get(self.bdms_url)
                if bdmc is None:
                    m = f"Failed to load BDM_STORE from URL: {self.bdms_url}"
                    logger.error(m)
                    raise ValueError(m)
                bdm_config : BDM_CONFIG = bdmc.bdm_config_object
                # Use the loaded BDM_STORE file as a config_object 
                self._BDM_STORE_loaded = True
            else:
                # Use the builtin default template as a config_object.
                bdm_config = BDMConfig.BDM_CONFIG_default()
                # Use the default BDM_CONFIG object as a config_object 
                self._BDM_STORE_loaded = False
            # Now to create the model and initialize it.
            model : BudgetDomainModel = BudgetDomainModel(bdm_config).bdm_initialize()
            if not model.bdm_initialized: 
                raise ValueError("BudgetModel is not initialized.")
            logger.debug(f"Complete: {p3u.stop_timer(st)}")
            return model
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BudManViewModel Class initialize_model() method                   +
    # ------------------------------------------------------------------------ +
    #region    ViewModelCommandProcessor_Base cp_initialize_cmd_map() method+
    def cp_initialize_cmd_map(self) -> None:
        """Initialize the cmd_map dictionary."""
        try:
            # Use the following cmd_map to dispatch the command for execution.
            self.cp_cmd_map = {
                "init_cmd_fin_inst": self.FI_init_cmd,
                "load_cmd_BDM_STORE": self.BDM_STORE_load_cmd,
                "save_cmd_BDM_STORE": self.BDM_STORE_save_cmd,
                "show_cmd_DATA_CONTEXT": self.DATA_CONTEXT_show_cmd,
                "show_cmd_workbooks": self.WORKBOOKS_show_cmd,
                "load_cmd_workbooks": self.WORKBOOKS_load_cmd,
                "save_cmd_workbooks": self.WORKBOOKS_save_cmd,
                "change_cmd_workbooks": self.CHANGE_cmd,
                "workflow_cmd_categorization": self.WORKFLOW_categorization_cmd,
                "workflow_cmd_apply": self.WORKFLOW_apply_cmd,
                "workflow_cmd_check": self.WORKFLOW_check_cmd,
                cp.CV_INTAKE_SUBCMD_KEY: self.WORKFLOW_intake_cmd,
                "show_cmd": self.SHOW_cmd,
                "change_cmd": self.CHANGE_cmd,
                "app_cmd": self.APP_cmd,
            }
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion ViewModelCommandProcessor_Base cp_initialize_cmd_map() method+
    # ------------------------------------------------------------------------ +
    #endregion BudManViewModel class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    ViewModelCommandProcessor_Base                                  +
    # ======================================================================== +
    #region    Design Notes                                                       +
    """ ViewModelCommandProcessor Design Notes (future ABC)

    A Command Pattern supports a means to represent a command as an object,
    in our case, a dictionary. The command is a request to perform an action
    and includes arguments. Both the command and the arguments are validated
    before executing the command. The command is a dictionary with a
    command key and a an optional sub-command value. The command key includes
    the name of the requested action, often, but not limited to a verb, 
    e.g., init, show, save, etc. That part is the cmd_name. So, here are some
    rules:
    - A cmd_name is a string of characters (which cannot include '_cmd').
    - A cmd_key is also a string composed of the cmd_name and the
      '_cmd' suffix.
    - A cmd_key becomes an actual 'key' in the cmd dict object with an 
      Optional[str] value. It is one identifier to use for binding to an
      execution function in the cmd_map.
    - A sub-command is given as a value to the cmd_key, but may be None.
    - A second key in the cmd dict is 'command_name' with the value being the 
      command name string, e.g., 'init', 'load', 'save', etc.
    - A third key used in a valid cmd dict object is 'subcmd_key' with a 
      string value constructed as" <cmd_key>_<subcmd_name>".

      Examples:
      - cli:  init fin_inst -> cmd_key = init_cmd, subcmd_key = init_cmd_fin_inst  
      - cli:  workflow categorization 2 -> cmd_key = workflow_cmd, subcmd_key = workflow_cmd_categorization   
      - cli:  app log rollover -> cmd_key = app_cmd, subcmd_key = app_cmd_log_subcmd

    When binding to an execution function, the subcmd_key is searched first, and
    used when present. If no subcmd_key binding exists in the cmd_map, then
    the cmd_key is sought and used. If no cmd_key binding found, then the cmd 
    is auto-bound to the UNKNOWN_cmd() exec function.

    The command key is a string, which is the name of the command.  
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
    #endregion design notes                                                    +
    # ------------------------------------------------------------------------ +
    #region    ViewModelCommandProcessor_Base Properties                       +
    @property
    def cp_cmd_map(self) -> Dict[str, Callable]:
        """Return the command map dictionary."""
        return self._cmd_map
    @cp_cmd_map.setter
    def cp_cmd_map(self, value: Dict[str, Callable]) -> None:
        """Set the command map dictionary."""
        if not isinstance(value, dict):
            raise ValueError("cmd_map must be a dictionary.")
        self._cmd_map = value

    #endregion ViewModelCommandProcessor_Base Properties                       +
    # ------------------------------------------------------------------------ +
    #region ViewModelCommandProcessor_Base ABC Interface methods               +
    # ------------------------------------------------------------------------ +
    #region cp_execute_cmd() Command Processor method
    def cp_execute_cmd(self, 
                         cmd : Dict = None,
                         raise_error : bool = False) -> Tuple[bool, Any]:
        """Execute a command for the View Model.

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
            success, result = self.cp_validate_cmd(cmd)
            if not success: return success, result
            # if cp_validate_cmd() is good, continue.
            exec_func: Callable = cmd[cp.CK_CMD_EXEC_FUNC]
            function_name = exec_func.__name__
            validate_only: bool = self.cp_cmd_attr_get(cmd, cp.CK_VALIDATE_ONLY)
            if validate_only:
                result = f"vo-command: {function_name}({str(cmd)})"
                logger.info(result)
                return True, result
            logger.info(f"Executing command: {function_name}({str(cmd)})")
            status, result = exec_func(cmd)
            # status, result = self.cp_cmd_map.get(full_cmd_key)(cmd)
            logger.info(f"Complete Command: [{p3u.stop_timer(st)}] {(status, str(result))}")
            return status, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            if raise_error:
                raise RuntimeError(m)
            return False, m
    #endregion cp_execute_cmd() Command Processor method
    #region cp_validate_cmd() Command Processor method
    def cp_validate_cmd(self, cmd : Dict = None,
                        validate_all : bool = False) -> BUDMAN_RESULT:
        """Validate the cmd object for cmd_key and parameters.

        Extract a valid, known full_cmd_key/cmd_key to succeed.
        Consider values to common arguments which can be validated with
        the data context.

        Arguments:
            cmd (Dict): A candidate Command object to validate.
            validate_all (bool): If True, validate all parts of the cmd, 
                before returning a result. If False, return on first discovery
                of an error.

        returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the
                cmd and arguments are valid.
                True returns the full cmd_key value as result.
                False, the message will contain an error message.
        """
        try:
            self.cp_validate_cmd_object(cmd, raise_error = True)
            # After cp_validate_cmd_object() returns, cmd dict has 
            # content to examine and validate.
            # For a few args, apply the DC values if no value given in the cmd.
            if self.cp_cmd_attr_get(cmd, cp.CK_FI_KEY) is None:
                self.cp_cmd_attr_set(cmd, cp.CK_FI_KEY,
                                    self.dc_FI_KEY)
            if self.cp_cmd_attr_get(cmd, cp.CK_WF_KEY) is None:
                self.cp_cmd_attr_set(cmd, cp.CK_WF_KEY,
                                    self.dc_WF_KEY)
            validate_all: bool = self.cp_cmd_attr_get(cmd, cp.CK_VALIDATE_ONLY)
            # If validate_all, then don't return a result until all cmd args 
            # are validated.
            all_results : str = "All Results:\n" if validate_all else ""
            result = "It's all good." 
            if validate_all:
                all_results = f"Command validation info: \n{P2}cmd: {str(cmd)}\n"
            success:bool = True
            # Validate the cmd arguments.
            for key, value in cmd.items():
                if key == cmd[cp.CK_CMD_KEY]: 
                    continue
                # elif key == cp.CK_ALL_WBS:
                #     cmd[cp.CK_WB_INDEX] = -1
                #     cmd[cp.CK_WB_LIST] = None
                elif key == cp.CK_WB_LIST:
                    for wb_index in cmd[cp.CK_WB_LIST]:
                        if not self.dc_WB_INDEX_validate(wb_index):
                            result = f"Invalid wb_list value: '{wb_index}'."
                            success = False 
                            logger.error(result)
                        continue
                    continue
                # elif key == cp.CK_WB_INDEX:
                #     if cmd[cp.CK_ALL_WBS] and value == -1:
                #         # If all_wbs is True, then wb_index is not used.
                #         continue
                #     elif not self.dc_WB_INDEX_validate(value):
                #         result = f"Invalid wb_index value: '{value}'."
                #         success = False 
                #         logger.error(result)
                #     continue
                elif key == cp.CK_FI_KEY:
                    if not self.dc_FI_KEY_validate(value):
                        result = f"Invalid fi_key value: '{value}'."
                        success = False 
                        logger.error(result)
                    continue
                elif key == cp.CK_WB_NAME:
                    continue
                elif key == cp.CK_WF_KEY:
                    if not self.dc_WF_KEY_validate(value):
                        result = f"Invalid wf_key value: '{value}'."
                        success = False 
                        logger.error(result)
                    if value == ALL_KEY:
                        logger.warning(f"wf_key: '{ALL_KEY}' not implemented."
                                    f" Defaulting to {BDM_WF_CATEGORIZATION}.")
                        cmd[key] = BDM_WF_CATEGORIZATION
                    continue
                elif key == cp.CK_WB_ID:
                    if not self.dc_WB_ID_validate(value):
                        result = f"Invalid wb_id level: '{value}'."
                        success = False 
                        logger.error(result)
                elif key == cp.CK_WB_INFO:
                    if not self.BMVM_cmd_WB_INFO_LEVEL_validate(value):
                        result = f"Invalid wb_info level: '{value}'."
                        success = False 
                        logger.error(result)
                elif key == cp.CK_PARSE_ONLY: 
                    po = cmd.get(cp.CK_PARSE_ONLY, False)
                    continue
                elif key == cp.CK_VALIDATE_ONLY: 
                    vo = cmd.get(cp.CK_VALIDATE_ONLY, False)
                    continue
                elif key == cp.CK_WHAT_IF: 
                    what_if = cmd.get(cp.CK_WHAT_IF, False)
                    continue
                elif key == cp.CK_CHECK_REGISTER:
                    continue
                else:
                    if key not in cp.BUDMAN_VALID_CK_ATTRS:
                        result = f"Unchecked argument key: '{key}': '{value}'."
                        logger.debug(result)
                # If not validate_all and success is False, return. Else, 
                # continue validating all cmd args.
                if not validate_all and not success:
                    # Without validate_all, if error, return, else continue
                    return success, result
                else:
                    # If validate_all, accumulate results.
                    all_results += f"{P2}{result}\n"
            # Argument check is complete
            if success:
                m = (f"Command validated - cmd_key: '{cmd[cp.CK_CMD_KEY]}' "
                            f"subcmd_key: {str(cmd[cp.CK_SUBCMD_KEY])}")
                logger.info(m)
                return success, m # The happy path return 
            if validate_all:
                return success, all_results
            return success, result
        except Exception as e:
            m = f"Error validating command: {str(cmd)}: {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m
    #endregion cp_validate_cmd() Command Processor method
    #region cp_validate_cmd_object() Command Processor method
    def cp_validate_cmd_object(self, 
                               cmd : Dict = None,
                               raise_error:bool=False) -> bool:
        """Validate Command Processor is initialized and the cmd object is valid.

        Test self.initialized property, must be True to proceed.

        Verify the cmd object is a dictionary, not None and not 0 length.

        Arguments:
            cmd (Dict): A candidate Command object to validate.
            raise_error (bool): If True, raise any errors encountered. 

        returns:
            bool: True if Command Processor is initialized, and cmd object is 
            a dictionary, False otherwise.

        Raise:
            RuntimeError: If raise_error is True, a RunTimeError is raised 
            with an error message.
        """
        # Primary Concern: Validate the cmd object is ready for parameter
        # validation. The current validation rules are:
        # 1. CommandProcessor is initialized, i.e., self.initialized is True.
        # 2. cmd is a dictionary, not None and not empty.
        # 3. cmd dictionary contains mandatory CK_CMD_KEY. There may be an 
        #    optional CK_SUBCMD_KEY, but it is not required.
        try:
            pfx = f"{self.__class__.__name__}.{self.cp_validate_cmd_object.__name__}: "
            logger.debug(f"Before Validating cmd object: {str(cmd)}")
            if not self.initialized:
                m = f"Command Processor is not initialized."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                cmd_type = type(cmd).__name__
                m = f"Invalid cmd object type: '{cmd_type}', no action taken."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if len(cmd) == 0:
                m = f"Command object is empty, no action taken."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            # Examine the cmd object for the required cmd values.
            # If necessary, try transitioning from the old cmd_key approach to 
            # the current one.
            success : bool = False
            cmd_exec_func : Callable = None
            # Check for the current cmd keys.
            cmd_key:str = cmd.get(cp.CK_CMD_KEY, None)
            cmd_name:str = cmd.get(cp.CK_CMD_NAME, None)
            subcmd_name:str = cmd.get(cp.CK_SUBCMD_NAME, None)
            subcmd_key:str = cmd.get(cp.CK_SUBCMD_KEY, None)
            # Bind the command execution function, using subcmd_key first,
            # then cmd_key, then the UNKNOWN_cmd function.
            if subcmd_key:
                cmd_exec_func = self.cp_exec_func_binding(subcmd_key, None)
            if cmd_key and cmd_exec_func is None:
                cmd_exec_func = self.cp_exec_func_binding(cmd_key, self.UNKNOWN_cmd)
            # Add it to the cmd object.
            cmd[cp.CK_CMD_EXEC_FUNC] = cmd_exec_func
            return True
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_validate_cmd_object() Command Processor method
    #region cp_exec_func_binding() Command Processor method
    def cp_exec_func_binding(self, cmd_key : str, default:Callable) -> Callable:
        """Get the command function for a given command key.

        This method retrieves the command function from the command map
        using the provided command key. If the command key is not found,
        it returns a function that handles unknown command cmd objects.

        Arguments:
            cmd_key (str): The command key to look up in the command map.

        Returns:
            Callable: The function associated with the command key, or an 
            UNKNOWN_cmd function if the key is not found.
        """
        if not p3u.str_notempty(cmd_key):
            raise ValueError("cmd_key must be a non-empty string.")
        exec_func : Callable = self.cp_cmd_map.get(cmd_key, None)
        if exec_func is None:
            # If no exec_func found, use the default UNKNOWN_cmd function.
            exec_func = default if default else None
        return exec_func
    #endregion cp_exec_func_binding() Command Processor method
    #region cp_cmd_name() Command Processor method
    def cp_cmd_name(self, cmd_key : str) -> str:
        """Extract the command name from the cmd_key.

        The command name is the front portion preceding the CMD_KEY_SUFFIX. 
        If no command name is found, an error message is returned.
        
        returns:
            BUDMAN_RESULT: The command name if found, else an error message.
        """
        try:
            if p3u.str_empty(cmd_key):
                m = "cmd_key is empty, no command name found."
                logger.error(m)
                return False, m
            result : str = cmd_key[:-4] if cmd_key.endswith(cp.CMD_KEY_SUFFIX) else cmd_key
            if len(result) == 0 or result == cmd_key:
                m = f"No command name found in: {str(cmd_key)}"
                logger.error(m)
                return False, m
            return True, result
        except Exception as e:
            m = f"Error extracting command name from cmd_key '{cmd_key}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m
    #endregion cp_cmd_name() Command Processor method
    #region cp_cmd_attr_get() Command Processor method
    def cp_cmd_attr_get(self, cmd: Dict,
                       key_name: str, default_value: Any = None) -> Any:
        """Use cmd attr key_name to get value or return default."""                  
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")    
        if not isinstance(key_name, str):
            raise TypeError("arg_name must be a string.")
        if key_name not in cmd:
            return default_value
        value = cmd.get(key_name, default_value)
        if value is None:
            return default_value
        return value
    #endregion cp_cmd_attr_get() Command Processor method
    #region cp_cmd_attr_set() Command Processor method
    def cp_cmd_attr_set(self, cmd: Dict,
                       arg_name: str, value: Any) -> None:
        """Set a command argument value in the cmd dictionary."""
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")
        if not isinstance(arg_name, str):
            raise TypeError("arg_name must be a string.")
        if arg_name not in cp.BUDMAN_VALID_CK_ATTRS:
            raise ValueError(f"Command argument '{arg_name}' is not a valid "
                             f"BudMan command argument. Valid arguments are: "
                             f"{cp.BUDMAN_VALID_CK_ATTRS}")
        if not isinstance(value, (str, int, float, bool)):
            raise TypeError(f"Command argument '{arg_name}' must be a string, "
                            f"int, float, or bool, not {type(value)}.")
        # Set the value in the cmd dictionary.
        cmd[arg_name] = value
    #endregion cp_cmd_attr_set() Command Processor method
    #region cp_cmd_attr_get_set() Command Processor method
    def cp_cmd_attr_get_set(self, cmd: Dict,
                       key_name: str, default_value: Any = None) -> Any:
        """Use cmd attr key_name to get value or set to default and return."""                  
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")    
        if not isinstance(key_name, str):
            raise TypeError("arg_name must be a string.")
        if key_name not in cmd:
            cmd[key_name] = default_value
        return cmd[key_name]
    #endregion cp_cmd_attr_get_set() Command Processor method
    #region BMVM_cmd_WB_INFO_LEVEL_validate() Command Processor method
    def BMVM_cmd_WB_INFO_LEVEL_validate(self, info_level) -> bool:
        """Return True if info_level is a valid value."""
        try:
            return info_level == ALL_KEY or info_level in VALID_WB_INFO_LEVELS
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BMVM_cmd_WB_INFO_LEVEL_validate() Command Processor method
    #region BMVM_cmd_exception() Command Processor method
    def BMVM_cmd_exception(self, e : Exception=None) -> Tuple[bool, str]:
        """Handle cmd exceptions.
        
        returns:
            Tuple[False, Error Message: str] 
        """
        try:
            # Extract a cmd key from the cmd, or error out.
            if e is None:
                e = RuntimeError("Exception arg 'e' was None.")
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion BMVM_cmd_exception() Command Processor method
    # ------------------------------------------------------------------------ +
    #endregion ViewModelCommandProcessor_Base methods                          +
    # ------------------------------------------------------------------------ +
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion ViewModelCommandProcessor_Base                                  +
    # ======================================================================== +
 
    # ======================================================================== +
    #region    Command Execution Methods                                       +
    # ======================================================================== +
    #region FI_init_cmd() command > init FI boa
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
            # TODO: prefix of the command, like "init FI boa" 
            result = "no result"
            if p3u.is_not_obj_of_type("cmd",cmd,dict):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{m}")
            fi_key = cmd.get(cp.CK_FI_KEY, None)
            wf_key = cmd.get(cp.CK_WF_KEY, BDM_WF_CATEGORIZATION)
            wf_purpose = cmd.get(cp.CK_WF_PURPOSE, WF_WORKING)
            wb_type = cmd.get(cp.CK_WB_TYPE, WF_WORKING)
            wb_name = cmd.get(cp.CK_WB_NAME, None)
            # TODO: Enable defaults for fi_key, wf_key, wb_type, wb_name in
            # settings.toml
            logger.info(f"Start: {str(cmd)}")
            if not p3u.is_non_empty_str("fi_key",fi_key):
                m = f"fi_key is None, no action taken."
                logger.error(m)
                raise RuntimeError(f"{m}")
            # Check for 'all'
            if fi_key == "all":
                raise NotImplementedError(f"fi_key 'all' not implemented.")
            # Check if valid fi_key            
            try:
                _ = self.dc_FI_KEY_validate(fi_key)
                # _ = self.budget_domain_model.bdm_FI_KEY_validate(fi_key)
            except ValueError as e:
                m = f"ValueError({str(e)})"
                logger.error(m)
                raise RuntimeError(f"{m}")
            # Load the workbooks for the FI,WF specified in the DC.
            # lwbl = self.DC.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
            # Set last values of FI_init_cmd in the DC.
            self.dc_FI_KEY = fi_key
            self.dc_WF_KEY = wf_key
            self.dc_WF_PURPOSE = wf_purpose
            self.dc_WB_TYPE = wb_type
            self.dc_WB_NAME = wb_name
            # Create result
            lwbl_names = list(self.dc_LOADED_WORKBOOKS.keys())
            result = f"Loaded {len(lwbl_names)} Workbooks: {str(lwbl_names)}"
            return True, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion FI_init_cmd() command method
    # ------------------------------------------------------------------------ +
    #region BDM_STORE_save_cmd() command > save bms
    def BDM_STORE_save_cmd(self, cmd : Dict) -> None:
        """Save the Budget Manager store (BDM_STORE) file with the BSM.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains the 
            BDM_STORE dict after updating DC_BDM_STORE in the DATA_CONTEXT.
            If False, a description of the error.
            
        Raises:
            RuntimeError: If the BDM_STORE file cannot be saved.
        """
        try:
            st = p3u.start_timer()
            logger.info(f"Start: ...")
            # Save the BDM_STORE file with the BSM.
            # Get a Dict of the BudgetModel to store.
            bdm_dict = BDMConfig.BDM_STORE_dehydrate(self.budget_domain_model)
            # budget_model_dict = self.budget_domain_model.to_dict()
            # Save the BDM_STORE file.
            bdm_url = self.dc_BDM_STORE[BDM_URL]
            bsm_BDM_STORE_url_put(bdm_dict, bdm_url)
            logger.info(f"Saved BDM_STORE url: {bdm_url}")
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, bdm_dict
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BDM_STORE_save_cmd() method
    # ------------------------------------------------------------------------ +
    #region BDM_STORE_load_cmd() command > load bms 
    def BDM_STORE_load_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Load the Budget Manager store (BDM_STORE) file from the BSM.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain load_cmd = 'BDM_STORE' resulting in
            a full command key of 'load_cmd_BDM_STORE'.

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
            logger.info(f"Start: ...")
            # Load the BDM_STORE file with the BSM.
            # Use the BDM_STORE configured in BUDMAN_SETTINGS.
            bdm_url = self.dc_BDM_STORE[BDM_URL]
            # Load the BDM_STORE file.
            budman_store_dict = bsm_BDM_STORE_url_get(bdm_url)
            self.dc_BDM_STORE = budman_store_dict
            self._BDM_STORE_loaded = True
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, budman_store_dict
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BDM_STORE_load_cmd() method
    # ------------------------------------------------------------------------ +
    #region DATA_CONTEXT_show_cmd() command > show dc
    def DATA_CONTEXT_show_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
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
            logger.debug(f"Start: ...")
            # Gather the current content of the DATA_CONTEXT.
            bs = self.dc_BDM_STORE
            bs_str = p3u.first_n(str(bs))
            # Prepare the Command output result
            result = f"Budget Manager Data Context:\n"
            result += f"{P2}{DC_BDM_STORE}: {bs_str}\n"
            result += (f"{P2}{DC_INITIALIZED}: {self.dc_INITIALIZED}"
                        f"{P2}{FI_KEY}: {self.dc_FI_KEY}"
                        f"{P2}{WF_KEY}: {self.dc_WF_KEY}"
                        f"{P2}{WF_PURPOSE}: {self.dc_WF_PURPOSE}\n")
            result += (f"{P2}{WB_ID}: {self.dc_WB_ID}"
                        f"{P2}{WB_INDEX}: {self.dc_WB_INDEX}"
                        f"{P2}{WB_NAME}: {self.dc_WB_NAME}"
                        f"{P2}{WB_TYPE}: {self.dc_WB_TYPE}\n")
            success, wdc_result = self.get_workbook_data_collection_info_str()
            result += wdc_result
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, result
        except Exception as e:
            m = f"Error showing Data Context: {p3u.exc_err_msg(e)}"
            logger.error(m)
            return False, m
    #endregion DATA_CONTEXT_show_cmd() method
    # ------------------------------------------------------------------------ +
    #region SHOW_cmd() command > show dc
    def SHOW_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """Show requested info from Budget Manager Data Context.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. 
    
        Required cmd object attributes:
            cmd_key: 'show_cmd' 
        Optional cmd object attributes:
            cmd_name: 'show'
            subcmd_name: CV_BUDGET_CATEGORIES_SUBCMD
            subcmd_key: 'show_cmd_BUDGET_CATEGORIES'
            CK_CAT_LIST: A list of budget categories to include, len()==0 means All. 

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
            logger.debug(f"Start: ...")
            if cmd[cp.CK_SUBCMD_NAME] == cp.CV_BUDGET_CATEGORIES_SUBCMD:
                # Show the budget categories.
                cat_list = self.cp_cmd_attr_get(cmd, cp.CK_CAT_LIST, [])
                tree_level = self.cp_cmd_attr_get(cmd, cp.CK_LEVEL, 2)
                result = output_category_tree(level=tree_level, cat_list=cat_list)
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, result
        except Exception as e:
            m = (f"Error executing cmd: {cmd[cp.CK_CMD_NAME]} {cmd[cp.CK_SUBCMD_NAME]}: "
                 f"{p3u.exc_err_msg(e)}")
            logger.error(m)
            return False, m
    #endregion SHOW_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKBOOKS_show_cmd() command > show wb 2
    def WORKBOOKS_show_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Show information about WORKBOOKS in the DC.

        A show_cmd_workbooks command will use the wb_ref value in the cmd. 
        Value is a number or a wb_name.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain show_cmd = 'workbooks' resulting in
            a full command key of 'show_cmd_workbooks'.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.debug(f"Start: ...")
            result = output_bdm_tree()
            return True, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion DATA_CONTEXT_show_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKBOOKS_load_cmd() command > load wb 0
    def WORKBOOKS_load_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """Model-aware: Load workbook content for one or more WORKBOOKS in the DC.

        A load_cmd_workbooks command will use the wb_ref value in the cmd. 
        Value is a number, a wb_name or ALL.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain load_cmd = 'workbooks' resulting in
            a full command key of 'load_cmd_workbooks'.

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
            logger.debug(f"Start: ...")
            bdm_wb : Optional[BDMWorkbook] = None
            wb_index : int = self.cp_cmd_attr_get(cmd, cp.CK_WB_INDEX, self.dc_WB_INDEX)
            all_wbs : bool = self.cp_cmd_attr_get(cmd, cp.CK_ALL_WBS, self.dc_ALL_WBS)
            wb_id : str = self.cp_cmd_attr_get(cmd, cp.CK_WB_ID, self.dc_WB_ID)

            wb_count = len(self.dc_WORKBOOK_DATA_COLLECTION)
            r = f"Budget Manager Workbooks({wb_count}):\n"
            # Now either all_wbs or a specific workbook is to be loaded.
            if not all_wbs:
                # WB_INDEX is already validated.
                bdm_wb = self.dc_WORKBOOK_by_index(wb_index)
                if bdm_wb is None:
                    m = f"wb_index '{wb_index}' is not valid."
                    logger.error(m)
                    return False, m
                success, result = self.dc_BDM_WORKBOOK_load(bdm_wb) 
                if not success:
                    return False, result
                # Cmd output string
                r_str = bdm_wb.wb_index_display_str(wb_index)
                r = f"{P2}Loaded {r_str}\n"
                logger.debug(f"Complete Command: 'Load' {p3u.stop_timer(st)}")   
                return success, r
            if all_wbs:
                # Load all the workbooks in the dc_WORKBOOK_DATA_COLLECTION.
                wdc = self.dc_WORKBOOK_DATA_COLLECTION
                r = f"Loading {len(wdc)} workbooks:\n"
                for wb_id, bdm_wb in wdc.items():
                    wb_index = self.dc_WORKBOOK_index(wb_id)
                    if bdm_wb is None:
                        m = f"wb_index '{wb_index}' is not valid."
                        logger.error(m)
                        return False, m
                    # Retrieve the workbook content from dc_LOADED_WORKBOOKS.
                    success, result = self.dc_BDM_WORKBOOK_load(bdm_wb) 
                    # Cmd output string
                    r_str = bdm_wb.wb_index_display_str(wb_index)
                    r = f"{P2}Loaded {r_str}\n"
                logger.debug(f"Complete Command: 'Load' {p3u.stop_timer(st)}")   
                return True, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKBOOKS_load_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKBOOKS_save_cmd() command > save wb 3
    def WORKBOOKS_save_cmd(self, cmd : Dict) -> BUDMAN_RESULT: 
        """Model-Aware: Execute save command for one WB_INDEX or ALL_WBS.
        In BudMan, loaded workbook content is maintained in the 
        dc_LOADED_WORKBOOKS collection. This command will cause that content
        to be saved to its storage location.        

        Raises:
            RuntimeError: For exceptions.
        """
        try:
            st = p3u.start_timer()  
            logger.debug(f"Start: {str(cmd)}")
            # Get the command arguments.
            bdm_wb : Optional[BDMWorkbook] = None
            wb_index : int = self.cp_cmd_attr_get(cmd, cp.CK_WB_INDEX, self.dc_WB_INDEX)
            all_wbs : bool = self.cp_cmd_attr_get(cmd, cp.CK_ALL_WBS, self.dc_ALL_WBS)
            # CK_WB_INDEX/CK_ALL_WBS are already validated.
            if all_wbs:
                # Put all the LOADED_WORKBOOK_COLLECTION from the DC to storage.
                lwbl = self.dc_LOADED_WORKBOOKS
                r = f"Saving {len(lwbl)} loaded workbooks:\n"
                # For each loaded workbook, save it to its the path .
                for wb_id, wb_content in lwbl.items():
                    wb_index = self.dc_WORKBOOK_index(wb_id)
                    bdm_wb = self.dc_WORKBOOK_DATA_COLLECTION[wb_id]
                    if bdm_wb is None:
                        m = f"wb_index '{wb_index}' is not valid."
                        r += f"{P2}Error wb_index: {wb_index:>2} wb_id: '{wb_id:<40}' Reason:{m}\n"
                        continue
                    if wb_content is None:
                        m = f"Workbook wb_id: '{wb_id}' has no loaded content."
                        logger.error(m)
                        r += f"{P2}Error wb_index: {wb_index:>2} wb_id: '{wb_id:<40}' Reason:{m}\n"
                        continue
                    # Save the workbook content.
                    success, result = self.dc_BDM_WORKBOOK_save(bdm_wb)
                    if not success:
                        m = f"Error saving wb_id: '{wb_id}': {result}"
                        logger.error(m)
                        r += f"{P2}Error wb_index: {wb_index:>2} wb_id: '{wb_id:<40}' Reason:{m}\n"
                        continue
                    r_str = bdm_wb.wb_index_display_str(wb_index)
                    r += f"{P2}Saved {result!r}\n"
                # Save the workbooks for the specified FI, WF, and WB-type.
                logger.info(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
                return True, r
            else:
                bdm_wb = self.dc_WORKBOOK_by_index(wb_index)
                if bdm_wb is None:
                    m = f"wb_index '{wb_index}' is not valid."
                    logger.error(m)
                    return False, m
                wb_id = bdm_wb.wb_id
                # Retrieve the workbook content from dc_LOADED_WORKBOOKS.
                wb_content = self.dc_LOADED_WORKBOOKS[wb_id]
                if wb_content is None:
                    m = f"Workbook content for wb_index: '{wb_index}' "
                    m += f"is not loaded. No action taken."
                    logger.error(m)
                    return False, m
                # Save the workbook content.
                success, result = self.dc_BDM_WORKBOOK_save(bdm_wb)
                if not success:
                    logger.error(f"Failed to save workbook wb_id: '{wb_id}': {result}")
                    return False, result
                # Cmd output string
                r_str = bdm_wb.wb_index_display_str(wb_index)
                r = f"{P2}Saved {r_str}\n"
                logger.debug(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
                return success, r
            # Resolve with current DC values.
            # self.recon_cmd_args_to_DC(cmd)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKBOOKS_save_cmd() command method
    # ------------------------------------------------------------------------ +
    #region CHANGE_cmd() command > wf cat 2
    def CHANGE_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Change aspects of the Data Context.

        A CHANGE_cmd command uses the wb_ref arg parameter.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. 
    
        Required cmd object attributes:
            cmd_key: 'change_cmd' 
        Optional cmd object attributes:
            cmd_name: 'change'
            subcmd_name: CV_BUDGET_CATEGORIES_SUBCMD
            subcmd_key: 'change_cmd_BUDGET_CATEGORIES'
            CK_CAT_LIST: A list of budget categories to include, len()==0 means All. 

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.info(f"Start: ...")
            if cmd[cp.CK_SUBCMD_NAME] == cp.CK_WB_TYPE:
                wb_index : int = self.cp_cmd_attr_get(cmd, cp.CK_WB_INDEX, self.dc_WB_INDEX)
                wb_type = self.cp_cmd_attr_get(cmd, cp.CK_WB_TYPE, self.dc_WB_TYPE)
                wb = self.dc_WORKBOOK_by_index(wb_index)
                if (wb):
                    # Process the change workbook command.
                    if wb_type is not None:
                        wb.wb_type = wb_type
                        result = (f"Changed workbook type to: '{wb_type}' for "
                                  f"wb_index: {wb_index:>2} wb_id: '{wb.wb_id}'")
                        return True, result
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion CHANGE_cmd() method
    # ------------------------------------------------------------------------ +
    #region APP_cmd() command > wf cat 2
    def APP_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """App commands to manipulate app values and settings.

        The APP_cmd command can use a variety of other command line arguments.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. 
    
        Required cmd object attributes:
            cmd_key: 'app_cmd' 
        Optional cmd object attributes:
            cmd_name: 'app'
            subcmd_key: 'app_cmd_delete'
            subcmd_name: CV_DELETE_SUBCMD
            subcmd_key: 'app_cmd_reload'
            subcmd_name: CV_RELOAD_SUBCMD
            subcmd_key: 'app_cmd_log'
            subcmd_name: CV_LOG_SUBCMD

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            r_msg: str = "Start:"
            m:Optional[str] = None
            logger.debug(r_msg)
            success: bool = False
            result: Any = None
            subcmd_name = cmd[cp.CK_SUBCMD_NAME]
            if subcmd_name == cp.CV_LOG_SUBCMD:
                # Show the current log level.
                return True, "App Log cmd."
            elif subcmd_name == cp.CV_RELOAD_SUBCMD_NAME:
                try:
                    reload_target = self.cp_cmd_attr_get(cmd, cp.CK_RELOAD_TARGET, None)
                    if reload_target is None:
                        m = f"reload_target is None, no action taken."
                        logger.error(m)
                        return False, m
                    if reload_target == CATEGORY_MAP:
                        catman: BDMTXNCategoryManager = BDMTXNCategoryManager() #self.WF_CATEGORY_MANAGER
                        category_catalog: TXNCategoryCatalog = None
                        if catman :
                            category_catalog = catman.catalogs[self.dc_FI_KEY]
                            category_catalog.CATEGORY_MAP_WORKBOOK_import()
                            mod = category_catalog.category_map_module
                            if mod:
                                cat_count = len(category_catalog.category_collection)
                                rule_count = len(category_catalog.category_map)
                                task = "CATEGORY_MAP_WORKBOOK_import()"
                                m = (f"{P2}Task: {task:30} {rule_count:>3} "
                                     f"rules, {cat_count:>3} categories.")
                                logger.debug(m)
                                return True, m
                            else:
                                return False, "Failed to reload category_map_module"
                        # cmc = category_map_count()
                        # m = f"Workflow reload: '{reload_target}' rule count = {cmc}\n"
                        # logger.debug(m)
                        # r_msg += f"\n{m}"
                        # clear_category_map()
                        # clear_compiled_category_map()
                        # importlib.reload(budget_category_mapping)
                        # cm = get_category_map()
                        # ccm = compile_category_map(cm)
                        # set_compiled_category_map(ccm)
                    if reload_target == FI_WORKBOOK_DATA_COLLECTION:
                        wdc: WORKBOOK_DATA_COLLECTION = None
                        wdc, m = self.model.bsm_FI_WORKBOOK_DATA_COLLECTION_resolve(self.dc_FI_KEY)
                        return True, m
                    return True, r_msg
                except Exception as e:
                    m = f"Error reloading target: {reload_target}: {p3u.exc_err_msg(e)}"
                    logger.error(m)
                    return False, m
            elif subcmd_name == cp.CV_DELETE_SUBCMD:
                try:
                    delete_target = self.cp_cmd_attr_get(cmd, cp.CK_DELETE_TARGET, -1)
                    if self.dc_WB_INDEX_validate(delete_target):
                        bdm_wb: BDMWorkbook = self.dc_WORKBOOK_remove(delete_target)
                        return True, f"Deleted workbook: {bdm_wb.wb_id}"
                    return False, f"Invalid wb_index: '{delete_target}'"
                except Exception as e:
                    m = f"Error deleting workbook: {delete_target}: {p3u.exc_err_msg(e)}"
                    logger.error(m)
                    return False, m
            else:
                return False, f"Unknown app subcmd: {subcmd_name}"
        except Exception as e:
            m = f"Error executing cmd: {cmd[cp.CK_CMD_NAME]} {cmd[cp.CK_SUBCMD_NAME]}: "
            m += p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion APP_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_categorization_cmd() command > wf cat 2
    def WORKFLOW_categorization_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """Apply categorization workflow to one or more WORKBOOKS in the DC.

        As a workflow process, the WORKFLOW_categorization_cmd method has the
        job to marshall the necessary input objects, implied by the command
        arguments and perhaps Data Context, and then invoke the appropriate 
        function or method to conduct the requested process, tasks, etc. It also
        catches the return status and result to return.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. 
    
        Required cmd object attributes:
            cmd_key: 'workflow_cmd' 
        Optional cmd object attributes:
            cmd_name: CV_WORKFLOW_CMD
            Valid subcommands:
                subcmd_key: 'workflow_cmd_categorization'
                subcmd_name: CV_DELETE_SUBCMD
            subcmd_key: 'app_cmd_reload'
            subcmd_name: CV_RELOAD_SUBCMD
            subcmd_key: 'app_cmd_log'
            subcmd_name: CV_LOG_SUBCMD

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            success : bool = False
            r : str = ""
            fr : str = f"Workflow Categorization \n"
            m : str = ""
            lwbc :LOADED_WORKBOOK_COLLECTION = None
            bdm_wb : Optional[BDMWorkbook] = None
            wb_content : Optional[WORKBOOK_CONTENT] = None
            wb_index : int = self.cp_cmd_attr_get(cmd, cp.CK_WB_INDEX, self.dc_WB_INDEX)
            all_wbs : bool = self.cp_cmd_attr_get(cmd, cp.CK_ALL_WBS, self.dc_ALL_WBS)
            load_workbook : bool = self.cp_cmd_attr_get(cmd, cp.CK_LOAD_WORKBOOK, False)
            # wb_index and all_wbs are validated already. 
            # Choose either all_wbs or a specific workbook designated by 
            # wb_index to be processed. This applies to loaded workbooks only, 
            # so configure wf_wb_list with the intended workbooks to categorize.
            if all_wbs:
                # If all_wbs, process all loaded workbooks.
                lwbc = self.dc_LOADED_WORKBOOKS
            else:
                # wb_index is already validated by cp_validate_cmd().
                bdm_wb = self.dc_WORKBOOK_by_index(wb_index)
                wb_id = bdm_wb.wb_id
                # bdm_wb.wb_loaded = wb_id in self.dc_LOADED_WORKBOOKS
                if not bdm_wb.wb_loaded:
                    if load_workbook:
                        # Load the workbook content for the wb_id.
                        task = "dc_BDM_WORKBOOK_load()"
                        m = (f"{P2}Task: {task:30} {wb_index:>2} '{wb_id:<40}'")
                        logger.debug(m)
                        fr += m + "\n"
                        success, m = self.dc_BDM_WORKBOOK_load(bdm_wb)
                        if not success:
                            m = (f"{P4}Task Failed: dc_BDM_WORKBOOK_load() "
                                 f"wb_id: '{wb_id}'\n{P8}Result: {m}")
                            logger.error(m)
                            return False, m
                    else:
                        m = f"Workbook: '{bdm_wb.wb_id}' is not loaded, no action taken."
                        logger.error(m)
                        return False, m
                # Obtain the wb_content for wb_id.
                # wb_content = self.dc_LOADED_WORKBOOKS[wb_id]
                # add the single wb to the process list.
                lwbc = {wb_id: bdm_wb.wb_content}
            # Process the intended workbooks.
            for wb_id, wb_content in lwbc.items():
                bdm_wb = self.dc_WORKBOOK_DATA_COLLECTION[wb_id]
                wb_index = self.dc_WORKBOOK_index(wb_id)
                self.dc_BDM_WORKBOOK = bdm_wb
                self.dc_WB_INDEX = wb_index  # Set the wb_index in the DC.
                # if bdm_wb.wb_type == WB_TYPE_CHECK_REGISTER:
                    # Check for a check register column, add it if not present.
                    # load the check register here
                    # check_register_dict = csv_DATA_COLLECTION_url_get(wb_url)
                    # apply_check_register(ws)
                if bdm_wb.wb_type == WB_TYPE_EXCEL_TXNS:
                    task = "process_budget_category()"
                    m = (f"{P2}Task: {task:30} {wb_index:>2} '{wb_id:<40}'")
                    logger.debug(m)
                    fr += m + "\n"
                    success, r = process_budget_category(bdm_wb, self.DC)
                    if not success:
                        r = (f"{P4}Task Failed: process_budget_category() Workbook: "
                             f"'{wb_id}'\n{P8}Result: {r}")
                        logger.error(r)
                        fr += r + "\n"
                        continue
                    task = "dc_WORKBOOK_content_put()"
                    m = (f"{P2}Task: {task:30} {wb_index:>2} '{wb_id:<40}'")
                    logger.debug(m)
                    fr += m + "\n"
                    success, m = self.dc_BDM_WORKBOOK_save(bdm_wb)
                    if not success:
                        m = (f"{P4}Task Failed: dc_BDM_WORKBOOK_save() Workbook: "
                             f"'{wb_id}'\n{P8}Result: {m}")
                        logger.error(m)
                        fr += m + "\n"
                        continue
                    fr += f"{P8}Result: {r}\n"
            logger.info(m)
            return True, fr
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_categorization_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_apply_cmd() command > wf cat 2
    def WORKFLOW_apply_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """Apply workflow tasks to WORKBOOKS.

        A WORKFLOW_apply_cmd command will use the wb_ref value in the cmd. 
        Value is a number or a wb_name.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain workflow_cmd = 'apply' resulting in
            a full command key of 'workflow_cmd_apply'.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.info(f"Start: ...")
            r_msg: str = "Start:"
            m:Optional[str] = None
            logger.debug(r_msg)
            success: bool = False
            result: Any = None
            subcmd_name = cmd[cp.CK_SUBCMD_NAME]
            if subcmd_name == cp.CV_APPLY_SUBCMD_NAME:
                # Update the txn_categories by apply the category_map.
                return True, "Applied category_map to txn_categories."
            return True, ""
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_apply_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_intake_cmd() command > wf cat 2
    def WORKFLOW_intake_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Execute workflow intake tasks.

        A WORKFLOW_intake_cmd command processes workbooks that have just
        arrived.

        Tasks:
            1. Load a new csv_txns workbook.
            2. Convert to excel_txns workbook.
            3. Validate columns.
            4. Save the workbook.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. 
    
        Required cmd object attributes:
            cmd_key: CV_WORKFLOW_CMD_KEY 
        Optional cmd object attributes:
            cmd_name: CV_WORKFLOW_CMD
            subcmd_key: CV_INTAKE_SUBCMD_KEY
            subcmd_name: CV_INTAKE_SUBCMD

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.debug(f"Start: process_txn_intake...")
            return process_txn_intake(cmd, self.DC)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_intake_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_check() command > wf check 2 
    def WORKFLOW_check_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """Apply workflow to one or more WORKBOOKS in the DC.

        A WORKFLOW_categorization_cmd command will use the wb_ref value in the cmd. 
        Value is a number or a wb_name.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain workflow_cmd = 'categorization' resulting in
            a full command key of 'workflow_cmd_categorization'.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.info(f"Start: ...")
            bdm_wb: BDMWorkbook
            wb_index : int = self.cp_cmd_attr_get(cmd, cp.CK_WB_INDEX, self.dc_WB_INDEX)
            wb_list : List[int] = cmd.get(cp.CK_WB_LIST, [])
            all_wbs : bool = self.cp_cmd_attr_get(cmd, cp.CK_ALL_WBS, self.dc_ALL_WBS)
            selected_bdm_wb_list : List[BDMWorkbook] = []
            load:bool = cmd[cp.CK_LOAD_WORKBOOK]
            if all_wbs:
                # If all_wbs is True, process all workbooks in the data context.
                return False, "method not implemented for all_wbs=True"
            if len(wb_list) > 0:
                for wb_index in wb_list:
                    bdm_wb = self.dc_WORKBOOK_by_index(wb_index)
                    selected_bdm_wb_list.append(bdm_wb)
            else:
                selected_bdm_wb_list.append(self.dc_WORKBOOK_by_index(wb_index))
    
            for bdm_wb in selected_bdm_wb_list:
                if bdm_wb is None:
                    m = f"wb_index '{wb_index}' is not valid, no action taken."
                    logger.error(m)
                    return False, m 
                if bdm_wb is None:
                    m = f"wb_index '{wb_index}' is not valid, no action taken."
                    logger.error(m)
                    return False, m
                bdm_wb_abs_path = bdm_wb.abs_path()
                if bdm_wb_abs_path is None:
                    m = f"Workbook path is not valid: {bdm_wb.wb_url}"
                    logger.error(m)
                    return False, m
                if load and not bdm_wb.wb_loaded:
                    # Load the workbook content if it is not loaded.
                    success, wb_content = self.dc_WORKBOOK_content_get(bdm_wb)
                    if not success:
                        m = f"Failed to load workbook '{bdm_wb.wb_id}': {wb_content}"
                        logger.error(m)
                        return False, m
                    bdm_wb.wb_loaded = True
                    self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id] = wb_content
                # Check cmd needs loaded workbooks to check
                if not bdm_wb.wb_loaded:
                    m = f"wb_name '{bdm_wb.wb_name}' is not loaded, no action taken."
                    logger.error(m)
                    return False, m
                wb_content = self.dc_LOADED_WORKBOOKS[bdm_wb.wb_id]
                # By default, check the sheet schema. But other cli switches
                # can added to check something else.
                if cmd[cp.CK_VALIDATE_CATEGORIES]:
                    # Validate the categories in the workbook.
                    task = "validate_budget_categories()"
                    m = (f"{P2}Task: {task:30} {bdm_wb.wb_index_display_str(wb_index)}")
                    logger.debug(m)
                    success, result = validate_budget_categories(bdm_wb, self.DC)
                    return success, result
                success: bool = check_sheet_schema(wb_content)
                r = f"Task: check_sheet_schema workbook: Workbook: '{bdm_wb.wb_id}' "
                if success:
                    return success, r
                if cmd[cp.CK_FIX_SWITCH]:
                    r = f"Task: check_sheet_columns workbook: Workbook: '{bdm_wb.wb_id}' "
                    ws = wb_content.active
                    success = check_sheet_columns(ws, add_columns=True)
                    if success: 
                        wb_content.save(bdm_wb_abs_path)
            return success, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_check_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_reload_cmd() command > wf check 3
    def WORKFLOW_reload_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Reload code modules to support dev.

        A WORKFLOW_reload_cmd command uses the reload_target value in the cmd. 
        Value is a module name string or 'all'.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain workflow_cmd = 'reload' resulting in
            a full command key of 'workflow_cmd_reload'.

        Returns:
            Tuple[success : bool, result : Any]: The outcome of the command 
            execution. If success is True, result contains result of the 
            command, if False, a description of the error.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
    #endregion WORKFLOW_reload_cmd() method
    # ------------------------------------------------------------------------ +
    #region UNKNOWN_cmd() command > wf cat 2
    def UNKNOWN_cmd(self, cmd : Dict) -> BUDMAN_RESULT:
        """A cmd received that is not found in the current cmd map.

        A CHANGE_cmd command uses the wb_ref arg parameter.

        Arguments:
            cmd (Dict): A BudManCommand object. 

        Returns:
            BUDMAN_RESULT:Tuple[success : bool, result : Any]: 
            success: False, Result: message about the cmd object content.
            
        Raises:
            RuntimeError: A description of the
            root error is contained in the exception message.
        """
        try:
            logger.info(f"Start: ...")
            func_name = self.UNKNOWN_cmd.__name__
            result = f"{func_name}(): Received unknown cmd object: {str(cmd)})"
            logger.warning(result)
            return False, result
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion CHANGE_cmd() method
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region    helper methods for command execution
    # ------------------------------------------------------------------------ +
    #region get_workbook_data_collection_info_str() method
    def get_workbook_data_collection_info_str(self) -> BUDMAN_RESULT: 
        """Construct an outout string with information about the WORKBOOKS."""
        try:
            logger.debug(f"Start: ...")
            # Be workbook-centric is this view of the DC
            wdc = self.dc_WORKBOOK_DATA_COLLECTION
            wdc_count = len(wdc) if wdc else 0
            lwbc = self.dc_LOADED_WORKBOOKS

            # Prepare the output result
            result = f"{P2}{FI_WORKBOOK_DATA_COLLECTION}: {wdc_count}\n"
            result += f"{P4}{WB_INDEX:6}{P2}{WB_ID:50}{P2}"
            result += f"{WB_TYPE:15}{P2}{WB_CONTENT:30}"
            # print(result)
            result += "\n"
            wb : BDMWorkbook = None
            if wdc_count > 0:
                for i, wb in enumerate(wdc.values()):
                    wb.wb_loaded = wb.wb_id in lwbc
                    r = f"{wb.wb_index_display_str(i)}"
                    result += r + "\n"
            logger.info(f"Complete:")
            return True, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion get_workbook_data_collection_info_str() method
    # ------------------------------------------------------------------------ +
    #region    wb_ref_not_valid() method
    def recon_cmd_args_to_DC(self, cmd: dict) -> bool:
        """Reconcile.

        Arguments:
            cmd: reconcile the args in cmd with the DC state values

        Returns:
            bool: 
        """
        # Get the command arguments.
        wb_index : int = self.cp_cmd_attr_get(cmd, cp.CK_WB_INDEX, self.dc_WB_INDEX)
        all_wbs : bool = self.cp_cmd_attr_get(cmd, cp.CK_ALL_WBS, self.dc_ALL_WBS)
        wb_ref : str = self.cp_cmd_attr_get(cmd, cp.CK_WB_REF, self.dc_WB_ID)
        # Get the command arguments.
        fi_key = cmd.get(cp.CK_FI_KEY, None)
        wf_key = cmd.get(cp.CK_WF_KEY, BDM_WF_CATEGORIZATION)
        wf_purpose = cmd.get(cp.CK_WF_PURPOSE, WF_INPUT)
        wb_type = cmd.get(cp.CK_WB_TYPE, WB_TYPE_EXCEL_TXNS)
        wb_name = cmd.get("wb_name", None)
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
        return True
    #endregion wb_ref_not_valid() method
    # ------------------------------------------------------------------------ +
    #region    wb_ref_not_valid() method
    @classmethod
    def wb_ref_not_valid(cls, all_wbs: bool, wb_index: int, wb_name: str) -> bool:
        """Check if the workbook reference is not valid.

        Arguments:
            all_wbs (bool): True if all workbooks are to be processed.
            wb_index (int): The index of the workbook.
            wb_name (str): The name of the workbook.

        Returns:
            bool: True if the workbook reference is not valid, False otherwise.
        """
        if not all_wbs and wb_index == -1 and wb_name is None:
            m = f"wb_ref '{wb_ref}' is not valid."
            logger.error(m)
            return True
        return False
    #endregion wb_ref_not_valid() method
    # ------------------------------------------------------------------------ +
    #endregion helper methods for command execution
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion Command Execution Methods                                       +
    # ======================================================================== +
 
    # ======================================================================== +
    #region    Model_Binding to BudgetDomainModel                              + 
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region    Model_Binding Properties                                        +
    @property
    def budget_domain_model(self) -> BudgetDomainModel:
        """Return the BudgetModel instance."""
        return self._budget_domain_model
    @budget_domain_model.setter
    def budget_domain_model(self, value: BudgetDomainModel) -> None:
        """Set the BudgetModel instance."""
        if not isinstance(value, BudgetDomainModel):
            raise ValueError("budget_model must be a BudgetModel instance.")
        self._budget_domain_model = value

    @property
    def model(self) -> Model_Base:
        """Return the model object reference."""
        return self._budget_domain_model
    @model.setter
    def model(self, bdm: Model_Base) -> None:
        """Set the model object reference."""
        if not isinstance(bdm, Model_Base):
            raise TypeError("model must be a BDMBaseInterface instance")
        self._budget_domain_model = bdm
    #endregion Model_Binding Properties                                        +
    #endregion ViewModelDataContext_Binding to BudManDataContext               +
    # ======================================================================== +
