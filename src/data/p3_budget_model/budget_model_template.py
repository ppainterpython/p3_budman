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
    
    Creates a BudgetModel object pre-poulated with default configuration values.

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
    budget_model_template = {  
        # BDM object
        BM_INITIALIZED: False,
        BM_FOLDER: BM_DEFAULT_BUDGET_FOLDER,               # bsm_BM_FOLDER_path()
        BM_STORE_URI: None,
        BM_FI_COLLECTION: { # FI_COLLECTION (dict) {FI_KEY: FI_OBJECT}
            "boa": # FI_KEY
            {      # FI_OBJECT
                FI_KEY: "boa",
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                FI_WORKFLOW_DATA: { # WF_WORKFLOWTA (dict) {wf_key: WF_WORKBOOK_DATA}
                     BM_WF_CATEGORIZATION: {  # WF_WOBKBOOK_DATA dcit {key: [(),() ...]} 
                        WF_WORKBOOKS_IN: [ # WF_WROKBOOK_LIST
                            ( "input_prefix_wb_name_1", "wb_abs_path_1" ),
                            ( "input_prefix_wb_name_2", "wb_abs_path_2" ),
                            ( "input_prefix_wb_name_3", "wb_abs_path_3" )
                        ], 
                        WF_WORKBOOKS_OUT: [
                            ( "output_prefix_wb_name_1", "wb_abs_path_4" ),
                            ( "output_prefix_wb_name_2", "wb_abs_path_5" ),
                            ( "output_prefix_wb_name_3", "wb_abs_path_6" )
                        ]
                        }
                    },
                },
            "merrill": # FI_KEY
            {          # FI_OBJECT
                FI_KEY: "merrill",
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                FI_WORKFLOW_DATA: None,
            },
        },
        BM_WF_COLLECTION: {
            BM_WF_INTAKE: {                    # bdm_fi_wf(fi_key, workflow)
                # WF Object - TODO: add WF_KEY, verify unique
                WF_KEY: BM_WF_INTAKE,
                WF_NAME: BM_WF_INTAKE,
                WF_FOLDER_IN: None,         # bsm_WF_WORKBOOKS_IN(fi_key, workflow)
                WF_PREFIX_IN: None,
                WF_FOLDER_OUT: "data/new",
                WF_PREFIX_OUT: None,
                WF_WORKBOOK_MAP:  {
                    WF_WORKBOOKS_OUT: WF_FOLDER_OUT,
                    WF_WORKBOOKS_IN: WF_FOLDER_IN
                }
            },
            BM_WF_CATEGORIZATION: {            # bdm_fi_wf(fi_key, workflow)
                # WF Object
                WF_KEY: BM_WF_CATEGORIZATION,
                WF_NAME: BM_WF_CATEGORIZATION,
                WF_FOLDER_IN: "data/new", # bsm_WF_WORKBOOKS_IN(fi_key, workflow)
                WF_FOLDER_OUT: "data/categorized",
                WF_PREFIX_IN: None,
                WF_PREFIX_OUT: "categorized_",
                WF_WORKBOOK_MAP:  {
                    WF_WORKBOOKS_OUT: WF_FOLDER_OUT,
                    WF_WORKBOOKS_IN: WF_FOLDER_IN
                }
            },
            BM_WF_FINALIZATION: {              # bdm_fi_wf(fi_key, workflow)
                # WF Object
                WF_KEY: BM_WF_FINALIZATION,
                WF_NAME: BM_WF_FINALIZATION,
                WF_FOLDER_IN: "data/categorized",   # bsm_WF_WORKBOOKS_IN(fi_key, workflow)
                WF_FOLDER_OUT: "data/finalized",
                WF_PREFIX_IN: "categorized_",
                WF_PREFIX_OUT: "finalized_",
                WF_WORKBOOK_MAP:  {
                    WF_WORKBOOKS_OUT: WF_FOLDER_OUT,
                    WF_WORKBOOKS_IN: WF_FOLDER_IN
                }
            }
        },
        BM_OPTIONS: {
            BMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BMO_LOG_LEVEL: "DEBUG",
            BMO_LOG_FILE: "logs/p3BudgetModel.log",
            BMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        },
        BM_CREATED_DATE: None,
        BM_LAST_MODIFIED_DATE: None,
        BM_LAST_MODIFIED_BY: None,
        BM_WORKING_DATA: None
    }
    #endregion BudgetModelTemplate Configuration Template
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate class constructor __init__.()
    # __init__() method for the BudgetModelTemplate class
    # Focus on populating the template for value inititialization in the
    # BudgetModel Domain class. Leave all Budget Storage Model (BSM) setup
    # for initialization elsewhere.
    def __init__(self, create_missing_folders : bool = True,
                 raise_errors : bool = True) -> None:
        """Construct a BudgetModelTemplate object used to initialize the budget model.
        
        The template class is largely a dictionary populated with default values
        and some example values. The idea is to use this template to create a new
        budget model or to initialize a new budget model from the template. 
        It is for internal use only.
        """
        st = p3u.start_timer()
        try:
            # Basic attribute atomic value inits. 
            logger.debug("Start:  ...")
            super().__init__(classname=BudgetModelTemplate.__name__)
            # Use of properties okay now.

            # Initialize values from the template as configuration values.
            bmt = BudgetModelTemplate.budget_model_template
            self.bm_initialized = bmt[BM_INITIALIZED] # property
            logger.debug(f"{P2}BM_INITIALIZED('{BM_INITIALIZED}'): "
                         f"{self.bm_initialized}")
            self.bm_folder = BM_DEFAULT_BUDGET_FOLDER   # property
            bf_p = self.bsm_BM_FOLDER_path() # budget folder path
            bmc = bf_p / BSM_DEFAULT_BUDGET_MODEL_FILE_NAME # bmc: BM config file
            bfp_exists = "exists." if bf_p.exists() else "does not exist!"
            bmc_exists = "exists." if bmc.exists() else "does not exist!"
            bmc_uri = p3u.path_to_file_uri(bmc) 
            self.bm_store_uri = bmc_uri # property
            self.bm_wf_collection = bmt[BM_WF_COLLECTION] # property
            logger.debug(f"{P2}BM_FOLDER('{BM_FOLDER}'): '{self.bm_store_uri}' {bfp_exists}")
            logger.debug(
                f"{P4}bsm_BM_FOLDER_path(): '{self.bsm_BM_FOLDER_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P4}bsm_BM_FOLDER_abs_path(): '{self.bsm_BM_FOLDER_abs_path()}' "
                f"{bfp_exists}")
            logger.debug(
                f"{P2}BM_STORE_URI('{BM_STORE_URI}): '{self.bm_store_uri}' "
                f"{bmc_exists}")
            logger.debug(
                f"{P2}BM_WORKFLOWS('{BM_WF_COLLECTION}'): "
                f" '{self.bm_wf_collection}'")
            # Financial Institutions (FI), copy from template.
            fic = len(bmt[BM_FI_COLLECTION])  # financial institutions count
            logger.debug(f"{P2}BM_FI('{BM_FI_COLLECTION}')({fic})")
            for fi_key, fi_dict in bmt[BM_FI_COLLECTION].items():
                self.bm_fi_collection[fi_key] = fi_dict.copy()  # property, copy
                fi_p = self.bsm_FI_FOLDER_path(fi_key)  # FI folder path
                fi_ap = self.bsm_FI_FOLDER_abs_path(fi_key) # FI folder abs path
                logger.debug(f"{P4}FI_KEY('{fi_key}') folder: '{fi_p}'")
                logger.debug(f"{P6}FI_KEY('{fi_key}') {str(fi_dict)}")
                if_p = self.bsm_FI_FOLDER_path(fi_key)
                if_p_exists = "exists." if if_p.exists() else "does not exist!"
                logger.debug(f"{P6}bsm_FI_FOLDER_path(): '{if_p}' "
                             f"{if_p_exists}")
                if_ap = self.bsm_FI_FOLDER_abs_path(fi_key)
                if_ap_exists = "exists." if if_ap.exists() else "does not exist!"
                logger.debug(f"{P6}bsm_FI_FOLDER_abs_path(): '{if_ap}'"
                             f"{if_ap_exists}")

            # Initialize Budget Model Options as a template
            self.bm_options = bmt[BM_OPTIONS].copy() # property
            bmoc = len(bmt[BM_OPTIONS])
            logger.debug(f"{P2}BM_OPTION('{BM_OPTIONS}')({bmoc})")
            for opt_key, opt in bmt[BM_OPTIONS].items():
                logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

            # And the rest
            self.bm_created_date = p3u.now_iso_date_string() # property
            self.bm_last_modified_date = self.bm_created_date # property
            self.bm_last_modified_by = getpass.getuser() # property
            self.bm_working_data = bmt[BM_WORKING_DATA] # property
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
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
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
    st = p3u.start_timer()
    try:
        logger.debug("Start: ...")
        bmt = BudgetModelTemplate()
        bmt.bsm_inititalize() # initialize the budget storage model 
        
        # Enumerate the financial institutions in the budget model template
        for fi_key, fi_dict in bmt.bm_fi_collection.items():
            logger.debug(f"Financial Institution: {fi_dict[FI_FOLDER]}:"
                         f"{fi_dict[FI_TYPE]}:{fi_dict[FI_NAME]}:")
        for wf_key, wf_dict in bmt.bm_wf_collection.items():
            logger.debug(f"{P2}Workflow('{wf_dict[WF_NAME]}'): "
                            f"{P2}WM_FOLDER_IN: '{wf_dict[WF_FOLDER_IN]}' "
                            f"{P2}WM_WORKBOOS_IN: {wf_dict[WF_WORKBOOKS_IN]}")
        # logger.debug(f"Budget Model Template:     str: '{str(bmt)}'")
        # logger.debug(f"Budget Model Template:    repr: '{repr(bmt)}'")
        # logger.debug(f"Budget Model Template: to_dict: '{bmt.to_dict()}'")
        logger.debug(f"Complete: {p3u.stop_timer(st)}")   
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        raise
#endregion tryout_budget_model_template() function
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
        bdm = bm.to_dict()

        logger.debug(f"Budget Model: str() = '{bms}'")
        logger.debug(f"Budget Model: repr() = '{bmr}'")
        logger.debug(f"Budget Model: to_dict() = '{bdm}'")

        _ = "pause"
    except Exception as e:
        m = p3u.exc_msg("__main__", e)
        logger.error(m)
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
