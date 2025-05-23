# ---------------------------------------------------------------------------- +
#region p3_budget_model_template.py module
""" Provide a functional template class for the budget_model class.

    Creates a functional instance from a declared dictionary used to document
    the data structure and configure defaults. It is useful for validation
    of constant names, different default settings, etc.

    4/29/2025: Soon, the budget_model configuration and setup will be from a 
    config file. The template could be used to create a pristine, new config 
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
import logging, time, os, getpass, copy
from pathlib import Path
from typing import List

# third-party modules and packages
from config import settings
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from .budget_model_constants import *
from .budget_domain_model_identity import BudgetDomainModelIdentity
from .budget_domain_model import BudgetDomainModel # lazy import, avoid circular
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Model Template and config support 
# ---------------------------------------------------------------------------- +
class BudgetModelTemplate(BudgetDomainModel):
    """Default BudgetModelTemplate class, contains default, example values.
    
    Creates a BudgetModel object pre-populated with default configuration values.

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
        BDM_ID: "1a2b3c4d",  # random, but unique BMT Id.
        BDM_INITIALIZED: False,
        BDM_FOLDER: BDM_DEFAULT_BUDGET_FOLDER,               # bsm_BDM_FOLDER_path()
        BDM_URL: None,
        BDM_FI_COLLECTION: { # FI_COLLECTION (dict) {FI_KEY: FI_DATA}
            "boa": # FI_KEY
            {      # FI_DATA
                FI_KEY: "boa",
                FI_NAME: "Bank of America",
                FI_TYPE: "bank",
                FI_FOLDER: "boa",
                FI_DATA_COLLECTION: { # WF_DATA_COLLECTION (dict) {wf_key: WF_WORKBOOK_DATA}
                     BDM_WF_CATEGORIZATION: {  # WF_WOBKBOOK_DATA dict {key: [(),() ...]} 
                        WF_INPUT: [ # input data objects
                            ( "input_prefix_wb_name_1", "wb_abs_path_1" ),
                            ( "input_prefix_wb_name_2", "wb_abs_path_2" ),
                            ( "input_prefix_wb_name_3", "wb_abs_path_3" )
                        ], 
                        WF_WORKING: [ # working data objects, input and output
                            ( "wb_name_1", "wb_abs_path_1" ),
                            ( "wb_name_2", "wb_abs_path_2" ),
                            ( "wb_name_3", "wb_abs_path_3" )
                        ], 
                        WF_OUTPUT: [
                            ( "output_prefix_wb_name_1", "wb_abs_path_4" ),
                            ( "output_prefix_wb_name_2", "wb_abs_path_5" ),
                            ( "output_prefix_wb_name_3", "wb_abs_path_6" )
                        ]
                        }
                    },
                },
            "merrill": # FI_KEY
            {          # FI_DATA
                FI_KEY: "merrill",
                FI_NAME: "Merrill Lynch",
                FI_TYPE: "brokerage",
                FI_FOLDER: "merrill",
                FI_DATA_COLLECTION: None,
            },
        },
        BDM_WF_COLLECTION: {
            BDM_WF_INTAKE: {                    # bdm_fi_wf(fi_key, workflow)
                # WF Object - TODO: add WF_KEY, verify unique
                WF_KEY: BDM_WF_INTAKE,
                WF_NAME: BDM_WF_INTAKE,
                WF_INPUT_FOLDER: None,         # bsm_WF_INPUT(fi_key, workflow)
                WF_PREFIX_IN: None,
                WF_WORKING_FOLDER: "data/new",
                WF_OUTPUT_FOLDER: "data/new",
                WF_PREFIX_OUT: None,
                WF_TYPE_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                }
            },
            BDM_WF_CATEGORIZATION: {            # bdm_fi_wf(fi_key, workflow)
                # WF Object
                WF_KEY: BDM_WF_CATEGORIZATION,
                WF_NAME: BDM_WF_CATEGORIZATION,
                WF_INPUT_FOLDER: "data/new", # bsm_WF_INPUT(fi_key, workflow)
                WF_WORKING_FOLDER: "data/categorized",
                WF_OUTPUT_FOLDER: "data/categorized",
                WF_PREFIX_IN: None,
                WF_PREFIX_OUT: "categorized_",
                WF_TYPE_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                }
            },
            BDM_WF_FINALIZATION: {              # bdm_fi_wf(fi_key, workflow)
                # WF Object
                WF_KEY: BDM_WF_FINALIZATION,
                WF_NAME: BDM_WF_FINALIZATION,
                WF_INPUT_FOLDER: "data/categorized",   # bsm_WF_INPUT(fi_key, workflow)
                WF_WORKING_FOLDER: "data/finalized",
                WF_OUTPUT_FOLDER: "data/finalized",
                WF_PREFIX_IN: "categorized_",
                WF_PREFIX_OUT: "finalized_",
                WF_TYPE_MAP:  {
                    WF_OUTPUT: WF_OUTPUT_FOLDER,
                    WF_WORKING: WF_WORKING_FOLDER,
                    WF_INPUT: WF_INPUT_FOLDER
                }
            }
        },
        BDM_OPTIONS: {
            BMO_LOG_CONFIG: "budget_model_logging_config.jsonc",
            BMO_LOG_LEVEL: "DEBUG",
            BMO_LOG_FILE: "logs/p3BudgetModel.log",
            BMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
        },
        BDM_CREATED_DATE: None,
        BDM_LAST_MODIFIED_DATE: None,
        BDM_LAST_MODIFIED_BY: None,
        BDM_WORKING_DATA: {}
    }
    @classmethod
    def get_budget_model_template(cls) -> dict:
        """Get a fresh copy of the budget model template dictionary."""
        try:
            logger.debug("Start:  ...")
            bmt = cls.budget_model_template
            fresh_bmt = copy.deepcopy(bmt) # make a fresh copy of the template
            fresh_bmt[BDM_CREATED_DATE] = p3u.now_iso_date_string()
            fresh_bmt[BDM_LAST_MODIFIED_DATE] = p3u.now_iso_date_string()
            fresh_bmt[BDM_LAST_MODIFIED_BY] = getpass.getuser()
            # Fresh identity
            bmt_id = BudgetDomainModelIdentity()
            fresh_bmt[BDM_ID] = bmt_id.uid
            fresh_bmt[BDM_URL] = bmt_id.bdm_store_abs_path().as_uri()
            logger.debug(f"Complete:")   
            return fresh_bmt
        except Exception as e:
            m = p3u.exc_msg(cls.get_budget_model_template, e)
            logger.error(m)
            raise
    #endregion BudgetModelTemplate Configuration Template
    # ------------------------------------------------------------------------ +
    #region BudgetModelTemplate class constructor __init__()
    def __init__(self) -> None:
        """Construct a BudgetModelTemplate object used for configuration.
        
        The BudgetModelTemplate class is used to populate new 
        BudgetModel objects with default and example values.
        It is for internal use only. There are two means to apply it when
        constructing a new BudgetModel object:
        1. Instantiate the BudgetModelTemplate, which sets the 
           BudgetModel._default_config_object class variable which should be
           used when no config_object parameters is used with BudgetModel().
        2. Use the BudgetModelTemplate.budget_model_template class variable
           as the config_object parameter when instantiating BudgetModel, as
           in BudgetModel(config_object = BudgetModelTemplate.budget_model_template)

        The other common use case is to use the BUDMAN_STORE object as the 
        config_object parameter when instantiating BudgetModel. 

        budget_model_template: dict (class variable)
            The dictionary that defines the structure of the budget model and
            gives default and example values.
        """
        st = p3u.start_timer()
        try:
            # Basic attribute atomic value inits. 
            logger.debug("Start:  ...")
            # Initialize values from the template as configuration values.
            bmt_dict = BudgetModelTemplate.budget_model_template
            # Invoke the base BudgetModel.__init__() to finish instance creation.
            # BudgetModel properties work after super().__init__()
            super().__init__(config_object = bmt_dict)
            # Make self the BudgetModel._default_config_object
            BudgetDomainModel._default_config_object = self

            # Complete the BudgetModelTemplate instance initialization.
            bmt_id = BudgetDomainModelIdentity(
                uid = bmt_dict[BDM_ID],
                filename = THIS_APP_NAME,
                filetype = BSM_DEFAULT_BUDGET_MODEL_FILE_TYPE)
            self.bdm_id = bmt_dict[BDM_ID]                            # property
            self.bdm_initialized = bmt_dict[BDM_INITIALIZED]            # property
            self.bdm_folder = BDM_DEFAULT_BUDGET_FOLDER                 # property
            self.bm_url = bmt_id.bdm_store_abs_path().as_uri()        # property
            self.bdm_wf_collection = bmt_dict[BDM_WF_COLLECTION].copy() # property
            for fi_key, fi_dict in bmt_dict[BDM_FI_COLLECTION].items():
                self.bdm_fi_collection[fi_key] = fi_dict.copy()        # property
            self.bdm_options = bmt_dict[BDM_OPTIONS].copy()             # property
            self.bdm_created_date = p3u.now_iso_date_string()          # property
            self.bdm_last_modified_date = self.bdm_created_date         # property
            self.bdm_last_modified_by = getpass.getuser()              # property
            self.bdm_working_data = bmt_dict[BDM_WORKING_DATA]          # property
            self.bdm_initialized = True
            logger.debug(f"Complete: {p3u.stop_timer(st)}")   
        except Exception as e:
            m = p3u.exc_msg(self.__init__, e)
            logger.error(m)
            raise
    #endregion BudgetModelTemplate class constructor __init__()
    # ------------------------------------------------------------------------ +
    #region log_BMT_info()
    @staticmethod
    def log_BMT_info(bmt : "BudgetModelTemplate") -> None:
        """Log the BudgetModelTemplate class information."""
        try:
            logger.debug("Start:  ...")
            logger.debug(f"{P2}BDM_INITIALIZED('{BDM_INITIALIZED}'): "
                         f"{bmt.bdm_initialized}")
            logger.debug(f"{P2}BDM_FOLDER('{BDM_FOLDER}'): '{bmt.bdm_url}'")
            logger.debug(f"{P2}BDM_URL('{BDM_URL}): '{bmt.bdm_url}' ")
            logger.debug(f"{P2}BDM_WORKFLOWS('{BDM_WF_COLLECTION}'): "
                         f" '{bmt.bdm_wf_collection}'")
            # Enumerate Financial Institutions (FI)
            fi_c = len(bmt.bdm_fi_collection)  # financial institutions count
            logger.debug(f"{P2}BDM_FI('{BDM_FI_COLLECTION}')({fi_c})")
            for fi_key, fi_object in bmt.bdm_fi_collection.items():
                logger.debug(f"{P4}Financial Institution: "
                         f"{fi_key}:{fi_object[FI_NAME]}:"
                         f"{fi_object[FI_TYPE]}: '{fi_object[FI_FOLDER]}'")
            # Enumerate Workflows in the budget model
            c = len(bmt.bdm_wf_collection)
            logger.debug(
                f"{P2}BDM_WF_COLLECTION['{BDM_WF_COLLECTION}']({c}): "
                f"{str(list(bm.bdm_wf_collection.keys()))}")
            for wf_key, wf_object in bm.bdm_wf_collection.items():
                logger.debug(f"{P4}Workflow:({wf_key}:{wf_object[WF_NAME]}: ")
                logger.debug(f"{P6}WF_INPUT: '{bmt.wf_object[WF_INPUT_FOLDER]}'")
                logger.debug(f"{P6}WF_OUTPUT_FOLDER: '{bmt.wf_object[WF_OUTPUT_FOLDER]}'")
                logger.debug(f"{P6}WF_PREFIX_IN: '{bmt.wf_object[WF_PREFIX_IN]}' "
                            f"WF_PREFIX_OUT: '{bmt.wf_object[WF_PREFIX_OUT]}'")
                logger.debug(f"{P6}WF_TYPE_MAP: {str(bmt.wf_object[WF_TYPE_MAP])}")
            # Enumerate Budget Model Options
            bmo_c = len(bmt.bdm_options)
            logger.debug(f"{P2}BDM_OPTION('{BDM_OPTIONS}')({bmo_c})")
            for opt_key, opt in bmt.bdm_options.items():
                logger.debug(f"{P4}Option('{opt_key}') = '{opt}'")

            # "And the rest. Here on Gilligan's Isle..."
            logger.debug(f"{P2}BDM_CREATED_DATE({BDM_CREATED_DATE}'): "
                         f"{bmt.bdm_created_date}")
            logger.debug(f"{P2}BDM_LAST_MODIFIED_DATE({BDM_LAST_MODIFIED_DATE}'): "
                            f"{bmt.bdm_last_modified_date}")
            logger.debug(f"{P2}BDM_LAST_MODIFIED_BY({BDM_LAST_MODIFIED_BY}'): "
                            f"{bmt.bdm_last_modified_by}")
            logger.debug(f"{P2}BDM_WORKING_DATA({BDM_WORKING_DATA}'): "
                            f"{bmt.bdm_working_data}")
            logger.debug(f"Complete:")   
        except Exception as e:
            m = p3u.exc_err_msg(e)
            logger.error(m)
            raise

    #endregion log_BMT_info()
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
        for fi_key, fi_dict in bmt.bdm_fi_collection.items():
            logger.debug(f"Financial Institution: {fi_dict[FI_FOLDER]}:"
                         f"{fi_dict[FI_TYPE]}:{fi_dict[FI_NAME]}:")
        for wf_key, wf_dict in bmt.bdm_wf_collection.items():
            logger.debug(f"{P2}Workflow('{wf_dict[WF_NAME]}'): "
                            f"{P2}WM_FOLDER_IN: '{wf_dict[WF_INPUT_FOLDER]}' "
                            f"{P2}WM_WORKBOOS_IN: {wf_dict[WF_INPUT]}")
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
