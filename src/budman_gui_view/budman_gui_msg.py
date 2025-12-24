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
        self._msg_tag_tokens: Dict[str, Dict[str, str]] = self.init_msg_tag_tokens() 
        self._msg_widget : Optional[scrolledtext.ScrolledText] = None
        self._budman_msg_queue = queue.Queue()
        self._after_id : Optional[str] = None
    #endregion  __init__()
    #--------------------------------------------------------------------------+
    #region init_msg_tag_tokens() method
    def init_msg_tag_tokens(self) -> Dict[str, Dict[str, str]]:
        """Initialize the message tag tokens dictionary.
        
        In this gui message service, the output of messages is formatted with
        markup tags for color and style, based on the Rich Console markup syntax.
        But the text in the gui domain will be displaed in tkinter using tags
        associated with style setting. This dictionary maps come of the console
        markup tokens to tags used to format text in a ScrolledText widget.
        """
        msg_tag_tokens: Dict[str, Dict[str, str]] = {
            BMG_NORMAL: {
                "prefix_tag": BMG_NORMAL,
                "open": "[bold black]",
                "close": "[/bold black]"
            },
            BMG_INFO: {
                "prefix_tag": BMG_INFO_PREFIX,  
                "open": "[dark green]",
                "close": "[/dark green]"
            },
            BMG_INFO_PREFIX: {
                "prefix_tag": None,
                "open": "[bold green]",
                "close": "[/bold green]"
            },
            BMG_DEBUG: {
                "prefix_tag": BMG_DEBUG_PREFIX,
                "open": "[cadet blue]",
                "close": "[/cadet blue]"
            },
            BMG_DEBUG_PREFIX: {
                "prefix_tag": None,
                "open": "[bold blue]",
                "close": "[/bold blue]"
            },
            BMG_VERBOSE: {
                "prefix_tag": BMG_VERBOSE_PREFIX,
                "open": "[light blue]",
                "close": "[/light blue]"
            },
            BMG_VERBOSE_PREFIX: {
                "prefix_tag": None,
                "open": "[bold dodger blue]",
                "close": "[/bold dodger blue]"
            },
            BMG_WARNING: {
                "prefix_tag": BMG_WARNING_PREFIX,
                "open": "[bold orange]",
                "close": "[/bold orange]"
            },
            BMG_WARNING_PREFIX: {
                "prefix_tag": None,
                "open": "[bold dark orange]",
                "close": "[/bold dark orange]"
            },
            BMG_ERROR: {
                "prefix_tag": BMG_ERROR_PREFIX,
                "open": "[red]",
                "close": "[/red]"
            },
            BMG_ERROR_PREFIX: {
                "prefix_tag": None,
                "open": "[bold red3]",
                "close": "[/bold red3]"
            },
            BMG_CRITICAL: {
                "prefix_tag": BMG_CRITICAL_PREFIX,
                "open": "[red2]",
                "close": "[/red2]"
            },
            BMG_CRITICAL_PREFIX: {
                "prefix_tag": None,
                "open": "[bold dark red]",
                "close": "[/bold dark red]"
            }
        }
        return msg_tag_tokens
    #endregion init_msg_tag_tokens() method
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
                self.update_msg_widget(msg_item["msg"], 
                                       msg_item["tag"],
                                       msg_item["prefix"] if "prefix" in msg_item else True)
        except queue.Empty:
            pass  # No message, continue waiting
        # poll for msgs every 100 ms
        self.root.after(100, self.msg_handler)
    
    def msg_handler_cancel(self):
        """Cancel the message handler."""
        if self._after_id is not None and self.root is not None:    
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def output(self, msg : str, tag: str = BMG_INFO, prefix:bool = True) -> None:
        """Output a message to the message queue."""
        if msg is not None and isinstance(msg, str) and len(msg) > 0:
            msg += "\n"
            msg_item = {"msg": msg, "tag": tag, "prefix": prefix}
            self._budman_msg_queue.put(msg_item)

    def update_msg_widget(self, msg : str, tag: str = BMG_INFO, prefix: bool = True) -> None:
        """Append a message to the message widget."""
        if (self._msg_widget and 
            isinstance(self._msg_widget, scrolledtext.ScrolledText)):
            prefixed = self.prefix_msg_with_tag(msg, tag, prefix)
            self.process_msg_output(prefixed, tag)
        else:
            logger.warning("Message widget is not set. Cannot append message.")

    def process_msg_output(self, msg: str, tag: str) -> None:
        """Process a message string for GUI output."""  
        msg_tokens: List[Dict[str, Any]] = self.reformat_console_markup(msg)
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

    def reformat_console_markup(self, msg_in: str) -> List[Dict[str, Any]]:
        new_output: List[str] = []
        """Reformat a message string for GUI output."""
        found_tokens: List[dict[str, Any]] = []
        msg_no_markup = ""
        new: Optional[Dict[str, Any]] = None

        for n, line in enumerate(msg_in.splitlines(), start=1):
            # Process each line to process tokens left to right.
            # if text is found not contained in a token, then wrap it in
            # a Normal token.

            # Empty line, wrap as Normal token, move to next line
            if len(line) == 0:
                new_output.append("\n")
                new = {
                    "open": "[normal]",
                    "close": "[/normal]",
                    "line_no": n,
                    "open_start": -1,
                    "close_end": -1,
                    "offset": len(msg_no_markup),
                    "text": "\n",
                    "tag": BMG_NORMAL,
                    "prefix_tag": None
                }
                msg_no_markup += new["text"]
                found_tokens.append(new)
                continue
            # Search line for any tokens
            last_token_end: int = -1
            while True:
                next_token: Dict[str, Any] = self.get_next_token(line, n)
                if next_token is None:
                    # no token found, wrap line in a normal token, go to next line
                    new = {
                        "open": "[normal]",
                        "close": "[/normal]",
                        "line_no": n,
                        "open_start": 0,
                        "close_end": -1,
                        "offset": len(msg_no_markup),
                        "text": line,
                        "tag": BMG_NORMAL,
                        "prefix_tag": None
                    }
                    msg_no_markup += new["text"]
                    found_tokens.append(new)
                    break
                # Found a token
                # If any text preceeds it, wrap in normal token
                pre_text_token: Optional[Dict[str, Any]] = None
                if next_token["open_start"] > 0:
                    pre_text: str = line[0:next_token["open_start"]]
                    pre_text_token = {
                        "open": "[normal]",
                        "close": "[/normal]",
                        "line_no": n,
                        "open_start": -1,
                        "close_end": -1,
                        "offset": len(msg_no_markup),
                        "text": pre_text,
                        "tag": BMG_NORMAL,
                        "prefix_tag": None
                    }
                    msg_no_markup += pre_text_token["text"]
                    found_tokens.append(pre_text_token)
                next_token["offset"] = len(msg_no_markup)
                msg_no_markup += next_token["text"]
                found_tokens.append(next_token)
                # Remove token from Line
                token_start: int = next_token["open_start"]
                token_end: int = next_token["close_end"] + 1
                line = line[:token_start] + line[token_end:]
                # If there was test before this token, remove it from line
                if pre_text_token is not None:
                    line = line[len(pre_text_token["text"])+1:]
            # After tokens, wrap any remaining text
            if len(line) > 0:
                new = {
                    "open": "[normal]",
                    "close": "[/normal]",
                    "line_no": n,
                    "open_start": -1,
                    "close_end": -1,
                    "offset": len(msg_no_markup),
                    "text": line,
                    "tag": BMG_NORMAL,
                    "prefix_tag": None
                }
                found_tokens.append(new)
                msg_no_markup += new["text"]
        found_tokens[-1]["text"] += "\n"  # ensure final newline
        return found_tokens
    
    def get_next_token(self, line:str, line_no: int) -> Optional[Dict[str, Any]]:
        """Get the next markup token from a line of text."""
        if line is None or len(line) == 0:
            return None
        open_start: int = line.find('[')
        if open_start == -1:
            return None
        open_end: int = line.find(']', open_start)
        if open_end == -1:
            return None
        token_str: str = line[open_start:open_end + 1]
        full_token: Optional[Dict[str, Any]] = None
        for k,v in self._msg_tag_tokens.items():
            if token_str == v["open"] :
                full_token = {
                    "open": v["open"],
                    "close": v["close"],
                    "line_no": line_no,
                    "open_start": open_start,
                    "close_end": -1,
                    "text": "",
                    "tag": k,
                    "prefix_tag": v["prefix_tag"]
                }
                break
        if full_token is None:
            return None # no matching token found
        close_start: int = line.find('[', open_end)
        if close_start == -1:
            return None
        close_end: int = line.find(']', close_start)
        if close_end == -1:
            return None
        token_str: str = line[close_start:close_end + 1]
        if token_str != full_token["close"]:
            return None
        full_token["close_end"] = close_end
        text_start: int = open_start + len(full_token["open"])
        text_end: int = close_end - len(full_token["close"]) + 1
        full_token["text"] = line[text_start:text_end]
        return full_token   

    def token_count(self, line:str) -> int:
        """Count the number of markup tokens in a line of text."""
        count: int = 0
        last_token_end: int = 0
        while last_token_end < len(line):
            next_token: Optional[Dict[str, Any]] = self.get_next_token(line[last_token_end:], 0)
            if next_token is None:
                break
            count += 1
            last_token_end = next_token["close_end"] + 1
        return count

    def prefix_msg_with_tag(self, msg: str, tag: str, prefix: bool = True) -> str:
        """Prefix a message string based on the tag applied to the msg."""
        mod_msg: str = ""
        for n, line in enumerate(msg.splitlines(), start=1):
            nl :str = '\n'
            if len(line) == 0:
                mod_msg += nl
                continue
            if not prefix:
                mod_msg += line + nl
                continue
            if tag == BMG_INFO:
                mod_msg += (f"[bold green]{tag:>7}:[/bold green] "
                        f"[dark green]{line.rstrip(nl)}[/dark green]{nl}")
            elif tag == BMG_WARNING:
                mod_msg += (f"[bold dark orange]{tag:>7}:[/bold dark orange] "
                        f"[bold orange]{line.rstrip(nl)}[/bold orange]{nl}")
            elif tag == BMG_ERROR:
                mod_msg += (f"[bold red3]{tag:>7}:[/bold red3] "
                        f"[red]{line.rstrip(nl)}[/red]{nl}")
            elif tag == BMG_CRITICAL:
                mod_msg += (f"[bold dark red]{tag:>7}:[/bold dark red] "
                        f"[red2]{line.rstrip(nl)}[/red2]{nl}    ")
            elif tag == BMG_DEBUG:
                mod_msg += (f"[bold blue]{tag:>7}:[/bold blue] "
                        f"[cadet blue]{line.rstrip(nl)}[/cadet blue]{nl}")
            elif tag == BMG_VERBOSE:
                mod_msg += (f"[bold dodger blue]{tag:>7}:[/bold dodger blue] "
                        f"[light blue]{line.rstrip(nl)}[/light blue]{nl}")
            else: # default
                mod_msg += f"[bold gray50]{tag:>7}:[/bold gray50] {line.rstrip(nl)}{nl}"
        return mod_msg

#endregion    BudManGuiMsg class methods
#--------------------------------------------------------------------------+

budman_msg = BudManGUIMsg()  # Singleton instance of BudManGuiMsg

