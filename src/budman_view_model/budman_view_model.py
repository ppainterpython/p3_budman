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
import logging, sys, getpass, time, copy, importlib
from pathlib import Path
from typing import List, Type, Optional, Dict, Tuple, Any, Callable
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from dynaconf import Dynaconf
from openpyxl import Workbook, load_workbook
# local modules and packages
from p3_mvvm import (Model_Base, Model_Binding)
from budman_settings import *
from budman_namespace.design_language_namespace import *
from budman_namespace.bdm_workbook_class import BDMWorkbook
from budman_workflows import (
    category_map_count, check_sheet_columns,
    check_sheet_schema,process_budget_category,
    apply_check_register, get_category_histogram
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
# BudMan Command Processor Argument Name Constants
# argparse converts hyphens '-' to underscores '_', so we use underscores
CMD_KEY_SUFFIX = "_cmd"
CMD_NAME = "cmd_name"
CMD_SUBCMD = "sub_cmd"
CMD_PARSE_ONLY = "parse_only"
CMD_VALIDATE_ONLY = "validate_only"
CMD_WHAT_IF = "what_if"
CMD_FI_KEY = "fi_key"
CMD_WF_KEY = "wf_key"
CMD_WF_PURPOSE = "wf_purpose"
CMD_WB_TYPE = "wb_type"
CMD_WB_NAME = "wb_name"
CMD_WB_INDEX = "wb_index"
CMD_ALL_WBS = "all_wbs"
CMD_WB_REF = "wb_ref"
CMD_WB_INFO = "wb_info"
CMD_CHECK_REGISTER = "check_register"
CMD_WF_TASK = "wf_task"
CMD_TASK_ARGS = "task_args"
CMD_TASK_NAME = "task_name"
CMD_HANDLER_NAME = "handler_name"
CMD_LIST_SWITCH = "list_switch" 
CMD_LEVEL_VALUE = "level_value"
CMD_ROLLOVER_SWITCH = "rollover_switch"
BUDMAN_VALID_CMD_ARGS = (CMD_PARSE_ONLY, CMD_VALIDATE_ONLY,
                        CMD_WHAT_IF, CMD_FI_KEY, CMD_WF_KEY,CMD_WF_PURPOSE,
                        CMD_WB_TYPE, CMD_WB_NAME, CMD_WB_REF,CMD_WB_INFO,
                        CMD_CHECK_REGISTER,CMD_HANDLER_NAME,CMD_LIST_SWITCH,
                        CMD_LEVEL_VALUE, CMD_ROLLOVER_SWITCH,CMD_WB_INDEX, 
                        CMD_ALL_WBS)

logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
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
    def __init__(self, bdms_url : str = None, settings : Dynaconf = None) -> None:
        super().__init__()
        self._bdm_store_url : str = bdms_url
        self._settings = settings
        self._initialized : bool = False
        self._BDM_STORE_loaded : bool = False
        self._budget_domain_model : BudgetDomainModel = None
        self._cmd_map : Dict[str, Callable] = None
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
    def settings(self) -> Dynaconf:
        """Return the application settings."""
        return self._settings
    @settings.setter
    def settings(self, settings: Dynaconf) -> None:
        """Set the application settings."""
        if not isinstance(settings, Dynaconf):
            raise TypeError("settings must be a Dynaconf instance")
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
                bdmc : BDMConfig= BDMConfig.BDM_STORE_url_load(self.bdms_url)
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
                "load_cmd_check_register": self.CHECK_REGISTER_load_cmd,
                "change_cmd": self.CHANGE_cmd,
                "change_cmd_workbooks": self.CHANGE_cmd,
                "workflow_cmd_categorization": self.WORKFLOW_categorization_cmd,
                "workflow_cmd_reload": self.WORKFLOW_reload_cmd,
                "workflow_cmd_apply": self.WORKFLOW_apply_cmd,
                "workflow_cmd_check": self.WORKFLOW_check_cmd,
                "workflow_cmd_task": self.WORKFLOW_task_cmd,
                "app_cmd_log_subcmd": self.APP_cmd
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
      Optional[str] value.
    - A sub-command is given as a value to the cmd_key, but may be None.
    - A second key in the cmd dict is 'command_name' with the value being the 
      command name string, e.g., 'init', 'load', 'save', etc.
    - A third key used in a valid cmd dict object is 'full_cmd_key' with a 
      string value constructed as" <cmd_key>_<sub_command_value>".

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
            validate_only: bool = self.cp_cmd_arg_get(cmd,CMD_VALIDATE_ONLY)
            full_cmd_key = result
            # TODO: create cp_cmd_func_get(full_cmd_key) with UNKNOWN_cmd()
            func = self.cp_cmd_map.get(full_cmd_key)
            function_name = func.__name__
            if validate_only:
                result = f"vo-command: {function_name}({str(cmd)})"
                logger.info(result)
                return True, result
            logger.info(f"Executing command: {function_name}({str(cmd)})")
            status, result = self.cp_cmd_map.get(full_cmd_key)(cmd)
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
                        validate_all : bool = False) -> Tuple[bool, str]:
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
        my_prefix = f"{self.__class__.__name__}.{self.cp_validate_cmd_object.__name__}: "
        try:
            self.cp_validate_cmd_object(cmd, my_prefix, raise_error = True)
            # After cp_validate_cmd_object() returns, cmd dict has 
            # content to examine and validate.
            # For a few args, apply the DC values if no value given in the cmd.
            if self.cp_cmd_arg_get(cmd, CMD_FI_KEY) is None:
                self.cp_cmd_arg_set(cmd, CMD_FI_KEY,
                                    self.dc_FI_KEY)
            if self.cp_cmd_arg_get(cmd, CMD_WF_KEY) is None:
                self.cp_cmd_arg_set(cmd, CMD_WF_KEY,
                                    self.dc_WF_KEY)
            validate_all: bool = self.cp_cmd_arg_get(cmd,CMD_VALIDATE_ONLY)
            # If validate_all, then don't return a result until all cmd args 
            # are validated.
            all_results : str = "All Results:\n" if validate_all else ""
            result = "It's all good." 
            if validate_all:
                all_results = f"Command validation info: \n{P2}cmd: {str(cmd)}\n"
            
            # Validation Step 1: Extract the full_cmd_key/cmd_key  
            # from the cmd. A full_cmd_key will include the cmd_key and a
            # possible sub-command value, or full_cmd_key can equal the cmd_key.
            success, full_cmd_key, cmd_key = self.cp_full_cmd_key(cmd)
            if not success:
                result = f"Error: cmd_key: '{str(cmd_key)}' "
                result += f"'{str(full_cmd_key)}' not in cmd_map."
                if not validate_all:
                    logger.warning(result)
                    return False, result
                else:
                    # accumulate msgs, validate all cmd args
                    success = False
            # Validate the cmd arguments.
            for key, value in cmd.items():
                if key == cmd_key: 
                    continue
                elif key == CMD_WB_INDEX:
                    if cmd[CMD_ALL_WBS] and value == -1:
                        # If all_wbs is True, then wb_index is not used.
                        continue
                    elif not self.dc_WB_INDEX_validate(value):
                        result = f"Invalid wb_index value: '{value}'."
                        success = False 
                        logger.error(result)
                    continue
                elif key == CMD_FI_KEY:
                    if not self.dc_FI_KEY_validate(value):
                        result = f"Invalid fi_key value: '{value}'."
                        success = False 
                        logger.error(result)
                    continue
                elif key == CMD_WB_NAME: 
                    continue
                elif key == CMD_WF_KEY:
                    if not self.dc_WF_KEY_validate(value):
                        result = f"Invalid wf_key value: '{value}'."
                        success = False 
                        logger.error(result)
                    if value == ALL_KEY:
                        logger.warning(f"wf_key: '{ALL_KEY}' not implemented."
                                    f" Defaulting to {BDM_WF_CATEGORIZATION}.")
                        cmd[key] = BDM_WF_CATEGORIZATION
                    continue
                elif key == CMD_WB_REF:
                    if not self.dc_WB_REF_validate(value):
                        result = f"Invalid wb_ref level: '{value}'."
                        success = False 
                        logger.error(result)
                elif key == CMD_WB_INFO:
                    if not self.BMVM_cmd_WB_INFO_LEVEL_validate(value):
                        result = f"Invalid wb_info level: '{value}'."
                        success = False 
                        logger.error(result)
                elif key == CMD_PARSE_ONLY: 
                    po = cmd.get(CMD_PARSE_ONLY, False)
                    continue
                elif key == CMD_VALIDATE_ONLY: 
                    vo = cmd.get(CMD_VALIDATE_ONLY, False)
                    continue
                elif key == CMD_WHAT_IF: 
                    what_if = cmd.get(CMD_WHAT_IF, False)
                    continue
                elif key == CMD_CHECK_REGISTER:
                    continue
                else:
                    if key not in BUDMAN_VALID_CMD_ARGS:
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
                logger.info(f"Command validated - full_cmd_key: '{full_cmd_key}' cmd: {str(cmd)}")
                return success, full_cmd_key # The happy path return 
            if validate_all:
                return success, all_results
            return success, result
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_validate_cmd() Command Processor method
    #region cp_validate_cmd_object() Command Processor method
    def cp_validate_cmd_object(self, 
                               cmd : Dict = None,
                               prefix: str = None,
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
        my_prefix = f"{self.__class__.__name__}.{self.cp_validate_cmd_object.__name__}: "
        pfx = prefix if prefix else my_prefix
        try:
            if not self.initialized:
                m = f"{pfx} Command Processor is not initialized."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                cmd_type = type(cmd).__name__
                m = f"{pfx}Invalid cmd object type: '{cmd_type}', no action taken."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            if len(cmd) == 0:
                m = f"{pfx}Command object is empty, no action taken."
                logger.error(m)
                if raise_error:
                    raise RuntimeError(m)
                return False
            return True
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_validate_cmd_object() Command Processor method
    #region cp_cmd_key() Command Processor method
    def cp_cmd_key(self, cmd : Dict = None) -> BUDMAN_RESULT:
        """Extract a cmd_key is present in the cmd, return it.

        A cmd_key is a key in the cmd dictionary that ends with 
        CMD_ARG_CMD_KEY_SUFFIX, which is typically set to "_cmd". If an 
        arg key matches this suffix, it is considered a command key.
        If no cmd_key is found, an error message is returned.
                
        returns:
            BUDMAN_RESULT(Tuple[success: bool, result: str]): 
                success = True: result = cmd_key value that was detected.
                success = False: result = an error message. No cmd_key detected.
        """
        try:
            # Check if the cmd contains a valid cmd_key.
            cmd_key = next((key for key in cmd.keys() 
                            if CMD_KEY_SUFFIX in key), None)
            if p3u.str_empty(cmd_key):
                m = f"No command key found in cmd: {str(cmd)}"
                logger.error(m)
                return False, m
            # Success, return the cmd_key.
            return True, cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_cmd_key() Command Processor method
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
            result : str = cmd_key[:-4] if cmd_key.endswith(CMD_KEY_SUFFIX) else cmd_key
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
    #region cp_full_cmd_key() Command Processor method
    def cp_full_cmd_key(self, cmd : Dict = None) -> Tuple[bool, str, str]:
        """Extract a full cmd key with subcommand if included.

        First, check for a cmd_key arg key. If it exists, the subcmd will be
        its value. A full_cmd_key is constructed by combining the cmd_key and
        the sub_cmd value inserting an underscore '_' om between. If no subcmd
        is found, but a cmd_key is, then the cmd_key and the full_cmd_key are
        the same.

                
        returns:
            Tuple[success: bool, full_cmd_key: str, cmd_key: str|None]: 
                A tuple of 3 values indicating success or failure. 
                success = True: 
                    The full_cmd_key exists in the cmd_map.
                    full_cmd_key, cmd_key values are returned.
                    If full_cmd_key == cmd_key, no subcmd was detected.
                success = False: 
                    No match in cmd_map for full_cmd_key.
                    full_cmd_key, cmd_key values returned, may be the same.
                    If full_cmd_key or cmd_key are None, no values were detected.
                    If success is False, cmd_key is not Null, and full_cmd_key
                    is None, then a cmd_key was detected, but is not in the
                    cmd_map.
               
        """
        try:
            success : bool = False 
            full_cmd_key : str = None
            # Extract a cmd key from the cmd, or error out.
            success, result = self.cp_cmd_key(cmd)
            if not success: return False, result, None
            cmd_key = result
            # Acquire sub-command key if present.
            sub_cmd = cmd[cmd_key]
            # Construct full_cmd_key from cmd_key and sub_cmd (may be None).
            # If no sub_cmd, use cmd_key as full_cmd_key.
            full_cmd_key = cmd_key + '_' + sub_cmd if p3u.str_notempty(sub_cmd) else cmd_key
            # Validate the full_cmd_key against the command map.
            if full_cmd_key not in self.cp_cmd_map:
                m = f"Command key '{full_cmd_key}' not found in the command map."
                logger.error(m)
                success = False
            return success, full_cmd_key, cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_full_cmd_key() Command Processor method
    #region cp_cmd_arg_get() Command Processor method
    def cp_cmd_arg_get(self, cmd: Dict,
                       arg_name: str, default_value: Any = None) -> Any:
        """Get a command argument value from the cmd dictionary."""                  
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")    
        if not isinstance(arg_name, str):
            raise TypeError("arg_name must be a string.")
        if arg_name not in cmd:
            return default_value
        value = cmd.get(arg_name, default_value)
        if value is None:
            return default_value
        return value
    #endregion cp_cmd_arg_get() Command Processor method
    #region cp_cmd_arg_set() Command Processor method
    def cp_cmd_arg_set(self, cmd: Dict,
                       arg_name: str, value: Any) -> None:
        """Set a command argument value in the cmd dictionary."""
        if not isinstance(cmd, dict):
            raise TypeError("cmd must be a dictionary.")
        if not isinstance(arg_name, str):
            raise TypeError("arg_name must be a string.")
        if arg_name not in BUDMAN_VALID_CMD_ARGS:
            raise ValueError(f"Command argument '{arg_name}' is not a valid "
                             f"BudMan command argument. Valid arguments are: "
                             f"{BUDMAN_VALID_CMD_ARGS}")
        if not isinstance(value, (str, int, float, bool)):
            raise TypeError(f"Command argument '{arg_name}' must be a string, "
                            f"int, float, or bool, not {type(value)}.")
        # Set the value in the cmd dictionary.
        cmd[arg_name] = value
    #endregion cp_cmd_arg_set() Command Processor method
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
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            result = "no result"
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            fi_key = cmd.get(CMD_FI_KEY, None)
            wf_key = cmd.get(CMD_WF_KEY, BDM_WF_CATEGORIZATION)
            wf_purpose = cmd.get(CMD_WF_PURPOSE, WF_WORKING)
            wb_type = cmd.get(CMD_WB_TYPE, WF_WORKING)
            wb_name = cmd.get(CMD_WB_NAME, None)
            # TODO: Enable defaults for fi_key, wf_key, wb_type, wb_name in
            # settings.toml
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
                _ = self.dc_FI_KEY_validate(fi_key)
                # _ = self.budget_domain_model.bdm_FI_KEY_validate(fi_key)
            except ValueError as e:
                m = f"ValueError({str(e)})"
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            # Load the workbooks for the FI,WF specified in the DC.
            lwbl = self.DC.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
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
            budget_model_dict = self.budget_domain_model.to_dict()
            # Save the BDM_STORE file.
            bdm_url = self.dc_BDM_STORE[BDM_URL]
            bsm_BDM_STORE_url_put(budget_model_dict, bdm_url)
            logger.info(f"Saved BDM_STORE url: {bdm_url}")
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, budget_model_dict
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
            # Be workbook-centric is this view of the DC
            wdc = self.dc_WORKBOOK_DATA_COLLECTION
            wdc_count = len(wdc) if wdc else 0
            lwbc = self.dc_LOADED_WORKBOOKS
            lwbc_count = len(lwbc) if lwbc else 0
    
            # Prepare the Command output result
            result = f"Budget Manager Data Context:\n"
            result += f"{P2}{DC_BDM_STORE}: {bs_str}\n"
            result += (f"{P2}{DC_INITIALIZED}: {self.dc_INITIALIZED}"
                        f"{P2}{FI_KEY}: {self.dc_FI_KEY}"
                        f"{P2}{WF_KEY}: {self.dc_WF_KEY}"
                        f"{P2}{WF_PURPOSE}: {self.dc_WF_PURPOSE}\n")
            result += (f"{P2}{WB_REF}: {self.dc_WB_REF}"
                        f"{P2}{WB_INDEX}: {self.dc_WB_INDEX}"
                        f"{P2}{WB_NAME}: {self.dc_WB_NAME}"
                        f"{P2}{WB_TYPE}: {self.dc_WB_TYPE}\n")
            success, wdc_result = self.get_workbook_data_collection_info_str()
            result += wdc_result
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, result
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion DATA_CONTEXT_show_cmd() method
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
            wb_ref = self.cp_cmd_arg_get(cmd, WB_REF, self.dc_WB_REF)
            fi_key = self.cp_cmd_arg_get(cmd, FI_KEY, self.dc_FI_KEY)
            wf_key = self.cp_cmd_arg_get(cmd, WF_KEY, self.dc_WF_KEY)
            wf_purpose = self.cp_cmd_arg_get(cmd, WF_PURPOSE, self.dc_WF_PURPOSE)
            wb_type = self.cp_cmd_arg_get(cmd, WB_TYPE, self.dc_WB_TYPE)
            all_wbs, wb_index, wb_name = self.dc_WB_REF_resolve(wb_ref)
            # Check for an invalid wb_ref value.
            if BudManViewModel.wb_ref_not_valid(all_wbs, wb_index, wb_name):
                return False, f"wb_ref '{wb_ref}' is not valid."
            wb_count = len(self.dc_WORKBOOK_DATA_COLLECTION)
            result = f"Budget Manager Workbooks({wb_count}):\n"
            # Now either all_wbs or a specific workbook is to be loaded.
            if all_wbs:
                success, wdc_result = self.get_workbook_data_collection_info_str()
                result += wdc_result
            else:
                wb : BDMWorkbook = None
                success, wb, _ = self.get_workbook(wb_ref, load=False) 
                if not success:
                    return False, f"Error getting workbook '{wb_ref}': {wb}"
                l = "Yes" if wb.wb_loaded else "No "
                result += f"{P2}{wb_index:>2} {l} {wb.wb_name} '{wb.wb_url}'\n"
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
            wb : Optional[WORKBOOK_OBJECT] = None
            wb_index : int = self.cp_cmd_arg_get(cmd, CMD_WB_INDEX, self.dc_WB_INDEX)
            all_wbs : bool = self.cp_cmd_arg_get(cmd, CMD_ALL_WBS, self.dc_ALL_WBS)
            wb_ref : str = self.cp_cmd_arg_get(cmd, WB_REF, self.dc_WB_REF)

            wb_count = len(self.dc_WORKBOOK_DATA_COLLECTION)
            r = f"Budget Manager Workbooks({wb_count}):\n"
            # Now either all_wbs or a specific workbook is to be loaded.
            if not all_wbs:
                # WB_INDEX is already validated.
                wb = self.dc_WORKBOOK_by_index(wb_index)
                if wb is None:
                    m = f"wb_index '{wb_index}' is not valid."
                    logger.error(m)
                    return False, m
                success, result = self.dc_WORKBOOK_content_get(wb) 
                # Cmd output string
                r_str = self.get_wb_content_repr(result)
                r = f"{P2}Loaded wb_index: {wb_index:>2} wb_id: '{wb.wb_id:<40}' {r_str}\n"
                logger.debug(f"Complete Command: 'Load' {p3u.stop_timer(st)}")   
                return success, r
            if all_wbs:
                # Load all the workbooks in the dc_WORKBOOK_DATA_COLLECTION.
                wdc = self.dc_WORKBOOK_DATA_COLLECTION
                r = f"Loading {len(wdc)} workbooks:\n"
                for wb_id, wb in wdc.items():
                    wb_index = self.dc_WORKBOOK_index(wb_id)
                    if wb is None:
                        m = f"wb_index '{wb_index}' is not valid."
                        logger.error(m)
                        return False, m
                    # Retrieve the workbook content from dc_LOADED_WORKBOOKS.
                    success, result = self.dc_WORKBOOK_content_get(wb) 
                    # Cmd output string
                    r_str = self.get_wb_content_repr(result)
                    r = f"{P2}Loaded wb_index: {wb_index:>2} wb_id: '{wb.wb_id:<40}' {r_str}\n"
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
            wb : Optional[WORKBOOK_OBJECT] = None
            wb_index : int = self.cp_cmd_arg_get(cmd, CMD_WB_INDEX, self.dc_WB_INDEX)
            all_wbs : bool = self.cp_cmd_arg_get(cmd, CMD_ALL_WBS, self.dc_ALL_WBS)
            # CMD_WB_INDEX/CMD_ALL_WBS are already validated.
            if all_wbs:
                # Put all the LOADED_WORKBOOK_COLLECTION from the DC to storage.
                lwbl = self.dc_LOADED_WORKBOOKS
                r = f"Saving {len(lwbl)} loaded workbooks:\n"
                # For each loaded workbook, save it to its the path .
                for wb_id, wb_content in lwbl.items():
                    wb_index = self.dc_WORKBOOK_index(wb_id)
                    wb = self.dc_WORKBOOK_DATA_COLLECTION[wb_id]
                    if wb is None:
                        m = f"wb_index '{wb_index}' is not valid."
                        logger.error(m)
                        return False, m
                    if wb_content is None:
                        m = f"Workbook wb_id: '{wb_id}' has no loaded content."
                        logger.error(m)
                        r += f"{P2}Error wb_index: {wb_index:>2} wb_id: '{wb_id:<40}' Reason:{m}\n"
                        continue
                    # Save the workbook content.
                    success, result = self.dc_WORKBOOK_content_put(wb_content, wb)
                    if not success:
                        m = f"Error saving wb_id: '{wb_id}': {result}"
                        logger.error(f"Failed to save wb_id: '{wb_id}': {result}")
                        r += f"{P2}Error wb_index: {wb_index:>2} wb_id: '{wb_id:<40}' Reason:{m}\n"
                        continue
                    r_str = self.get_wb_content_repr(wb_content)
                    r += f"{P2}Saved wb_index: {wb_index:>2} wb_id: '{wb_id:<40}' wb_content: {result!r}\n"
                # Save the workbooks for the specified FI, WF, and WB-type.
                logger.info(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
                return True, r
            else:
                wb = self.dc_WORKBOOK_by_index(wb_index)
                if wb is None:
                    m = f"wb_index '{wb_index}' is not valid."
                    logger.error(m)
                    return False, m
                wb_id = wb.wb_id
                # Retrieve the workbook content from dc_LOADED_WORKBOOKS.
                wb_content = self.dc_LOADED_WORKBOOKS[wb_id]
                if wb_content is None:
                    m = f"Workbook content for wb_index: '{wb_index}' "
                    m += f"is not loaded. No action taken."
                    logger.error(m)
                    return False, m
                # Save the workbook content.
                success, result = self.dc_WORKBOOK_content_put(wb_content, wb)
                if not success:
                    logger.error(f"Failed to save workbook wb_id: '{wb_id}': {result}")
                    return False, result
                # Cmd output string
                r_str = self.get_wb_content_repr(wb_content)
                r = f"{P2}Saved wb_index: {wb_index:>2} wb_id: '{wb.wb_id:<40}' {r_str}\n"
                logger.debug(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
                return success, r
            # Resolve with current DC values.
            # self.recon_cmd_args_to_DC(cmd)
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKBOOKS_save_cmd() command method
    # ------------------------------------------------------------------------ +
    #region CHECK_REGISTER_load_cmd() command > load wb 0
    def CHECK_REGISTER_load_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Model-aware: Load one or more CHECK_REGISTER .csv files in the DC.

        A load_cmd_check_register command will use the wb_ref value in the cmd. 
        Value is a number or a wb_name.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain load_cmd = 'check_register' resulting in
            a full command key of 'load_cmd_check_register'.

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
            wb_ref = self.cp_cmd_arg_get(cmd, CMD_WB_REF, self.dc_WB_REF)
            fi_key = self.cp_cmd_arg_get(cmd, CMD_FI_KEY, self.dc_FI_KEY)
            wf_key = self.cp_cmd_arg_get(cmd, CMD_WF_KEY, self.dc_WF_KEY)
            wf_purpose = self.cp_cmd_arg_get(cmd, CMD_WF_PURPOSE, self.dc_WF_PURPOSE)
            wb_type = self.cp_cmd_arg_get(cmd, CMD_WB_TYPE, self.dc_WF_KEY)
            wb_count = len(self.dc_CHECK_REGISTERS)
            r = f"Budget Manager Loaded Check Register ({wb_count}):\n"
            # A check register workbook is a .csv file.
            all_wbs, wb_index, wb_name = self.dc_WB_REF_resolve(wb_ref)
            if all_wbs:
                lwbl = self.DC.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
                self.DC.dc_WB_REF = ALL_KEY # Set the wb_ref in the DC.
                self.DC.dc_WB_NAME = None   # Set the wb_name in the DC.
                for wb_name in list(lwbl.keys()):
                    wb_index = self.dc_WORKBOOK_index(wb_name)
                    r += f"{P2}wb_index: {wb_index:>2} wb_name: '{wb_name:<40}'\n"
            else:
                cr_data = self.dc_CHECK_REGISTER_load(wb_name, wb_ref)
                if cr_data is None:
                    m = f"Failed to load Check Register data from '{wb_ref}'."
                    logger.error(m)
                    return False, m
                # Add it to the WORKBOOKS list.
                self.dc_WORKBOOK_add((wb_name, wb_ref))
                # Add to LOADED_WORKBOOKS_COLLECTION.
                self.dc_LOADED_WORKBOOKS[wb_name] = cr_data
                r += f"{P2}wb_index: {wb_index:>2} wb_name: '{wb_name:<40}'\n"
                self.dc_WB_REF = str(wb_index)  # Set the wb_ref in the DC.
                self._dc_WB_NAME = wb_name  # Set the wb_name in the DC.
            return True, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion CHECK_REGISTER_load_cmd() method
    # ------------------------------------------------------------------------ +
    #region CHANGE_cmd() command > wf cat 2
    def CHANGE_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Change aspects of the Data Context.

        A CHANGE_cmd command uses the wb_ref arg parameter.

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
            validate_only = self.cp_cmd_arg_get(cmd, CMD_VALIDATE_ONLY, None)
            what_if = self.cp_cmd_arg_get(cmd, CMD_WHAT_IF, None)
            fi_key = self.cp_cmd_arg_get(cmd, CMD_FI_KEY, self.dc_FI_KEY)
            wf_key = self.cp_cmd_arg_get(cmd, CMD_WF_KEY, self.dc_WF_KEY)
            wb_ref = self.cp_cmd_arg_get(cmd, CMD_WB_REF, self.dc_WB_REF)
            wb_type = self.cp_cmd_arg_get(cmd, CMD_WB_TYPE, self.dc_WB_TYPE)
            wf_purpose = self.cp_cmd_arg_get(cmd, CMD_WF_PURPOSE, None)
            all_wbs, wb_index, wb_name = self.dc_WB_REF_resolve(wb_ref)
            # Verify LOADED_WORKBOOKS to process.
            wdc = self.dc_WORKBOOK_DATA_COLLECTION
            wb = self.dc_WORKBOOK_by_index(wb_index)
            if (wb):
                wb_name = wb.wb_name
                wb_loaded = wb.loaded
                wb_content = wb.content
                # Process the change workbook command.
                if wb_type is not None:
                    wb.wb_type = wb_type
            if what_if:
                return True, f"what_if: apply_check_register(cr_wb_ref, transaction_wb_ref)"
            # apply_check_register(ws)
            return True, ""
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion CHANGE_cmd() method
    # ------------------------------------------------------------------------ +
    #region APP_cmd() command > wf cat 2
    def APP_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """View or change app settings.

        The APP_cmd command can use a variety of other command line arguments.

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain app_cmd = 'log' resulting in
            a full command key of 'app_cmd_log' as well as others to come.

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
            validate_only = self.cp_cmd_arg_get(cmd, CMD_VALIDATE_ONLY, None)
            what_if = self.cp_cmd_arg_get(cmd, CMD_WHAT_IF, None)
            handler_name = self.cp_cmd_arg_get(cmd, CMD_HANDLER_NAME, None)
            list_switch = self.cp_cmd_arg_get(cmd, CMD_LIST_SWITCH, False)
            level_value = self.cp_cmd_arg_get(cmd, CMD_LEVEL_VALUE, None)
            rollover_switch = self.cp_cmd_arg_get(cmd, CMD_ROLLOVER_SWITCH, False)
            return True, ""
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
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
            success : bool = False
            r : str = ""
            fr : str = f"Workflow Categorization \n"
            m : str = ""
            lwbc :LOADED_WORKBOOK_COLLECTION = None
            bdm_wb : Optional[BDMWorkbook] = None
            wb_content : Optional[WORKBOOK_CONTENT] = None
            wb_index : int = self.cp_cmd_arg_get(cmd, CMD_WB_INDEX, self.dc_WB_INDEX)
            all_wbs : bool = self.cp_cmd_arg_get(cmd, CMD_ALL_WBS, self.dc_ALL_WBS)
            # wb_index and all_wbs are validated already. 
            # Choose either all_wbs or a specific workbook designated by 
            # wb_index to be processed. This applies to loaded workbooks only, 
            # so configure wf_wb_list with the intended workbooks to categorize.
            if all_wbs:
                # If all_wbs, process all loaded workbooks.
                lwbc = self.dc_LOADED_WORKBOOKS
            else:
                # wb_index is already validated.
                bdm_wb = self.dc_WORKBOOK_by_index(wb_index)
                if bdm_wb is None:
                    m = f"wb_index '{wb_index}' is not valid."
                    logger.error(m)
                    return False, m
                wb_id = bdm_wb.wb_id
                bdm_wb.wb_loaded = wb_id in self.dc_LOADED_WORKBOOKS
                if not bdm_wb.wb_loaded:
                    m = f"Workbook '{bdm_wb.wb_id}' is not loaded, no action taken."
                    logger.error(m)
                    return False, m
                # Obtain the wb_content for wb_id.
                wb_content = self.dc_LOADED_WORKBOOKS[wb_id]
                # add the single wb to the process list.
                lwbc = {wb_id: wb_content}
            # Process the intended workbooks.
            for wb_id, wb_content in lwbc.items():
                bdm_wb = self.dc_WORKBOOK_DATA_COLLECTION[wb_id]
                wb_index = self.dc_WORKBOOK_index(wb_id)
                self.dc_WORKBOOK = bdm_wb
                self.dc_WB_INDEX = wb_index  # Set the wb_index in the DC.
                # if bdm_wb.wb_type == WB_TYPE_CHECK_REGISTER:
                    # Check for a check register column, add it if not present.
                    # load the check register here
                    # check_register_dict = csv_DATA_COLLECTION_url_get(wb_url)
                    # apply_check_register(ws)
                if bdm_wb.wb_type == WB_TYPE_TRANSACTIONS:
                    m = (f"{P2}Task: process_budget_category() " 
                         f"wb_index: {wb_index:>2} wb_id: '{wb_id:<40}', ")
                    logger.debug(m)
                    fr += m + "\n"
                    success, r = process_budget_category(bdm_wb, self.DC)
                    if not success:
                        r = (f"{P4}Task Failed: process_budget_category() wb_id: "
                             f"'{wb_id}'\n{P8}Result: {r}")
                        logger.error(r)
                        fr += r + "\n"
                        continue
                    m = (f"{P2}Task: dc_WORKBOOK_content_put() " 
                        f"wb_index: {wb_index:>2} wb_id: '{wb_id:<40}', ")
                    logger.debug(m)
                    fr += m + "\n"
                    success, m = self.dc_WORKBOOK_content_put(wb_content, bdm_wb)
                    if not success:
                        m = (f"{P4}Task Failed: dc_WORKBOOK_content_put() wb_id: "
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
            # capture cmd args
            validate_only = self.cp_cmd_arg_get(cmd, CMD_VALIDATE_ONLY, None)
            what_if = self.cp_cmd_arg_get(cmd, CMD_WHAT_IF, None)
            fi_key = self.cp_cmd_arg_get(cmd, CMD_FI_KEY, self.dc_FI_KEY)
            wf_key = self.cp_cmd_arg_get(cmd, CMD_WF_KEY, self.dc_WF_KEY)
            wb_ref = self.cp_cmd_arg_get(cmd, CMD_WB_REF, self.dc_WB_REF)
            wb_type = self.cp_cmd_arg_get(cmd, CMD_WB_TYPE, self.dc_WB_TYPE)
            wf_purpose = self.cp_cmd_arg_get(cmd, CMD_WF_PURPOSE, None)
            cr_wb_ref = self.cp_cmd_arg_get(cmd, CMD_CHECK_REGISTER, None)
            # Needs a check_register (cr) and a transaction workbook (wb).
            success, cr_wb, cr_content = self.get_workbook(cr_wb_ref)
            if not success:
                m = f"Failed to load check register '{cr_wb_ref}' - {cr_content}"
                logger.error(m)
                return False, m
            success, wb, wb_content = self.get_workbook(wb_ref)
            if not success:
                m = f"Failed to load transaction workbook '{wb_ref}' - {wb_content}"
                logger.error(m)
                return False, m
            logger.debug(f"cr_wb_name: {cr_wb.wb_name}, wb_name: {wb.wb_name}, ")
            # Ready to apply the check register to the workbook.
            apply_check_register(cr_content, wb_content)
            return True, ""
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_apply_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_task_cmd() command > wf cat 2
    def WORKFLOW_task_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Execute workflow tasks to WORKBOOKS.

        A WORKFLOW_apply_cmd command will use the wb_task, task_name, and 
        task_args attributes in the cmd. 

        Arguments:
            cmd (Dict): A valid BudMan View Model Command object. For this
            command, must contain workflow_cmd = 'task' resulting in
            a full command key of 'workflow_cmd_task'.

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
            validate_only = self.cp_cmd_arg_get(cmd, CMD_VALIDATE_ONLY, None)
            what_if = self.cp_cmd_arg_get(cmd, CMD_WHAT_IF, None)
            fi_key = self.cp_cmd_arg_get(cmd, CMD_FI_KEY, self.dc_FI_KEY)
            wf_key = self.cp_cmd_arg_get(cmd, CMD_WF_KEY, self.dc_WF_KEY)
            wb_ref = self.cp_cmd_arg_get(cmd, CMD_WB_REF, self.dc_WB_REF)
            wb_type = self.cp_cmd_arg_get(cmd, CMD_WB_TYPE, self.dc_WB_TYPE)
            wf_purpose = self.cp_cmd_arg_get(cmd, CMD_WF_PURPOSE, self.dc_WF_PURPOSE)
            task_name = self.cp_cmd_arg_get(cmd, CMD_TASK_NAME, None)
            task_args = self.cp_cmd_arg_get(cmd, CMD_TASK_ARGS, None)

            return True, ""
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_task_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_check() command > wf check 2 
    def WORKFLOW_check_cmd(self, cmd : Dict) -> Tuple[bool, str]:
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
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            logger.info(f"Start: ...")
            wb_ref = cmd.get(WB_REF, None)
            if wb_ref is None:
                m = f"wb_ref is None, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            wb_name = self.dc_WB_NAME
            all_wbs : bool = False
            r = f"Budget Manager Categorization Workflow:\n"
            all_wbs, wb_index = self.dc_WB_REF_resolve(wb_ref)
            # TODO: what_if arg stops here. Build a list of LOADED_WORKBOOKS to process.
            # Check cmd needs loaded workbooks to check
            lwbl = self.dc_LOADED_WORKBOOKS
            lwbl_count = len(lwbl) if lwbl else 0
            if lwbl_count == 0:
                m = f"No LOADED_WORKBOOKS found, check_cmd requires loaded workbook."
                logger.warning(m)
                return False, m
            if not self.dc_WORKBOOK_loaded(wb_name):
                m = f"wb_name '{wb_name}' not found in LOADED_WORKBOOKS."
                logger.error(m)
                return False, m
            if all_wbs:
                return False, f"Checking all loaded workbooks is not implemented yet."

            # wb = self.budget_domain_model.bdmwd_WORKBOOK_load(wb_name)
            wb = lwbl[wb_name]
            check_sheet_schema(wb)
            self.budget_domain_model.bdmwd_WORKBOOK_save(wb_name, wb)
            r += f"Checked workbook: Workbook({wb_ref}) '{wb_name}'\n"
            return True, r
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
        try:
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            logger.info(f"Start: ...")
            reload_target = self.cp_cmd_arg_get(cmd, RELOAD_TARGET, None)
            if reload_target is None:
                m = f"reload_target is None, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            if reload_target == CATEGORY_MAP:
                cmc = category_map_count()
                r = f"Workflow reload: '{reload_target}' rule count = {cmc}\n"
                logger.debug(r)
                importlib.reload(budget_category_mapping)
                importlib.reload(budman_cli_parser)
                importlib.reload(budman_cli_view)
            return True, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_reload_cmd() method
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
            lwbc_count = len(lwbc) if lwbc else 0

            # Prepare the output result
            result = f"{P2}{FI_WORKBOOK_DATA_COLLECTION}: {wdc_count}\n"
            result += f"{P4}{WB_INDEX:6}{P2}{WB_ID:50}{P2}"
            result += f"{WB_TYPE:14}{P2}wb_loaded{P2}{WB_CONTENT:30}"
            # print(result)
            result += "\n"
            wb : BDMWorkbook = None
            if wdc_count > 0:
                for i, wb in enumerate(wdc.values()):
                    wb.wb_loaded = wb.wb_id in lwbc
                    wb_content = lwbc[wb.wb_id] if wb.wb_loaded else None
                    wb_c_str = self.get_wb_content_repr(wb_content)
                    r = f"{wb.display_str(i,wb_c_str)}"
                    # print(r)
                    result += r + "\n"
            # if lwbc_count > 0:
            #     result += f"{P2}{DC_LOADED_WORKBOOKS}: {lwbc_count}\n"
            #     wdcl = list(wdc.keys())
            #     for wb_id in list(lwbc.keys()):
            #         wb = self.dc_WORKBOOK_DATA_COLLECTION[wb_id]
            #         i = wdcl.index(wb_id) if wb_id in wdcl else -1
            #         result += (f"{wdc[wb.wb_id].display_brief_str(i)}  "
            #                    f"{wb_c_str}\n")
            logger.info(f"Complete:")
            return True, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion get_workbook_data_collection_info_str() method
    # ------------------------------------------------------------------------ +
    #region get_wb_content_repr() method
    def get_wb_content_repr(self, wb_content:Any) -> str: 
        """Return a display string representation fo the wb_content."""
        try:
            if wb_content is None:
                return "not loaded"
            d = p3u.dscr(wb_content)
            if isinstance(wb_content, Workbook):
                return f"({wb_content!r})"
            elif isinstance(wb_content, dict):
                return f"{d}[{len(wb_content)} items]"
            else:
                return f"{d}"
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m, None
    #endregion get_wb_content_repr() method
    # ------------------------------------------------------------------------ +
    #region get_workbook_content() method
    def get_workbook(self, wb_ref:str, load : bool = True) -> Tuple[bool, BDMWorkbook, WORKBOOK_CONTENT]: 
        """From the wb_ref, validate and return the loaded content of the workbook."""
        try:
            wb : Optional[BDMWorkbook] = None
            all_wbs, wb_index, wb = self.dc_WB_REF_resolve(wb_ref)
            if self.wb_ref_not_valid(all_wbs, wb_index, wb):
                m = f"wb_ref '{wb_ref}' is not valid."
                logger.error(m)
                return False, m, None
            if all_wbs:
                m = f"wb_ref '{wb_ref}' all_wbs is not supported here."
                logger.error(m)
                return False, m, None
            if not wb:     
                m = f"wb_ref '{wb_ref}' not found in WORKBOOK_DATA_COLLECTION."
                logger.error(m)
                return False, m, None
            wb_content = None
            wb.wb_loaded = wb.wb_id in self.dc_LOADED_WORKBOOKS
            if not wb.wb_loaded and load:
                success, wb_content = self.dc_WORKBOOK_content_get(wb)
                if not success or wb_index not in self.dc_LOADED_WORKBOOKS:
                    m = f"Failed trying to load wb_ref '{wb_index}':'{wb.wb_id}'."
                    logger.error(m)
                    return False, m, None
            return True, wb, wb_content
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m, None
    #endregion get_workbook_content() method
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
        wb_index : int = self.cp_cmd_arg_get(cmd, CMD_WB_INDEX, self.dc_WB_INDEX)
        all_wbs : bool = self.cp_cmd_arg_get(cmd, CMD_ALL_WBS, self.dc_ALL_WBS)
        wb_ref : str = self.cp_cmd_arg_get(cmd, WB_REF, self.dc_WB_REF)
        # Get the command arguments.
        fi_key = cmd.get(CMD_FI_KEY, None)
        wf_key = cmd.get(CMD_WF_KEY, BDM_WF_CATEGORIZATION)
        wf_purpose = cmd.get(CMD_WF_PURPOSE, WF_INPUT)
        wb_type = cmd.get(CMD_WB_TYPE, WB_TYPE_TRANSACTIONS)
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
