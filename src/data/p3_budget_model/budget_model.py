# ---------------------------------------------------------------------------- +
#region budget_model.py module
""" budget_model implements the Budget Domain Model, providing an API to
    upstream actors such as User Interfaces and other system packages.

    Following a rough MVVM pattern, the BudgetModel class is acting as 
    both the ViewModel and the Model. As the package matures, the
    ViewModel and Model will be separated into different packages.

    At present, the BudgetModel class is a singleton class that manages the 
    mapping of excel "workbooks" stored in the filesystem to the budget model.
    The BudgetModel class presents properties and methods to the outside world.
    Methods are separated into ViewModel-ish methods for the Budget Domain 
    and Model-ish methods for the Storage Domain, which is the filesystem.

    In the Budget Domain Model, a data pipeline pattern is used, anticipating 
    "raw data" will be introduced from finanancial institutions (FI) and and 
    proceed through a series of transformations to a "finalized", although
    updatable budget model. Raw data is a "workbook", often an excel file, 
    or a .cvs file.
    
    A "folder" concept is aligned with the stages of transformation as a 
    series of "workflows" applied to the data. Roughly, workflow stage works 
    on data in its associated folder and then may process data inplace locally 
    or as modifications or output to workbooks to another stage folder.

    [raw_data] -> [incoming] -> [categorized] -> [finalized]

    Workflows are functional units of work with clearly defined concerns applied
    to input data and producing outout data. 

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
    workbooks in the filesystem. It maps the Budget Domain structure to 
    filesystem folders and files.

    Assumptions:
    - The FI transactions are in a folder specified in the budget_config.
    - Banking transaction files are typical excel spreadsheets. 
    - Data content starts in cell A1.
    - Row 1 contains column headers. All subsequent rows are data.
"""
#endregion budget_model.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass, time
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from .budget_model_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class SingletonMeta(type):
    """Metaclass for implementing the Singleton pattern for subclasses."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Invokes cls.__init__()
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
# ---------------------------------------------------------------------------- +
class BudgetModel(metaclass=SingletonMeta):
    # ======================================================================== +
    #region BudgetModel class intrinsics
    # ======================================================================== +
    """BudgetModel class implementing Singleton pattern.
    
        A singleton class to manage the budget model for the application.
        This class is used to store and manage the budget data, including
        the budget folder, institutions, and options. Uses only dict-friendly
        items.

        Properties:
        -----------
        - budget_folder_path_str: A pathname to a parent budget folder, 
            e.g., ~/OneDrive/budget.
        - budget_folder_abs_path: A Path object representing the absolute path
            to the budget folder.
        - institutions: A dictionary to store the financial institutions.
        - options: A dictionary to store the options for the budget model.
        - budget_data: A dictionary to store non-persistent the budget data.
    """
    config_template : object = None #
    # ------------------------------------------------------------------------ +
    def __init_subclass__(cls, **kwargs):
        # called at import time, not at runtime.
        print(f"BudgetModel.__init_subclass__({cls}): called")
    # ------------------------------------------------------------------------ +
    #region    BudgetModel class constructor __init__()
    def __init__(self,classname : str = "BudgetModel") -> None:
        """Initialize the BudgetModel class."""
        self._classname = classname
        BudgetModel.config_template = self if classname == "BudgetModelTemplate" else None

        # Private attributes initialization, basic stuff only.
        # for serialization ease, always persist dates as str type.
        logger.debug("Start: BudgetModel().__init__() ...")
        setattr(self, BM_INITIALIZED, False)
        setattr(self, BM_FOLDER, None)  # budget folder path
        setattr(self, BM_FI, {})  # financial institutions
        setattr(self, BM_STORE_URI, None)  # uri for budget model store
        setattr(self, BM_WORKFLOWS, None) 
        setattr(self, BM_OPTIONS, {})  # budget model options
        setattr(self, BM_CREATED_DATE, p3u.now_iso_date_string()) 
        setattr(self, BM_LAST_MODIFIED_DATE, self._created_date)
        setattr(self, BM_LAST_MODIFIED_BY, getpass.getuser())
        setattr(self, BM_WORKING_DATA, {})  # wd - budget model working data
        logger.debug("Complete: BudgetModel().__init__() ...")
    #endregion BudgetModel class constructor __init__()
    # ------------------------------------------------------------------------ +
    #region    BudgetModel internal class methods
    def to_dict(self):
        '''Return BudgetModelTemplate dictionary object. Used for serialization.'''
        ret = {
            BM_INITIALIZED: self.bm_initialized,
            BM_FOLDER: self.bm_folder,
            BM_FI: self.bm_fi,
            BM_STORE_URI: self.bm_store_uri,
            BM_WORKFLOWS: self.bm_supported_workflows,
            BM_OPTIONS: self.bm_options,
            BM_CREATED_DATE: self.bm_created_date,
            BM_LAST_MODIFIED_DATE: self.bm_last_modified_date,
            BM_LAST_MODIFIED_BY: self.bm_last_modified_by,
            BM_WORKING_DATA: self.bm_working_data
        }
        return ret
    def __repr__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"{{ "
        ret += f"'{BM_INITIALIZED}': {self.bm_initialized}, "
        ret += f"'{BM_FOLDER}': '{self.bm_folder}', "
        ret += f"'{BM_FI}': '{self.bm_fi}', "
        ret += f"'{BM_STORE_URI}': '{self.bm_store_uri}', "
        ret += f"'{BM_WORKFLOWS}': '{self.bm_supported_workflows}', "
        ret += f"'{BM_OPTIONS}': '{self.bm_options}', "
        ret += f"'{BM_CREATED_DATE}': '{self.bm_created_date}', "
        ret += f"'{BM_LAST_MODIFIED_DATE}': '{self.bm_last_modified_date}', "
        ret += f"'{BM_LAST_MODIFIED_BY}': '{self.bm_last_modified_by}', "
        ret += f"'{BM_WORKING_DATA}': '{self.bm_working_data}' }} "
        return ret
    def __str__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"{self.__class__.__name__}({str(self.bm_folder)}): "
        ret += f"{BM_INITIALIZED} = {str(self.bm_initialized)}, "
        ret += f"{BM_FOLDER} = '{str(self.bm_folder)}', "
        ret += f"{BM_FI} = [{', '.join([repr(fi_key) for fi_key in self.bm_fi.keys()])}], "
        ret += f"{BM_STORE_URI} = '{self.bm_store_uri}' "
        ret += f"{BM_WORKFLOWS} = '{self.bm_supported_workflows}' "
        ret += f"{BM_OPTIONS} = '{self.bm_options}' "
        ret += f"{BM_CREATED_DATE} = '{self.bm_created_date}', "
        ret += f"{BM_LAST_MODIFIED_DATE} = '{self.bm_last_modified_date}', "
        ret += f"{BM_LAST_MODIFIED_BY} = '{self.bm_last_modified_by}', "
        ret += f"{BM_WORKING_DATA} = {self.bm_working_data}"
        return ret
    #endregion BudgetModel internal class methods
    # ------------------------------------------------------------------------ +
    #region    BudgetModel public class properties
    @property
    def bm_initialized(self) -> bool:
        """The initialized value."""
        return self._initialized
    
    @bm_initialized.setter
    def bm_initialized(self, value )-> None:
        """Set the initialized value."""
        self._initialized = value

    @property
    def bm_folder(self) -> str:
        """The budget folder path is a string, e.g., '~/OneDrive/."""
        return self._budget_folder

    @bm_folder.setter
    def bm_folder(self, value: str) -> None:
        """Set the budget folder path."""
        self._budget_folder = value

    @property
    def bm_store_uri(self) -> str:
        """The budget model store URI."""
        return self._budget_model_store_uri
    
    @bm_store_uri.setter
    def bm_store_uri(self, value: str) -> None:
        """Set the budget model store URI."""
        self._budget_model_store_uri = value

    @property
    def bm_workflows(self) -> dict:
        """The worklow dictionary."""
        return self._workflows
    
    @bm_workflows.setter
    def bm_workflows(self, value: dict) -> None:
        """Set the worklows dictionary."""
        self._workflows = value

    @property
    def bm_fi(self) -> dict:
        """The financial institutions dictionary."""
        return self._financial_institutions
    
    @bm_fi.setter
    def bm_fi(self, value: dict) -> None:
        """Set the financial institutions dictionary."""
        self._financial_institutions = value

    @property
    def bm_options(self) -> dict:
        """The budget model options dictionary."""
        return self._options
    
    @bm_options.setter
    def bm_options(self, value: dict) -> None:
        """Set the budget model options dictionary."""
        self._options = value

    @property
    def bm_created_date(self) -> str:
        """The created date."""
        return self._created_date
    
    @bm_created_date.setter
    def bm_created_date(self, value: str) -> None:  
        """Set the created date."""
        self._created_date = value

    @property
    def bm_last_modified_date(self) -> str:
        """The last modified date."""
        return self._last_modified_date
    
    @bm_last_modified_date.setter
    def bm_last_modified_date(self, value: str) -> None:
        """Set the last modified date."""
        self._last_modified_date = value

    @property
    def bm_last_modified_by(self) -> str:
        """The last modified by."""
        return self._last_modified_by
    
    @bm_last_modified_by.setter
    def bm_last_modified_by(self, value: str) -> None:
        """Set the last modified by."""
        self._last_modified_by = value
    
    @property
    def bm_working_data(self) -> dict:
        """The budget model working data."""
        return self._wd
    
    @bm_working_data.setter
    def bm_working_data(self, value: dict) -> None:
        """Set the budget model working data."""
        self._wd = value

    #endregion BudgetModel public class properties
    #endregion BudgetModel class intrinsics
    # ======================================================================== +

    # ======================================================================== +
    #region    BudgetModel Domain methods
    # ======================================================================== +
    #region    BudgetModel.initialize(self, budget_node : dict = None) public 
    def inititailize(self, 
                 bm_config_src:dict=None, 
                 bms_init : bool = True,
                 create_missing_folders : bool = True,
                 raise_errors : bool = True
                 ) -> None:
        """Initialize BMD from config, either bm_config_src, or the template.

        Args:
            bm_config_src (dict): A BudgetModelStore object to configure from. If
                None, use the BudgetModelTemplate internally.
            bms_init (bool): Initialize the BSM if True.
            create_missing_folders (bool): Create missing folders if True.
            raise_errors (bool): Raise errors if True.
        """
        st = p3u.start_timer()
        bm_config : dict = None
        try:
            if bm_config_src is None:
                logger.debug("bm_config_src parameter is None, using builtin template.")
                bm_config = BudgetModel.config_template
            else:
                bm_config = bm_config_src
            logger.debug(f"Start: ...")
            # Apply the configuration to the budget model (self)
            self.bm_initialized = bm_config.bm_initialized
            self.bm_folder = bm_config.bm_folder
            self.bm_fi = bm_config.bm_fi.copy() if bm_config.bm_fi else {}
            self.bm_store_uri = bm_config.bm_store_uri
            self.bm_supported_workflows = bm_config.bm_supported_workflows.copy() if bm_config.bm_supported_workflows else None
            self.bm_options = bm_config.bm_options.copy() if bm_config.bm_options else {}
            self.bm_created_date = bm_config.bm_created_date
            self.bm_last_modified_date = bm_config.bm_last_modified_date
            self.bm_last_modified_by = bm_config.bm_last_modified_by
            self.bm_working_data = bm_config.bm_working_data.copy() if bm_config.bm_working_data else {}
            if bms_init:
                self.bms_inititalize(create_missing_folders, raise_errors)
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion BudgetModel.initialize(self, budget_node : dict = None) public 
    # ------------------------------------------------------------------------ +
    #region    budget_model_working_data methods
    # budget_model_working_data is a dictionary to store dynamic, non-property data.
    def set_budget_model_working_data(self, key, value):
        self.budget_model_working_data[key] = value

    def get_budget_model_working_data(self, key):
        return self.budget_model_working_data.get(key, 0)
    #endregion budget_model_data methods
    # ------------------------------------------------------------------------ +
    #region FI pseudo-Object properties
    def bmd_validate_fi_key(self, fi_key:str) -> bool:
        """Validate the financial institution key."""
        if fi_key not in self.bm_fi.keys():
            m = f"Financial Institution '{fi_key}' not found in "
            m += f"{self.bm_fi.keys()}"
            logger.error(m)
            raise ValueError(m)
        return True

    def bmd_fi(self, fi_key:str) -> dict:
        """Return the FI dictionary for the specified fi_key."""
        self.bmd_validate_fi_key(fi_key)
        return self.bm_fi[fi_key]
    
    def bmd_fi_key(self, fi_key:str) -> str:
        """Return the FI_KEY value of the FI dictionary specified fi_key.."""
        return self.bmd_fi(fi_key)[FI_KEY]

    def bmd_fi_name(self, fi_key:str) -> str:
        """Return the FI_NAME value of the FI dictionary specified fi_key.."""
        return self.bmd_fi(fi_key)[FI_NAME]
    
    def bmd_fi_type(self, fi_key:str) -> str:
        """Return the FI_TYPE value of the FI dictionary specified fi_key.."""
        return self.bmd_fi(fi_key)[FI_TYPE]

    def bmd_fi_folder(self, fi_key:str) -> str:
        """Return the FI_FOLDER value of the FI dictionary specified fi_key."""
        return self.bmd_fi(fi_key)[FI_FOLDER]
    #endregion FI pseudo-Object properties
    # ------------------------------------------------------------------------ +
    #region WF pseudo-Object properties
    def bmd_validate_wf_key(self, wf_key:str) -> bool:
        """Validate the workflow key."""
        supp_wf = self.bm_supported_workflows
        if supp_wf is None or wf_key not in supp_wf:
            m = f"Workflow('{wf_key}') not found supported workflows "
            m += f"{self.bm_supported_workflows}"
            logger.error(m)
            raise ValueError(m)
        return True

    def bmd_wf(self, wf_key:str) -> dict:
        """Return the WF dictionary specified by wf_key."""
        self.bmd_validate_wf_key(wf_key)
        return self.bm_workflows[wf_key]
    
    def bmd_wf_key(self, wf_key:str) -> str:
        """Return the WF_KEY value the WF dictionary specified by wf_key."""
        return self.bmd_wf(wf_key)[WF_KEY]

    def bmd_wf_name(self, wf_key:str) -> str:
        """Return the WF_NAME value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_NAME]
    
    def bmd_wf_folder_in(self, wf_key:str) -> str:
        """Return the WF_FOLDER_IN value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_FOLDER_IN]
    
    def bmd_wf_workbooks_in(self, wf_key:str) -> List[str]:
        """Return the WF_WORKBOOKS_IN value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_WORKBOOKS_IN]
    
    def bmd_wf_in_prefix(self, wf_key:str) -> str:
        """Return the WF_IN_PREFIX value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_IN_PREFIX]
    
    def bmd_wf_folder_out(self, wf_key:str) -> str:
        """Return the WF_FOLDER_OUT value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_FOLDER_OUT]
    
    def bmd_wf_workbooks_out(self, wf_key:str) -> List[str]:
        """Return the WF_WORKBOOKS_OUT value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_WORKBOOKS_OUT]
    
    def bmd_wf_out_prefix(self, wf_key:str) -> str:
        """Return the WF_OUT_PREFIX value for the specified wf_key."""
        return self.bmd_wf(wf_key)[WF_OUT_PREFIX]    
    #endregion WF pseudo-Object properties
    # ------------------------------------------------------------------------ +
    #endregion BudgetModel Domain methods
    # ======================================================================== +

    # ======================================================================== +
    #region BudgetModel Storage Model methods
    """ BudgetModel Storage Model (BSM) Methods

    All storage is in the filesystem. BSM works with Path objects filenames,
    folders, relative, absolute path names and actual filesystem operations. 
    All paths should be persisted as strings. Internally, Path objects are used.

    The configuration data and stored budget model data contains str values 
    that are utilized in path names for folders and files. The following 
    naming conventions applyr to the purpose of the BMD and BSM methods to 
    separate the concerns for partial path names, full path names and absolute
    pathname values..

    Naming Conventions:
    -------------------
    - bm_ - BudgetModel class properties, e.g., bm_folder, bm_fi, etc.
    - fi_ - Related to financial institution, e.g., fi_key, fi_name, etc.
    - wf_ - Related to workflow, e.g., wf_key, wf_name, etc.
    - bmd_ - BudgetModel Domain methods, concerning the in memory data model.
    - bms_ - BudgetModel Storage Model methods, folders/files stored the filesystem.
    - _path_str - is the simplest string for a path name or component of. These
    methods return str values and do not manipulate with Path objects. Some
    folder values in the BMD, for example, are simply the name of a folder, 
    not a complete path name.
    - _path - constructs a Path object using _path_str values, 
    invokes .expanduser(). 
    _abs_path - invokes .resovle() on _path results, return Path object.
    - Path objects are never serialized to .jsonc files, only _path_str values.

    Abrevs used in method names: 
        bmd - Budget Model Domain, the domain model of the budget model.
        bms - Budget Storage Model, the filesystem storage model.
        bm - BudgetModel class instance, parent of the Budget Model data structure.
        bf - budget folder - attribute, root folder, used in path objects.
        fi - financial institution dictionary, attribute of bm.
             fi_key = int_key, short name of FI, e.g., "boa", "chase", etc.
             fi_value = dict of info about the FI.
        wf - workflow
    """
    # ======================================================================== +
    #region bms_inititalize() method
    def bms_inititalize(self, create_missing_folders:bool=True,
                        raise_errors:bool=True) -> None:
        """Initialize BSM aspects of the BDM.
        
        Examine elements of self, the BudgetModel class, representing the BDM.
        Validate the mapping of the BDM data dependent on mapping to folders 
        and files in the filesystem. Flags control whether to create the
        filesystem structure if it is not present. Also scan the workflow 
        folders for the presence of workbook excel files and load their 
        references into the BDM as appropriate.

        Args:
            create_missing_folders (bool): Create missing folders if True.
            raise_errors (bool): Raise errors if True.
        """
        st = p3u.start_timer()
        # Plan: validate filesystem folders: bf, fi, wf
        #       update the BMD workbook mappings to BMS 
        try:
            logger.debug("Start: ...")
            if self.bm_folder is None:
                m = f"Budget folder path is not set. "
                m += f"Set the '{BM_FOLDER}' property to a valid path."
                logger.error(m)
                raise ValueError(m)
            logger.info(f"Checking budget forlder path: '{self.bm_folder}'")
            bf_ap = self.bms_bm_folder_abs_path()
            verify_folder(bf_ap, create_missing_folders, raise_errors)
            # Enumerate the financial institutions in the budget model.
            for fi_key, inst in self.bm_fi.items():
                # Check each FI folder path is preesnt.
                logger.info(f"Checking financial institution folder: '{fi_key}'")
                fi_ap = self.bms_fi_folder_abs_path(fi_key)
                verify_folder(fi_ap, create_missing_folders, raise_errors)
                # Enumerate the workflows for the financial institution.
                for wf_key, wf in self.bm_workflows.items():
                    # Check each workflow folder path is present.
                    logger.info(f"Checking folder for workflow: '{wf_key}'")
                    wf_ap = self.bms_wf_folder_in_abs_path(fi_key, wf_key)
                    verify_folder(wf_ap, create_missing_folders, raise_errors)
                    # Resolve the WF_WORKBOOKS_IN dictionary for the workflow.
                    wf_dict = self.bms_fi_folder_wf_resolve_workbooks(fi_key, wf_key)
                    self.bms_set_wf_workbooks_in(wf_key, wf_dict)
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
    #endregion bms_inititalize() method
    # ------------------------------------------------------------------------ +    
    #region BM Folder (BF) Path methods
    def bms_bm_folder_path_str(self) -> str:
        """str version of the BM_FOLDER value as a Path."""
        return str(Path(self.bm_folder))
    def bms_bm_folder_path(self) -> Path:
        """Path of self.bms_bm_folder_path_str().expanduser()."""
        return Path(self.bms_bm_folder_path_str()).expanduser()
    def bms_bm_folder_abs_path(self) -> Path:
        """Path of self.bms_bm_folder_path().resolve()."""
        return self.bms_bm_folder_path().resolve()
    def bms_bm_folder_abs_path_str(self) -> str:
        """str of self.bms_bm_folder_abs_path()."""
        return str(self.bms_bm_folder_abs_path())
    #endregion BM Folder (BF) Path methods
    # ------------------------------------------------------------------------ +
    #region FI pseudo-Object methods
    # ------------------------------------------------------------------------ +   
    #region FI Path methods
    def bms_fi_folder_path_str(self, fi_key: str) -> str:
        """str version of the FI_FOLDER value as a Path."""
        bf_p_s = self.bms_bm_folder_path_str()
        fi_p_s = str(Path(self.bmd_fi_folder(fi_key)))    
        return str(Path(bf_p_s) / fi_p_s)
    def bms_fi_folder_path(self, fi_key: str) -> Path:
        """Path of self.bms_fi_folder_path_str().expanduser()."""
        return Path(self.bms_fi_folder_path_str(fi_key)).expanduser()
    def bms_fi_folder_abs_path(self, fi_key: str) -> Path:
        """Path of self.bms_fi_folder_path().resolve()."""
        return Path(self.bms_fi_folder_path(fi_key)).resolve()
    def bms_fi_folder_abs_path_str(self, fi_key: str) -> str:
        """str of self.bms_fi_folder_abs_path()."""
        return str(self.bms_fi_folder_abs_path(fi_key))
    #endregion FI Path methods
    # ------------------------------------------------------------------------ +   
    #endregion FI pseudo-Object methods 
    # ------------------------------------------------------------------------ +   
    #region WF pseudo-Object methods
    # ------------------------------------------------------------------------ +   
    #region bm_fi_wf_workbooks methods
    def bms_wf_workbooks_in(self, wf_key:str) -> dict:
        """Get WF_WOOKBOOKS_IN value (dict) of the WF specified by wf_key.        """
        return self.bmd_wf_workbooks_in(wf_key)
    
    def bms_set_wf_workbooks_in(self, wf_key : str, value: dict) -> None:
        """Set WF_WORKBOOKS_IN dict for specified FI fi_key and workflow."""
        self.bmd_wf[wf_key][WF_WORKBOOKS_IN] = value
    #endregion bm_fi_wf_workbooks methods
    # ------------------------------------------------------------------------ +   
    #region WF Path methods
    def bms_wf_folder_in_str(self, fi_key : str, wf_key : str) -> str:
        """str version of the WF_FOLDER_IN value for fi_key/wf_key."""
        fi_p_s = self.bms_fi_folder_path_str(fi_key) # FI_FOLDER Path component
        wf_p_s = self.bmd_wf_folder_in(wf_key)
        combined_p = Path(fi_p_s) / wf_p_s
        return str(combined_p)
    def bms_wf_folder_in_path(self, fi_key : str, wf_key : str) -> Path:
        """Path of self.bms_wf_folder_path_str().expanduser()."""
        return Path(self.bms_wf_folder_in_str(fi_key, wf_key)).expanduser()
    def bms_wf_folder_in_abs_path(self, fi_key : str, wf_key : str) -> Path:
        """Path of self.bms_wf_folder_path().resolve()."""
        return Path(self.bms_wf_folder_in_path(fi_key, wf_key)).resolve()
    def bms_wf_folder_in_abs_path_str(self, fi_key : str, wf_key : str) -> str:
        """str of self.bms_wf_folder_abs_path()."""
        return str(self.bms_wf_folder_in_abs_path(fi_key, wf_key))
    #endregion WF Path methods
    # ------------------------------------------------------------------------ +
    #region bms_fi_folder_wf_resolve_workbooks(self, fi_key, workflow) -> List:
    def bms_fi_folder_wf_resolve_workbooks(self, fi_key: str, workflow : str) -> dict:
        """Return list of all of the workbook files in the fi_wf folder. 
        Folder and return a WF_WORKBOOKS_IN dictionary for the specified workflow.

        WF_WORKBOOKS_IN dict:
        { "workbook_name": "file_abs_path", ... }

        Args:
            fi_key (str): The key of the institution to get the workbooks for.
            workflow (str): The workflow to get the workbooks for.

        Returns:
            List[str]: A list of workbook file names in the workflow folder.
        """
        try:
            fi_wf_ap = self.bms_fi_folder_wf_abs_path(fi_key, workflow)
            wb_files = list(fi_wf_ap.glob("*.xlsx"))
            wf_dict = {}
            for wb_p in wb_files:
                wb_name = wb_p.name
                wf_dict[wb_name] = str(wb_p)
            return wf_dict
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion bms_fi_folder_wf_resolve_workbooks(self, fi_key, workflow) -> List:
    # ------------------------------------------------------------------------ +
    #endregion Workflow Object (dict) methods
    # ------------------------------------------------------------------------ +   
    #region load_fi_transactions() function
    def load_fi_transactions(self, fi_key:str, process_folder: str, 
                             trans_file : str = None) -> Workbook:
        """Get FI transactions from an excel file into an openpyxl.Workbook.
        
        Transactions downloaded from an FI are in a folder. 
        The file is assumed to be in the folder specified in the budget_config. 
        A folder is specified in the budget_config.json file. That folder is scanned 
        for transactions in excel files if a particular file is not specified.

        TODO: If trans_file is not specified, then scan the folder for files. 
        Return a dictionary of workbooks with the file name as the key.

        Args:
            trans_file (str): The name of the transaction file to load.

        Returns:
            Workbook: The workbook containing the FI transactions.

        """
        me = self.load_fi_transactions
        st = time.time()
        try:
            trans_path = self.fi_abs_path / trans_file
            logger.info("Loading FI transactions...")
            wb = load_workbook(filename=trans_path)
            logger.info(f"Loaded FI transactions from {str(trans_path)}")
            delta = f"{time.time() - st:.3f} seconds."
            logger.info(f"Complete: {delta}")
            return wb
        except Exception as e:
            logger.error(p3u.exc_msg(me, e))
            raise    
    #endregion load_fi_transactions() function
    # ------------------------------------------------------------------------ +
    #region fi_load_workbook(self, fi_key:str, process_folder:str, file_name:str) function
    def fi_load_workbook(self, fi_key:str, workflow:str, 
                              workbook_name:str) -> Workbook:
        """Load a transaction file for a Financial Institution Workflow.

        ViewModel: This is a ViewModel function, mapping budget domain model 
        to how budget model data is stored in filesystem.

        Args:
            fi_key (str): The key of the institution to load the transaction file for.
            workflow (str): The workflow to load the transaction file from.
            workbook_name (str): The name of the workbook file to load.

        Returns:
            Workbook: The loaded transaction workbook.
        """
        me = self.fi_load_workbook
        try:
            # Budget Folder Financial Institution Workflow Folder absolute path
            bffiwfap = self.bms_fi_folder_wf_abs_path(fi_key, workflow) 
            wbap = bffiwfap / workbook_name # workbook absolute path
            m = f"BMD: Loading FI('{fi_key}') workflow('{workflow}') "
            m += f"workbook('{workbook_name}'): abs_path: '{str(wbap)}'"
            logger.debug(m)
            wb = self.bms_load_workbook(wbap)
            return wb
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    #endregion fi_load_workbook(self, fi_key:str, process_folder:str) function
    # ------------------------------------------------------------------------ +
    #region bms_load_workbook(self, workbook_path:Path) function
    def bms_load_workbook(self, workbook_path:Path) -> Workbook:
        """Load a transaction file for a Financial Institution Workflow.

        Storage Model: This is a Model function, loading an excel workbook
        file into memory.

        Args:
            workbook_path (Path): The path of the workbook file to load.

        Returns:
            Workbook: The loaded transaction workbook.
        """
        me = self.bms_load_workbook
        try:
            logger.debug(f"BMS: Loading workbook file: '{workbook_path}'")
            wb = load_workbook(filename=workbook_path)
            return wb
        except Exception as e:
            logger.error(p3u.exc_msg(me, e))
            raise
    #endregion bms_load_workbook(self, fi_key:str, process_folder:str) function
    # ------------------------------------------------------------------------ +
    #region bms_save_workbook() function
    def bms_save_workbook(self, workbook : Workbook = None, output_path:str=None) -> None:
        """Save the FI transactions workbook to the filesystem.
        
        The file is assumed to be in the folder specified in the budget_config. 
        Use the folder specified in the budget_config.json file. 
        the budget_config may have an output_prefix specified which will be
        prepended to the output_path name.

        TODO: If output_path is not specified, then scan the folder for files. 
        Return a dictionary of workbooks with the file name as the key.

        Args:
            output_path (str): The absolute path of the transaction file to save.

        Returns:
            None

        """
        me = self.save_fi_transactions
        st = time.time()
        try:
            # TODO: add logic to for workbook open in excel, work around.
            if (budget_config["output_prefix"] is not None and 
                isinstance(budget_config["output_prefix"], str) and
                len(budget_config["output_prefix"]) > 0):
                file_path = budget_config["output_prefix"] + output_path
            else:
                file_path = output_path
            trans_path = Path(budget_config["bank_transactions_folder"]) / file_path
            logger.info("Saving FI transactions...")
            workbook.save(filename=trans_path)
            logger.info(f"Saved FI transactions to '{str(trans_path)}'")
            return
        except Exception as e:
            logger.error(p3u.exc_msg(me, e))
            raise    
    #endregion bms_save_workbook() function
    # ------------------------------------------------------------------------ +
    #endregion BudgetModel Storage Model methods
    # ======================================================================== +
# ---------------------------------------------------------------------------- +
#region log_BMD_info() function
def log_BMD_info(bmd : BudgetModel) -> None:  
    try:
        logger.debug("BMD Content:")
        logger.debug(f"{P2}BM_INITIALIZED('{BM_INITIALIZED}'): "
                     f"{bmd.bm_initialized}")
        bf_p = bmd.bms_bm_folder_path() # budget folder path
        bf_p_exists = "exists." if bf_p.exists() else "does not exist!"
        bf_ap = bmd.bms_bm_folder_abs_path() # budget folder path
        bf_ap_exists = "exists." if bf_ap.exists() else "does not exist!"
        logger.debug(f"{P2}BM_FOLDER('{BM_FOLDER}'): '{bmd.bm_folder}' {bf_ap_exists}")
        logger.debug(f"{P4}bms_bm_folder_path(): '{str(bf_p)}' {bf_p_exists}")
        logger.debug(f"{P4}bms_bm_folder_abs_path(): '{str(bf_ap)}' {bf_ap_exists}")
        bmc_p = bf_p / BMS_DEFAULT_BUDGET_MODEL_FILE_NAME # bmc: BM config file
        bmc_p_exists = "exists." if bmc_p.exists() else "does not exist!"
        logger.debug(
            f"{P2}BM_STORE_URI('{BM_STORE_URI}): '{bmd.bm_store_uri}' "
            f"{bmc_p_exists}")
        logger.debug(
            f"{P2}BM_WORKFLOWS('{BM_WORKFLOWS}'): "
            f" '{bmd.bm_supported_workflows}'")
        # Enumerate the financial institutions in the budget model
        for fi_key, fi_dict in bmd.bm_fi.items():
            logger.debug(f"{P2}Financial Institution: {fi_dict[FI_FOLDER]}:"
                         f"{fi_dict[FI_TYPE]}:{fi_dict[FI_NAME]}:")
            for wf_key, wf_dict in bmd.bm_workflows.items():
                logger.debug(f"{P4}Workflow('{wf_dict[WF_NAME]}'): ")
                logger.debug(f"{P6}WF_FOLDER_IN: '{bmd.bmd_wf_folder_in()}' ")
                logger.debug(f"{P6}WF_WORKBOOKS_IN: {bmd.bmd_wf_workbooks_in()}")
        # Enumerate Budget Model Options
        bmoc = len(bmd.bm_options)
        logger.debug(f"{P2}BM_OPTION('{BM_OPTIONS}')({bmoc})")
        for opt_key, opt in bmd.bm_options.items():
            logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

        # And the rest
        logger.debug(f"{P2}BM_CREATED_DATE({BM_CREATED_DATE}'): "
                        f"{bmd.bm_created_date}")
        logger.debug(f"{P2}BM_LAST_MODIFIED_DATE({BM_LAST_MODIFIED_DATE}'): "
                        f"{bmd.bm_last_modified_date}")
        logger.debug(f"{P2}BM_LAST_MODIFIED_BY({BM_LAST_MODIFIED_BY}'): "
                        f"{bmd.bm_last_modified_by}")
        logger.debug(f"{P2}BM_WORKING_DATA({BM_WORKING_DATA}'): "
                        f"{bmd.bm_working_data}")

    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion log_BMD_info() function
# ---------------------------------------------------------------------------- +
#region check_budget_model() -> bool
def check_budget_model() -> bool:   
    """Quick check of the budget model schema is valid.

    Returns:
        bool: True if the budget model schema is valid, raise otherwise.
    """
    me = check_budget_model
    global budget_config, budget_model, budget_config_expected_keys
    global institution_expected_keys, options_expected_keys
    try:
        if (budget_model is None or 
            not isinstance(budget_model, dict) or
            len(budget_model) == 0):
            logger.warning("Budget model is not initialized.")
            return False
        # Check if the budget model contains expected keys
        for key in budget_config_expected_keys:
            if key not in budget_model:
                m = f"Budget model missing key: '{key}'"
                logger.error(m)
                raise ValueError(m)
        # Check if the institutions are valid
        for institution_key in BudgetModel.valid_institutions_keys:
            if institution_key not in budget_config["institutions"].keys():
                m = f"Budget model has invalid institution key: '{institution_key}'"
                logger.error(m)
                raise ValueError(m)
            for key in institution_expected_keys:
                if key not in budget_model["institutions"][institution_key]:
                    m = f"Budget model institution[{institution_key}] missing key: '{key}'"
                    logger.error(m)
                    raise ValueError(m)
        for key in options_expected_keys:
            if key not in budget_model["options"]:
                m = f"Budget model missing options key: '{key}'"
                logger.error(m)
                raise ValueError(m)
        return True
    except Exception as e:
        logger.error(p3u.exc_msg(me, e))
        return False
#endregion check_budget_model() -> bool
# ---------------------------------------------------------------------------- +
#region verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
def verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool:
    """Verify the folder exists, create it if it does not exist.

    Args:
        ap (Path): The absolute path to the folder to verify.
        create (bool): Create the folder if it does not exist.
        raise_errors (bool): Raise errors if True.
    """
    try:
        if not ap.is_absolute():
            m = f"Path is not absolute: '{str(ap)}'"
            logger.error(m)
            raise ValueError(m)
        if ap.exists() and ap.is_dir():
            logger.debug(f"Folder exists: '{str(ap)}'")
            return True
        if not ap.exists():
            m = f"Folder does not exist: '{str(ap)}'"
            logger.error(m)
            if create:
                logger.info(f"Creating folder: '{str(ap)}'")
                ap.mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(m)
    except Exception as e:
        logger.error(p3u.exc_msg(verify_folder, e))
        raise
#endregion verify_folder(ap: Path, create:bool=True, raise_errors:bool=True) -> bool
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        # this_app_name = os.path.basename(__file__)
        # Configure logging
        logger_name = THIS_APP_NAME
        log_config = "budget_model_logging_config.jsonc"
        # Set the log filename for this application.
        # filenames = {"file": "logs/p3ExcelBudget.log"}
        _ = p3l.setup_logging(
            logger_name = logger_name,
            config_file = log_config
        )
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"+ Running {THIS_APP_NAME} ...")
        logger.info("+ ----------------------------------------------------- +")
        logger.debug(f"Start: {THIS_APP_NAME}...")

        bm = BudgetModel()
        bm.inititailize()
        bms = str(bm)
        bmr = repr(bm)
        bmd = bm.to_dict()

        logger.debug(f"Budget Model: str() = '{bms}'")
        logger.debug(f"Budget Model: repr() = '{bmr}'")
        logger.debug(f"Budget Model: to_dict() = '{bmd}'")
        logger.info(f"Budget Model: {str(bm)}")
        _ = "pause"
    except Exception as e:
        m = p3u.exc_msg("__main__", e)
        logger.error(m)
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
