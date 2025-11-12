print("Starting BudMan GUI Application...")
import time, logging
from pathlib import Path
st = time.time()
from p3_utils.p3_app_timing import APP_START_TIME
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
import p3logging as p3l
from budman_settings.budman_settings_constants import *
from budman_settings.budman_settings import BudManSettings
from budman_gui_view  import BudManGUIView
from budget_storage_model import BSMFileTree
# ---------------------------------------------------------------------------- +
#region configure_logging() method
def configure_logging(logger_name : str, log_config_url: str, logtest : bool = True) -> None:
    """Setup the application logger."""
    try:
        # Convert log_config_url to a file path.
        log_config_file = Path.from_uri(log_config_url).expanduser().resolve()
        # Configure logging
        _ = p3l.setup_logging(
            logger_name = logger_name,
            config_file = str(log_config_file)
            )
        p3l.set_log_flag(p3l.LOG_FLAG_PRINT_CONFIG_ERRORS, True)
        logger = logging.getLogger(logger_name)
        logger.propagate = True
        logger.setLevel(logging.DEBUG)
        prog = Path(__file__).name
        logger.info(f"+ {60 * '-'} +")
        logger.info(f"+ running {prog}({logger_name}) ...")
        logger.info(f"+ {60 * '-'} +")
        if(logtest): 
            p3l.quick_logging_test(logger_name, log_config_file, reload = False)

        root_logger = logging.getLogger()  # or logging.getLogger("root")
        print("Logging configuration:")
        for handler in root_logger.handlers:
            print(f"  Handler: '{handler.name}' {handler}, Level: {handler.level}, Type: {type(handler)}")
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion configure_logging() function
# ---------------------------------------------------------------------------- +
logger = logging.getLogger(__name__)
it = time.time() -st
print(f"  Imports completed in {it:.3f} seconds.")
BudManMain_settings : BudManSettings = BudManSettings()
if BudManMain_settings is None:
        raise ValueError("BudMan Settings not configured.")
app_name = BudManMain_settings.get(APP_NAME, "BudManApp")
logging_config_url = BudManMain_settings.logging.config_url
configure_logging(app_name, logging_config_url, logtest=False)
logger.debug(f"Settings and logger configured: {p3u.elapsed_timer_str(APP_START_TIME)}")

VALID_WB_TYPES = [".bdm_store", ".bdm_config", ".txn_register", ".excel_txns",
                  ".txn_categories", ".category_map", ".budget"]
VALID_PREFIXES = ["txn_input_", "categorized_", "budget_"]
BDM_FOLDER_URL = "file:///C:/Users/ppain/OneDrive/budget"

if __name__ == "__main__":
    try:
        print(f"  Time since app start: {p3u.elapsed_timer_str(APP_START_TIME)}")
        gui_app: BudManGUIView = BudManGUIView()
        print(f"  GUI setup time: {p3u.elapsed_timer_str(APP_START_TIME)}")
        gui_app.initialize()
        print(f"  GUI initialized in: {p3u.elapsed_timer_str(APP_START_TIME)}")
        bsm_file_tree: BSMFileTree = BSMFileTree(folder_url=BDM_FOLDER_URL,
                                                valid_wb_types=VALID_WB_TYPES,
                                                valid_prefixes=VALID_PREFIXES)
        gui_app.file_tree = bsm_file_tree.file_tree
        gui_app.root.budman_gui_frame.file_tree = gui_app.file_tree
        gui_app.root.budman_gui_frame.refresh_file_treeview()
        print(f"  BSMFileTree initialized in: {p3u.elapsed_timer_str(APP_START_TIME)}")
        # gui_app.root.load_sample_data()
        print(f"Running BudMan GUI Application...")
        cmd_result: p3m.CMD_RESULT_TYPE = None
        cmd_result = gui_app.run()
        print(f"Application finished with result: {cmd_result}")
    except Exception as e:
        print(p3u.exc_err_msg(e))
