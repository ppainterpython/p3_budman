# ---------------------------------------------------------------------------- +
#region budman_gui_msg.py module
""" budman_gui_msg.py implements the class BudManGuiMsg.
"""
#endregion budman_gui_msg.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging, queue
from typing import Optional, List, Dict, Any
import tkinter as tk
from tkinter import scrolledtext
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from budman_namespace import BDMSingletonMeta
from .budman_gui_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(BMG_WINDOW_TITLE)  # create logger for the module
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUIMsg(metaclass=BDMSingletonMeta):
    #--------------------------------------------------------------------------+
    #region BudManGuiMsg class Intrinsics
    #--------------------------------------------------------------------------+
    #region BudManGuiMsg doc string
    """ BudManGuiMsg class.
        The BudManGuiMsg class implements a singleton message handler for the
        BudMan GUI application.
    """
    #endregion BudManGuiMsg doc string
    #--------------------------------------------------------------------------+
    #region    __init__() 
    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self._root: Optional[tk.Tk] = root
        self._msg_widget : Optional[scrolledtext.ScrolledText] = None
        self._budman_msg_queue = queue.Queue()
        self._after_id : Optional[str] = None
    #endregion  __init__()
    #--------------------------------------------------------------------------+
    #region    BudManGUIMsg class properties
    @property
    def root(self) -> tk.Tk:
        """Get the root window."""
        return self._root
    @root.setter
    def root(self, root : tk.Tk) -> None:
        """Set the root window."""
        self._root = root
    @property
    def msg_widget(self) -> Optional[scrolledtext.ScrolledText]:
        """Get the message widget."""
        return self._msg_widget
    @msg_widget.setter
    def msg_widget(self, widget : scrolledtext.ScrolledText) -> None:
        """Set the message widget."""
        self._msg_widget = widget
    #endregion BudManGUIMsg class properties
    #--------------------------------------------------------------------------+
    #region    BudManGuiMsg class methods
    def msg_handler(self) -> None:
        """Dispatch messages from the message queue to the message widget."""
        if self.root is None:
            logger.warning("Root window is not set. Cannot handle messages.")
            return
        try:
            while True:
                msg_item = self._budman_msg_queue.get_nowait()
                if msg_item is None:
                    break  # Exit signal, requires explicit .put(None) to stop
                self.update_msg_widget(msg_item["msg"], msg_item["tag"])
        except queue.Empty:
            pass  # No message, continue waiting
        # poll for msgs every 100 ms
        self.root.after(100, self.msg_handler)
    
    def msg_handler_cancel(self):
        """Cancel the message handler."""
        if self._after_id is not None and self.root is not None:    
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def output(self, msg : str, tag: str = BMG_INFO) -> None:
        """Output a message to the message queue."""
        if msg is not None and isinstance(msg, str) and len(msg) > 0:
            msg += "\n"
            msg_item = {"msg": msg, "tag": tag}
            self._budman_msg_queue.put(msg_item)

    def update_msg_widget(self, msg : str, tag: str = BMG_INFO) -> None:
        """Append a message to the message widget."""
        if (self._msg_widget and 
            isinstance(self._msg_widget, scrolledtext.ScrolledText)):
            prefixed = prefix_msg_with_tag(msg, tag)
            self.process_msg_output(prefixed, tag)
        else:
            logger.warning("Message widget is not set. Cannot append message.")

    def process_msg_output(self, msg: str, tag: str) -> None:
        """Process a message string for GUI output."""  
        msg_tokens: List[Dict[str, Any]] = reformat_console_markup(msg)
        if len(msg_tokens) == 0:
            return
        for t in msg_tokens:
            lastline: int = int(self._msg_widget.index(tk.END).split(".")[0])
            # Process each token as needed for GUI output
            ln : int = lastline + int(t["line_no"] ) - 1
            i_start = f"{ln}.{t['offset']}"
            i_end = f"{ln}.{t['offset'] + len(t['text'])}"
            # indx: str = f"{ln}.end"
            self._msg_widget.insert(i_start, t["text"],(t["tag"],))
            # self._msg_widget.tag_add(t["tag"], i_start, i_end)
            self._msg_widget.see(tk.END)  # Scroll to the end
        return
#endregion    BudManGuiMsg class methods
#--------------------------------------------------------------------------+

budman_msg = BudManGUIMsg()  # Singleton instance of BudManGuiMsg

def reformat_console_markup(msg_in: str) -> List[Dict[str, Any]]:
    new_output: List[str] = []
    """Reformat a message string for GUI output."""
    token : Dict[str, Any] = {
        "open": "",
        "close": "",
        "line_no": 0,
        "offset": 0,
        "text": "",
        "tag": ""
    }
    tokens: List[dict[str, Any]] = [
        {
            "tag": BMG_INFO,
            "open": "[bold green]",
            "close": "[/bold green]"
        },
        {
            "tag": BMG_DEBUG,
            "open": "[bold blue]",
            "close": "[/bold blue]"
        },
        {
            "tag": BMG_WARNING,
            "open": "[bold orange]",
            "close": "[/bold orange]"
        },
        {
            "tag": BMG_VERBOSE,
            "open": "[bold light blue]",
            "close": "[/bold light blue]"
        },
        {
            "tag": BMG_NORMAL,
            "open": "[bold black]",
            "close": "[/bold black]"
        },
        {
            "tag": BMG_ERROR,
            "open": "[bold red]",
            "close": "[/bold red]"
        },
        {
            "tag": BMG_CRITICAL,
            "open": "[bold dark red]",
            "close": "[/bold dark red]"
        }
    ]
    found_tokens: List[dict[str, Any]] = []

    for n, line in enumerate(msg_in.splitlines(), start=1):
        if len(line) == 0:
            new_output.append("\n")
            new = {
                "open": "[normal]",
                "close": "[/normal]",
                "line_no": n,
                "offset": 0,
                "text": "\n",
                "tag": BMG_NORMAL
            }
            found_tokens.append(new)
            continue
        msg_no_markup = ""
        for t in tokens:
            pos_o = line.find(t["open"])
            pos_c = line.find(t["close"])
            if pos_o != -1 and pos_c != -1 and pos_c > pos_o:
                new = {
                    "open": t["open"],
                    "close": t["close"],
                    "line_no": n,
                    "offset": pos_o, # starting colume of text in token w/o markup
                    "text": line[pos_o + len(t["open"]):pos_c],
                    "tag": t["tag"]
                }
                found_tokens.append(new)  # New formatted text token
                msg_no_markup += new["text"]
                line = line[pos_c + len(t["close"]):]  # text after close markup
        line += '\n'
        new = {
            "open": "[normal]",
            "close": "[/normal]",
            "line_no": n,
            "offset": len(msg_no_markup),
            "text": line,
            "tag": BMG_NORMAL
        }
        found_tokens.append(new)
        msg_no_markup += line  # append any remaining text
        new_output.append(f"{msg_no_markup}\n")
    return found_tokens

def prefix_msg_with_tag(msg: str, tag: str) -> str:
    """Prefix a message string with a tag for GUI output."""
    if tag == BMG_INFO:
        return f"[bold green]{tag:>7}:[/bold green] {msg}"
    elif tag == BMG_WARNING:
        return f"[bold orange]{tag:>7}:[/bold orange] {msg}"
    elif tag == BMG_ERROR:
        return f"[bold red]{tag:>7}:[/bold red] {msg}"
    elif tag == BMG_CRITICAL:
        return f"[bold dark red]{tag:>7}:[/bold dark red] {msg}"
    elif tag == BMG_DEBUG:
        return f"[bold blue]{tag:>7}:[/bold blue] {msg}"
    elif tag == BMG_VERBOSE:
        return f"[bold light blue]{tag:>7}:[/bold light blue] {msg}"
    else: # default
        return f"[bold gray50]{tag:>7}:[/bold gray50] {msg}"
