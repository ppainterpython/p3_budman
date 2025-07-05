# ---------------------------------------------------------------------------- +
#region budget_domain_model.py module
""" budget_domain_model.py implements the class BudgetDomainModel.

    Following a rough MVVM pattern, the BudgetDomainModel class is acting as 
    both the cohesive Model, representing a budget model domain in
    memory as object API. 

    At present, the BudgetDomainModel class is a singleton class that manages the 
    mapping of excel "workbooks" stored in the filesystem to the budget model.
    The BudgetDomainModel class presents properties and methods to the outside world.
    Methods are separated into DomainModel-ish methods for the 
    Budget Domain Model (BDM), which is the in-memory data model,
    and StorageModel-ish methods for the Budget Storage Model (BSM), 
    which is the filesystem model structure.

    In the Budget Domain Model, a data pipeline pattern is used, anticipating 
    "raw data" will be introduced from financial institutions (FI) and and 
    processed through a series of workflow tasks. Raw data is a "workbook", 
    often an excel file, or a .cvs file.
    
    A "folder" concept is aligned with the stages of a pipeline as a 
    series of "workflows" applied to the data. Roughly, workflow task works 
    on data in its associated "work" folder, processing data inplace locally 
    or as modifications or output to workbooks in other folders. Configuration 
    is used to map the BDM folders to the BSM folders. But, a simple workflow 
    scheme is for a task to have a designated input, work and output folder in 
    BDM. Incoming data appears in the input folder. Tasks own the responsibility
    to move it into their work folder, and if and when to move it to the
    output folder. The workflow pipeline is roughly:

    Workflow: a function grouping of tasks to be applied to input data.
    workflowTaskFunc(InputFolder, Workfolder) -> OutputFolder

    Workflows are functional units of work with clearly defined concerns applied
    to input data and producing work and outout data. 

    Key Concepts:
    -------------
    - Folders: containers of workbooks associated with a workflow stage.
    - Workflows: a defined set of process functions applied to data.
    - Workbooks: a container of financial transaction data, e.g., excel file.
    - Raw Data: original data from a financial institution (FI), read-only.
    - Financial Budget: the finalized output, composed of workbooks,
        representing time-series transactions categorized by payments and
        deposits (debits and credits).
    - Financial Institution (FI): a bank or brokerage financial institution.
        
    Perhaps the primary domain should be "Financial Budget" instead of
    "Budget Model". The FB Domain and the "Storage Domain" or Sub-Domain. 

    The Budget Domain Model has the concern of presenting an API that is 
    independent of where the workbook data is sourced and stored. The 
    Budget Storage Model has the concern of managing sourcing and storing 
    workbooks in a storage system. Currently, it just maps the BDM structure to 
    filesystem folders and files.

    Assumptions:
    - The FI transaction data resides in a folder specified in the budget_config.
    - Banking transaction files are typically excel spreadsheets, referred to 
      as workbooks. 
    - A workbook's data content starts in cell A1.
    - Row 1 contains column headers. All subsequent rows are data with no blank
      rows until the end of the data.
"""
#endregion budget_domain_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from abc import ABCMeta
import logging, os, getpass, time, copy
from pathlib import Path
from typing import List, Type, Generator, Dict, Tuple, Any, TYPE_CHECKING
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook
# local modules and packages
from budman_namespace.bdm_singleton_meta import BDMSingletonMeta
from budman_namespace.design_language_namespace import *
from budget_storage_model import (
    bsm_verify_folder, 
    bsm_get_workbook_names,
    bsm_get_workbook_names2,
    bsm_WORKBOOK_content_file_load,
    bsm_WORKBOOK_content_file_save,
    )                              
from p3_mvvm.model_base_ABC import Model_Base
from budman_namespace.bdm_workbook_class import BDMWorkbook
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudgetDomainModel(Model_Base,metaclass=BDMSingletonMeta):
    # ======================================================================== +
    #region BudgetDomainModel class intrinsics
    # ======================================================================== +
    """BudgetDomainModel class implementing Singleton pattern.
    
        A singleton class to manage the budget model for the application.
        This class is used to store and manage the budget data, including
        the budget folder, institutions, and options. 

        When instantiated, a config object is provided to the constructor.

    """
    # ------------------------------------------------------------------------ +
    #region    BudgetDomainModel class constructor __init__()
    def __init__(self, bdm_config : Dict = None) -> None:
        """Constructor for the BudgetDomainModel class."""
        # Note: _subclassname set by SingletonMeta after __init__() completes.
        logger.debug("Start:")
        # Keep the constructor simple, just set initial values to create the 
        # attributes in the object with one critical exception.
        # A valid bdm_config dictionary created by one of the methods on the
        # BDMConfig class is required here. Here is is just added to the
        # BDM_STORE_OBJECT property. The real work happens in bdm_initialize().
        if bdm_config is None:
            m = "bdm_config parameter is None, must be a valid configuration dictionary "
            m += "created by one of the BDMConfig methods prior to BudgetDomainModel()." 
            logger.error(m)
            raise ValueError(m)
        setattr(self, BDM_ID, None)
        setattr(self, BDM_STORE_OBJECT, bdm_config) # CRITICAL to later initialization.
        setattr(self, BDM_INITIALIZED, False)
        setattr(self, BDM_FILENAME, None)
        setattr(self, BDM_FILETYPE, None)
        setattr(self, BDM_FOLDER, None)  
        setattr(self, BDM_URL, None)  
        setattr(self, BDM_FI_COLLECTION, {})
        setattr(self, BDM_WF_COLLECTION, {}) 
        setattr(self, BDM_OPTIONS, {})
        setattr(self, BDM_CREATED_DATE, p3u.now_iso_date_string()) 
        setattr(self, BDM_LAST_MODIFIED_DATE, self._created_date)
        setattr(self, BDM_LAST_MODIFIED_BY, getpass.getuser())
        setattr(self, BDM_WORKING_DATA, {})  
        setattr(self, BDM_DATA_CONTEXT, {})  
        logger.debug("Complete:")
    #endregion BudgetDomainModel class constructor __init__()
    # ------------------------------------------------------------------------ +
    #region    BudgetDomainModel internal class methods
    def to_dict(self):
        '''Return BudgetDomainModelTemplate dictionary object. Used for serialization.'''
        ret = {
            BDM_ID: self.bdm_id,
            BDM_STORE_OBJECT: self.bdm_store_object,
            BDM_INITIALIZED: self.bdm_initialized,
            BDM_FILENAME: self.bdm_filename,
            BDM_FILETYPE: self.bdm_filetype,
            BDM_FOLDER: self.bdm_folder,
            BDM_URL: self.bdm_url,
            BDM_FI_COLLECTION: self.bdm_fi_collection,
            BDM_WF_COLLECTION: self.bdm_wf_collection,
            BDM_OPTIONS: self.bdm_options,
            BDM_CREATED_DATE: self.bdm_created_date,
            BDM_LAST_MODIFIED_DATE: self.bdm_last_modified_date,
            BDM_LAST_MODIFIED_BY: self.bdm_last_modified_by,
            BDM_DATA_CONTEXT: self.bdm_data_context,
            BDM_WORKING_DATA: self.bdm_working_data
        }
        return ret
    def __repr__(self) -> str:
        ''' Return a str representation of the BudgetDomainModel object '''
        ret = f"{{ "
        ret += f"'{BDM_ID}': {self.bdm_id}, "
        ret += f"'{BDM_STORE_OBJECT}': {self.bdm_store_object}, "
        ret += f"'{BDM_INITIALIZED}': {self.bdm_initialized}, "
        ret += f"'{BDM_FOLDER}': '{self.bdm_folder}', "
        ret += f"'{BDM_FI_COLLECTION}': '{self.bdm_fi_collection}', "
        ret += f"'{BDM_URL}': '{self.bdm_url}', "
        ret += f"'{BDM_WF_COLLECTION}': '{self.bdm_wf_collection}', "
        ret += f"'{BDM_OPTIONS}': '{self.bdm_options}', "
        ret += f"'{BDM_CREATED_DATE}': '{self.bdm_created_date}', "
        ret += f"'{BDM_LAST_MODIFIED_DATE}': '{self.bdm_last_modified_date}', "
        ret += f"'{BDM_LAST_MODIFIED_BY}': '{self.bdm_last_modified_by}', "
        ret += f"'{BDM_WORKING_DATA}': '{self.bdm_working_data}' }} "
        return ret
    def __str__(self) -> str:
        ''' Return a str representation of the BudgetDomainModel object '''
        ret = f"{self.__class__.__name__}({str(self.bdm_folder)}): "
        ret += f"{BDM_ID} = {self.bdm_id}, "
        ret += f"{BDM_STORE_OBJECT} = {str(self.bdm_store_object)}, "
        ret += f"{BDM_INITIALIZED} = {str(self.bdm_initialized)}, "
        ret += f"{BDM_FOLDER} = '{str(self.bdm_folder)}', "
        ret += f"{BDM_FI_COLLECTION} = [{', '.join([repr(fi_key) for fi_key in self.bdm_fi_collection.keys()])}], "
        ret += f"{BDM_URL} = '{self.bdm_url}' "
        ret += f"{BDM_WF_COLLECTION} = '{self.bdm_wf_collection}' "
        ret += f"{BDM_OPTIONS} = '{self.bdm_options}' "
        ret += f"{BDM_CREATED_DATE} = '{self.bdm_created_date}', "
        ret += f"{BDM_LAST_MODIFIED_DATE} = '{self.bdm_last_modified_date}', "
        ret += f"{BDM_LAST_MODIFIED_BY} = '{self.bdm_last_modified_by}', "
        ret += f"{BDM_WORKING_DATA} = {self.bdm_working_data}"
        return ret
    #endregion BudgetDomainModel internal class methods
    # ------------------------------------------------------------------------ +
    #region    BudgetDomainModel (BDM) properties
    @property
    def bdm_initialized(self) -> bool:
        """The initialized value."""
        return self._initialized
    @bdm_initialized.setter
    def bdm_initialized(self, value )-> None:
        """Set the initialized value."""
        self._initialized = value

    @property
    def bdm_id(self) -> str:
        """The budget model ID."""
        return getattr(self, BDM_ID)
    @bdm_id.setter
    def bdm_id(self, value: str) -> None:
        """Set the budget model ID."""
        if not isinstance(value, str):
            raise ValueError(f"bm_id must be a string: {value}")
        setattr(self, BDM_ID, value)

    @property
    def bdm_store_object(self) -> object:
        """The budget model configuration object."""
        return getattr(self, BDM_STORE_OBJECT)
    @bdm_store_object.setter
    def bdm_store_object(self, value: object) -> None:
        """Set the budget model configuration object."""
        if not isinstance(value, object):
            raise ValueError(f"bm_config_object must be an object: {value}")
        setattr(self, BDM_STORE_OBJECT, value)

    @property
    def bdm_filename(self) -> str:
        """The bdm_store filename is a string, e.g., 'bdm_store"""
        return self._bdm_filename
    @bdm_filename.setter
    def bdm_filename(self, value: str) -> None:
        """Set the bdm_store filename."""
        self._bdm_filename = value

    @property
    def bdm_filetype(self) -> str:
        """The bdm_store filetype, e.g., '.jsonc"""
        return self._bdm_filetype
    @bdm_filetype.setter
    def bdm_filetype(self, value: str) -> None:
        """Set the bdm_store filetype."""
        self._bdm_filetype = value

    @property
    def bdm_folder(self) -> str:
        """The budget folder path is a string, e.g., '~/OneDrive/."""
        return self._budget_folder
    @bdm_folder.setter
    def bdm_folder(self, value: str) -> None:
        """Set the budget folder path."""
        self._budget_folder = value

    @property
    def bdm_url(self) -> str:
        """The budget manager store file url."""
        return self._bdm_url
    @bdm_url.setter
    def bdm_url(self, value: str) -> None:
        """Set the budget manager store file url."""
        self._bdm_url = value

    @property
    def bdm_fi_collection(self) -> FI_COLLECTION:
        """The financial institutions collection."""
        return self._financial_institutions
    @bdm_fi_collection.setter
    def bdm_fi_collection(self, value: FI_COLLECTION) -> None:
        """Set the financial institutions collection."""
        self._financial_institutions = value

    @property
    def bdm_wf_collection(self) -> WF_COLLECTION:
        """The workflow collection."""
        return self._workflows
    @bdm_wf_collection.setter
    def bdm_wf_collection(self, value: WF_COLLECTION) -> None:
        """Set the workflows collection."""
        self._workflows = value

    @property
    def bdm_options(self) -> BDMO_OBJECT:
        """The budget model options dictionary."""
        return self._options
    @bdm_options.setter
    def bdm_options(self, value: BDMO_OBJECT) -> None:
        """Set the budget model options dictionary."""
        self._options = value

    @property
    def bdm_created_date(self) -> str:
        """The created date."""
        return self._created_date
    @bdm_created_date.setter
    def bdm_created_date(self, value: str) -> None:  
        """Set the created date."""
        self._created_date = value

    @property
    def bdm_last_modified_date(self) -> str:
        """The last modified date."""
        return self._last_modified_date
    @bdm_last_modified_date.setter
    def bdm_last_modified_date(self, value: str) -> None:
        """Set the last modified date."""
        self._last_modified_date = value

    @property
    def bdm_last_modified_by(self) -> str:
        """The last modified by."""
        return self._last_modified_by
    @bdm_last_modified_by.setter
    def bdm_last_modified_by(self, value: str) -> None:
        """Set the last modified by."""
        self._last_modified_by = value
    
    @property
    def bdm_working_data(self) -> BDM_WORKING_DATA_OBJECT:
        """The budget domain model working data."""
        self._wd = {} if self._wd is None else self._wd
        return self._wd
    @bdm_working_data.setter
    def bdm_working_data(self, value: BDM_WORKING_DATA_OBJECT) -> None:
        """Set the budget domain model working data."""
        self._wd = {} if self._wd is None else self._wd
        self._wd = value

    @property
    def bdm_data_context(self) -> DATA_CONTEXT:
        """The budget domain model data context values."""
        self._data_context = {} if self._data_context is None else self._data_context
        return self._data_context
    @bdm_data_context.setter
    def bdm_data_context(self, value: DATA_CONTEXT) -> None:
        """Set the budget domain model working data."""
        self._data_context = value

    #BDMBaseInterface properties
    @property
    def model_id(self) -> str:
        """Return the model ID."""
        return __class__.__name__ + "-" + self.bdm_id

    #endregion BudgetDomainModel (BDM)) properties
    # ------------------------------------------------------------------------ +
    #endregion BudgetDomainModel class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    BDM - Budget Domain Model methods
    """ Budget Model Domain Model (BDM) Documentation.

    Budget model Domain Model (BDM) is the conceptual model used to track and 
    analyze transactions from financial institutions (FI) overtime for the 
    purpose of following a budget. As a Domain Model, the implementation is 
    the python data structures used to represent the domain data.

    Class BudgetDomainModel is the base class for the budget model domain. As a 
    convention, while designing the structure, I adopted the use of constants
    for names of the various types and fields used for th class properties,
    default values and methods. Also, I adopted a pattern to use the
    BudgetDomainModelTemplate class, a subclass of BudgetDomainModel, as a means
    for storing the template for a budget model used for configuration and
    other conveniences. Each BudgetDomainModel created by a user, may have an 
    associated Budget Manager (BudMan) store. This is referred to as the 
    BDM_STORE and can be used as the configuration template.

    All BDM data storage is the concern of the BSM. BSM works with Path 
    objects, filenames, folders, relative, absolute path names and actual 
    filesystem operations. In the configuration data, the BDM data is stored 
    as strings. Internally, Path objects are used.

    In the BDM, all data is associated with a financial institution (FI). Data 
    is processed by workflow (WF) tasks that are configured for an FI. 
    Each FI has a unique fi_key which the api uses to keep data separated.

    Throughout, the following identifiers are used in reference to parts of
    the BDM.

    BDM_FOLDER - refers to the root folder for the budget model. BDM_FOLDER is 
    a path element, which is a str that will end up as a part of a Path str, 
    which is the BSM concern. See bsm_BDM_FOLDER methods for that.

    FI_FOLDER - refers to the root folder configured for a specific 
    Financial Institutions (FI). FI_FOLDER is a path element, which is a 
    str that will end up as a part of a Path str, which is the BSM concern.
    See bsm_FI_FOLDER methods for that. There is only one FI_FOLDER for
    each FI. The FI_FOLDER is a subfolder of the BDM_FOLDER.

    WF_INPUT_FOLDER - refers to the input folder for a specific workflow, again, 
    always in the context of a specific FI through the fi_key. WF_INPUT_FOLDER is
    a Path with various str reprs.

    WF_INPUT - is a WF_PURPOSE, indicating used for input to a workflow. 
    Likely, workbooks of this type are referenced in the collection of 
    workbooks currently in the WF_INPUT_FOLDER folder.

    WF_WORKING_FOLDER - refers to the folder for a specific workflow. It is
    a Path with various str reprs.

    WF_WORKING - is a WF_PURPOSE, indicating used to work on (input and output) 
    data for a workflow. Likely, workbooks of this type are referenced in the 
    collection of workbooks currently in the WF_WORKING_FOLDER folder. It is
    typical that working data is opened for read and write.

    WF_OUTPUT_FOLDER - refers to the output folder for a specific workflow. It is
    a Path with various str reprs.

    WF_OUTPUT - is a WF_PURPOSE, indicating used for output from a workflow. 
    Likely, workbooks of this type are referenced in the collection of 
    workbooks currently in the WF_OUTPUT_FOLDER folder. A common pattern is
    for a workflow to just copy workbooks to an output folder.

    From the configuration data, the values of BDM_FOLDER, FI_FOLDER and
    WF_FOLDER are used to construct folder and file names for the file system
    and the BSM. The BDM methods do not use Path objects. The overlap seen in 
    the WB_INPUT and WB_OUTPUT for a purpose. The workbooks are
    common in the two layers.
     
    The following naming conventions apply to the purpose of the BDM and BSM 
    methods to  separate the concerns for partial path names, full path names 
    and absolute pathname values..

    Naming Conventions:
    -------------------
    - bm_ - BudgetDomainModel class properties, e.g., bm_folder, bm_fi, etc.
    - fi_ - Related to financial institution, e.g., fi_key, fi_name, etc.
    - wf_ - Related to workflow, e.g., wf_key, wf_name, etc.
    - bdm_ - BudgetDomainModel Domain methods, concerning the in memory data model.
    - bsm_ - BudgetDomainModel Storage Model methods, folders/files stored the filesystem.
    - _path_str - is the simplest string for a path name or component of. These
    methods return str values and do not manipulate with Path objects. Some
    folder values in the BDM, for example, are simply the name of a folder, 
    not a complete path name.
    - _path - constructs a Path object using _path_str values, 
    invokes .expanduser(). 
    _abs_path - invokes .resolve() on _path results, return Path object.
    - Path objects are never serialized to .jsonc files, only _path_str values.

    Abbrevs used in method names: 
        bdm - Budget Model Domain, the domain model of the budget model.
        bms - Budget Storage Model, the filesystem storage model.
        bm - BudgetDomainModel class instance, parent of the Budget Model data structure.
        bf - budget folder - attribute, root folder, used in path objects.
        fi - financial institution dictionary, attribute of bdm.
             fi_key = int_key, short name of FI, e.g., "boa", "chase", etc.
             fi_value = dict of info about the FI.
        wf - workflow
    """
    # ======================================================================== +
    #region    BDM bdm_initialize(self, bsm_init, ...)
    def bdm_initialize(self, 
                 bsm_init : bool = True,
                 create_missing_folders : bool = True,
                 raise_errors : bool = True
                 ) -> "BudgetDomainModel":
        """Initialize BDM, from a config_object.

        Currently, as a singleton class, BudgetDomainModel is initialized just once.
        So, having a resolved config_object Dict is important, lest not much
        can be initialized. That is the concern of bdm_resolve_config_src().

        Args:
            bsm_init (bool): Initialize the BSM if True.
            create_missing_folders (bool): Create missing folders if True.
            raise_errors (bool): Raise errors if True.
        """
        st = p3u.start_timer()
        logger.info(f"BizEVENT: Model setup for BudgetDomainModel (BDM)")
        try:
            # A valid bdm_config_object dictionary created by one of the methods on the
            # BDMConfig class is required here. Here is is just added to the
            # BDM_STORE_OBJECT property. The real work happens in bdm_initialize().
            if self.bdm_store_object is None:
                m = "bdm_config_object property is None, must be a valid configuration dictionary "
                m += "created by one of the BDMConfig methods prior to BudgetDomainModel().bdm_initialize()." 
                logger.error(m)
                raise ValueError(m)
            # Apply the configuration to the budget model (self)
            # No defaults here, the bdm_config_object must have all keys and values.
            bdm_config = self.bdm_store_object
            setattr(self, BDM_ID, bdm_config.get(BDM_ID))
            setattr(self, BDM_STORE_OBJECT, bdm_config)
            setattr(self, BDM_INITIALIZED, bdm_config.get(BDM_INITIALIZED))
            setattr(self, BDM_FILENAME, bdm_config.get(BDM_FILENAME))
            setattr(self, BDM_FILETYPE, bdm_config.get(BDM_FILETYPE))
            setattr(self, BDM_FOLDER, bdm_config.get(BDM_FOLDER))  
            setattr(self, BDM_URL, bdm_config.get(BDM_URL))  
            setattr(self, BDM_FI_COLLECTION, copy.deepcopy(bdm_config[BDM_FI_COLLECTION]))
            setattr(self, BDM_WF_COLLECTION, copy.deepcopy(bdm_config[BDM_WF_COLLECTION])) 
            setattr(self, BDM_OPTIONS, copy.deepcopy(bdm_config[BDM_OPTIONS]))
            setattr(self, BDM_CREATED_DATE, bdm_config[BDM_CREATED_DATE]) 
            setattr(self, BDM_LAST_MODIFIED_DATE, bdm_config[BDM_LAST_MODIFIED_DATE])
            setattr(self, BDM_LAST_MODIFIED_BY, bdm_config[BDM_LAST_MODIFIED_BY])
            setattr(self, BDM_WORKING_DATA, {})
            setattr(self, BDM_DATA_CONTEXT, bdm_config[BDM_DATA_CONTEXT])

            if bsm_init:
                self.bsm_initialize(create_missing_folders, raise_errors)
                all_workbooks = self.bsm_WORKBOOKS_discover()
            self.bdm_working_data = self.bdm_BDM_WORKING_DATA_initialize()
            self.bdm_initialized = True
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
            return self
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM bdm_initialize(self, bsm_init, ...) 
    # ------------------------------------------------------------------------ +
    #region    BDM FI_OBJECT methods
    def bdm_FI_OBJECT(self, fi_key:str) -> FI_OBJECT:
        """Return the FI_OBJECT for fi_key."""
        self.bdm_FI_KEY_validate(fi_key)
        return self.bdm_fi_collection[fi_key]
    
    def bdm_FI_KEY(self, fi_key:str) -> str:
        """Return the FI_KEY value of the FI_OBJECT for fi_key.."""
        return self.bdm_FI_OBJECT(fi_key)[FI_KEY]

    def bdm_FI_NAME(self, fi_key:str) -> str:
        """Return the FI_NAME value of the FI_OBJECT for fi_key.."""
        return self.bdm_FI_OBJECT(fi_key)[FI_NAME]
    
    def bdm_FI_TYPE(self, fi_key:str) -> str:
        """Return the FI_TYPE value of the FI_OBJECT for fi_key.."""
        return self.bdm_FI_OBJECT(fi_key)[FI_TYPE]

    def bdm_FI_FOLDER(self, fi_key:str) -> str:
        """Return the FI_FOLDER value of the FI_OBJECT for fi_key."""
        return self.bdm_FI_OBJECT(fi_key)[FI_FOLDER]
    
    def bdm_FI_WORKFLOW_DATA_COLLECTION(self, fi_key:str) -> DATA_COLLECTION:
        """Return the DATA_COLLECTION object of the FI_OBJECT for fi_key."""
        return self.bdm_FI_OBJECT(fi_key)[FI_WORKFLOW_DATA_COLLECTION]

    def bdm_FI_WORKBOOK_DATA_COLLECTION(self, fi_key:str) -> DATA_COLLECTION:
        """Return the FI_WORKBOOK_COLLECTION object of the FI_OBJECT for fi_key."""
        return self.bdm_FI_OBJECT(fi_key)[FI_WORKBOOK_DATA_COLLECTION]

    def bdm_FI_WORKFLOW_DATA_COLLECTION_count(self, fi_key:str) -> int:
        """Return a count of objects in the FI_DATA_COLLECTION."""
        fi_data_collection = self.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key)
        if fi_data_collection is None:
            return 0
        if not isinstance(fi_data_collection, dict):
            m = f"FI_DATA_COLLECTION is not a dict: {type(fi_data_collection)}"
            logger.error(m)
            raise ValueError(m)
        return len(fi_data_collection)

    def bdm_FI_WORKBOOK_DATA_COLLECTION_set(self, fi_key:str, value:DATA_COLLECTION) -> DATA_COLLECTION:
        """Set the FI_WORKBOOK_COLLECTION object of the FI_OBJECT for fi_key."""
        try:
            self.bdm_FI_OBJECT(fi_key)[FI_WORKBOOK_DATA_COLLECTION] = value
            return
        except Exception as e:
            m = f"Error setting FI_WORKBOOK_COLLECTION for fi_key '{fi_key}': {p3u.exc_err_msg(e)}"
            logger.error(m)
            raise ValueError(m)

    def bdm_FI_KEY_validate(self, fi_key:str) -> bool:
        """Validate the financial institution key."""
        if fi_key not in self.bdm_fi_collection and fi_key != ALL_KEY:
            m = f"Financial Institution '{fi_key}' not 'all' or not found in "
            m += f"{self.bdm_fi_collection.keys()}"
            logger.error(m)
            raise ValueError(m)
        return True
    #endregion BDM FI_OBJECT methods
    # ------------------------------------------------------------------------ +
    #region    BDM FI_WF_OBJECT WORKFLOW_DATA_COLLECTION methods
    def bdm_WORKFLOW_DATA_COLLECTION(self, fi_key:str, wf_key : str) -> DATA_OBJECT:
        """Return the WF_DATA_OBJECT value for fi_key, wf_key."""
        if self.bdm_FI_WORKFLOW_DATA_COLLECTION_count(fi_key) == 0:
            return None
        if self.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key) is None:
            return None
        if wf_key not in self.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key).keys():
            return None
        return self.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key)[wf_key]
    
    def bdm_WORKBOOK_DATA_LIST(self, 
                                fi_key:str, wf_key:str, 
                                wf_purpose:str) -> WORKBOOK_DATA_LIST:
        """Return the WORKBOOK_DATA_LIST for the specified fi_key, wf_key, wf_purpose."""
        if not self.bdm_FI_KEY_validate(fi_key):
            m = f"Invalid financial institution key '{fi_key}'."
            logger.error(m)
            raise ValueError(m)
        if not self.bdm_WF_KEY_validate(wf_key):
            m = f"Invalid workflow key '{wf_key}'."
            logger.error(m)
            raise ValueError(m)
        if wf_purpose not in VALID_WF_PURPOSE_VALUES:
            m = f"Invalid workbook type '{wf_purpose}' for workflow '{wf_key}'."
            logger.error(m)
            raise ValueError(m)
        wb_data_collection = self.bdm_WORKFLOW_DATA_COLLECTION(fi_key, wf_key)
        if wb_data_collection is None:
            return None
        if wf_purpose not in wb_data_collection.keys():
            return None
        # Capture the WORKBOOK_DATA_LIST for the specified wf_purpose.
        wb_data_list = wb_data_collection[wf_purpose]
        if wb_data_list is None:
            return None
        if not isinstance(wb_data_list, list):
            m = f"FI_DATA '{fi_key}' '{wf_key}' is not a WORKBOOK_DATA_LIST"
            m += f"{type(wb_data_list)}"
            logger.error(m)
            raise ValueError(m)
        return wb_data_list

    def bdm_FI_WF_WORKBOOK_DATA_LIST_count(self,
                                fi_key:str, wf_key:str, wb_type:str) -> int:
        """Return a count of WORKBOOK_DATA_LIST in the FI_DATA for fi_key, wf_key."""
        wf_wbl = self.bdm_WORKBOOK_DATA_LIST(fi_key, wf_key, wb_type)
        if wf_wbl is None:
            return 0
        if not isinstance(wf_wbl, list):
            m = f"FI_DATA '{fi_key}' '{wf_key}' is not a WORKBOOK_DATA_LIST"
            m += f"{type(wf_wbl)}"
            logger.error(m)
            raise ValueError(m)
        return len(wf_wbl)
    #endregion BDM FI_WF_OBJECT WORKFLOW_DATA_COLLECTION methods
    # ------------------------------------------------------------------------ +
    #region    BDM WF_OBJECT Dict attribute getter methods
    def bdm_WF_OBJECT(self, wf_key:str) -> WF_OBJECT:
        """Return the WF_OBJECT specified wf_key."""
        self.bdm_WF_KEY_validate(wf_key)
        return self.bdm_wf_collection[wf_key]
    
    def bdm_WF_OBJECT_count(self) -> int:
        """Return a count of WF_OBJECTS in the BDM_WF_COLLECTION."""
        if self.bdm_wf_collection is None:
            return 0
        if not isinstance(self.bdm_wf_collection, dict):
            m = f"BDM_WF_COLLECTION is not a dict, "
            m+= "but type: {type(self.bdm_wf_collection)}"
            logger.error(m)
            raise ValueError(m)
        return len(self.bdm_wf_collection)
    
    def bdm_WF_KEY(self, wf_key:str) -> str:
        """Return the WF_KEY value the WF_OBJECT for wf_key."""
        return self.bdm_WF_OBJECT(wf_key)[WF_KEY]

    def bdm_WF_NAME(self, wf_key:str) -> str:
        """Return the WF_NAME value for wf_key."""
        return self.bdm_WF_OBJECT(wf_key)[WF_NAME]
    
    def bdm_WF_FOLDER(self, wf_key:str, folder_id : str) -> str:
        """Return the WF_FOLDER value for (wf_key, folder_id).
        Not a full path, just the configuration value."""
        if folder_id not in WF_FOLDER_PATH_ELEMENTS:
            m = f"Invalid folder_id '{folder_id}' for workflow '{wf_key}'."
            logger.error(m)
            raise ValueError(m)
        return self.bdm_WF_OBJECT(wf_key)[folder_id]
    
    def bdm_WF_PREFIX_IN(self, wf_key:str) -> str:
        """Return the WF_PREFIX_IN value for wf_key."""
        return self.bdm_WF_OBJECT(wf_key)[WF_PREFIX_IN]
    
    def bdm_WF_PREFIX_OUT(self, wf_key:str) -> str:
        """Return the WF_PREFIX_OUT value for wf_key."""
        return self.bdm_WF_OBJECT(wf_key)[WF_PREFIX_OUT]    
    
    def bdm_WF_PURPOSE_FOLDER_MAP(self, wf_key:str, wf_purpose:str=None) -> str|dict:
        """Return the WF_PURPOSE_FOLDER_MAP or specific mapped value for wb_type."""
        if wf_purpose is None:
            return self.bdm_WF_OBJECT(wf_key)[WF_PURPOSE_FOLDER_MAP]
        return self.bdm_WF_OBJECT(wf_key)[WF_PURPOSE_FOLDER_MAP][wf_purpose]

    def bdm_WF_KEY_validate(self, wf_key:str) -> bool:
        """Validate the workflow key."""
        supp_wf = self.bdm_wf_collection
        if supp_wf is None or (wf_key not in supp_wf and wf_key != ALL_KEY):
            m = f"Workflow('{wf_key}') is not 'all' and not found in "
            m += f"{str(self.bdm_wf_collection)}"
            logger.error(m)
            raise ValueError(m)
        return True
    #endregion BDM WF_OBJECT pseudo-Object properties
    # ------------------------------------------------------------------------ +
    #region    BDM_WORKING_DATA bdm_BDM_WORKING_DATA_initialize() 
    def bdm_BDM_WORKING_DATA_initialize(self, override:bool=False) -> BDM_WORKING_DATA_OBJECT:
        """Initialize BDMWD, the budget domain working data.
        
        When BudgetDomain Model is initialized, the BDM_WORKING_DATA property is
        initialized here. It should be the last step in the initialization 
        sequence, because it captures values based on the BDM state.

        Assume that bdm_initialize() set bdm_working_data to an empty dict 
        object. Only initialize if the current value is None or empty, unless
        override is True. 

        Note: use the get_BDM_WORKING_DATA() and 
        set_BDM_WORKING_DATA() methods to access the working data.
        """
        try:
            logger.debug("Start: ...")
            # If the BDM_WORKING_DATA is already initialized, return it.
            if (hasattr(self, BDM_WORKING_DATA) and
                isinstance(self.bdm_working_data, dict) and
                BDMWD_INITIALIZED in self.bdm_working_data and
                self.bdm_working_data[BDMWD_INITIALIZED] and
                not override):
                logger.debug("BDM_WORKING_DATA already initialized, returning.")
                return self.bdm_working_data
            
            # Gather default values from the application settings.
            # TODO: Fix this when bdmwd is free
            def_fi = VALID_FI_KEYS[0]
            def_wf = BDM_WF_CATEGORIZATION
            def_wfp = WF_WORKING
            def_wbt = WB_TYPE_EXCEL_TXNS
            # Initialize the budget model working data.
            self.bdm_working_data = {}
            self.set_BDM_WORKING_DATA(BDMWD_INITIALIZED, False)
            self.set_BDM_WORKING_DATA(BDMWD_FI_KEY, def_fi)
            self.set_BDM_WORKING_DATA(BDMWD_WF_KEY, def_wf)
            self.set_BDM_WORKING_DATA(BDMWD_WF_PURPOSE, def_wfp)
            self.set_BDM_WORKING_DATA(BDMWD_WB_TYPE, def_wbt)
            self.set_BDM_WORKING_DATA(BDMWD_WB_NAME, None)
            self.set_BDM_WORKING_DATA(BDMWD_WORKBOOKS, list())
            self.set_BDM_WORKING_DATA(BDMWD_LOADED_WORKBOOKS, dict())
            # Now resolve the bdwd content to current BDM state.
            self.bdmwd_WORKBOOKS_resolve(initializing=True)
            # BDMWD initialization is now complete.
            self.set_BDM_WORKING_DATA(BDMWD_INITIALIZED, True)
            logger.debug("Complete: BDM_WORKING_DATA initialized.")
            return self.bdm_working_data
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion   BDM_WORKING_DATA bdm_BDM_WORKING_DATA_initialize() 
    # ------------------------------------------------------------------------ +
    #endregion BDM - Budget Domain Model methods
    # ======================================================================== +

    # ======================================================================== +
    #region    BSM - Budget Storage Model methods
    """ Budget model Storage Model (BSM) Documentation.

    All BDM data is stored in the filesystem by the BSM. BSM works with Path 
    objects, filenames, folders, relative, absolute path names and actual 
    filesystem operations. In the configuration data, the BDM data is stored 
    as strings. Internally, Path objects are used.

    In the BDM, all data is associated with a financial institution (FI). Data 
    is processed by workflows (WF) that are configured for an FI. Hence,
    in all cases the BSM requires an fi_key to identify which FI's data is being
    processed. The wf_key, identifying a particular workflow, is also used
    in the BSM methods, because naming conventions for folder and files are 
    based on the workflow settings.

    Throughout, the following identifiers are used as a convention:
    
    FI_FOLDER - refers to the root folder configured for a specific 
    Financial Institutions (FI). FI_FOLDER is a Path with various str reprs.

    WF_INPUT_FOLDER - refers to the input folder for a specific workflow, again, 
    always in the context of a specific FI through the fi_key. WF_INPUT_FOLDER is
    a Path with various str reprs.

    WB_INPUT - refers to the type of workbooks currently in the 
    WF_INPUT_FOLDER folder.

    WF_OUTPUT_FOLDER - refers to the output folder for a specific workflow. It is
    a Path with various str reprs.

    WB_OUTPUT - refers to the type of workbooks currently in 
    the WF_OUTPUT_FOLDER folder.

    The configuration data and stored budget model data contains str values 
    that are utilized in path names for folders and files. The following 
    naming conventions apply to the purpose of the BDM and BSM methods to 
    separate the concerns for partial path names, full path names and absolute
    pathname values..

    Naming Conventions:
    -------------------
    - bm_ - BudgetDomainModel class properties, e.g., bm_folder, bm_fi, etc.
    - fi_ - Related to financial institution, e.g., fi_key, fi_name, etc.
    - wf_ - Related to workflow, e.g., wf_key, wf_name, etc.
    - bdm_ - BudgetDomainModel methods, concerning the in memory data model.
    - bsm_ - BudgetDomainModel Storage Model methods, folders/files stored the filesystem.
    - _path_str - is the simplest string for a path name or component of. These
    methods return str values and do not manipulate with Path objects. Some
    folder values in the BDM, for example, are simply the name of a folder, 
    not a complete path name.
    - _path - constructs a Path object using _path_str values, 
    invokes .expanduser(). 
    _abs_path - invokes .resolve() on _path results, return Path object.
    - Path objects are never serialized to .jsonc files, only _path_str values.

    Abbrevs used in method names: 
        bdm - Budget Model Domain, the domain model of the budget model.
        bms - Budget Storage Model, the filesystem storage model.
        bm - BudgetDomainModel class instance, parent of the Budget Model data structure.
        bf - budget folder - attribute, root folder, used in path objects.
        fi - financial institution dictionary, attribute of bdm.
             fi_key = int_key, short name of FI, e.g., "boa", "chase", etc.
             fi_value = dict of info about the FI.
        wf - workflow
    """
    # ======================================================================== +
    #region bsm_initialize() method
    def bsm_initialize(self, 
                        create_missing_folders:bool=True,
                        raise_errors:bool=True) -> "BudgetDomainModel":
        """Initialize BSM aspects of the BDM.
        
        Examine elements of self, the BudgetDomainModel class, as initialized
        so far from configuration (BDM_STORE, or Template). Validate the 
        BDM data dependent on folders and files in the filesystem. Flags control 
        whether to create the filesystem structure if it is not present. Also 
        scan the workflow folders for the presence of workbook excel files and 
        resolve their references from the BDM as appropriate.

        During resolution, differences between the workbooks referenced in the
        BDM thus far from the configuration and the actual workbooks in the
        filesystem are detected. The BDM might reference a workbook which is
        no longer present in the BSM. The BSM may discover a workbook in the
        filesystem which is not referenced in the BDM. 

        TODO: Re-visit the options needed to control the behavior of the BSM
        when it encounters a workbook in the filesystem which is not referenced
        in the BDM. The BSM should be able to add that workbook to the BDM
        and update the BDM to reflect that. The BSM should also be able to
        remove a workbook from the BDM if it is no longer present in the
        filesystem. The BDM_STORE should be updated to reflect these changes.

        Args:
            create_missing_folders (bool): Create missing folders if True.
            raise_errors (bool): Raise errors if True.
        """
        st = p3u.start_timer()
        # Plan: validate filesystem folders: bf, fi, wf
        #       update the BDM workbook mappings to BSM 
        try:
            logger.info("BizEVENT: Model setup for BudgetStorageModel (BSM)")
            self.bsm_BDM_FOLDER_resolve(create_missing_folders, raise_errors)
            # Enumerate the financial institutions.
            _ = [self.bsm_FI_initialize(fi_key, create_missing_folders, raise_errors) 
                   for fi_key, fi_object in self.bdm_fi_collection.items()]                
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
            return self
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion bsm_initialize() method
    # ------------------------------------------------------------------------ +    
    #region bsm_FI_initialize() method
    def bsm_FI_initialize(self, fi_key : str, 
                        create_missing_folders:bool=True,
                        raise_errors:bool=True) -> bool:
        """Initialize BSM aspects for a financial institution.
        
        Examine elements of self for the financial institution indicated by
        fi_key. Validate the mapping of the BDM data dependent on mapping to 
        folders and files in the filesystem. Flags control whether to create the
        filesystem structure if it is not present. Also scan the workflow 
        folders for the presence of workbook excel files and load their 
        references into the BDM as appropriate.

        Args:
            fi_key (str): The financial institution key.
            create_missing_folders (bool): Create missing folders if True.
            raise_errors (bool): Raise errors if True.
            
        Returns:
            bool: True if successful, False otherwise.

        Raises:
            TypeError: If the financial institution key is not a string.
            ValueError: If the financial institution key is not valid.
            Exception: If there is an error during initialization.
        """
        st = p3u.start_timer()
        # Plan: validate filesystem folders: bf, fi, wf
        #       update the BDM workbook mappings to BSM 
        try:
            logger.debug("Start: ...")
            p3u.str_empty(fi_key, raise_error=True) # Raises TypeError, ValueError
            # Resolve FI_FOLDER path.
            self.bsm_FI_FOLDER_resolve(fi_key, 
                                        create_missing_folders, raise_errors)
            # Resolve WF_FOLDER paths for the workflows.
            self.bsm_WF_FOLDER_resolve(fi_key, 
                                        create_missing_folders, raise_errors)
            # Resolve the FI_DATA collection, refresh actual
            # data from folders in BSM.
            self.bsm_FI_DATA_COLLECTION_resolve(fi_key)
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
            return True
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion bsm_FI_initialize() method
    # ------------------------------------------------------------------------ +    
    #region BDM_FOLDER Path methods
    def bsm_BDM_FOLDER_validate(self) -> bool:
        """Validate the bm_folder property setting.
        
        Raise a ValueError if the bm_folder property is not set or is not
        usable as part of a valid path string.
        """
        # TODO: expand and resolve flags?
        if self.bdm_folder is None or len(self.bdm_folder) == 0:
            m = f"Budget folder path is not set. "
            m += f"Set the BDM_FOLDER('{BDM_FOLDER}') property to valid path value."
            logger.error(m)
            raise ValueError(m)
        return True
    def bsm_BDM_FOLDER_path_str(self) -> str:
        """str version of the BDM_FOLDER value as a Path."""
        # In the BSM, the bm_folder property must be a valid setting that will
        # result in a valid Path. Raise a ValueError if not.
        self.bsm_BDM_FOLDER_validate() # Raises ValueError if not valid
        return str(Path(self.bdm_folder))
    def bsm_BDM_FOLDER_path(self) -> Path:
        """Path of self.bsm_BDM_FOLDER_path_str().expanduser()."""
        return Path(self.bsm_BDM_FOLDER_path_str()).expanduser()
    def bsm_BDM_FOLDER_abs_path(self) -> Path:
        """Path of self.bsm_BDM_FOLDER_path().resolve()."""
        return self.bsm_BDM_FOLDER_path().resolve()
    def bsm_BDM_FOLDER_abs_path_str(self) -> str:
        """str of self.bsm_BDM_FOLDER_abs_path()."""
        return str(self.bsm_BDM_FOLDER_abs_path())
    
    def bsm_BDM_FOLDER_resolve(self, 
                              create_missing_folders : bool=True,
                              raise_errors : bool=True) -> None:
        """Resolve the BDM_FOLDER path and create it if it does not exist."""
        try:
            logger.debug(f"Checking BDM_FOLDER path: '{self.bdm_folder}'")
            if self.bdm_folder is None:
                m = f"Budget folder path is not set. "
                m += f"Set the '{BDM_FOLDER}' property to a valid path."
                logger.error(m)
                raise ValueError(m)
            # Resolve the BDM_FOLDER path.
            bf_ap = self.bsm_BDM_FOLDER_abs_path()
            bsm_verify_folder(bf_ap, create_missing_folders, raise_errors)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_FOLDER Path methods
    # ------------------------------------------------------------------------ +
    #region BDM_URL Path methods
    def bsm_BDM_URL_validate(self) -> bool:
        """Validate the BDM_URL property setting.
        
        Raise a ValueError if the BDM_URL property is not set or is not
        usable as part of a valid path string.
        """
        # TODO: expand and resolve flags?
        if self.bdm_url is None or not isinstance(self.bdm_url,str) or len(self.bdm_url) == 0:
            m = f"BDM_URL value is not set to a non-zero length str. "
            m += f"Set the BDM_URL('{BDM_URL}') property to valid path str."
            logger.error(m)
            raise ValueError(m)
        return True
    def bsm_BDM_URL_path_str(self) -> str:
        """str version of the BDM_URL validated as a Path."""
        # In the BSM, the BDM_URL property must be a valid setting that will
        # result in a valid Path. Raise a ValueError if not.
        self.bsm_BDM_URL_validate() # Raises ValueError if not valid
        return str(Path(self.bdm_url))
    def bsm_BDM_URL_path(self) -> Path:
        """Path of self.bsm_BDM_URL_path_str().expanduser()."""
        return Path(self.bsm_BDM_URL_path_str()).expanduser()
    def bsm_BDM_URL_abs_path(self) -> Path:
        """Path of self.bsm_BDM_URL_path().resolve()."""
        return self.bsm_BDM_URL_path().resolve()
    def bsm_BDM_URL_abs_path_str(self) -> str:
        """str of self.bsm_BDM_URL_abs_path()."""
        return str(self.bsm_BDM_URL_abs_path())
    
    def bsm_BDM_URL_resolve(self, 
                              create_missing_folders : bool=True,
                              raise_errors : bool=True) -> None:
        """Resolve the BDM_URL path and create it if it does not exist."""
        try:
            logger.debug(f"Checking BDM_URL path: '{self.bdm_url}'")
            if self.bdm_url is None:
                m = f"Budget folder path is not set. "
                m += f"Set the '{BDM_URL}' property to a valid path."
                logger.error(m)
                raise ValueError(m)
            # Resolve the BDM_URL path.
            bf_ap = self.bsm_BDM_URL_abs_path()
            bsm_verify_folder(bf_ap, create_missing_folders, raise_errors)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BDM_URL Path methods
    # ------------------------------------------------------------------------ +
    #region FI_DATA FI_FOLDER Path methods
    def bsm_FI_FOLDER_path_str(self, fi_key: str) -> str:
        """str version of the FI_FOLDER value as a Path.
        
        Raises ValueError for invalid settings for any of: bm_folder property,
        fi_key, of FI_FOLDER value of FI dictionary."""
        bf_p_s = self.bsm_BDM_FOLDER_path_str() # ValueError on BDM_FOLDER property
        self.bdm_FI_KEY_validate(fi_key) # ValueError fi_key
        fi_p_s = str(Path(self.bdm_FI_FOLDER(fi_key))) 
        if fi_p_s is None or len(fi_p_s) == 0:
            m = f"FI_FOLDER value is not set for FI_KEY('{fi_key}'). "
            m += f"In the BudgetDomainModel configuration, correct FI_FOLDER setting."
            logger.error(m)
            raise ValueError(m)   
        return str(Path(bf_p_s) / fi_p_s)
    def bsm_FI_FOLDER_path(self, fi_key: str) -> Path:
        """Path of self.bsm_FI_FOLDER_path_str().expanduser()."""
        return Path(self.bsm_FI_FOLDER_path_str(fi_key)).expanduser()
    def bsm_FI_FOLDER_abs_path(self, fi_key: str) -> Path:
        """Path of self.bsm_FI_FOLDER_path().resolve()."""
        return Path(self.bsm_FI_FOLDER_path(fi_key)).resolve()
    def bsm_FI_FOLDER_abs_path_str(self, fi_key: str) -> str:
        """str of self.bsm_FI_FOLDER_abs_path()."""
        return str(self.bsm_FI_FOLDER_abs_path(fi_key))
    def bsm_FI_FOLDER_resolve(self, fi_key : str,
                              create_missing_folders : bool=True,
                                raise_errors : bool=True) -> None: 
        """Resolve the FI_FOLDER path and create it if it does not exist."""
        fi_ap = self.bsm_FI_FOLDER_abs_path(fi_key)
        logger.debug(f"FI_KEY('{fi_key}') Checking FI_FOLDER('{fi_ap}')")
        bsm_verify_folder(fi_ap, create_missing_folders, raise_errors)
    #endregion FI_DATA FI_FOLDER Path methods
    # ------------------------------------------------------------------------ +   
    #region bsm_WORKBOOKS_discover() method
    def bsm_WORKBOOKS_discover(self) -> Dict[str, DATA_COLLECTION]:
        """Discover WORKBOOKS for all FI's in the BDM."""
        try:
            logger.debug("Start:")
            all_wbc = {}
            if len(self.bdm_fi_collection) == 0:
                m = f"No FI's to discover."
                logger.debug(m)
                return
            for fi_key in self.bdm_fi_collection.keys():
                # Discover WORKBOOKS for each FI.
                logger.debug(f"Discover WORKBOOKS for FI_KEY('{fi_key}')")
                wbc = self.bsm_FI_WORKFLOW_DATA_COLLECTION_discover(fi_key)
                all_wbc[fi_key] = wbc
            # Now have scanned all of the BDM storage to capture all BDMWorkbooks
            # as a Dict[fi_key, BDMWorkbook] return the combined collection.
            logger.debug("Complete:")
            return all_wbc
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion bsm_WORKBOOKS_discover() method
    # ------------------------------------------------------------------------ +   
    #region bsm_FI_WORKFLOW_DATA_COLLECTION_discover() method
    def bsm_FI_WORKFLOW_DATA_COLLECTION_discover(self, fi_key:str) -> WORKBOOK_DATA_COLLECTION:
        """Discover all WORKBOOKS for the FI. Return a DATA_COLLECTION of BDMWorkbook objects."""
        try:
            logger.debug(f"Start: FI_KEY('{fi_key}') discover WORKBOOKS")
            if self.bdm_FI_WORKFLOW_DATA_COLLECTION_count(fi_key) == 0:
                m = f"FI_KEY('{fi_key}') has no workflow data."
                logger.debug(m)
                return
            # Traverse the FI_OBJECT's FI_WORKFLOW_DATA_COLLECTION structure, 
            # compile a list of WORKBOOKS as BDMWorkbook objects with populated
            # metadata. Then reconcile list with the FI_WORKBOOK_DATA_COLLECTION.
            # In progress refactoring in favor of the FI_WORKBOOK_DATA_COLLECTION 
            # to eliminate the FI_WORKFLOW_DATA_COLLECTION.
            wb_collection = {}
            for wf_key, wb_data_collection in self.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key).items():
                for wf_purpose, wb_data_list in wb_data_collection.items():
                    folder_id = self.bdm_WF_PURPOSE_FOLDER_MAP(wf_key, wf_purpose)
                    if folder_id is None or len(folder_id) == 0:
                        m = f"wb_data_collection('{fi_key}', '{wf_key}') has no '{wf_purpose}' wb_data_list."
                        logger.debug(m)
                        continue
                    wf_folder = self.bdm_WF_FOLDER(wf_key, folder_id)
                    if wf_folder is None or len(wf_folder) == 0:
                        m = f"wb_data_collection('{fi_key}', '{wf_key}') has no '{wf_purpose}' wf_folder."
                        logger.debug(m)
                        continue
                    wb_paths = []
                    id = f"('{fi_key}', '{wf_key}', '{wf_purpose}', '{folder_id}')"
                    folder_abs_path = self.bsm_WF_FOLDER_abs_path(fi_key, wf_key, folder_id)
                    if folder_abs_path is None: 
                        m = f"'{id}' wf_folder path  is None.",
                        logger.debug(m)
                        continue
                    if not folder_abs_path.exists():
                        m = f"'{id}' path does not exist: {folder_abs_path}"
                        logger.debug(m)
                        continue
                    # This is where the bsm scans a folder for actual workbook files.
                    wb_paths = bsm_get_workbook_names2(folder_abs_path)
                    if len(wb_paths) == 0:
                        m = f"'{id}' path has no workbooks: {folder_abs_path}"
                        logger.debug(m)
                        continue
                    logger.debug(f"'{id}' found {len(wb_paths)} workbooks: {folder_abs_path}")
                    for wb_path in wb_paths:
                        # Create a BDMWorkbook object for each workbook.
                        wb_filename = wb_path.stem
                        wb_filetype = wb_path.suffix.lower()
                        wb_name = wb_path.name
                        wb_url = wb_path.as_uri()
                        wb = BDMWorkbook(
                            wb_name = wb_name, 
                            wb_filename =  wb_filename,
                            wb_filetype = wb_filetype,
                            wb_url = wb_url,
                            fi_key= fi_key,
                            wf_key = wf_key,
                            wf_purpose = wf_purpose,
                            wf_folder_id = folder_id,
                            wf_folder = wf_folder,
                            wb_loaded = False
                            )
                        wb_id = wb.wb_id
                        wb_collection[wb_id] = wb
            # Now have scanned all of the BSM storage to capture all BDMWorkbooks
            # from the FI_WORKFLOW_DATA_COLLECTION structure mapped to storage.
            # Now reconcile the list of BDMWorkbook objects with the 
            # FI_WORKBOOK_DATA_COLLECTION.
            logger.debug(f"FI_KEY('{fi_key}') discovered {len(wb_collection)} workbooks.")
            self.bsm_FI_WORKBOOK_DATA_COLLECTION_reconcile(fi_key, wb_collection)
            logger.debug(f"Complete:")
            return wb_collection
        except Exception as e:
                m = p3u.exc_err_msg(e)
                logger.error(m)
                raise
    #endregion bsm_FI_WORKFLOW_DATA_COLLECTION_discover() method
    # ------------------------------------------------------------------------ + 
    #region bsm_FI_WORKBOOK_DATA_COLLECTION_reconcile() method
    def bsm_FI_WORKBOOK_DATA_COLLECTION_reconcile(self, fi_key:str,
                                                  disc_wdc:WORKBOOK_DATA_COLLECTION) -> None:
        """Reconcile the FI_WORKBOOK_DATA_COLLECTION with the discovered workbooks.
        
        This method reconciles the discovered workbooks with the existing 
        FI_WORKBOOK_DATA_COLLECTION. It updates the BDM to reflect the current
        state of the workbooks in the storage system.
        
        Args:
            fi_key (str): The financial institution key.
            disc_wdc (Dict[str, BDMWorkbook]): The discovered workbooks.
        """
        try:
            logger.debug(f"Start: FI_KEY('{fi_key}') reconcile WORKBOOK_DATA_COLLECTION")
            wdc = self.bdm_FI_WORKBOOK_DATA_COLLECTION(fi_key)
            if len(wdc) == 0:
                m = f"FI_KEY('{fi_key}') has no workflow data."
                logger.debug(m)
                return
            # Enumerate the discoverd WORKFLOW_DATA_COLLECTION (disc_wdc),
            # and test the FI WORKBOOK_DATA_COLLECTION for the presence of each
            # discovered BDMWorkbook. If the BDMWorkbook is not present, add it.
            added : List[str] = []
            for wb_id, wb in disc_wdc.items():
                if wb_id not in wdc:
                    # Add a new discovered workbook.
                    logger.debug(f"FI_KEY('{fi_key}') adding discovered "
                                 f"BDMWorkbook '{wb_id}' to FI_WORKBOOK_DATA_COLLECTION.")
                    wdc[wb_id] = wb
                    added.append(wb_id)
            logger.debug(f"Complete: FI_KEY('{fi_key}') reconciled, added "
                         f"{len(added)} new BDMWorkbook(s) {str(added)}")
        except Exception as e:
                m = p3u.exc_err_msg(e)
                logger.error(m)
                raise
    #endregion bsm_FI_WORKBOOK_DATA_COLLECTION_reconcile() method
    # ------------------------------------------------------------------------ + 
    #region bsm_FI_DATA_COLLECTION_resolve() method
    def bsm_FI_DATA_COLLECTION_resolve(self, fi_key:str) -> None:
        """Resolve the FI_WORKFLOW_DATA for the specified fi_key and wf_key."""
        try:
            if self.bdm_FI_WORKFLOW_DATA_COLLECTION_count(fi_key) == 0:
                m = f"FI_KEY('{fi_key}') has no workflow data."
                logger.debug(m)
                return
            # Enumerate the FI_OBJECT FI_DATA_COLLECTION,
            # which is Dict[wf_key, WORKFLOW_DATA_COLLECTION]. There could be
            # a WORKFLOW_DATA_COLLECTION for each workflow, or none.
            for wf_key, wb_data_collection in self.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key).items():
                # Resolve each WORKFLOW_DATA_COLLECTION.
                self.bsm_WORKFLOW_DATA_COLLECTION_resolve(wb_data_collection,fi_key, wf_key)
        except Exception as e:
                m = p3u.exc_err_msg(e)
                logger.error(m)
                raise
    #endregion bsm_FI_DATA_COLLECTION_resolve() method
    # ------------------------------------------------------------------------ + 
    #region WF_OBJECT WF_FOLDER Path methods
    """WF_FOLDER path name element for a folder path name for a workflow.

    Budget Manager uses the folder pattern to contain data used by a workflow
    for a financial institution. Each FI has a folder under the root
    BDM_FOLDER. Configuration specifies a WF_FOLDER for each workflow, which
    is the name of a folder under the FI_FOLDER. These Path methods are used
    to combine the BDM_FOLDER, FI_FOLDER and WF_FOLDER name elements into
    actual Path objects for use in the BSM.
    """
    def bsm_WF_FOLDER_path_str(self, fi_key : str, wf_key : str,
                               folder_id : str) -> str:
        """str version of the WF_FOLDER value for fi_key/wf_key/folder_id."""
        if folder_id not in WF_FOLDER_PATH_ELEMENTS:
            m = f"Invalid folder_id '{folder_id}' for FI_KEY('{fi_key}') "
            m += f"and WF_KEY('{wf_key}')"
            logger.error(m)
            raise ValueError(m)
        fi_p_s = self.bsm_FI_FOLDER_path_str(fi_key) # FI_FOLDER Path component
        wf_p_s = self.bdm_WF_FOLDER(wf_key, folder_id)
        return str(Path(fi_p_s) / wf_p_s) if wf_p_s is not None else None
    def bsm_WF_FOLDER_path(self, fi_key : str, wf_key : str, 
                           folder_id:str) -> Path:
        """Path of self.bsm_wf_folder_path_str().expanduser()."""
        p_s = self.bsm_WF_FOLDER_path_str(fi_key, wf_key, folder_id)
        return Path(p_s).expanduser() if p_s is not None else None
    def bsm_WF_FOLDER_abs_path(self, fi_key : str, wf_key : str,
                               folder_id : str) -> Path:
        """Path of self.bsm_wf_folder_path().resolve()."""
        p = self.bsm_WF_FOLDER_path(fi_key, wf_key, folder_id)
        return p.resolve() if p is not None else None
    def bsm_WF_FOLDER_abs_path_str(self, fi_key : str, wf_key : str,
                                   folder_id : str) -> str:
        """str of self.bsm_wf_folder_abs_path()."""
        p = self.bsm_WF_FOLDER_abs_path(fi_key, wf_key, folder_id)
        return str(p) if p is not None else None
    def bsm_WF_FOLDER_resolve(self, fi_key:str, 
                              create_missing_folders:bool=True, 
                              raise_errors:bool=True) -> None:
        """Resolve any WF-related folders for the fi_key, create if requested."""
        try:
            logger.debug(f"FI_KEY('{fi_key}') scan all WF_FOLDERs.")
            for wf_key, wf_object in self.bdm_wf_collection.items():
                # Resolve the WF_FOLDER path elements.
                for f_id in WF_FOLDER_PATH_ELEMENTS:
                    wf_in_p = self.bsm_WF_FOLDER_path(fi_key, wf_key, f_id)
                    if wf_in_p is not None:
                        logger.debug(f"FI_KEY('{fi_key}') WF_KEY('{wf_key}') "
                                    f"Checking WF_FOLDER('{f_id}')")
                        bsm_verify_folder(wf_in_p, create_missing_folders, 
                                         raise_errors)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion WF_OBJECT WF_FOLDER Path methods
    # ------------------------------------------------------------------------ +
    #region WORKFLOW_DATA_COLLECTION aka WF_DATA_OBJECT (WF_DO) pseudo-property methods
    """
    A WORKFLOW_DATA_COLLECTION(Dict) is a DATA_OBJECT(Dict) with key/value pairs specific
    to data for a workflow. A wb_data_collection is retrieved with the 
    bdm_FI_WF_DATA_OBJECT() method which could return other types of 
    DATA_OBJECTs in the future. These methods are BSM-related.

    With the BSM, the wb_data_collection properties relating to the storage 
    model are based on the workflow purpose values: WF_INPUT_FOLDER, WF_INPUT, 
    WF_WORKING_FOLDER, WF_WORKING, WF_OUTPUT_FOLDER and WF_OUTPUT. These 
    concern actual access to data in the storage system. 3 workflow purposes
    are defined for each workflow and have corresponding folders mapped to them.
    The WF_PURPOSE_FOLDER_MAP contains the mapping of workflow_purpose to
    workflow_folder, used to map to actual folder paths in a storage system. 
    
    """
    def bsm_WORKFLOW_DATA_COLLECTION_resolve(self, wb_data_collection: WF_DATA_OBJECT,
                                   fi_key : str, wf_key : str):
        """Resolve the WORKFLOW_DATA_COLLECTION based on the keys and values present."""
        try:
            logger.debug(f"FI_KEY('{fi_key}') WF_KEY('{wf_key}')")
            if wb_data_collection is None or len(wb_data_collection) == 0:
                logger.debug(f"  WORKFLOW_DATA_COLLECTION is empty.")
                return
            logger.debug(f"  WORKFLOW_DATA_COLLECTION({len(wb_data_collection)} "
                         f"keys): {str(list(wb_data_collection.keys()))}")
            # Resolve all keys in the WORKFLOW_DATA_COLLECTION, which is a
            # dictionary of workflow purpose values to WORKBOOK_DATA_LISTs, or
            # Dict[wf_purpose, WORKBOOK_DATA_LIST].
            did_workbook_lists = False
            for wf_purpose, wf_do_value in wb_data_collection.items():
                if wf_purpose not in VALID_WF_PURPOSE_VALUES:
                    m = f"Invalid WORKFLOW_DATA_COLLECTION key '{wf_purpose}' "
                    m += f"for FI_KEY('{fi_key}') and WF_KEY('{wf_key}')"
                    logger.error(m)
                    raise ValueError(m)
                if wf_purpose in VALID_WF_PURPOSE_VALUES:
                    if not did_workbook_lists:
                        # Resolve all the WORKBOOK_DATA_LIST for WF_FOLDERs, just once.
                        self.bsm_WF_DATA_OBJECT_WORKBOOKS_resolve(wb_data_collection, fi_key, wf_key)
                        did_workbook_lists = True
                    else:
                        continue
                else:
                    raise NotImplementedError(f"WORKFLOW_DATA_COLLECTION key '{wf_purpose}' ")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
 
    def bsm_WF_DATA_OBJECT_WORKBOOKS_resolve(self, wb_data_collection: WF_DATA_OBJECT, 
                                 fi_key: str, wf_key : str):
        """Resolve all WORKBOOK_DATA_LISTs for WF_FOLDERS(fi_key, wf_key) in the WF_DATA_OBJECT. 

        Workbooks are contained in folders in the filesystem. The folder_id 
        determines the absolute path to the folder, as per the following 
        mapping:
        - WB_INPUT -> WF_INPUT_FOLDER - input folder for the workflow.
        - WB_WORKING -> WF_WORKING_FOLDER - working folder for the workflow.
        - WB_OUTPUT -> WF_OUTPUT_FOLDER - output folder for the workflow.

        Args:
            wf_do (WF_DATA_OBJECT): The workflow data object to resolve.
            fi_key (str): The key of the institution to get the workbooks for.
            wf_key (str): The workflow to get the workbooks for.

        Returns:
            dict { str: str, ... }: A dict of workbook file names and their paths.
        """
        try:
            # TODO: validate parameters.
            for wf_purpose in wb_data_collection.keys():
                # Only handle WF_PURPOSE scope for the workflow.
                # A wb_data_collection may have other keys, but we only care about the workbooks.
                if wf_purpose not in VALID_WF_PURPOSE_VALUES:
                    logger.debug(f"  Skipping WORKFLOW_DATA_COLLECTION key: '{wf_purpose}'")
                    continue
                # Only interested in the WF_PURPOSE key values. Each of them
                # is configured to one WF_FOLDER_PATH_ELEMENT. Get the
                # appropriate folder_id for the WF_PURPOSE.
                f_id = self.bdm_WF_PURPOSE_FOLDER_MAP(wf_key, wf_purpose)
                if f_id is None:
                    logger.debug(f"  FI('{fi_key}') WF('{wf_key}') "
                                f"WF_DO['{wf_purpose}'] is None")
                    continue
                # WORKBOOKS are found in WF_FOLDERS, scan them all.
                # Resolve all folders in this workflow for fi_key, wf_key.
                wb_list = []
                # absolute path to the folder for this workflow and fi_key.
                wf_f_ap = self.bsm_WF_FOLDER_abs_path(fi_key, wf_key, f_id)
                # TODO: refactor the tuple-list concept
                wb_files = bsm_get_workbook_names(wf_f_ap)
                for wb_p in wb_files:
                    wb_name = wb_p.name
                    wb_item = (wb_name, str(wb_p))
                    wb_list.append(wb_item)
                wb_data_collection[wf_purpose] = wb_list # save wb_list to the wf_do
                logger.debug(f"  FI('{fi_key}') WF('{wf_key}') "
                            f"WF_DO['{wf_purpose}'] maps to FOLDER('{f_id}') "
                            f"with {len(wb_list)} workbooks)")
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion WF_DATA_OBJECT (WF_DO) pseudo-property methods
    # ------------------------------------------------------------------------ +   
    #region bsm_WORKBOOKS_LIST_load Methods
    def bsm_WORKBOOKS_LIST_load(self,
                        wbl : WORKBOOK_DATA_LIST = None) -> LOADED_WORKBOOK_COLLECTION: 
        """Load WORKBOOK_DATA_LIST returning a LOADED_WORKBOOK_COLLECTION
        
        A WORKBOOK_DATA_LIST has tuples of wb_name and wb_abs_path. Iterate the
        list and load each one. This is BSM-scope only, loads from the 
        filesystem, no side effects to the BDM or BDMWD.

        Args:
            wbl (WORKBOOK_DATA_LIST): A list of tuples containing the workbook name
            and the absolute path to the workbook file.
        
        Returns:
            LOADED_WORKBOOK_COLLECTION: new Dict[filename,Workbook] loaded workbooks.

        Raises: exceptions from any errors.
        """
        try:
            st = p3u.start_timer()
            if wbl is None:
                logger.warning("No workbooks to load, wbl arg was None.")
                return None
            logger.debug(f"Loading {len(wbl)} workbooks.")
            returned_wbs = {}
            for wb_name, wb_path in wbl:
                wb = load_workbook(filename=wb_path)
                returned_wbs[wb_name] = wb
            logger.debug(f"Complete: Loaded {len(returned_wbs)} workbooks. "
                         f"{p3u.stop_timer(st)}")
            return returned_wbs
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bsm_LOADED_WORKBOOKS_save(self,
                                  lwbl : LOADED_WORKBOOK_COLLECTION,
                                  wbl : WORKBOOK_DATA_LIST) -> None: 
        """Save LOADED_WORKBOOK_COLLECTION to the filesystem.
        
        A LOADED_WORKBOOK_COLLECTION has tuples of wb_name and a loaded Workbook
        object. Iterate the list, obtain the abs_path_str for each wb_name from 
        the provided WORKBOOK_DATA_LIST, and save the workbook. This is BSM-scope 
        only, saves to the filesystem, no side effects to the BDM or BDMWD.

        Args:
            lwbl (LOADED_WORKBOOK_COLLECTION): A list of tuples containing the 
            workbook name and associated loaded Workbook object.
        
        Returns:
            None.

        Raises: exceptions from any errors.
        """
        try:
            if lwbl is None:
                logger.warning("No loaded workbooks to save, lwbl arg was None.")
                return
            if wbl is None:
                logger.warning("No workbooks abs_path_str, wbl arg was None.")
                return None
            for wb_name, wb in lwbl:
                # Find the corresponding workbook path in the WORKBOOK_DATA_LIST.
                for wbn, wb_path in wbl:
                    if wbn == wb_name:
                        break
                wb.save(wb_path)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bsm_FI_WF_WORKBOOKS_generate(self,
                fi_key : str, 
                wf_key : str, 
                wb_type : str) -> Generator[Tuple[str, Workbook], None, None]: 
        """Generate a list of loaded workbooks.
        
        For fi_key,wf_key,wb_type, yield (wb_name, loaded_Workbook).
        
        Yields:
            Tuple[str, Workbook]: a tuple containing the file name the 
            loaded workbook object.
        """
        try:
            wbl = self.bdm_WORKBOOK_DATA_LIST(fi_key, wf_key, wb_type)
            if wbl is None:
                return
            for wb_name, wb_path in wbl:
                wb = load_workbook(filename=wb_path)
                self.bdmwd_LOADED_WORKBOOKS_add(wb_name, wb)
                yield (wb_name, wb)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bsm_FI_WF_WORKBOOK_save(self, wb : Workbook, wb_name: str, 
                               fi_key:str, wf_key:str, wb_type : str):
        """Save workbook output to storage associated (fi_key,wf_key,wb_type).
        
        Map the fi_key and wf_key to the appropriate WF_OUTPUT_FOLDER folder in 
        the filesystem.
        """
        try:
            f_id = self.bdm_WF_PURPOSE_FOLDER_MAP(wf_key, wb_type)
            if f_id is None:
                m = f"Invalid folder_id '{f_id}' for FI_KEY('{fi_key}') "
                m += f"and WF_KEY('{wf_key}')"
                logger.error(m)
                raise ValueError(m)
            fi_wf_ap = self.bsm_WF_FOLDER_abs_path(fi_key, wf_key, f_id)
            # TODO: strip the in_prefix if it is there.
            # Prepend the out_prefix to the workbook name.
            wb_name = f"{self.bdm_WF_PREFIX_OUT(wf_key)}{wb_name}"
            wb_path = fi_wf_ap / wb_name
            wb.save(wb_path)
            logger.info(f"BizEVENT: Saved workbook '{wb_name}' to '{str(fi_wf_ap)}'")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bsm_FI_WF_WORKBOOK_load(self, fi_key:str, wf_key:str, 
                              workbook_name:str) -> Workbook:
        """Load a workbook transaction file for a Financial Institution Workflow.

        ViewModel: This is a ViewModel function, mapping budget domain model 
        to how budget model data is stored in filesystem.

        Args:
            fi_key (str): The key of the institution to load the transaction file for.
            workflow (str): The workflow to load the transaction file from.
            workbook_name (str): The name of the workbook file to load.

        Returns:
            Workbook: The loaded transaction workbook.
        """
        me = self.bsm_FI_WF_WORKBOOK_load
        try:
            # Budget Folder Financial Institution Workflow Folder absolute path
            bffiwfap = self.bsm_FI_FOLDER_wf_abs_path(fi_key, wf_key) 
            wbap = bffiwfap / workbook_name # workbook absolute path
            m = f"BDM: Loading FI_KEY('{fi_key}') WF_KEY('{wf_key}') "
            m += f"workbook('{workbook_name}'): abs_path: '{str(wbap)}'"
            logger.debug(m)
            wb = bsm_WORKBOOK_content_file_load(wbap)
            return wb
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion FI_WF Methods
    # ------------------------------------------------------------------------ +   
    #endregion BSM - Budget Storage Model methods
    # ======================================================================== +

    # ======================================================================== +
    #region    BDMWD - Budget Domain Model Working Data methods - DC Interface
    """ Budget Domain Model Working Data (BDMWD) methods.

    The BDMWD is intended to serve as a transient data store for the
    BudgetDomainModel (BDM) and BudgetStorageModel (BSM). Also, it is intended
    to be a concrete implementation of the BudgetManagerDataContextInterface 
    (BudManDCI). So, the BDMWD methods are a superset of the BudManDCI methods. 
    All BudManDCI required methods are mapped to the BDMWD methods.

    BDMWD methods are used to access the working data in the BDM. The working
    data is used by client packages for ViewModel, View, UX, CLI etc.
    It is transient data derived from the BDM/BSM operations.

    Note: the bdmwd_ prefixed methods only use the 
    get_BDM_WORKING_DATA() and set_BDM_WORKING_DATA() 
    methods to access the BDM_WORKING_DATA property.
    """
    # --------------------------------------------------------------------- +
    #region    BDMWD getter/setter methods.
    def set_BDM_WORKING_DATA(self, key, value) -> None:
        self.bdm_working_data[key] = value

    def get_BDM_WORKING_DATA(self, key) -> Any:
        return self.bdm_working_data.get(key, 0)
    #endregion    BDMWD getter/setter methods.
    # --------------------------------------------------------------------- +
    #region    BDMWD properties
    def _valid_BDMWD(self) -> BDM_WORKING_DATA_OBJECT:
        """Init self.bdm_working_data if it None."""
        try:
            self.bdm_working_data = self.bdm_working_data if self.bdm_working_data else {}
            return self.bdm_working_data
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    
    @property
    def bdmwd_FI_KEY(self) -> str:
        """Return the current BDMWD_FI_KEY value in the BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_FI_KEY not in bdwd:
            self.bdm_working_data[BDMWD_FI_KEY] = None
        return self.bdm_working_data[BDMWD_FI_KEY]
    @bdmwd_FI_KEY.setter
    def bdmwd_FI_KEY(self, value: str) -> None:
        """Set the current BDMWD_FI_KEY value in the BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_FI_KEY] = value

    @property
    def bdmwd_WF_KEY(self) -> str:
        """Return the current BDMWD_WF_KEY value in the BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_WF_KEY not in bdwd:
            self.bdm_working_data[BDMWD_WF_KEY] = None
        return self.bdm_working_data[BDMWD_WF_KEY]
    @bdmwd_WF_KEY.setter
    def bdmwd_WF_KEY(self, value: str) -> None:
        """Set the current BDMWD_WF_KEY value in the BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_WF_KEY] = value

    @property
    def bdmwd_WF_PURPOSE(self) -> str:
        """Return the current BDMWD_WF_PURPOSE value in the BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_WF_PURPOSE not in bdwd:
            self.bdm_working_data[BDMWD_WF_PURPOSE] = None
        return self.bdm_working_data[BDMWD_WF_PURPOSE]
    @bdmwd_WF_PURPOSE.setter
    def bdmwd_WF_PURPOSE(self, value: str) -> None:
        """Set the current BDMWD_WF_PURPOSE value in the BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_WF_PURPOSE] = value

    @property
    def bdmwd_WB_TYPE(self) -> str:
        """Return the current BDMWD_WB_TYPE value in the BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_WB_TYPE not in bdwd:
            self.bdm_working_data[BDMWD_WB_TYPE] = None
        return self.bdm_working_data[BDMWD_WB_TYPE]
    @bdmwd_WB_TYPE.setter
    def bdmwd_WB_TYPE(self, value: str) -> None:
        """Set the current BDMWD_WB_TYPE value in the BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_WB_TYPE] = value

    @property
    def bdmwd_WB_NAME(self) -> str:
        """Return the current BDMWD_WB_NAME value in the BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_WB_NAME not in bdwd:
            self.bdm_working_data[BDMWD_WB_NAME] = None
        return self.bdm_working_data[BDMWD_WB_NAME]
    @bdmwd_WB_NAME.setter
    def bdmwd_WB_NAME(self, value: str) -> None:
        """Set the current BDMWD_WB_NAME value in the BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_WB_NAME] = value

    @property 
    def bdmwd_WORKBOOKS(self) -> WORKBOOK_DATA_LIST:
        """Return the current BDMWD_WORKBOOKS value in BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_WORKBOOKS not in bdwd:
            self.bdm_working_data[BDMWD_WORKBOOKS] = None
        return self.bdm_working_data[BDMWD_WORKBOOKS]
    @bdmwd_WORKBOOKS.setter
    def bdmwd_WORKBOOKS(self, value: WORKBOOK_DATA_LIST) -> None:
        """Set the current  BDMWD_WORKBOOKS value in BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_WORKBOOKS] = value

    @property 
    def bdmwd_LOADED_WORKBOOKS(self) -> LOADED_WORKBOOK_COLLECTION:
        """Return the current BDMWD_LOADED_WORKBOOKS value in BDMWD."""
        bdwd = self._valid_BDMWD()
        if BDMWD_LOADED_WORKBOOKS not in bdwd:
            self.bdm_working_data[BDMWD_LOADED_WORKBOOKS] = None
        return self.bdm_working_data[BDMWD_LOADED_WORKBOOKS]
    @bdmwd_LOADED_WORKBOOKS.setter
    def bdmwd_LOADED_WORKBOOKS(self, value: LOADED_WORKBOOK_COLLECTION) -> None:
        """Set the current  BDMWD_LOADED_WORKBOOKS value in BDMWD."""
        _ = self._valid_BDMWD()
        self.bdm_working_data[BDMWD_LOADED_WORKBOOKS] = value

    #endregion BDMWD properties 
    # --------------------------------------------------------------------- +
    #region bdmwd_WORKBOOKS() methods
    def bdmwd_WORKBOOKS_count(self) -> int:
        """Return count of BDMWD_WORKBOOKS value in BDMWD."""
        self.bdmwd_INITIALIZED()
        return len(self.bdmwd_WORKBOOKS_get())

    def bdmwd_WORKBOOKS_get(self) -> LOADED_WORKBOOK_COLLECTION | None:
        """Get the BDMWD_WORKBOOKS value from the BDM_WORKING_DATA.

        Returns:
            WORKBOOK_DATA_LIST: A list of tuples containing the workbook name and
            the workbook abs_pat_str.
        """
        try:
            self.bdmwd_INITIALIZED()
            if self.bdm_working_data is None:
                m = f"BDM_WORKING_DATA is not set. "
                logger.error(m)
                raise ValueError(m)
            return self.get_BDM_WORKING_DATA(BDMWD_WORKBOOKS)
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bdmwd_WORKBOOKS_add(self,wb_name : str, wb_abs_path_str : str) -> None:
        """Add an entry to BDMWD_WORKBOOKS in the BDM_WORKING_DATA.

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
        try:
            self.bdmwd_INITIALIZED()
            p3u.is_str_or_none("wb_name", wb_name, raise_error = True)
            p3u.is_str_or_none("wb_abs_path_str",wb_abs_path_str,raise_error=True)
            if self.bdwb_WORKBOOKS_member(wb_name):
                # If the workbook is already a member, do not add it again.
                m = f"Wb: '{wb_name}' already member of BDMWD_WORKBOOKS."
                logger.debug(m)
                return None
            wbs_list = self.bdmwd_WORKBOOKS_get()
            wbs_list.append((wb_name, wb_abs_path_str))
            logger.debug(f"Added ('{wb_name}', '{wb_abs_path_str}') "
                         f"to BDMWD_WORKBOOKS.")
            return None
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bdwb_WORKBOOKS_member(self, wb_name:str) -> bool: 
        """Return True if wb_name is a member of DC.WORKBOOKS list."""
        try:
            _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
            # Reference the DC.WORKBOOKS property.
            wbl = self.bdmwd_WORKBOOKS_get()
            if len(wbl) == 0:
                return False
            for target_wb_name, _ in wbl:
                if target_wb_name == wb_name:
                    return True
            return False
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def bdmwd_WORKBOOKS_resolve(self,initializing:bool=False) -> WORKBOOK_DATA_LIST:
        """Refresh the BDMWD_WORKBOOKS value relative to current BDM state.

        Args:
            wb_name (str): The name of the workbook to add.
            wb_abs_path_str (str): The absolute path of the workbook to add.    

        Returns:
            BDMWD_WORKBOOKS refreshed value on success.

        Raises:
            Exception: if error occurs downstream.
            RunTimeException: if DC content error detected.
        """
        _ = self.bdmwd_INITIALIZED() if not initializing else None
        try:
            fi_key = self.bdmwd_FI_KEY
            wf_key = self.bdmwd_WF_KEY
            wf_purpose = self.bdmwd_WF_PURPOSE
            d = data_desc(fi_key, wf_key, wf_purpose)

            wbl = self.bdm_WORKBOOK_DATA_LIST(fi_key, wf_key, wf_purpose)
            self.bdmwd_WORKBOOKS = wbl
            logger.debug(f"{d} BDMWD_WORKS resolved to: {wbl}")
            return self.bdmwd_WORKBOOKS
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bdmwd_WORKBOOK_load(self, wb_name) -> Workbook:
        """Load 1 workbook into the BDMWD, based on current BDMWD values.

        The named workbook is located for the current FI, WF, and WF_PURPOSE.
        If loaded successfully, add it to the BDMWD_LOADED_WORKBOOKS list.
        If the workbook is already loaded, return it.

        Args:
            wb_name (str): The name of the workbook to load.

        Returns:
            Loaded Workbook.

        Raises:
            Exception: if error occurs downstream.
            RunTimeException: if DC content error detected.
        """
        _ = self.bdmwd_INITIALIZED()
        try:
            _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
            fi_key = self.bdmwd_FI_KEY
            wf_key = self.bdmwd_WF_KEY
            wf_purpose = self.bdmwd_WF_PURPOSE
            d = data_desc(fi_key, wf_key, wf_purpose)

            wbl = self.bdm_WORKBOOK_DATA_LIST(fi_key, wf_key, wf_purpose)
            wb_ap = [val for key, val in wbl if key == wb_name][0]
            if wb_ap is None:
                m = f"Workbook '{wb_name}' not found in BDMWD_WORKBOOKS."
                logger.error(m)
                raise ValueError(m)
            wb = bsm_WORKBOOK_content_file_load(wb_ap)
            self.bdmwd_LOADED_WORKBOOKS_add(wb_name, wb)
            logger.debug(f"{d} loaded wb: '{wb_name}' from '{wb_ap}'")
            return wb
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bdmwd_WORKBOOK_save(self, wb_name:str, wb:Workbook) -> None:
        """Save 1 workbook into the BDMWD, based on current BDMWD values.

        The named workbook is located for the current FI, WF, and WF_PURPOSE.

        Args:
            wb_name (str): The name of the workbook to load.

        Returns:
            Loaded Workbook.

        Raises:
            Exception: if error occurs downstream.
            RunTimeException: if DC content error detected.
        """
        _ = self.bdmwd_INITIALIZED()
        try:
            _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
            fi_key = self.bdmwd_FI_KEY
            wf_key = self.bdmwd_WF_KEY
            wf_purpose = self.bdmwd_WF_PURPOSE
            d = data_desc(fi_key, wf_key, wf_purpose)

            wbl = self.bdm_WORKBOOK_DATA_LIST(fi_key, wf_key, wf_purpose)
            wb_ap = [val for key, val in wbl if key == wb_name][0]
            if wb_ap is None:
                # This wb_name is not known in the BDM.
                m = f"Workbook '{wb_name}' not found in BDMWD_WORKBOOKS."
                logger.error(m)
                raise ValueError(m)
            wb = bsm_WORKBOOK_content_file_save(wb,wb_ap)
            logger.debug(f"{d} saved wb: '{wb_name}' to '{wb_ap}'")
            return wb
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    def bdmwd_WORKBOOK_abs_path_str(self, wb_name:str) -> str:
        """BDMWD-aware: Get the absolute path of a workbook in the BDMWD_WORKBOOKS.

        Args:
            wb_name (str): The name of the workbook to get the absolute path for.

        Returns:
            str: The absolute path of the workbook file.
        
        Raises:
            ValueError: if the workbook is not found in BDMWD_WORKBOOKS.
        """
        _ = self.bdmwd_INITIALIZED()
        try:
            _ = p3u.is_str_or_none("wb_name", wb_name, raise_error=True)
            wbl = self.bdmwd_WORKBOOKS_get()
            wb_ap = [val for key, val in wbl if key == wb_name][0]
            if wb_ap is None:
                m = f"Workbook '{wb_name}' not found in BDMWD_WORKBOOKS."
                logger.error(m)
                raise ValueError(m)
            return wb_ap
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    
    def bdmwd_WB_REF_validate(self, wb_ref:str|int) -> bool:
        """Validate a workbook reference in the BDMWD_WORKBOOKS.

        Args:
            wb_ref (str|int): The workbook reference to validate. 
                If str, it is the workbook name or the index digit. 
                If int, it is the index.

        Returns:
            bool: True if the workbook reference is valid, False otherwise.
        
        Raises:
            TypeError: if wb_ref is not a str or int.
        """
        _ = self.bdmwd_INITIALIZED()
        try:
            if isinstance(wb_ref, str):
                if wb_ref == ALL_KEY:
                    return True
                if wb_ref.isdigit():
                    # If the wb_ref is a digit, treat it as an index.
                    wb_ref_index = int(wb_ref)
                    wbl = self.bdmwd_WORKBOOKS_get()
                    return 0 <= wb_ref_index < len(wbl)
                return self.bdwb_WORKBOOKS_member(wb_ref)
            elif isinstance(wb_ref, int):
                wbl = self.bdmwd_WORKBOOKS_get()
                return 0 <= wb_ref < len(wbl)
            else:
                raise TypeError(f"wb_ref must be str or int, got {type(wb_ref)}")
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion bdmwd_WORKBOOKS() methods
    # --------------------------------------------------------------------- +
    #endregion    BDMWD - Budget Domain Model Working Data methods - DC Interface
    # ======================================================================== +

# ---------------------------------------------------------------------------- +
#region utility functions
def data_desc(fi_key:str, wf_key:str, wf_purpose:str) -> str:
    """Return a string describing the data for the given fi_key, wf_key and WF_PURPOSE.

    Args:
        fi_key (str): The financial institution key.
        wf_key (str): The workflow key.
        wf_purpose (str): The workflow purpose.

    Returns:
        str: A string describing the data for the given fi_key, wf_key and wf_purpose.
    """
    return f"FI('{fi_key}') WF('{wf_key}') WBT('{wf_purpose}')"
#endregion utility functions
# ---------------------------------------------------------------------------- +
#region log_BDM_info() function
def log_BDM_info(bdm : BudgetDomainModel) -> None:  
    try:
        if bdm is None:
            logger.warning("bm parameter is None.")
            return None
        logger.debug("BDM Content:")
        logger.debug(f"{P2}BDM_INITIALIZED['{BDM_INITIALIZED}']: "
                     f"{bdm.bdm_initialized}")
        logger.debug(f"{P2}BDM_FOLDER['{BDM_FOLDER}']: '{bdm.bdm_folder}'")
        logger.debug(f"{P2}BDM_URL['{BDM_URL}]: '{bdm.bdm_url}'")
        # Enumerate the financial institutions in the budget model
        c = len(bdm.bdm_fi_collection)
        logger.debug(
            f"{P2}BDM_FI_COLLECTION['{BDM_FI_COLLECTION}']({c}): "
            f"{str(list(bdm.bdm_fi_collection.keys()))}")
        for fi_key in bdm.bdm_fi_collection.keys():
            logger.debug(f"{P4}Financial Institution: "
                         f"{bdm.bdm_FI_KEY(fi_key)}:{bdm.bdm_FI_NAME(fi_key)}:"
                         f"{bdm.bdm_FI_TYPE(fi_key)}: '{bdm.bdm_FI_FOLDER(fi_key)}'")
        # Enumerate workflows in the budget model
        c = bdm.bdm_WF_OBJECT_count()
        logger.debug(
            f"{P2}BDM_WF_COLLECTION['{BDM_WF_COLLECTION}']({c}): "
            f"{str(list(bdm.bdm_wf_collection.keys()))}")
        for wf_key in bdm.bdm_wf_collection.keys():
            logger.debug(f"{P4}Workflow:({bdm.bdm_WF_KEY(wf_key)}:{bdm.bdm_WF_NAME(wf_key)}: ")
            logger.debug(f"{P6}WF_INPUT_FOLDER: '{bdm.bdm_WF_FOLDER(wf_key,WF_INPUT_FOLDER)}'")
            logger.debug(f"{P6}WF_WORKING_FOLDER: '{bdm.bdm_WF_FOLDER(wf_key,WF_WORKING_FOLDER)}'")
            logger.debug(f"{P6}WF_OUTPUT_FOLDER: '{bdm.bdm_WF_FOLDER(wf_key,WF_OUTPUT_FOLDER)}'")
            logger.debug(f"{P6}WF_PREFIX_IN: '{bdm.bdm_WF_PREFIX_IN(wf_key)}' "
                         f"WF_PREFIX_OUT: '{bdm.bdm_WF_PREFIX_OUT(wf_key)}'")
            logger.debug(f"{P6}WF_PURPOSE_FOLDER_MAP: {str(bdm.bdm_WF_PURPOSE_FOLDER_MAP(wf_key))}")
        # Enumerate Budget Model Options
        bmoc = len(bdm.bdm_options)
        logger.debug(f"{P2}BDM_OPTION['{BDM_OPTIONS}']({bmoc})")
        for opt_key, opt in bdm.bdm_options.items():
            logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

        # And the rest
        logger.debug(f"{P2}BDM_OPTIONS['{BDM_OPTIONS}']: "
                        f"{bdm.bdm_created_date}")
        logger.debug(f"{P2}BDM_LAST_MODIFIED_DATE['{BDM_LAST_MODIFIED_DATE}']: "
                        f"{bdm.bdm_last_modified_date}")
        logger.debug(f"{P2}BDM_LAST_MODIFIED_BY['{BDM_LAST_MODIFIED_BY}']: "
                        f"'{bdm.bdm_last_modified_by}'")
        logger.debug(f"{P2}BDM_WORKING_DATA('{BDM_WORKING_DATA}'): "
                        f"'{bdm.bdm_working_data}'")
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion log_BDM_info() function
# ---------------------------------------------------------------------------- +
#region log_BSM_info() function
def log_BSM_info(bdm : BudgetDomainModel) -> None:  
    try:
        if bdm is None:
            logger.warning("bm parameter is None.")
            return None
        logger.debug("BSM Content:")
        bf_p = bdm.bsm_BDM_FOLDER_path() # budget folder path
        bf_p_exists = "exists." if bf_p.exists() else "does not exist!"
        bf_ap = bdm.bsm_BDM_FOLDER_abs_path() # budget folder path
        bf_ap_exists = "exists." if bf_ap.exists() else "does not exist!"
        logger.debug(f"{P2}BDM_FOLDER['{BDM_FOLDER}']: '{bdm.bdm_folder}' {bf_ap_exists}")
        logger.debug(f"{P4}bsm_BDM_FOLDER_path(): '{str(bf_p)}' {bf_p_exists}")
        logger.debug(f"{P4}bsm_BDM_FOLDER_abs_path(): '{str(bf_ap)}' {bf_ap_exists}")
        # TODO: fix the BDM_STORE file name reference
        bmc_full_filename = f"{bdm.filename}{bdm.bdm_filetype}"
        bmc_p = bf_p / bmc_full_filename # bmc: BM config file
        bmc_p_exists = "exists." if bmc_p.exists() else "does not exist!"
        logger.debug(
            f"{P2}BDM_URL['{BDM_URL}]: '{bdm.bdm_url}' "
            f"{bmc_p_exists}")
        # Enumerate the financial institutions in the budget model
        c = len(bdm.bdm_fi_collection)
        logger.debug(
            f"{P2}BDM_FI_COLLECTION['{BDM_FI_COLLECTION}']({c}): "
            f"{str(list(bdm.bdm_fi_collection.keys()))}")
        for fi_key in bdm.bdm_fi_collection.keys():
            logger.debug(f"{P4}Financial Institution: "
                         f"{bdm.bdm_FI_KEY(fi_key)}:{bdm.bdm_FI_NAME(fi_key)}:"
                         f"{bdm.bdm_FI_TYPE(fi_key)}: '{bdm.bdm_FI_FOLDER(fi_key)}'")
            c = bdm.bdm_FI_WORKFLOW_DATA_COLLECTION_count(fi_key)
            fi_data = bdm.bdm_FI_WORKFLOW_DATA_COLLECTION(fi_key)
            m = str(list(fi_data.keys())) if fi_data is not None else "'None'"
            logger.debug(f"{P6}FI Data({c}): {m}")
        # Enumerate workflows in the budget model
        c = bdm.bdm_WF_OBJECT_count()
        logger.debug(
            f"{P2}BDM_WF_COLLECTION['{BDM_WF_COLLECTION}']({c}): "
            f"{str(list(bdm.bdm_wf_collection.keys()))}")
        for wf_key in bdm.bdm_wf_collection.keys():
            logger.debug(f"{P4}Workflow:({bdm.bdm_WF_KEY(wf_key)}:{bdm.bdm_WF_NAME(wf_key)}: ")
            logger.debug(f"{P6}WF_INPUT_FOLDER: '{bdm.bdm_WF_FOLDER(wf_key,WF_INPUT_FOLDER)}'")
            logger.debug(f"{P6}WF_OUTPUT_FOLDER: '{bdm.bdm_WF_FOLDER(wf_key,WF_OUTPUT_FOLDER)}'")
            logger.debug(f"{P6}WF_PURPOSE_FOLDER_MAP: {str(bdm.bdm_WF_PURPOSE_FOLDER_MAP(wf_key))}")
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion log_BSM_info() function
# ---------------------------------------------------------------------------- +
