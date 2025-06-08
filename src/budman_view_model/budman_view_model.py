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

    - Provides Command Processing for the command pattern, used by Views and
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
from typing import List, Type, TYPE_CHECKING, Dict, Tuple, Any, Callable
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from dynaconf import Dynaconf
from openpyxl import Workbook, load_workbook
# local modules and packages
from budman_settings import *
from budman_namespace import *
from budget_domain_model import (
    BDMBaseInterface, BDMClientInterface, BudgetDomainModel, 
    check_budget_category, check_sheet_columns,
    map_budget_category, category_map_count, 
    budget_category_mapping, BDMConfig,
    check_sheet_schema)
from budget_storage_model import *
from budman_data_context import BDMWorkingData
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManViewModel(BDMClientInterface): # future ABC for DC, CP, VM interfaces
    # ======================================================================== +
    #region BudManViewModel class intrinsics
    """A Budget Manager View Model providing CommandProcessing & Data Context.
    
    This ViewModel provides 3 primary design pattern implementations:
        1. ViewModel - the behavior of a View Model in MVVM.
        2. Command Processing (CP) and
        3. Data Context (DC)
         
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
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self, bdms_url : str = None, settings : Dynaconf = None) -> None:
        super().__init__()
        self._bdms_url : str = bdms_url
        self._settings = settings
        self._initialized : bool = False
        self.BDM_STORE_loaded : bool = False
        self._budget_domain_model : BudgetDomainModel = None
        self._data_context : BDMWorkingData = None
        self._cmd_map : Dict[str, Callable] = None
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #region Properties
    @property
    def model(self) -> BDMBaseInterface:
        """Return the model object reference."""
        return self._budget_domain_model
    @model.setter
    def model(self, bdm: BDMBaseInterface) -> None:
        """Set the model object reference."""
        if not isinstance(bdm, BDMBaseInterface):
            raise TypeError("model must be a BDMBaseInterface instance")
        self._budget_domain_model = bdm

    @property
    def bdms_url(self) -> str:
        """Return the BDM_STORE URL."""
        return self._bdms_url
    @bdms_url.setter
    def bdms_url(self, url: str) -> None:
        """Set the BDM_STORE URL."""
        if not isinstance(url, str):
            raise TypeError("bdms_url must be a string")
        if not url.startswith("file://") and not url.startswith("http://"):
            raise ValueError("bdms_url must be a valid file or http URL")
        self._bdms_url = url

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

    def _valid_DC(self) -> BDMWorkingData:
        """Init self._data_context if it is None."""
        try:
            if (self._data_context is None or 
                not isinstance(self._data_context, BDMWorkingData)):
                m = f"data_context property is not a BDMWorkingData instance, " 
                m += f"it is {type(self._data_context)}."
                logger.error(m)
                raise TypeError(m)
            return self._data_context
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    @property
    def data_context(self) -> BDMWorkingData:
        """Return the data context object."""
        _ = self._valid_DC()  # Ensure _data_context is valid
        return self._data_context
    @data_context.setter
    def data_context(self, value: BDMWorkingData) -> None:
        """Set the data context object."""
        if not isinstance(value, BDMWorkingData):
            raise ValueError("data_context must be a BDMWorkingData instance.")
        self._data_context = value
    @property
    def DC(self) -> BDMWorkingData:
        """Return the data context (DC) dictionary.
        This is an alias for the data_context property."""
        _ = self._valid_DC()  # Ensure _data_context is valid
        return self._data_context
    @DC.setter
    def DC(self, value: BDMWorkingData) -> None:
        """Set the data context (DC) dictionary.
        This is an alias for the data_context property."""
        if not isinstance(value, BDMWorkingData):
            raise ValueError("DC property value must be a BDMWorkingData object.")
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
    def initialize(self, load_user_store : bool = False) -> "BudManViewModel":
        """Initialize the command view_model."""
        try:
            st = p3u.start_timer()
            logger.info(f"Start: Configure Budget Manager View Model: ...")
            # Check if the budget domain model is initialized.
            bdm = self.initialize_bdm(load_user_store=load_user_store)
            # Create/initialize a BDMWorkingData data_context 
            self.data_context = BDMWorkingData(self.model).initialize()
            # Initialize the command map.
            self.initialize_cmd_map()  # TODO: move to DataContext class
            self.initialized = True
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize() method
    # ------------------------------------------------------------------------ +
    #region initialize_bdm() method
    def initialize_bdm(self, load_user_store : bool = False) -> "BudManViewModel":
        """Initialize the view_model's budget_domain_model."""
        try:
            st = p3u.start_timer()
            logger.info(f"Start: ...")
            # Check if the budget domain model exists.
            if (self.budget_domain_model is None or 
                not isinstance(self.budget_domain_model, BudgetDomainModel)):
                # There is no valid budget_model. Load a BDM_STORE file?
                if load_user_store:
                    # if a bdms_url is provided, load the BDM_STORE file.
                    if p3u.str_empty(self.bdms_url):
                        m = "No BDM_STORE URL provided, cannot load."
                        logger.error(m)
                        raise ValueError(m)                    
                    bdmc = BDMConfig.BDM_STORE_url_load(self.bdms_url)
                    if bdmc is None:
                        m = f"Failed to load BDM_STORE from URL: {self.bdms_url}"
                        logger.error(m)
                        raise ValueError(m)
                    bdm_config = bdmc.bdm_config_object
                    # Use the loaded BDM_STORE file as a config_object 
                    # config_object = bsm_BDM_STORE_file_load()
                    self.BDM_STORE_loaded = True
                else:
                    # Use the builtin default template as a config_object.
                    bdm_config = BDMConfig.BDM_CONFIG_default()
                # Now to initialize the budget model.
                self.model = BudgetDomainModel(bdm_config).bdm_initialize()
            if not self.budget_domain_model.bdm_initialized: 
                raise ValueError("BudgetModel is not initialized.")
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return self
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize_bdm() method
    # ------------------------------------------------------------------------ +
    #region initialize_cmd_map() method
    def initialize_cmd_map(self) -> None:
        """Initialize the cmd_map dictionary."""
        try:
            # Use the following cmd_map to dispatch the command for execution.
            self.cmd_map = {
                "init_cmd_fin_inst": self.FI_init_cmd,
                "save_cmd_workbooks": self.FI_LOADED_WORKBOOKS_save_cmd,
                "load_cmd_BDM_STORE": self.BDM_STORE_load_cmd,
                "save_cmd_BDM_STORE": self.BDM_STORE_save_cmd,
                "show_cmd_DATA_CONTEXT": self.DATA_CONTEXT_show_cmd,
                "show_cmd_workbooks": self.WORKBOOKS_show_cmd,
                "load_cmd_workbooks": self.WORKBOOKS_load_cmd,
                "workflow_cmd_categorization": self.WORKFLOW_categorization_cmd,
                "workflow_cmd_reload": self.WORKFLOW_reload_cmd,
                "workflow_cmd_check": self.WORKFLOW_check_cmd
            }
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion initialize_cmd_map() method
    # ------------------------------------------------------------------------ +
    #endregion BudManViewModel class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region BudManViewModel - Budget Manager View Model implementation         +
    """BudManViewModel provides 3 services for clients:

       1. ViewModel - the behavior of a View Model in MVVM.
       2. ViewModelCommandProcessor - the Command Pattern.
       3. ViewModelDataContext - the Data Context Pattern.

    See the module notes at the top of this file.
    """
    # ======================================================================== +
    #                                                                          +
    # ======================================================================== +
    #region ViewModelCommandProcessor implementing the Command Pattern        +
    """ ViewModelCommandProcessor Design Notes (future ABC)

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
    #region ViewModelCommandProcessor interface methods
    # ------------------------------------------------------------------------ +
    #region cp_execute_cmd() Command Processing method
    def cp_execute_cmd(self, 
                         cmd : Dict = None,
                         raise_errors : bool = False) -> Tuple[bool, Any]:
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
            validate_only: bool = cmd.get("validate_only", False)
            if not self.initialized:
                m = f"{self.__class__.__name__} is not initialized."
                logger.error(m)
                return False, m
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                return False, m
            success, result = self.cp_validate_cmd(cmd)
            if not success: return success, result
            full_cmd_key = result
            func = self.cmd_map.get(full_cmd_key)
            function_name = func.__name__
            if validate_only:
                result = f"vo-command: {function_name}({str(cmd)})"
                logger.info(result)
                return True, result
            logger.info(f"Executing command: {function_name}({str(cmd)})")
            status, result = self.cmd_map.get(full_cmd_key)(cmd)
            logger.info(f"Complete Command: [{p3u.stop_timer(st)}] {(status, str(result))}")
            return status, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            if raise_errors:
                raise RuntimeError(m)
            return False, m
    #endregion cp_execute_cmd() Command Processing method
    #region cp_validate_cmd() Command Processing method
    def cp_validate_cmd(self, cmd : Dict = None) -> Tuple[bool, str]:
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
            # Validate full cmd key from the cmd, or error out.
            success, result, cmd_key = self.cp_full_cmd_key(cmd)
            if not success: return False, result
            full_cmd_key = result
            # Validate the cmd arguments.
            for key, value in cmd.items():
                if key == cmd_key: continue
                elif key == FI_KEY:
                    if not self.dc_FI_KEY_validate(value):
                        m = f"Invalid fi_key value: '{value}'."
                        logger.error(m)
                        return False, m
                    continue
                elif key == WB_NAME: continue
                elif key == WF_KEY:
                    if not self.dc_WF_KEY_validate(value):
                        m = f"Invalid wf_key value: '{value}'."
                        logger.error(m)
                        return False, m
                    if value == ALL_KEY:
                        logger.warning(f"wf_key: '{ALL_KEY}' not implemented."
                                    f" Defaulting to {BDM_WF_CATEGORIZATION}.")
                        cmd[key] = BDM_WF_CATEGORIZATION
                    continue
                elif key == WB_REF:
                    if not self.dc_WB_REF_validate(value):
                        m = f"Invalid wb_ref level: '{value}'."
                        logger.error(m)
                        return False, m
                elif key == WB_INFO:
                    if not self.BMVM_cmd_WB_INFO_LEVEL_validate(value):
                        m = f"Invalid wb_info level: '{value}'."
                        logger.error(m)
                        return False, m
                else:
                    m = f"Unchecked argument key: '{key}': '{value}'."
                    logger.debug(m)
            logger.debug(f"Full command key: '{full_cmd_key}' cmd: {str(cmd)}")
            return True, full_cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_validate_cmd() Command Processing method
    #region cp_cmd_key() Command Processing method
    def cp_cmd_key(self, cmd : Dict = None) -> Tuple[bool, str]:
        """Validate a cmd_key is present in the cmd, return it.
                
        returns:
            Tuple[success: bool, result: str: 
                success = True: result = valid full_cmd_key value, cmd_key value.
                success = False: result = an error message.
        """
        try:
            if not self.initialized:
                m = f"{self.__class__.__name__} is not initialized."
                logger.error(m)
                return False, m
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
            # Success, return the cmd_key.
            return True, cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_cmd_key() Command Processing method
    #region cp_full_cmd_key() Command Processing method
    def cp_full_cmd_key(self, cmd : Dict = None) -> Tuple[bool, str]:
        """Validate a full cmd key with subcommand if included.
        
        returns:
            Tuple[success: bool, result: str, cmd_key: str|None]: 
                A tuple containing a boolean indicating success or failure. 
                True: result = valid full_cmd_key value, cmd_key value.
                False: result = an error message.
        """
        try:
            # Extract a cmd key from the cmd, or error out.
            success, result = self.cp_cmd_key(cmd)
            if not success: return False, result, None
            cmd_key = result
            # Acquire sub-command key if present.
            sub_cmd = cmd[cmd_key]
            # Construct full_cmd_key from cmd_key and sub_cmd (may be None).
            full_cmd_key = cmd_key + '_' + sub_cmd if p3u.str_notempty(sub_cmd) else cmd_key
            # Validate the full_cmd_key against the command map.
            if full_cmd_key not in self.cmd_map:
                m = f"Command key '{full_cmd_key}' not found in command map."
                logger.error(m)
                return False, m, None
            return True, full_cmd_key, cmd_key
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion cp_full_cmd_key() Command Processing method
    #region BMVM_cmd_WB_INFO_LEVEL_validate() Command Processing method
    def BMVM_cmd_WB_INFO_LEVEL_validate(self, info_level) -> bool:
        """Return True if info_level is a valid value."""
        try:
            return info_level == ALL_KEY or info_level in WB_INFO_VALID_LEVELS
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BMVM_cmd_WB_INFO_LEVEL_validate() Command Processing method
    #region BMVM_cmd_exception() Command Processing method
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
    #endregion BMVM_cmd_exception() Command Processing method
    # ------------------------------------------------------------------------ +
    #endregion Command Processing methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Command Execution Methods
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region FI_init_command() command > init FI boa
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
            fi_key = cmd.get("fi_key", None)
            wf_key = cmd.get("wf_key", BDM_WF_CATEGORIZATION)
            wb_type = cmd.get("wb_type", WF_WORKING)
            wb_name = cmd.get("wb_name", None)
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
                _ = self.DC.dc_FI_KEY_validate(fi_key)
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
            self.dc_WB_TYPE = wb_type
            self.dc_WB_NAME = wb_name
            # Create result
            lwbl_names = list(self.DC.dc_LOADED_WORKBOOKS.keys())
            # lwbl_names = self.FI_get_loaded_workbook_names()
            result = f"Loaded {len(lwbl_names)} Workbooks: {str(lwbl_names)}"
            return True, result
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion FI_init_command() command method
    # ------------------------------------------------------------------------ +
    #region FI_LOADED_WORKBOOKS_save_cmd() command > save wb 3
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
            wf_key = cmd.get("wf_key", BDM_WF_CATEGORIZATION)
            wb_type = cmd.get("wb_type", WF_INPUT)
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
                _ = self.budget_domain_model.bdm_FI_KEY_validate(fi_key)
            except ValueError as e:
                m = f"ValueError({str(e)})"
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            # Get the LOADED_WORKBOOK_COLLECTION from the BDM_WORKING_DATA.
            lwbl = self.dc_LOADED_WORKBOOKS
            # For each loaded workbook, save it to its the path .
            for wb_name, wb in lwbl:
                self.budget_domain_model.bsm_FI_WF_WORKBOOK_save(wb, wb_name,
                                                          fi_key, wf_key, wb_type)
            # Save the workbooks for the specified FI, WF, and WB-type.
            logger.info(f"Complete Command: 'Save' {p3u.stop_timer(st)}")   
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_LOADED_WORKBOOKS_save_cmd() command method
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
            # Construct the abs_path from BDM_STORE info configured in 
            # BUDMAN_SETTINGS.
            budman_store_filename_value = self.settings[BDM_STORE_FILENAME]
            budman_store_filetype_value = self.settings[BDM_STORE_FILETYPE]
            budman_store_full_filename = f"{budman_store_filename_value}.{budman_store_filetype_value}"
            budman_folder = self.settings[BUDMAN_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_full_filename
            # Update some values prior to saving.
            self.budget_domain_model.bdm_url = budman_store_abs_path.as_uri()
            self.budget_domain_model.bdm_last_modified_date = p3u.now_iso_date_string()
            self.budget_domain_model.bdm_last_modified_by = getpass.getuser()
            # Get a Dict of the BudgetModel to store.
            budget_model_dict = self.budget_domain_model.to_dict()
            # Save the BDM_STORE file.
            bsm_BDM_STORE_file_save(budget_model_dict, budman_store_abs_path)
            logger.info(f"Saved BDM_STORE file: {budman_store_abs_path}")
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
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            logger.info(f"Start: ...")
            # Load the BDM_STORE file with the BSM.
            # Use the BDM_STORE configured in BUDMAN_SETTINGS.
            budman_store_filename_value = self.settings[BDM_STORE_FILENAME]
            budman_store_filetype_value = self.settings[BDM_STORE_FILETYPE]
            budman_store_full_filename = f"{budman_store_filename_value}.{budman_store_filetype_value}"
            budman_folder = self.settings[BUDMAN_FOLDER]
            budman_folder_abs_path = Path(budman_folder).expanduser().resolve()
            budman_store_abs_path = budman_folder_abs_path / budman_store_full_filename
            # Load the BDM_STORE file.
            budman_store_dict = bsm_BDM_STORE_file_load(budman_store_abs_path)
            self.dc_BDM_STORE = budman_store_dict
            self.BDM_STORE_loaded = True
            logger.info(f"Complete: {p3u.stop_timer(st)}")
            return True, budman_store_dict
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion BDM_STORE_load_cmd() method
    # ------------------------------------------------------------------------ +
    #region DATA_CONTEXT_show_cmd() command > show dc
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
            # Gather the current content of the DATA_CONTEXT.
            bs = self.dc_BDM_STORE
            bs_str = p3u.first_n(str(bs))
            wbl = self.dc_WORKBOOKS
            wbl_count = len(wbl) if wbl else 0
            lwbl = self.dc_LOADED_WORKBOOKS
            lwbl_count = len(lwbl) if lwbl else 0
            # Update the current list of workbooks open in Excel
            excel_wb_list = self.DC.dc_EXCEL_WORKBOOKS
            success, result = p3u.open_excel_workbooks()
            if success:
                # result is a WB_INFO_COLLECTION, create a list of wb_names
                excel_wb_list = list(result.keys())
                self.DC.dc_EXCEL_WORKBOOKS = excel_wb_list

            # Prepare the output result
            result = f"Budget Manager Data Context:\n"
            result += f"{P2}{DC_INITIALIZED}: {self.dc_INITIALIZED}\n"
            result += f"{P2}{WB_NAME}: {self.dc_WB_NAME}\n"
            result += f"{P2}{WB_REF}: {self.dc_WB_REF}\n"
            result += f"{P2}{FI_KEY}: {self.dc_FI_KEY}\n"
            result += f"{P2}{WF_KEY}: {self.dc_WF_KEY}\n"
            result += f"{P2}{WB_TYPE}: {self.dc_WB_TYPE}\n"
            result += f"{P2}{DC_BDM_STORE}: {bs_str}\n"
            result += f"{P2}{DC_WORKBOOKS}: {wbl_count}\n"
            if wbl_count > 0:
                result += f"{P4}wb_ref wb_name{29 * ' '}excel abs_path\n"
                # Enumerate the WORKBOOK_LIST (a DATA_TUPLE_LIST)
                for i, (wb_name, wb_ap) in enumerate(wbl):
                    ewb : bool = 'Y' if wb_name in excel_wb_list else 'N'
                    result += f"{P4}  {i:2}   {wb_name:<35}   {ewb}   '{wb_ap}'\n"
            result += f"{P2}{DC_LOADED_WORKBOOKS}: {lwbl_count}\n"
            if lwbl_count > 0:
                # Iterate the LOADED_WORKBOOKS_COLLECTION (a DATA_COLLECTION)
                for wb_name in list(lwbl.keys()):
                    wb_index = self.DC.dc_WORKBOOK_index(wb_name)
                    r += f"{P2}wb_index: {wb_index:>2} wb_name: '{wb_name:<40}'\n"
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
            pfx = f"{self.__class__.__name__}.{self.FI_init_cmd.__name__}: "
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            logger.info(f"Start: ...")
            wb_ref = cmd.get(WB_REF, None)
            wb_info = cmd.get(WB_INFO, None)
            if wb_ref is None:
                m = f"wb_ref is None, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            wb_count = len(self.dc_WORKBOOKS)
            r = f"Budget Manager Workbooks({wb_count}):\n"
            if wb_ref.isdigit():
                wb_refnum = int(wb_ref)
                wb_info = self.dc_WORKBOOKS[wb_refnum] if wb_refnum < wb_count else None
                l = "Yes" if self.WB_loaded(wb_info[0]) else "No "
                r += f"{P2}{wb_refnum:>2} {l} {wb_info[0]:<40} '{wb_info[1]}'\n"
            elif wb_ref == ALL_KEY:
                for i, (wb_name, wb_ap) in enumerate(self.dc_WORKBOOKS):
                    l = "Yes" if self.WB_loaded(wb_name) else "No "
                    r += f"{P2}{i:>2} {l} {wb_name:<40} '{wb_ap}'\n"
            return True, r
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            return False, m
    #endregion DATA_CONTEXT_show_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKBOOKS_load_cmd() command > load wb 0
    def WORKBOOKS_load_cmd(self, cmd : Dict) -> Tuple[bool, str]:
        """Load one or more WORKBOOKS in the DC.

        A load_cmd_workbooks command will use the wb_ref value in the cmd. 
        Value is a number or a wb_name.

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
            fi_key = self.dc_FI_KEY
            wf_key = self.dc_WF_KEY
            wb_type = self.dc_WB_TYPE
            wb_count = len(self.dc_WORKBOOKS)
            r = f"Budget Manager Loaded Workbooks({wb_count}):\n"
            all_wbs, wb_index, wb_name = self.DC.bdmwd_WB_REF_resolve(wb_ref)
            # Check for an invalid wb_ref value.
            if not all_wbs and wb_index == -1 and wb_name is None:
                m = f"wb_ref '{wb_ref}' is not valid."
                logger.error(m)
                return False, m
            if all_wbs:
                lwbl = self.model.bdmwd_FI_WORKBOOKS_load(fi_key, wf_key, wb_type)
                self.DC.dc_WB_REF = ALL_KEY # Set the wb_ref in the DC.
                self.DC.dc_WB_NAME = None   # Set the wb_name in the DC.
                for wb_name in list(lwbl.keys()):
                    wb_index = self.DC.dc_WORKBOOK_index(wb_name)
                    r += f"{P2}wb_index: {wb_index:>2} wb_name: '{wb_name:<40}'\n"
            elif wb_index >= 0:
                _ = self.model.bdmwd_WORKBOOK_load(wb_name)
                r += f"{P2}wb_index: {i:>2} wb_name: '{wb_name:<40}'\n"
                self.DC.dc_WB_REF = str(i)  # Set the wb_ref in the DC.
                self.DC._WB_NAME = wb_name  # Set the wb_name in the DC.
            return True, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKBOOKS_load_cmd() method
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_categorization_cmd() command > wf cat 2
    def WORKFLOW_categorization_cmd(self, cmd : Dict) -> Tuple[bool, str]:
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
            logger.info(f"Start: ...")
            if p3u.is_not_obj_of_type("cmd",cmd,dict,pfx):
                m = f"Invalid cmd object, no action taken."
                logger.error(m)
                return False, m
            wb_ref = cmd.get(WB_REF, None) # from the cmd args
            if wb_ref is None and self.dc_WB_REF is None:
                    m = f"wb_ref is None, no action taken."
                    logger.error(m)
                    return False, m
            # Verify LOADED_WORKBOOKS to process.
            wb_ref = wb_ref or self.dc_WB_REF
            lwbl = self.dc_LOADED_WORKBOOKS
            lwbl_count = len(lwbl) if lwbl else 0
            if lwbl_count == 0:
                m = f"No LOADED_WORKBOOKS found, no action taken."
                logger.error(m)
                return False, m
            all_wbs, wb_index, wb_name = self.DC.bdmwd_WB_REF_resolve(wb_ref)
            # Check for an invalid wb_ref value.
            if not all_wbs and wb_index == -1 and wb_name is None:
                m = f"wb_ref '{wb_ref}' is not valid."
                logger.error(m)
                return False, m
            # Now either all_wbs or a specific workbook is to be processed.
            # This applies to loaded workbooks only.
            # wb_count = len(self.dc_WORKBOOKS)
            wf_wb_list = []
            r = f"Budget Manager Categorization Workflow:\n"
            if all_wbs:
                # If all_wbs, process all loaded workbooks.
                for wb_name, wb in lwbl.items():
                    wf_wb_list.append(wb)
            else:
                # Obtain the wb for wb_index, and save the wb_name
                wb = self.dc_LOADED_WORKBOOKS[wb_name] 
                wf_wb_list.append(wb)

            for wb in wf_wb_list:
                wb = lwbl[wb_name]
                ws = wb.active
                # Check for budget category column, add it if not present.
                # check_budget_category(ws)
                check_sheet_columns(ws)
                # Map the 'Original Description' column to the 'Budget Category' column.
                map_budget_category(ws,"Original Description", BUDGET_CATEGORY_COL)
                self.budget_domain_model.bdmwd_WORKBOOK_save(wb_name, wb)
                r += f"Categorization Workflow applied to '{wb_name}'\n"
            return True, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_categorization_cmd() method
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
            all_wbs, wb_index = self.bdmwd_WB_REF_resolve(wb_ref)
            # TODO: what_if arg stops here. Build a list of LOADED_WORKBOOKS to process.
            # Check cmd needs loaded workbooks to check
            lwbl = self.dc_LOADED_WORKBOOKS
            lwbl_count = len(lwbl) if lwbl else 0
            if lwbl_count == 0:
                m = f"No LOADED_WORKBOOKS found, check_cmd requires loaded workbook."
                logger.warning(m)
                return False, m
            if not self.DC.dc_WORKBOOK_loaded(wb_name):
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
            reload_target = cmd.get(RELOAD_TARGET, None)
            if reload_target is None:
                m = f"reload_target is None, no action taken."
                logger.error(m)
                raise RuntimeError(f"{pfx}{m}")
            r = f"Budget Manager Workflow: reload '{reload_target}'\n"
            if reload_target == CATEGORY_MAP:
                cmc = category_map_count()
                m = f"{P4}Reloading target: '{reload_target}' count = {cmc}"
                logger.info(m)
                r += f"{m}\n"
                importlib.reload(budget_category_mapping)
                cmc = category_map_count()
                m = f"{P4}reloaded modules for target: '{reload_target}' count = {cmc}\n"
                logger.info(m)
                r += f"{m}\n"
            return True, r
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WORKFLOW_reload_cmd() method
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion Command Execution Methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    #endregion ViewModelCommandProcessor implementing the Command Pattern     +
    # ======================================================================== +
    #                                                                          +
    # ======================================================================== +
    #region ViewModelData_Context client implementation                            +
    """BDM view_model Data Context Interface Documentation.

    Data Context (DC) Interface Overview
    ------------------------------------

    Budget Manager is designed around the MVVM (Model View ViewModel) design
    pattern. In MVVM implementations, a View binds to a ViewModel through an
    abstract Data Context (DC) object interface. Also, there is often a Command
    Processing pattern to map command actions from a user interface View to 
    data actions in the DC. 
    
    Herein, the design is to have the DC interface provide support Commands 
    as well as Data properties and methods. To keep the scope of the View Model 
    limited concerning DC data, all understanding of the structure of  
    data is in the DC which binds to the Model BDMWD object. The DC properties and
    methods are where downstream APIs are used, not in the Command Binding
    Implementation methods.
    
    These DC methods are used by Commands to access and perform actions on the
    DC data values. As an API, the DC methods are an abstraction to support a 
    View Model and View trying to interact upstream with a user. Some are data 
    requests and others perform work on the Data Context state while owning
    the concern for syncing with the Model downstream.    

    This View Model leverages the DC as a single interface to leverages 
    BudgetManager Domain Model (BDM) through Budget Domain Working Data (BDMWD)
    "library" to reference actual data for the application Model, in memory. 
    When storage actions are required, the DC may utilize the 
    BudgetManager Storage Model (BSM) interface library.

    Data Context Scope
    ------------------

    In the BudgetManager design language, the primary object concepts are
    FI - Financial Institution, WF - Workflow, WB - Workbook, and BDM_STORE
    - Budget Manager Store where user-specific budget data is maintained. 
    The Data Context data is always scoped to the current values of the 'keys' 
    for these primary objects: FI_KEY, WF_KEY, WB_TYPE, and WB_NAME. Changing 
    these values will cause the DC to flag the need for a refresh of the
    underlying data.

    Data Context Concrete Implementation
    ------------------------------------
    The BudgetManagerDataContextInterface is an abstract interface used by client
    modules through binding to an object with a concrete implementation of the
    interface. The concrete implementation is the BudgetManagerDataContext class 
    in the Budget Manager application design. This singleton instance is 
    referenced by the ViewModel and, possibly, View if needed.

    DC is initialized with a reference to the BudgetDomainModel 
    BudgetDomainWorkingData object, available in the BudgetDomainManager 
    bdm_working_data property. 
    """
    # ======================================================================== +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Data Context (DC) Object binding (client sdk) methods
    # ------------------------------------------------------------------------ +
    #region get_DC() method
    def get_DC(self) -> Any:
        """Return the Data Context for the ViewModel."""
        try:
            return self.DC
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion get_DC() method
    # ------------------------------------------------------------------------ +
    #region set_DC() method
    def set_DC(self, dc : Any) -> None:
        """Set the Data Context (DC) object binding for the ViewModel."""
        try:
            self.DC = dc
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion set_DC() method
    # ------------------------------------------------------------------------ +
    #endregion Data Context (DC) Object binding (client sdk) methods
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region BudMan Data Context Interface (client sdk) Properties                                            +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    @property
    def dc_INITIALIZED(self) -> bool:
        """Return the value of the DC_INITIALIZED attribute."""
        return self.DC.dc_INITIALIZED
    @dc_INITIALIZED.setter
    def dc_INITIALIZED(self, value: bool) -> None:
        """Set the value of the DC_INITIALIZED attribute."""
        self.DC.dc_INITIALIZED = value

    @property
    def dc_FI_KEY(self) -> str:
        """Return the current financial institution key value in DC."""
        return self.DC.dc_FI_KEY
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """Set the current financial institution key value in DC."""
        self.DC.dc_FI_KEY = value

    @property
    def dc_WF_KEY(self) -> str:
        """Return the current workflow key value in DC."""
        return self.DC.dc_WF_KEY
    @dc_WF_KEY.setter
    def dc_WF_KEY(self, value: str) -> None:
        """Set the current workflow key value in DC."""
        self.DC.dc_WF_KEY = value

    @property
    def dc_WB_TYPE(self) -> str:
        """Return the current workbook type value in DC."""
        return self.DC.dc_WB_TYPE
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the current workbook type value in DC."""
        self.DC.dc_WB_TYPE = value

    @property
    def dc_WB_NAME(self) -> str:
        """Return the current workbook name value in DC."""
        return self.DC.dc_WB_NAME

    @dc_WB_NAME.setter
    def dc_WB_NAME(self, value: str) -> None:
        """Set the current workbook name value in DC."""
        self.DC.dc_WB_NAME = value

    @property
    def dc_WB_REF(self) -> str:
        """Return the current workbook ref value in DC."""
        return self.DC.dc_WB_REF

    @dc_WB_REF.setter
    def dc_WB_REF(self, value: str) -> None:
        """Set the current workbook ref value in DC."""
        self.DC.dc_WB_REF = value

    @property
    def dc_BDM_STORE(self) -> str:
        """Return the current BDM_STORE value in DC."""
        return self.DC.dc_BDM_STORE
    @dc_BDM_STORE.setter
    def dc_BDM_STORE(self, value: str) -> None:
        """Set the current BDM_STORE value in DC."""
        self.DC.dc_BDM_STORE = value

    @property 
    def dc_WORKBOOKS(self) -> WORKBOOK_LIST:
        """Return the current workbooks value in DC per FI_KEY, WF_KEY, WB_TYPE."""
        return self.DC.dc_WORKBOOKS
    @dc_WORKBOOKS.setter
    def dc_WORKBOOKS(self, value: WORKBOOK_LIST) -> None:
        """Set the current  dc_WORKBOOK value in DC."""
        self.DC.dc_WORKBOOKS = value

    @property 
    def dc_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Return the current loaded workbooks value in DC."""
        return self.DC.dc_LOADED_WORKBOOKS
    @dc_LOADED_WORKBOOKS.setter
    def dc_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Set the current loaded workbooks value in DC."""
        self.DC.dc_LOADED_WORKBOOKS = value

    @property 
    def dc_EXCEL_WORKBOOKS(self) -> DATA_COLLECTION:
        """Return the current collection of workbooks open in excel."""
        return self.DC.dc_EXCEL_WORKBOOKS
    @dc_EXCEL_WORKBOOKS.setter
    def dc_EXCEL_WORKBOOKS(self, value: DATA_COLLECTION) -> None:
        """Set the current collection of workbooks open in excel."""
        self.DC.dc_EXCEL_WORKBOOKS = value
    # ------------------------------------------------------------------------ +
    #endregion BudMan Data Context Interface (client sdk) Properties
    # ------------------------------------------------------------------------ +
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region Data Context  (client sdk) Methods
    #                                                                          +
    # ------------------------------------------------------------------------ +
    #region dc_FI_KEY_validate() method
    def dc_FI_KEY_validate(self, fi_key : str) -> int: 
        """Return True if the fi_key is valid."""
        try:
            # Bind through the DC (data_context) object.
            return self.DC.dc_FI_KEY_validate(fi_key)
            # return self.budget_domain_model.bdm_FI_KEY_validate(fi_key)
        except Exception as e:
            return self.BMVM_cmd_exception(e)
    #endregion dc_FI_KEY_validate() method
    # ------------------------------------------------------------------------ +
    #region dc_WF_KEY_validate() method
    def dc_WF_KEY_validate(self, wf_key : str) -> bool: 
        """Return True if the wf_key is valid."""
        try:
            # Bind through the DC (data_context) object.
            return self.DC.dc_WF_KEY_validate(wf_key)
        except Exception as e:
            return self.BMVM_cmd_exception(e)
    #endregion dc_WF_KEY_validate() method
    # ------------------------------------------------------------------------ +
    #region dc_WB_REF_validate() method
    def dc_WB_REF_validate(self, wb_ref : str) -> bool: 
        """Return True if the wb_ref is valid."""
        try:
            # Bind through the DC (data_context) object
            return self.DC.dc_WB_REF_validate(wb_ref)
        except Exception as e:
            return self.BMVM_cmd_exception(e)
    #endregion dc_WB_REF_validate() method
    # ------------------------------------------------------------------------ +
    #region WB_loaded(wb_name) method
    def WB_loaded(self, wb_name:str) -> bool: 
        """Return True if wb_name is in the DC.LOADED_WORKBOOKS list."""
        raise NotImplementedError("deprecated, use dc_WORKBOOK_loaded()")
    #endregion WB_loaded(wb_name) method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbooks() method
    def FI_WORKBOOKS_get(self) -> List[str]: 
        """Retrieve the current WORKBOOK_LIST for the DC fi_key,wf_key,wb_type."""
        try:
            # Reference the BDMWD_LOADED_WORKBOOKS.
            return self.budget_domain_model.bdmwd_LOADED_WORKBOOKS_get()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbook_names() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbooks_count() method
    def FI_get_loaded_workbooks_count(self) -> int: 
        """Return count of all loaded workbooks from Data Context."""
        try:
            # Reference the BDMWD_LOADED_WORKBOOKS.
            return self.budget_domain_model.bdmwd_LOADED_WORKBOOKS_count()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbooks_count() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbooks() method
    def FI_get_loaded_workbooks(self) -> List[str]: 
        """Return names of all loaded workbooks from Data Context."""
        try:
            # Reference the BDMWD_LOADED_WORKBOOKS.
            return self.budget_domain_model.bdmwd_LOADED_WORKBOOKS_get()
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_get_loaded_workbook_names() method
    # ------------------------------------------------------------------------ +
    #region FI_get_loaded_workbook_names() method
    def FI_get_loaded_workbook_names(self) -> List[str]: 
        """Return names of all loaded workbooks from Data Context."""
        try:
            # Reference the BDMWD_LOADED_WORKBOOKS.
            bdmwd_wb_list = self.budget_domain_model.bdmwd_LOADED_WORKBOOKS_get()
            wb_name_list = []
            for wb_name, _ in bdmwd_wb_list:
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
            # Reference the BDMWD_LOADED_WORKBOOKS.
            bdmwd_wb_list = self.budget_domain_model.bdmwd_LOADED_WORKBOOKS_get()
            if i < len(bdmwd_wb_list):
                wb_name, wb = bdmwd_wb_list[i]
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
            # Reference the BDMWD_LOADED_WORKBOOKS.
            bdmwd_wb_list = self.budget_domain_model.bdmwd_LOADED_WORKBOOKS_get()
            for wb_name, wb in bdmwd_wb_list:
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
    #endregion ViewModelData_Context client implementation                         +
    # ======================================================================== +
    #                                                                          +
    #endregion BudManViewModel - BudMan View Model implementation
    # ======================================================================== +
