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
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
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
def cli_view_cmd_output(cmd: Dict, result: p3m.CMD_RESULT_TYPE ) -> None:
    """Display the command output based on the command result."""
    if p3m.is_CMD_RESULT(result):
        # A CMD_RESULT_OBJECT was returned.
        CMD_RESULT_output(result)
    else:
        # A simple string or other object was returned.
        console.print(result)
# ---------------------------------------------------------------------------- +
#region dispatch_CMD_RESULT() function
def CMD_RESULT_output(cmd_result: p3m.CMD_RESULT_TYPE) -> None:
    """Route the cmd_result to the appropriate output handler."""
    if (cmd_result is None or 
        not p3m.is_CMD_RESULT(cmd_result)):
        m = f"Invalid command result: {cmd_result}"
        logger.error(m)
        err_output(m)
        return
    if not cmd_result.get(p3m.CMD_RESULT_STATUS, False):
        # If the command result status is False, output the error message.
        err_msg = str(cmd_result.get(p3m.CMD_RESULT_CONTENT, "No error message provided."))
        err_output(err_msg)
        return
    result_type = cmd_result.get(p3m.CMD_RESULT_CONTENT_TYPE, None)
    if result_type == p3m.CMD_STRING_OUTPUT:
        # OUTPUT_STRING input is a simple string.
        result_content = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
        console.print(result_content)
    elif result_type == p3m.CMD_JSON_OUTPUT:
        # JSON_STRING input is a JSON string.
        result_content = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
        console.print_json(result_content)
    elif result_type == p3m.CMD_WORKBOOK_INFO_TABLE:
        # INFO_TABLE input is an array dictionaries.
        result_table = cmd_result.get(p3m.CMD_RESULT_CONTENT, [])
        hdr = list(result_table[0].keys()) if result_table else []
        table = Table(*hdr, show_header=True, header_style="bold green")
        for row in result_table:
            table.add_row(*[str(cell) for cell in row.values()])
        console.print(table)
    elif result_type == p3m.CMD_WORKBOOK_TREE_VIEW:
        # TREE_VIEW input is a string representation of a tree view.
        result_tree = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
        console.print(result_tree)
    else:
        logger.warning(f"Unknown command result type: {result_type}")
        result_content = str(cmd_result.get(p3m.CMD_RESULT_CONTENT, ""))
        console.print(result_content)
#endregion dispatch_CMD_RESULT() function
# ---------------------------------------------------------------------------- +
#region err_output() function
def err_output(msg: str) -> None:
    """Display error msg output."""
    console.print(f"[red]Error:[/red] {msg}", style="bold red")
#endregion err_output() function
# ---------------------------------------------------------------------------- +
