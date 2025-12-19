#------------------------------------------------------------------------------+
# fooey.py - a place to fool around with experiments, not a dependent.
#------------------------------------------------------------------------------+
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict, Any, List
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
# local modules and packages
import p3_mvvm as p3m
from p3_mvvm.cp_message_service import cp_user_message_callback
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ------------------------------------------------------------------------ +
#region configure_logging() method
def configure_logging(logger_name : str = __name__, logtest : bool = False) -> None:
    """Setup the application logger."""
    try:
        # Configure logging
        log_config_file = "budget_model_logging_config.jsonc"
        _ = p3l.setup_logging(
            logger_name = logger_name,
            config_file = log_config_file
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
    except Exception as e:
        logger.error(p3u.exc_err_msg(e))
        raise
#endregion configure_logging() function
# ------------------------------------------------------------------------ +
@p3m.cp_user_message_callback
def cli_view_cp_user_output(message: p3m.CPUserOutputMessage) -> None:
    """Handle user output messages from the Command Processor."""
    print(f"CLI View User Message [{message.tag}]: {message.message}")

@p3m.cp_user_message_callback
def cli_view2_cp_user_output(message: p3m.CPUserOutputMessage) -> None:
    """Handle user output messages from the Command Processor."""
    print(f"CLI View2 User Message [{message.tag}]: {message.message}")

test_text = """
[bold blue]  DEBUG :[/bold blue] Catalog Map Update button clicked.
[bold blue]   INFO:[/bold blue] Starting Command Execution: {'cmd_name': 'workflow', 'cmd_key': 'workflow_cmd', 'cmd_exec_func': None, 'subcmd_name': 'update', 'subcmd_key': 'workflow_cmd_update', 'cmd_async_id': None, 'cmd_async_result_subscriber': None, 'fi_key': 'boa', 'update_category_map_workbook': True}
[bold blue]   INFO:[/bold blue] Executing command: WORKFLOW_cmd({'cmd_name': 'workflow', 'cmd_key': 'workflow_cmd', 'cmd_exec_func': <bound method BudManViewModel.WORKFLOW_cmd of <budman_view_model.budman_view_model.BudManViewModel object at 0x000002BEDA5BC590>>, 'subcmd_name': 'update', 'subcmd_key': 'workflow_cmd_update', 'cmd_async_id': None, 'cmd_async_result_subscriber': None, 'fi_key': 'boa', 'update_category_map_workbook': True, 'wf_key': 'categorize_transactions'})
[bold blue]       :[/bold blue] string_output
[bold blue]   INFO:[/bold blue] Complete Command: [0.248009 seconds] True
"""
def reformat(msg: str) -> str:
    new_output: List[str] = []
    """Reformat a message string for GUI output."""
    token : Dict[str, Any] = {
        "open": "[bold blue]",
        "close": "[/bold blue]",
        "count": 0
    }
    tokens: List[dict[str, Any]] = [
        {
            "open": "[bold blue]",
            "close": "[/bold blue]",
            "offset": 0,
            "count": 0
        },
        {
            "open": "[bold yellow]",
            "close": "[/bold yellow]",
            "offset": 0,
            "count": 0
        },
        {
            "open": "[bold red]",
            "close": "[/bold red]",
            "offset": 0,
            "count": 0
        },

    ]
    for line in test_text.splitlines():
        line = line.strip()
        for t in tokens:
            pos = line.find(t["open"])
        if line.startswith("[bold blue]") and ":[/bold blue]" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                tag_part = parts[0].strip()
                msg_part = ":".join(parts[1:]).strip()
                tag = tag_part.replace("[bold blue]", "").replace("[/bold blue]", "").strip()
                new_output.append(f"{token['open']}{tag:>7}:{token['close']} {msg_part}")
            else:
                new_output.append(line)
        else:
            new_output.append(line)
    return ""
    
if __name__ == "__main__":
    try:
        configure_logging(__name__, logtest=False)
        p3m.cp_msg_svc.subscribe_user_message(cli_view_cp_user_output)
        p3m.cp_msg_svc.subscribe_user_message(cli_view2_cp_user_output)
        p3m.cp_msg_svc.subscribe_user_message(p3m.cp_print_user_message)
        p3m.cp_msg_svc.user_message("BudManCLIView initialized.", tag='INFO')


    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
    # bdm = bdms.bsm_BDM_STORE_url_load(bdms_url)
    logger.info(f"Complete.")

exit(0)
