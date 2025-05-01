# ---------------------------------------------------------------------------- +
#region p3_budget_model_template.py module
""" Provide a functiona template class for the budget_model class.

    Creates a functional instance from a declared dictionary used to document
    the data structure and configure defaults. It is useful for validation
    of constant names, different default settings, etc.

    4/29/2025: Soon, the budget_model configuration and setup will be from a 
    config file. The template could be used to create a pristing, new config 
    file for a new budget_model instance. But for now, budget_model is a 
    singleton class.

    Assumptions:
    - The FI transactions are in a folder specified in the budget_config.
    - Banking transaction files are typical excel spreadsheets. 
    - Data content starts in cell A1.
    - Row 1 contains column headers. All subsequent rows are data.
"""
#endregion p3_execl_budget.p3_banking_transactions transaction_files.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, os, getpass
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from .budget_model_constants import *
from .budget_model import BudgetModel
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Model Template and config support 
# ---------------------------------------------------------------------------- +
class _BudgetModelTemplate(BudgetModel):
    """Default BbudgetModelTemplate class, contains default, example values.
    
    Defines the BudgetModel structure with two example Financial Institutions.
    Convenient for developer.
    """
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate Configuration Template
    # The main difference between the BudgetModel and the BudgetModelTemplate 
    # is the following budget_model_template dictionary. The BudgetModelTemplate 
    # covers the file structure where user data is stored as 
    # settings for options and preferences. Keep it simple.
    # There is both an object model used in the application (in memory) and a
    # file system structure used to store the data. In addition, the idea is that 
    # users are placing new FI transactions in an "incoming" folder folder 
    # for processing through stages to arrive in updating the budget. Long-view is 
    # anticipate more than one bank or financial institution sourcing regular 
    # statements in spreadsheet format. So, the "budget" will cover multiple "banks"
    # information for a given user.
    budget_config_expected_keys = (BM_INITIALIZED,BM_BF, BM_FI, 
                                BM_OPTIONS)
    valid_institutions_keys = ("boa", "merrill")
    institution_expected_keys = (
        FI_NAME, 
        FI_TYPE, 
        FI_FOLDER, 
        FI_IF,
        FI_IF_WORKBOOKS,
        FI_CF,
        FI_CF_WORKBOOKS,
        FI_FF,
        FI_FF_WORKBOOKS
        )
    options_expected_keys = (
        BMO_FI_IF_PREFIX, 
        BMO_FI_CF_PREFIX,
        BMO_FI_FF_PREFIX,
        BMO_LOG_CONFIG,
        BMO_LOG_LEVEL,
        BMO_LOG_FILE,
        BMO_JSON_LOG_FILE
        )
    budget_model_template = {  # _abs_path is not serialized, only _abs_path_str is serialized
        BM_INITIALIZED: False,
        BM_BF: BM_DEFAULT_BUDGET_FOLDER,
        BM_STORE_URI: None,
        BM_SUPPORTED_WORKFLOWS: [
            BM_WF_INTAKE, 
            BM_WF_CATEGORIZATION, 
            BM_WF_FINALIZATION
            ],
        BM_FI: {
            "boa": {
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                FI_WORKFLOWS: {
                    BM_WF_INTAKE: {
                        WF_NAME: BM_WF_INTAKE,
                        WF_FOLDER: "data/new",
                        WF_WORKBOOKS: {}
                    },
                    BM_WF_CATEGORIZATION: {
                        WF_NAME: BM_WF_CATEGORIZATION,
                        WF_FOLDER: "data/categorized",
                        WF_WORKBOOKS: {}
                    },
                    BM_WF_FINALIZATION: {
                        WF_NAME: BM_WF_FINALIZATION,
                        WF_FOLDER: "data/processed",
                        WF_WORKBOOKS: {}
                    }
                },
                # FI_IF: "data/new",
                # FI_IF_WORKBOOKS: {}, # key = file name, value = absolute path
                # # Categorized folder name and list of workbook names,
                # # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
                # FI_CF: "data/categorized",
                # FI_CF_WORKBOOKS: {}, # key = file name, value = absolute path
                # # Processed folder name and list of workbook names,
                # # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
                # FI_FF: "data/processed",
                # FI_FF_WORKBOOKS: {} # key = file name, value = absolute path
            },
            "merrill": {
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                FI_WORKFLOWS: {
                    BM_WF_INTAKE: {
                        WF_NAME: BM_WF_INTAKE,
                        WF_FOLDER: "data/new",
                        WF_WORKBOOKS: {}
                    },
                    BM_WF_CATEGORIZATION: {
                        WF_NAME: BM_WF_CATEGORIZATION,
                        WF_FOLDER: "data/categorized",
                        WF_WORKBOOKS: {}
                    },
                    BM_WF_FINALIZATION: {
                        WF_NAME: BM_WF_FINALIZATION,
                        WF_FOLDER: "data/processed",
                        WF_WORKBOOKS: {}
                    }
                },
                # # Incoming folder name and list of workbook names,
                # # e.g. ["new_boa-1391-2024-04-28.xlsx"]
                # FI_IF: "data/new",
                # FI_IF_WORKBOOKS: {}, # key = file name, value = absolute path
                # # Categorized folder name and list of workbook names,
                # # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
                # FI_CF: "data/categorized",
                # FI_CF_WORKBOOKS: {}, # key = file name, value = absolute path
                # # Processed folder name and list of workbook names,
                # # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
                # FI_FF: "data/finalized",
                # FI_FF_WORKBOOKS: {} # key = file name, value = absolute path
            },
        },
        BM_OPTIONS: {
            BMO_FI_IF_PREFIX: "new_",
            BMO_FI_CF_PREFIX: "categorized_",
            BMO_FI_CF_PREFIX: "processed_",
            BMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BMO_LOG_LEVEL: logging.DEBUG,
            BMO_LOG_FILE: "logs/p3BudgetModel.log",
            BMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        }
    }
    # Template-only versions of structure attributes.
    #endregion BudgetModelTemplate Configuration Template
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate class constructor __init__.()
    # __init__() method for the BudgetModelTemplate class
    def __init__(self, create_missing_folders : bool = True,
                 raise_errors : bool = True) -> None:
        """Construct a BudgetModelTemplate object used to initialize the budget model.
        
        The template class is largely a dictionary populated with default values
        and some example values. The idea is to use this template to create a new
        budget model or to initialize a new budget model from the template. 
        It is for internal use only.
        """
        try:
            # Basic attribute atomic value inits. 
            # logger = logging.getLogger(THIS_APP_NAME)
            logger.debug("Start: BudgetModelTemplate().__init__() ...")
            super().__init__()
            # Set attribute defaults for the budget model
            logger.debug(f"{P2}BM_INITIALIZED('{BM_INITIALIZED}'): "
                         f"{getattr(self,BM_INITIALIZED)}")
            setattr(self, BM_BF, BM_DEFAULT_BUDGET_FOLDER) 
            bf = getattr(self, BM_BF)  # budget folder setting, a str
            bfp = Path(bf).expanduser() # budget folder path
            bmc = bfp / BMS_DEFAULT_BUDGET_MODEL_FILE_NAME # bmc: BM config file
            bfp_exists = "exists." if bfp.exists() else "does not exist!"
            bmc_exists = "exists." if bmc.exists() else "does not exist!"
            bmc_uri = p3u.path_to_file_uri(bmc) # uri for budget model config
            setattr(self, BM_STORE_URI, bmc_uri)
            logger.debug(f"{P2}BM_BF('{BM_BF}'): '{getattr(self,BM_BF)}' {bfp_exists}")
            logger.debug(
                f"{P4}_bf_path(): '{self._bf_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P4}_bf_abs_path(): '{self._bf_abs_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P2}BM_STORE_URI('{BM_STORE_URI}): '{getattr(self,BM_STORE_URI)}' "
                f"{bmc_exists}")
            logger.debug(
                f"{P4}BM_SUPPORTED_WORKFLOWS('{BM_SUPPORTED_WORKFLOWS}'): "
                f" '{self._supported_workflows}'")
            # Financial Institutions (FI) as a template        # Institution folders
            bmt = _BudgetModelTemplate.budget_model_template
            fic = len(bmt[BM_FI])  # financial institutions count
            logger.debug(f"{P2}BM_FI('{BM_FI}')({fic})")
            for inst_key, inst in bmt[BM_FI].items():
                inst_folder_path = bfp / inst_key
                inst_folder_abs_path = inst_folder_path.resolve()
                ifap_exists = "exists." if inst_folder_abs_path.exists() else "does not exist!"
                logger.debug(f"{P4}Inst('{inst_key}') folder: '{inst_folder_path}'")
                if not inst_folder_abs_path.exists():
                    # If create_missing_folders is True, create the folder
                    if create_missing_folders:
                        logger.debug(f"{P4}Creating folder: '{inst_folder_abs_path}'")
                        inst_folder_abs_path.mkdir(parents=True, exist_ok=True)
                    else:
                        m = (f"{P4}Budget institution({inst_key}) " 
                            f"folder does not exist: '{str(inst_folder_abs_path)}'")
                        logger.error(m)
                        raise FileNotFoundError(m) if raise_errors else None
                getattr(self,BM_FI)[inst_key] = inst.copy()  # Copy the template values
                logger.debug(f"{P6}FI_KEY()'{inst_key}') {str(inst)}")
                ifp = self._fi_f_path(inst_key)
                ifp_exists = "exists." if ifp.exists() else "does not exist!"
                logger.debug(f"{P6}_fi_f_path(): '{ifp}' "
                             f"{ifp_exists}")
                ifap = self._fi_f_abs_path(inst_key)
                logger.debug(f"{P6}_fi_f_abs_path(): '{ifap}'"
                             f"{ifap_exists}")

            # Initialize Budget Model Options as a template
            bmoc = len(bmt[BM_OPTIONS])
            logger.debug(f"{P2}BM_OPTION('{BM_OPTIONS}')({bmoc})")
            for opt_key, opt in bmt[BM_OPTIONS].items():
                logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

            # And the rest
            logger.debug(f"{P2}BM_CREATED_DATE({BM_CREATED_DATE}'): "
                         f"{getattr(self,BM_CREATED_DATE)}")
            logger.debug(f"{P2}BM_LAST_MODIFIED_DATE({BM_LAST_MODIFIED_DATE}'): "
                            f"{getattr(self,BM_LAST_MODIFIED_DATE)}")
            logger.debug(f"{P2}BM_LAST_MODIFIED_BY({BM_LAST_MODIFIED_BY}'): "
                            f"{getattr(self,BM_LAST_MODIFIED_BY)}")
            logger.debug(f"{P2}BM_WORKING_DATA({BM_WORKING_DATA}'): "
                            f"{getattr(self,BM_WORKING_DATA)}")
            # BudgetModelTemplate initialization is complete.
            setattr(self, BM_INITIALIZED, True)
            logger.debug(f"{P2}{BM_INITIALIZED}: {getattr(self,BM_INITIALIZED)}")
            logger.debug(f"Complete: BudgetModelTemplate().__init__() ...")
        except Exception as e:
            m = p3u.exc_msg(self.__init__, e)
            logger.error(m)
            raise
    #endregion BudgetModelTemplate class constructor __init__.()
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate internal class methods
    def to_dict(self):
        '''Return BudgetModelTemplate dictionary object. Used for serialization.'''
        ret = {
            BM_INITIALIZED: self.bm_initialized,
            BM_BF: self.bm_bf,
            BM_FI: self.bm_fi,
            BM_STORE_URI: self.bm_store_uri,
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
        ret += f"'{BM_BF}': '{self.bm_bf}', "
        ret += f"'{BM_FI}': '{self.bm_fi}', "
        ret += f"'{BM_STORE_URI}': '{self.bm_store_uri}', "
        ret += f"'{BM_OPTIONS}': '{self.bm_options}', "
        ret += f"'{BM_CREATED_DATE}': '{self.bm_created_date}', "
        ret += f"'{BM_LAST_MODIFIED_DATE}': '{self.bm_last_modified_date}', "
        ret += f"'{BM_LAST_MODIFIED_BY}': '{self.bm_last_modified_by}', "
        ret += f"'{BM_WORKING_DATA}': '{self.bm_working_data}' }} "
        return ret
    def __str__(self) -> str:
        ''' Return a str representation of the BudgetModel object '''
        ret = f"BudgetModlelTemplate({str(self.bm_bf)}): "
        ret += f"{BM_INITIALIZED} = {str(self.bm_initialized)}, "
        ret += f"{BM_BF} = '{str(self.bm_bf)}', "
        ret += f"{BM_FI} = [{', '.join([repr(fi_key) for fi_key in self.bm_fi.keys()])}], "
        ret += f"{BM_STORE_URI} = '{self.bm_store_uri}' "
        ret += f"{BM_OPTIONS} = '{self.bm_options}' "
        ret += f"{BM_CREATED_DATE} = '{self.bm_created_date}', "
        ret += f"{BM_LAST_MODIFIED_DATE} = '{self.bm_last_modified_date}', "
        ret += f"{BM_LAST_MODIFIED_BY} = '{self.bm_last_modified_by}', "
        ret += f"{BM_WORKING_DATA} = {self.bm_working_data}"
        return ret
    #endregion BudgetModelTemplate internal class methods
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate public class properties
    @property
    def bm_initialized(self) -> bool:
        """The initialized value."""
        return self._initialized
    
    @bm_initialized.setter
    def bm_initialized(self, value )-> None:
        """Set the initialized value."""
        self._initialized = value

    @property
    def bm_bf(self) -> str:
        """The budget folder path is a string, e.g., '~/OneDrive/."""
        return self._budget_folder

    @bm_bf.setter
    def bm_bf(self, value: str) -> None:
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
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate public methods
    # ------------------------------------------------------------------------ +
    def _bf_path(self) -> str:
        return Path(getattr(self,BM_BF)).expanduser()
    def _bf_abs_path(self) -> str:
        return self._bf_path().resolve()

    def _fi_f_path(self, inst_key: str) -> str:
        """Calculate the path of a Financial Institution folder in the
        Budget Storage Model.
        
        Each FI key, or inst_key, maps to a file folder in the budget folder.
        """
        bfp = self._bf_path().expanduser()
        bfip = bfp / inst_key # bank folder institution path
        return bfip
    def _fi_f_abs_path(self, inst_key: str) -> str:
        return self._fi_f_path(inst_key).resolve()

    def resolve_wf_workbooks(self) -> None:
        """Resolve the workbooks for all workflows."""
        try:
            logger.debug("Start: resolve_wf_workbooks()...")
            for inst_key, inst in self.bm_fi.items():
                fi_folder = self._fi_f_path(inst_key)
                fi_abs_folder = self._fi_f_abs_path(inst_key)
                logger.debug(f"Financial Institution: '{fi_folder}'")
                for wf_key, wf_dict in inst[FI_WORKFLOWS].items():
                    wf_folder = fi_folder / wf_dict[WF_FOLDER]
                    wf_abs_folder = fi_abs_folder / wf_dict[WF_FOLDER]
                    logger.debug(f"Workflow('{wf_dict[WF_NAME]}'): "
                                 f"Folder: '{wf_folder}' "
                                 f"Workbooks: {wf_dict[WF_WORKBOOKS]}")


        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise
        return
    #endregion BudgetModel public methods
    # ------------------------------------------------------------------------ +       
# ---------------------------------------------------------------------------- +
#region tryout_budget_model_template() function
def tryout_budget_model_template() -> None: 
    """Test the BudgetModelTemplate class."""
    try:
        logger.debug("Start: tryout_budget_model_template()...")
        bmt = _BudgetModelTemplate()
        logger.debug(f"Budget Model Template: {str(bmt)}")
        logger.debug(f"Budget Model Template: {repr(bmt)}")
        logger.debug(f"Budget Model Template: {bmt.to_dict()}")

        # Enumerate the financial institutions in the budget model template
        for inst_key, inst in bmt.bm_fi.items():
            n = inst[FI_NAME]
            t = inst[FI_TYPE]
            f = inst[FI_FOLDER]
            wf = list(inst[FI_WORKFLOWS].keys()) 
            logger.debug(f"Financial Institution: {f}:{t}:{n}:{str(wf)}")
            for wf_key, wf_dict in inst[FI_WORKFLOWS].items():
                logger.debug(f"Workflow('{wf_dict[WF_NAME]}'): "
                             f"Folder: '{wf_dict[WF_FOLDER]}' "
                             f"Workbooks: {wf_dict[WF_WORKBOOKS]}")
                bmfiwf_workbooks = bmt.bm_fi[inst_key][FI_WORKFLOWS][wf_key][WF_WORKBOOKS]
        ...
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
    logger.debug("Complete: tryout_budget_model_template()...")
#endregion tryout_budget_model_template() function
# # ---------------------------------------------------------------------------- +       
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
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"+ Running {THIS_APP_NAME} ...")
        logger.info("+ ----------------------------------------------------- +")
        logger.debug(f"Start: {THIS_APP_NAME}...")

        bm = _BudgetModelTemplate()
        bms = str(bm)
        bmr = repr(bm)
        bmd = bm.to_dict()

        logger.debug(f"Budget Model: str() = '{bms}'")
        logger.debug(f"Budget Model: repr() = '{bmr}'")
        logger.debug(f"Budget Model: to_dict() = '{bmd}'")

        _ = "pause"
    except Exception as e:
        m = p3u.exc_msg("__main__", e)
        logger.error(m)
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
