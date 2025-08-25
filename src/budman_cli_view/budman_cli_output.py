# ---------------------------------------------------------------------------- +
#region    budman_cli_view.py module
""" BudMan CLI View output formatting and presentation.
"""
#endregion budman_cli_view.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, sys, io, os, time, toml
from typing import Dict, List, Any, Union

# third-party modules and packages
from treelib import Tree
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
def cli_view_cmd_output(cmd: p3m.CMD_OBJECT_TYPE, result: p3m.CMD_RESULT_TYPE ) -> None:
    """Output in the View any output based on the command result."""
    if p3m.is_CMD_RESULT(result):
        # A CMD_RESULT_OBJECT was returned.
        CMD_RESULT_output(result)
    else:
        # Fall back, try to show something.
        console.print(str(result))
# ---------------------------------------------------------------------------- +
#region dispatch_CMD_RESULT() function
def CMD_RESULT_output(cmd_result: p3m.CMD_RESULT_TYPE) -> None:
    """Route the cmd_result to the appropriate output handler."""
    try:
        if (cmd_result is None or 
            not p3m.is_CMD_RESULT(cmd_result)):
            err_output(f"Invalid command result: {str(cmd_result)}")
            return
        if not cmd_result.get(p3m.CMD_RESULT_STATUS, False):
            # If the command result status is False, output the error message.
            err_output(cmd_result)
            return
        result_type = cmd_result.get(p3m.CMD_RESULT_CONTENT_TYPE, None)
        # CMD_STRING_OUTPUT
        if result_type == p3m.CMD_STRING_OUTPUT:
            # OUTPUT_STRING input is a simple string.
            result_content = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
            console.print(result_content)
        # CMD_JSON_OUTPUT
        elif result_type == p3m.CMD_JSON_OUTPUT:
            # JSON_STRING input is a JSON string.
            result_content = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
            console.print_json(result_content)
        # CMD_TREE_OBJECT
        elif result_type == p3m.CMD_TREE_OBJECT:
            # CMD_RESULT content is a treelib.Tree.
            result_tree = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
            formatted_tree = format_tree_view(result_tree)
            console.print(formatted_tree)
        # CMD_FILE_TREE_OBJECT
        elif result_type == p3m.CMD_FILE_TREE_OBJECT:
            # CMD_RESULT content is a treelib.Tree with file information.
            result_tree = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
            formatted_tree = format_tree_view(result_tree)
            console.print(formatted_tree)
        # CMD_WORKBOOK_TREE_OBJECT
        elif result_type == p3m.CMD_WORKBOOK_TREE_OBJECT:
            # CMD_WORKBOOK_TREE_OBJECT input is a treelib.Tree with workbook information.
            result_tree = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
            console.print(result_tree)
        # CMD_WORKBOOK_INFO_TABLE
        elif result_type == p3m.CMD_WORKBOOK_INFO_TABLE:
            # INFO_TABLE input is an array dictionaries.
            result_table = cmd_result.get(p3m.CMD_RESULT_CONTENT, [])
            hdr = list(result_table[0].keys()) if result_table else []
            table = Table(*hdr, show_header=True, header_style="bold green")
            for row in result_table:
                table.add_row(*[str(cell) for cell in row.values()])
            console.print(table)
        elif result_type == p3m.CMD_WORKBOOK_TREE_OBJECT:
            # TREE_VIEW input is a string representation of a tree view.
            result_tree = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
            console.print(result_tree)
        else:
            logger.warning(f"Unknown command result type: {result_type}")
            result_content = str(cmd_result.get(p3m.CMD_RESULT_CONTENT, ""))
            console.print(result_content)
    except Exception as e:
        err_output(f"Error processing command result: {e}") 
#endregion dispatch_CMD_RESULT() function
# ---------------------------------------------------------------------------- +
#region format_tree_view() function
def format_tree_view(tree_view:Tree=None) -> str:
    """Format a Tree object for console output."""
    try:
        # Format the tree for console output
        original_stdout = sys.stdout  # Save the original stdout
        buffer = io.StringIO()
        sys.stdout = buffer  # Redirect stdout to capture tree output
        tree_view.show()
        sys.stdout = original_stdout  # Reset stdout
        return buffer.getvalue()
    except Exception as e:
        m = p3u.exc_err_msg(e)
        logger.error(m)
        return m
#endregion format_tree_view() function
# ---------------------------------------------------------------------------- +
#region err_output() function
def err_output(cmd_result: Union[p3m.CMD_RESULT_TYPE,str]) -> None:
    """Display error msg output."""
    if isinstance(cmd_result, str):
        err_msg = cmd_result
    elif p3m.is_CMD_RESULT(cmd_result):
        err_msg = str(cmd_result.get(p3m.CMD_RESULT_CONTENT, "No error message provided."))
    else:
        err_msg = f"Invalid err_output input type: {type(cmd_result).__name__}"
    logger.error(err_msg)
    console.print(f"Error: {err_msg}", style="bold red")
#endregion err_output() function
# ---------------------------------------------------------------------------- +
