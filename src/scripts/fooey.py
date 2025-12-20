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
[bold blue]  DEBUG:[/bold blue] Here is a DEBUG message.
[bold blue]   INFO:[/bold blue] Starting Command Execution: {'cmd_name': 'workflow', 'cmd_key': 'workflow_cmd', 'cmd_exec_func': None, 'subcmd_name': 'update', 'subcmd_key': 'workflow_cmd_update', 'cmd_async_id': None, 'cmd_async_result_subscriber': None, 'fi_key': 'boa', 'update_category_map_workbook': True}
[bold red]  ERROR:[/bold red] Executing command: WORKFLOW_cmd({'cmd_name': 'workflow', 'cmd_key': 'workflow_cmd', 'cmd_exec_func': <bound method BudManViewModel.WORKFLOW_cmd of <budman_view_model.budman_view_model.BudManViewModel object at 0x000002BEDA5BC590>>, 'subcmd_name': 'update', 'subcmd_key': 'workflow_cmd_update', 'cmd_async_id': None, 'cmd_async_result_subscriber': None, 'fi_key': 'boa', 'update_category_map_workbook': True, 'wf_key': 'categorize_transactions'})
[bold yellow]WARNING:[/bold yellow] Warning message example.
[bold blue]   INFO:[/bold blue] Complete Command: [0.248009 seconds] True
[bold green]   INFO:[/bold green] Green Complete Command: [0.248009 seconds] True
"""
def reformat_console_markup(msg: str) -> Dict[str, Any]:
    new_output: List[str] = []
    """Reformat a message string for GUI output."""
    token : Dict[str, Any] = {
        "open": "",
        "close": "",
        "line_no": 0,
        "offset": 0,
        "text": ""
    }
    tokens: List[dict[str, Any]] = [
        {
            "open": "[bold blue]",
            "close": "[/bold blue]"
        },
        {
            "open": "[bold yellow]",
            "close": "[/bold yellow]"
        },
        {
            "open": "[bold green]",
            "close": "[/bold green]"
        },
        {
            "open": "[bold black]",
            "close": "[/bold black]"
        },
        {
            "open": "[bold red]",
            "close": "[/bold red]"
        },

    ]
    found_tokens: List[dict[str, Any]] = []

    for n, line in enumerate(msg.splitlines(), start=1):
        if len(line) == 0:
            new_output.append("\n")
            continue
        msg = ""
        for t in tokens:
            pos_o = line.find(t["open"])
            pos_c = line.find(t["close"])
            if pos_o != -1 and pos_c != -1 and pos_c > pos_o:
                new = {
                    "open": t["open"],
                    "close": t["close"],
                    "line_no": n,
                    "offset": len(msg),
                    "text": line[len(msg)+len(t["open"]):pos_c]
                }
                msg += new["text"] # text between open and close tokens
                line = line[pos_c + len(t["close"]):]  # rest of line after close token
                found_tokens.append(new)
        if len(line) > 0:
            new = {
                "open": "[normal]",
                "close": "[/normal]",
                "line_no": n,
                "offset": len(msg),
                "text": line
            }
            found_tokens.append(new)
            msg += line  # append any remaining text
        new_output.append(f"{msg}\n")
    return new_output
    
if __name__ == "__main__":
    try:
        newmsg = reformat_console_markup(test_text)
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
