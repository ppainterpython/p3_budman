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
import logging, time, os, getpass
from pathlib import Path
from typing import List

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from .budget_model_constants import *
from .budget_model import BudgetModel # lazy import, avoid circular
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Model Template and config support 
# ---------------------------------------------------------------------------- +
class BudgetModelTemplate(BudgetModel):
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
    budget_config_expected_keys = (
        BM_INITIALIZED,
        BM_BF, 
        BM_STORE_URI,
        BM_SUPPORTED_WORKFLOWS,
        BM_FI, 
        BM_OPTIONS,
        BM_CREATED_DATE,
        BM_LAST_MODIFIED_DATE,
        BM_LAST_MODIFIED_BY,
        BM_WORKING_DATA
        )
    valid_workflows = BM_VALID_WORKFLOWS
    workflow_expected_keys = (
        WF_NAME,
        WF_FOLDER,
        WF_WORKBOOKS
        )
    valid_institutions_keys = ("boa", "merrill")
    institution_expected_keys = (
        FI_NAME, 
        FI_TYPE, 
        FI_FOLDER,
        FI_WORKFLOWS 
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
    budget_model_template = {  
        BM_INITIALIZED: False,
        BM_BF: BM_DEFAULT_BUDGET_FOLDER,               # bms_bf_path()
        BM_STORE_URI: None,
        BM_SUPPORTED_WORKFLOWS: [
            BM_WF_INTAKE, 
            BM_WF_CATEGORIZATION, 
            BM_WF_FINALIZATION
            ],
        BM_FI: {
            "boa": {                                   # bmd_fi(inst_key) -> object
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",                      # bms_fi_path(inst_key)
                FI_WORKFLOWS: {
                    BM_WF_INTAKE: {                    # bmd_fi_wf(inst_key, workflow)
                        WF_NAME: BM_WF_INTAKE,
                        WF_FOLDER: "data/new",         # bms_fi_wf_path(inst_key, workflow)
                        WF_WORKBOOKS: {}
                    },
                    BM_WF_CATEGORIZATION: {            # bmd_fi_wf(inst_key, workflow)
                        WF_NAME: BM_WF_CATEGORIZATION,
                        WF_FOLDER: "data/categorized", # bms_fi_wf_path(inst_key, workflow)
                        WF_WORKBOOKS: {}
                    },
                    BM_WF_FINALIZATION: {              # bmd_fi_wf(inst_key, workflow)
                        WF_NAME: BM_WF_FINALIZATION,
                        WF_FOLDER: "data/processed",   # bms_fi_wf_path(inst_key, workflow)
                        WF_WORKBOOKS: {}
                    }
                },
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
            },
        },
        BM_OPTIONS: {
            BMO_FI_IF_PREFIX: "new_",
            BMO_FI_CF_PREFIX: "categorized_",
            BMO_FI_CF_PREFIX: "final_",
            BMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BMO_LOG_LEVEL: "DEBUG",
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
        # Make BudgetModel_template only about BM Domain initialization.
        st = time.time()
        try:
            # Basic attribute atomic value inits. 
            logger.debug("Start:  ...")
            super().__init__(classname=BudgetModelTemplate.__name__)
            # Use of properties okay now.

            # Initialize values from the template as configuration values.
            bmt = BudgetModelTemplate.budget_model_template
            self.bm_initialized = bmt[BM_INITIALIZED] 
            logger.debug(f"{P2}BM_INITIALIZED('{BM_INITIALIZED}'): "
                         f"{self.bm_initialized}")
            self.bm_bf = bmt[BM_DEFAULT_BUDGET_FOLDER] # budget folder setting, a str
            bf_p = self.bms_bf_path() # budget folder path
            bmc = bf_p / BMS_DEFAULT_BUDGET_MODEL_FILE_NAME # bmc: BM config file
            bfp_exists = "exists." if bf_p.exists() else "does not exist!"
            bmc_exists = "exists." if bmc.exists() else "does not exist!"
            bmc_uri = p3u.path_to_file_uri(bmc) 
            self.bm_store_uri = bmc_uri # uri for budget model config
            self.bm_supported_workflows = bmt[BM_SUPPORTED_WORKFLOWS]
            logger.debug(f"{P2}BM_BF('{BM_BF}'): '{self.bm_store_uri}' {bfp_exists}")
            logger.debug(
                f"{P4}bms_bf_path(): '{self.bms_bf_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P4}bms_bf_abs_path(): '{self.bms_bf_abs_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P2}BM_STORE_URI('{BM_STORE_URI}): '{self.bm_store_uri}' "
                f"{bmc_exists}")
            logger.debug(
                f"{P2}BM_SUPPORTED_WORKFLOWS('{BM_SUPPORTED_WORKFLOWS}'): "
                f" '{self.bm_supported_workflows}'")
            # Financial Institutions (FI), copy from template.
            fic = len(bmt[BM_FI])  # financial institutions count
            logger.debug(f"{P2}BM_FI('{BM_FI}')({fic})")
            for inst_key, inst in bmt[BM_FI].items():
                self.bm_fi[inst_key] = inst.copy()  # Copy the template values
                fi_p = self.bms_fi_path(inst_key)  # FI folder path
                fi_ap = self.bms_fi_abs_path(inst_key) # FI folder abs path
                logger.debug(f"{P4}FI_KEY('{inst_key}') folder: '{fi_p}'")
                # move mkdir() stuff to separate bms_initialize() method.
                if not fi_ap.exists():
                    # If create_missing_folders is True, create the folder
                    if create_missing_folders:
                        logger.debug(f"{P4}Creating folder: '{fi_ap}'")
                        fi_ap.mkdir(parents=True, exist_ok=True)
                    else:
                        m = (f"{P4}Budget institution({inst_key}) " 
                            f"folder does not exist: '{str(fi_ap)}'")
                        logger.error(m)
                        raise FileNotFoundError(m) if raise_errors else None
                logger.debug(f"{P6}FI_KEY('{inst_key}') {str(inst)}")
                if_p = self.bms_fi_path(inst_key)
                if_p_exists = "exists." if if_p.exists() else "does not exist!"
                logger.debug(f"{P6}bms_fi_path(): '{if_p}' "
                             f"{if_p_exists}")
                if_ap = self.bms_fi_abs_path(inst_key)
                if_ap_exists = "exists." if if_ap.exists() else "does not exist!"
                logger.debug(f"{P6}bms_fi_abs_path(): '{if_ap}'"
                             f"{if_ap_exists}")
                wf_dict = bmt.bms_fi_wf_resolve_workbooks("boa", BM_WF_INTAKE)
                bmt.set_bm_fi_wf_workbooks("boa", BM_WF_INTAKE, wf_dict)

            # Initialize Budget Model Options as a template
            bmoc = len(bmt[BM_OPTIONS])
            logger.debug(f"{P2}BM_OPTION('{BM_OPTIONS}')({bmoc})")
            for opt_key, opt in bmt[BM_OPTIONS].items():
                logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

            # And the rest
            logger.debug(f"{P2}BM_CREATED_DATE({BM_CREATED_DATE}'): "
                         f"{self.bm_created_date}")
            logger.debug(f"{P2}BM_LAST_MODIFIED_DATE({BM_LAST_MODIFIED_DATE}'): "
                            f"{self.bm_last_modified_date}")
            logger.debug(f"{P2}BM_LAST_MODIFIED_BY({BM_LAST_MODIFIED_BY}'): "
                            f"{self.bm_last_modified_by}")
            logger.debug(f"{P2}BM_WORKING_DATA({BM_WORKING_DATA}'): "
                            f"{self.bm_working_data}")
            # BudgetModelTemplate initialization is complete.
            self.bm_initialized = True
            logger.debug(f"{P2}{BM_INITIALIZED}: {self.bm_initialized}")
            delta = f"{time.time() - st:.3f} seconds."
            logger.debug(f"Complete: {delta}")   
        except Exception as e:
            m = p3u.exc_msg(self.__init__, e)
            logger.error(m)
            raise
    #endregion BudgetModelTemplate class constructor __init__.()
    # ------------------------------------------------------------------------ +
# ---------------------------------------------------------------------------- +
#region tryout_budget_model_template() function
def tryout_budget_model_template() -> None: 
    """Test the BudgetModelTemplate class."""
    st = time.time()
    try:
        logger.debug("Start: ...")
        bmt = BudgetModelTemplate()
        logger.debug(f"Budget Model Template:     str: '{str(bmt)}'")
        logger.debug(f"Budget Model Template:    repr: '{repr(bmt)}'")
        logger.debug(f"Budget Model Template: to_dict: '{bmt.to_dict()}'")

        wf_dict = bmt.bms_fi_wf_resolve_workbooks("boa", BM_WF_INTAKE)
        before = bmt.get_bm_fi_wf_workbooks("boa", BM_WF_INTAKE)
        bmt.set_bm_fi_wf_workbooks("boa", BM_WF_INTAKE, wf_dict)
        after = bmt.get_bm_fi_wf_workbooks("boa", BM_WF_INTAKE)
        # Enumerate the financial institutions in the budget model template
        for inst_key, inst in bmt.bm_fi.items():
            n = inst[FI_NAME]
            t = inst[FI_TYPE]
            f = inst[FI_FOLDER]
            wf = list(inst[FI_WORKFLOWS].keys()) 
            logger.debug(f"Financial Institution: {f}:{t}:{n}:{str(wf)}")
            for wf_key, wf_dict in inst[FI_WORKFLOWS].items():
                logger.debug(f"{P2}Workflow('{wf_dict[WF_NAME]}'): "
                             f"{P2}Folder: '{wf_dict[WF_FOLDER]}' "
                             f"{P2}Workbooks: {wf_dict[WF_WORKBOOKS]}")
                wf_wb_ap = bmt.fi_wf_abs_path(inst_key, wf_key)
                bmfiwf_workbooks = bmt.bm_fi[inst_key][FI_WORKFLOWS][wf_key][WF_WORKBOOKS]
        delta = f"{time.time() - st:.3f} seconds."
        logger.debug(f"Complete: {delta}")   
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

        bm = BudgetModelTemplate()
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
