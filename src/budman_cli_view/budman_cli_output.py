# ---------------------------------------------------------------------------- +
#region    budman_cli_view.py module
""" BudMan CLI View output formatting and presentation.
"""
#endregion budman_cli_view.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time, toml
from typing import Dict, List, Any, Union

# third-party modules and packages
from rich.console import Console
from rich.table import Table
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
import budman_namespace.design_language_namespace as bdm
from budman_namespace.bdm_workbook_class import BDMWorkbook
import budman_command_processor as cp
from budman_workflows import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
console = Console(force_terminal=True, width=bdm.BUDMAN_WIDTH, highlight=True,
                  soft_wrap=False)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

#region cli_view_cmd_output(status: bool, result: Any) -> None
def cli_view_cmd_output(cmd: Dict, result: Any) -> None:
    if cp.is_CMD_RESULT(result):
        dispatch_CMD_RESULT(cmd, result)
    else:
        console.print(result)
# ---------------------------------------------------------------------------- +
#region dispatch_CMD_RESULT() function
def dispatch_CMD_RESULT(cmd: Dict, cmd_result: Dict[str, Any]) -> None:
    """Based on cmd parameter, route the cmd_result to the appropriate output handler."""
    if not cp.is_CMD_RESULT(cmd_result):
        logger.error(f"Invalid command result: {cmd_result}")
        return
    cmd_key = cmd.get(cp.CK_CMD_KEY, None)
    subcmd_key = cmd.get(cp.CK_SUBCMD_KEY, None)
    if cmd_key == cp.CV_WORKFLOW_CMD_KEY:
        if subcmd_key == cp.CV_LIST_SUBCMD_KEY:
            console.print(cmd_result[bdm.CMD_RESULT_CONTENT])
    elif cmd_key == cp.CV_SHOW_CMD_KEY:
        if subcmd_key == cp.CV_SHOW_WORKBOOKS_SUBCMD_KEY:
            show_cmd_output(cmd_result)
        # elif subcmd_key == cp.CV_SHOW_BDM_STORE_SUBCMD_KEY:
        #     show_cmd_output(cmd_result)
    else:
        console.print(f"No output handler for command result: {cmd_result}")
#endregion dispatch_CMD_RESULT() function
# ---------------------------------------------------------------------------- +
#region show_cmd_output() function
def show_cmd_output(cmd_result: Dict[str, Any]) -> None:
    """Display the command result output."""
    if cmd_result is None:
        return
    result_type = cmd_result.get(bdm.CMD_RESULT_TYPE, None)
    if result_type == bdm.CLIVIEW_OUTPUT_STRING:
        output_content = cmd_result.get(bdm.CMD_RESULT_CONTENT, "")
        console.print(output_content)
    elif result_type == bdm.CLIVIEW_WORKBOOK_INFO_TABLE:
        output_table = cmd_result.get(bdm.CMD_RESULT_CONTENT, [])
        hdr = list(output_table[0].keys()) if output_table else []
        table = Table(*hdr, show_header=True, header_style="bold green")
        for row in output_table:
            table.add_row(*[str(cell) for cell in row.values()])
        console.print(table)
    elif result_type == bdm.CLIVIEW_WORKBOOK_TREE_VIEW:
        tree_view = cmd_result.get(bdm.CMD_RESULT_CONTENT, "")
        console.print(tree_view)
    else:
        logger.warning(f"Unknown command result type: {result_type}")
#endregion show_cmd_output() function
# ---------------------------------------------------------------------------- +
#region show_cmd_output() function
def show_cmd_output(cmd_result: Dict[str, Any]) -> None:
    """Display the command result output."""
    if cmd_result is None:
        return
    result_type = cmd_result.get(bdm.CMD_RESULT_TYPE, None)
    if result_type == bdm.CLIVIEW_OUTPUT_STRING:
        output_content = cmd_result.get(bdm.CMD_RESULT_CONTENT, "")
        console.print(output_content)
    elif result_type == bdm.CLIVIEW_WORKBOOK_INFO_TABLE:
        output_table = cmd_result.get(bdm.CMD_RESULT_CONTENT, [])
        hdr = list(output_table[0].keys()) if output_table else []
        table = Table(*hdr, show_header=True, header_style="bold green")
        for row in output_table:
            table.add_row(*[str(cell) for cell in row.values()])
        console.print(table)
    elif result_type == bdm.CLIVIEW_WORKBOOK_TREE_VIEW:
        tree_view = cmd_result.get(bdm.CMD_RESULT_CONTENT, "")
        console.print(tree_view)
    else:
        logger.warning(f"Unknown command result type: {result_type}")
#endregion show_cmd_output() function