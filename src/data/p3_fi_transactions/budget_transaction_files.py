# ---------------------------------------------------------------------------- +
#region p3_execl_budget.p3_banking_transactions transaction_files.py module
""" Support for reading and writing excel files for FI transactions.

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
import pathlib as Path, logging

# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
from openpyxl import Workbook, load_workbook

# local modules and packages
from p3_excel_budget_constants import  *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(THIS_APP_NAME)
# ---------------------------------------------------------------------------- +
#region Budget Model Configuration
# Budget configuration covers the file structure where user data is stored as 
# settings for options and preferences. Keep it simple.
# There is both an object model used in the application (in memory) and a
# file system structure used to store the data. In addition, the idea is that 
# users are placing new FI transactions in an "incoming" folder folder 
# for processing through stages to arrive in updating the budget. Long-view is 
# anticipate more than one bank or financial institution sourcing regular 
# statements in spreadsheet format. So, the "budget" will cover multiple "banks"
# information for a given user.
budget_config_expected_keys = (BM_BUDGET_FOLDER, BT_FINANCIAL_INSTITUTIONS, 
                               BMO_OPTIONS)
valid_institutions_keys = ("boa", "merrill")
institution_expected_keys = (
    FI_NAME, 
    FI_TYPE, 
    FI_FOLDER, 
    FI_FOLDER_ABS_PATH_STR,
    FI_FOLDER_ABS_PATH,
    IF_INCOMING_FOLDER,
    IF_INCOMING_FOLDER_ABS_PATH_STR,
    IF_INCOMING_FOLDER_ABS_PATH,
    IF_INCOMING_FOLDER_WORKBOOKS,
    CF_CATEGORAIZED_FOLDER,
    CF_CATEGORAIZED_FOLDER_ABS_PATH_STR,
    CF_CATEGORAIZED_FOLDER_ABS_PATH,
    CF_CATEGORAIZED_FOLDER_WORKBOOKS,
    PF_PROCESSED_FOLDER,
    PF_PROCESSED_FOLDER_ABS_PATH_STR,
    PF_PROCESSED_FOLDER_ABS_PATH,
    PF_PROCESSED_FOLDER_WORKBOOKS
    )
options_expected_keys = (
    BMO_INCOMING_PREFIX, 
    BMO_CATEGORIZED_PREFIX,
    BMO_PROCESSED_PREFIX,
    BMO_LOG_CONFIG,
    BMO_LOG_LEVEL,
    BMO_LOG_FILE,
    BMO_JSON_LOG_FILE
    )

budget_config = {  # _abs_path is not serialized, only _abs_path_str is serialized
    BM_INITIALIZED: False,
    BM_BUDGET_FOLDER: "~/OneDrive/budget",
    BM_BUDGET_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
    BM_BUDGET_FOLDER_ABS_PATH: None,    # Not serialized
    BT_FINANCIAL_INSTITUTIONS: {
        "boa": {
            FI_NAME: "Bank of America",
            FI_TYPE: "bank",
            FI_FOLDER: "boa",
            FI_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
            FI_FOLDER_ABS_PATH: None,    # Not serialized
            # Incoming folder name and list of workbook names,
            # e.g. ["new_boa-1391-2024-04-28.xlsx"]
            IF_INCOMING_FOLDER: "data/new",
            IF_INCOMING_FOLDER_ABS_PATH_STR: None,    # Set in init_budget_model()
            IF_INCOMING_FOLDER_ABS_PATH: None,    # Not serialized
            IF_INCOMING_FOLDER_WORKBOOKS: {}, # key = file name, value = absolute path
            # Categorized folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
            CF_CATEGORAIZED_FOLDER: "data/categorized",
            CF_CATEGORAIZED_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
            CF_CATEGORAIZED_FOLDER_ABS_PATH: None,    # Not serialized
            CF_CATEGORAIZED_FOLDER_WORKBOOKS: {}, # key = file name, value = absolute path
            # Processed folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
            PF_PROCESSED_FOLDER: "data/processed",
            PF_PROCESSED_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
            PF_PROCESSED_FOLDER_ABS_PATH: None,    # Not serialized
            PF_PROCESSED_FOLDER_WORKBOOKS: {} # key = file name, value = absolute path
        },
        "merrill": {
            FI_NAME: "Merrill Lynch",
            FI_TYPE: "brokerage",
            FI_FOLDER: "merrill",
            FI_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
            FI_FOLDER_ABS_PATH: None,    # Not serialized
            # Incoming folder name and list of workbook names,
            # e.g. ["new_boa-1391-2024-04-28.xlsx"]
            IF_INCOMING_FOLDER: "data/new",
            IF_INCOMING_FOLDER_ABS_PATH_STR: None,    # Set in init_budget_model()
            IF_INCOMING_FOLDER_ABS_PATH: None,    # Not serialized
            IF_INCOMING_FOLDER_WORKBOOKS: {}, # key = file name, value = absolute path
            # Categorized folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-04-28.xlsx"]
            CF_CATEGORAIZED_FOLDER: "data/categorized",
            CF_CATEGORAIZED_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
            CF_CATEGORAIZED_FOLDER_ABS_PATH: None,    # Not serialized
            CF_CATEGORAIZED_FOLDER_WORKBOOKS: {}, # key = file name, value = absolute path
            # Processed folder name and list of workbook names,
            # e.g. ["categorized_boa-1391-2024-03-28.xlsx"]
            PF_PROCESSED_FOLDER: "data/processed",
            PF_PROCESSED_FOLDER_ABS_PATH_STR: None, # Set in init_budget_model()
            PF_PROCESSED_FOLDER_ABS_PATH: None,    # Not serialized
            PF_PROCESSED_FOLDER_WORKBOOKS: {} # key = file name, value = absolute path
        },
    },
    BMO_OPTIONS: {
        BMO_INCOMING_PREFIX: "new_",
        BMO_CATEGORIZED_PREFIX: "categorized_",
        BMO_PROCESSED_PREFIX: "processed_",
        BMO_LOG_CONFIG: p3l.STDOUT_FILE_LOG_CONFIG_FILE,
        BMO_LOG_LEVEL: logging.DEBUG,
        BMO_LOG_FILE: "logs/p3BudgetModel.log",
        BMO_JSON_LOG_FILE: "logs/p3BudgetModel.jsonl"
    }
}
#endregion Budget Model Configuration
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Budget Model (MVVM sense of Model)
# ---------------------------------------------------------------------------- +
budget_model :dict = None
budget_abs_path : Path.Path = None
selected_institution : str = "boa"
incoming_folder_abs_path : Path.Path = None
categorized_folder_abs_path : Path.Path = None
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
        for institution_key in valid_institutions_keys:
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
#region init_budget_model(budget_config) -> None
def init_budget_model(create_missing_folders : bool = True, raise_errors : bool = False) -> dict:
    """Initialize the budget model with the given configuration.

    Args:
        budget_config (dict): The budget configuration dictionary.

    Returns:
        dict: The initialized budget model.
    """
    me = init_budget_model
    try:
        global budget_config, budget_model, budget_abs_path, selected_institution
        global incoming_folder_abs_path, categorized_folder_abs_path
        if budget_model is not None and isinstance(budget_model, dict):
            # Already initialized, so just return
            logger.info(f"Budget model already initialized.")
            return budget_model
        # -------------------------------------------------------------------- +
        logger.info(f"Initializing budget model...")

        # Use the budget_config to set up the budget model
        # TODO: Load value from model storage (e.g. json file) if it exists.

        # Deep copy budget_config using comprehensions
        budget_model = {
            key: (
                {k: (v[:] if isinstance(v, list) else v) for k, v in value.items()}
                if isinstance(value, dict) else value
            )
            for key, value in budget_config.items()
        }
        # Check the budget model schema
        if not check_budget_model():
            m = "Budget model schema is not valid."
            logger.error(m)
            raise ValueError(m)
        
        # Set up Paths for the appropariate folders
        # Start with budget folder, then institution folder, then incoming folder
        # and categorized folder. Construct and validate absolute paths for all folders.
        logger.debug(f"{BM_BUDGET_FOLDER}: '{budget_model[BM_BUDGET_FOLDER]}'")
        budget_folder_path = Path.Path(budget_model[BM_BUDGET_FOLDER]).expanduser()
        budget_folder_abs_path = budget_folder_path.resolve()
        logger.debug(f"budget_folder_abs_path: '{budget_folder_abs_path}'")
        if not budget_folder_abs_path.exists():
            m = f"Budget folder does not exist: '{str(budget_folder_abs_path)}' ."
            logger.error(m)
            raise FileNotFoundError(m)
        budget_model["budget_folder_abs_path_str"] = str(budget_folder_abs_path)
        budget_model["budget_folder_abs_path"] = budget_folder_abs_path

        # Institution folders
        for institution_key, institution in budget_model[BT_FINANCIAL_INSTITUTIONS].items():
            institution_folder_path = budget_folder_path / institution["folder"]
            institution_folder_abs_path = institution_folder_path.resolve()
            logger.debug(f"{institution_key} folder: '{institution_folder_path}'")
            logger.debug(f"{institution_key} folder_abs_path: '{institution_folder_abs_path}'")
            if not institution_folder_abs_path.exists():
                # If create_missing_folders is True, create the folder
                if create_missing_folders:
                    logger.debug(f"Creating folder: '{institution_folder_abs_path}'")
                    institution_folder_abs_path.mkdir(parents=True, exist_ok=True)
                else:
                    m = (f"Budget institution({institution_key}) " 
                        f"folder does not exist: '{str(institution_folder_abs_path)}'")
                    logger.error(m)
                    raise FileNotFoundError(m) if raise_errors else None
            budget_model[BT_FINANCIAL_INSTITUTIONS][institution_key]["folder_abs_path_str"] = str(institution_folder_abs_path)
            budget_model[BT_FINANCIAL_INSTITUTIONS][institution_key]["folder_abs_path"] = institution_folder_abs_path
        
        # Create transaction subfolders if they do not exist
        for institution in budget_model[BT_FINANCIAL_INSTITUTIONS].values():
            for subfolder_type in ["incoming_folder", "categorized_folder", "processed_folder"]:
                subfolder_path = institution["folder_abs_path"] / institution[subfolder_type]
                if not subfolder_path.exists():
                    logger.debug(f"Creating folder: {subfolder_path}")
                    subfolder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Institution({institution["folder"]})[{subfolder_type}]: '{str(subfolder_path)}'")
                institution[subfolder_type + "_abs_path_str"] = str(subfolder_path)
                institution[subfolder_type + ABS_PATH] = subfolder_path.resolve()

        # Look for subfolder workbooks
        for institution in budget_config[BT_FINANCIAL_INSTITUTIONS].values():
            for subfolder_type in [IF_INCOMING_FOLDER, CF_CATEGORAIZED_FOLDER, PF_PROCESSED_FOLDER]:
                subfolder_path = institution[subfolder_type + ABS_PATH]
                # Get the list of workbooks in the subfolder
                workbooks = list(subfolder_path.glob("*.xlsx"))
                # Add the workbook names to the budget model
                institution[subfolder_type + "_workbooks"] = {path.name: path for path in workbooks}
                logger.debug(f"Institution({institution["folder"]})[{subfolder_type}]: Workbooks: '{str(institution[subfolder_type + "_workbooks"])}'")
        budget_model[BM_INITIALIZED] = True
        return budget_model
    except Exception as e:
        m = p3l.exc_msg(me, e)
        logger.error(m)
        raise
#endregion init_budget_model(budget_config) -> None
# ---------------------------------------------------------------------------- +
#endregion Budget Model (MVVM sense of Model)
# ---------------------------------------------------------------------------- +
#region save_fi_transactions() function
def save_fi_transactions(workbook : Workbook = None, trans_file:str=None) -> None:
    """Save the FI transactions workbook to the filesystem.
    
    The file is assumed to be in the folder specified in the budget_config. 
    Use the folder specified in the budget_config.json file. 
    the budget_config may have an output_prefix specified which will be
    prepended to the trans_file name.

    TODO: If trans_file is not specified, then scan the folder for files. 
    Return a dictionary of workbooks with the file name as the key.

    Args:
        trans_file (str): The path of the transaction file to save.

    Returns:
        Workbook: The workbook containing the FI transactions.

    """
    try:
        # TODO: add logic to for workbook open in excel, work around.
        if (budget_config["output_prefix"] is not None and 
            isinstance(budget_config["output_prefix"], str) and
            len(budget_config["output_prefix"]) > 0):
            file_path = budget_config["output_prefix"] + trans_file
        else:
            file_path = trans_file
        trans_path = Path.Path(budget_config["bank_transactions_folder"]) / file_path
        logger.info("Saving FI transactions...")
        workbook.save(filename=trans_path)
        logger.info(f"Saved FI transactions to '{str(trans_path)}'")
        return
    except Exception as e:
        logger.error(p3l.exc_msg(load_fi_transactions, e))
        raise    
#endregion save_fi_transactions() function
# ---------------------------------------------------------------------------- +
#region load_fi_transactions() function
def load_fi_transactions(trans_file:str=None) -> Workbook:
    """Get the FI transactions from configured sources into a workbook.
    
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
    try:
        trans_path = Path.Path(budget_config["bank_transactions_folder"]) / trans_file

        logger.info("Loading FI transactions...")
        wb = load_workbook(filename=trans_path)
        logger.info(f"Loaded FI transactions from {str(trans_path)}")

        return wb
    except Exception as e:
        logger.error(p3l.exc_msg(load_fi_transactions, e))
        raise    
#endregion load_fi_transactions() function
# ---------------------------------------------------------------------------- +
#region fi_if_workbook_keys() function
def fi_if_workbook_keys(inst_key:str=None) -> dict:
    """Get the list of workbooks in the incoming folder for the specified institution.

    Args:
        inst_key (str): The key of the institution to get the workbooks for.

    Returns:
        dict: A dictionary of workbooks with the file name as the key.
    """
    try:
        if inst_key is None or inst_key not in budget_model["institutions"]:
            m = f"Invalid institution key: '{inst_key}'"
            logger.error(m)
            raise ValueError(m)
        institution = budget_model[BT_FINANCIAL_INSTITUTIONS][inst_key]
        workbooks = institution[IF_INCOMING_FOLDER_WORKBOOKS].keys()
        return workbooks
    except Exception as e:
        logger.exception(p3l.exc_msg(fi_if_workbook_keys, e))
        raise

#endregion fi_if_workbook_keys() function
# ---------------------------------------------------------------------------- +
#region fi_if_workbook_abs_paths() function
def fi_if_workbook_abs_path(inst_key:str, wb_key : str) -> Path.Path:
    """Get abs path of Incoming Folder workbook from an inst_key and wb_key.

    For a Finacial Institution (FI) designated by inst_key, get the absolute path
    of the workbook designated by wb_key. The workbook is assumed to be in the
    incoming folder (if) for the institution.

    Args:
        inst_key (str): The key of the institution to get the workbooks for.
        wb_key (str): The key of the workbook to get the absolute path for.

    Returns:
        Path: An abs path to the workbook with the wb_key as file name.
    """
    try:
        if inst_key is None or inst_key not in budget_model["institutions"]:
            m = f"Invalid institution key: '{inst_key}'"
            logger.error(m)
            raise ValueError(m)
        institution = budget_model[BT_FINANCIAL_INSTITUTIONS][inst_key]
        workbooks = institution[IF_INCOMING_FOLDER_WORKBOOKS].values()
        return workbooks
    except Exception as e:
        logger.exception(p3l.exc_msg(fi_if_workbook_abs_path, e))
        raise
#endregion fi_if_workbook_abs_paths() function
# ---------------------------------------------------------------------------- +
#region Local __main__ stand-alone
if __name__ == "__main__":
    try:
        # Configure logging
        log_config = p3l.STDOUT_FILE_LOG_CONFIG_FILE
        # Set the log filename for this application.
        filenames = {"file": "logs/p3ExcelBudget.log"}
        _ = p3l.setup_logging(logger_name = THIS_APP_NAME,
                                           config_file = log_config,
                                           filenames = filenames)
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger.info("+ ----------------------------------------------------- +")
        logger.info(f"+ Running transaction_files.py ...")
        logger.info("+ ----------------------------------------------------- +")
        # init budget model
        bm = init_budget_model()
        # load_fi_transactions()
    except Exception as e:
        logger.error(p3l.exc_msg("__main__",e))
    logger.info(f"Exiting {THIS_APP_NAME}...")
    exit(1)
#endregion
# ---------------------------------------------------------------------------- +
