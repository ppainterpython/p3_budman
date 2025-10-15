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
def cli_view_cmd_output(cmd: p3m.CMD_OBJECT_TYPE, cmd_result: p3m.CMD_RESULT_TYPE ) -> None:
    """Output in the View any output based on the command result."""
    if p3m.is_CMD_RESULT(cmd_result):
        # A CMD_RESULT_OBJECT was returned.
        CMD_RESULT_output(cmd_result)
    else:
        # Fall back, try to show something.
        console.print(str(cmd_result))
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
        result_content: Any = cmd_result.get(p3m.CMD_RESULT_CONTENT, "")
        # CMD_STRING_OUTPUT
        if result_type == p3m.CMD_STRING_OUTPUT:
            # OUTPUT_STRING input is a simple string.
            console.print(result_content)
        # CMD_DICT_OUTPUT
        elif result_type == p3m.CMD_DICT_OUTPUT:
            # Python dictionary (dict) input object.
            output_str: str = p3u.first_n(str(result_content), 100)
            console.print(output_str)
        # CMD_JSON_OUTPUT
        elif result_type == p3m.CMD_JSON_OUTPUT:
            # JSON_STRING input is a JSON string.
            console.print_json(result_content)
        # CMD_TREE_OBJECT
        elif result_type == p3m.CMD_TREE_OBJECT:
            # CMD_RESULT content is a treelib.Tree.
            formatted_tree = format_tree_view(result_content)
            console.print(formatted_tree)
        # CMD_FILE_TREE_OBJECT
        elif result_type == p3m.CMD_FILE_TREE_OBJECT:
            # CMD_RESULT content is a treelib.Tree with file information.
            formatted_tree = format_tree_view(result_content)
            console.print(formatted_tree)
        # CMD_WORKBOOK_TREE_OBJECT
        elif result_type == p3m.CMD_WORKBOOK_TREE_OBJECT:
            # CMD_WORKBOOK_TREE_OBJECT input is a treelib.Tree with workbook information.
            formatted_tree = format_tree_view(result_content)
            console.print(formatted_tree)
        # CMD_WORKBOOK_INFO_TABLE
        elif result_type == p3m.CMD_WORKBOOK_INFO_TABLE:
            # INFO_TABLE input is an array dictionaries.
            hdr = list(result_content[0].keys()) if result_content else []
            table = Table(*hdr, show_header=True, header_style="bold green")
            for row in result_content:
                table.add_row(*[str(cell) for cell in row.values()])
            console.print(table)
        elif result_type == p3m.CMD_WORKBOOK_TREE_OBJECT:
            # TREE_VIEW input is a string representation of a tree view.
            console.print(result_content)
        else:
            logger.warning(f"Unknown command result type: {result_type}")
            console.print(result_content)
    except Exception as e:
        err_output(f"Error processing command result: {e}") 
#endregion dispatch_CMD_RESULT() function
# ---------------------------------------------------------------------------- +
#region format_tree_view() function
def format_tree_view(tree_view:Tree=None) -> str:
    """Format a Tree object for console output."""
    try:
        p3u.is_not_obj_of_type("tree_view", tree_view, Tree, raise_error=True) 
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
