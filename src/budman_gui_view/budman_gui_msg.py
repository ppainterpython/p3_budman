# ---------------------------------------------------------------------------- +
#region budman_gui_msg.py module
""" budman_gui_msg.py implements the class BudManGuiMsg.
"""
#endregion budman_gui_msg.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging, queue
from typing import Optional
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
                    break  # Exit signal
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

    def update_msg_widget(self, msg : str, tag: str = BMG_INFO) -> None:
        """Append a message to the message widget."""
        if self._msg_widget:
            self._msg_widget.insert(tk.END, msg, tag)
            self._msg_widget.see(tk.END)  # Scroll to the end
        else:
            logger.warning("Message widget is not set. Cannot append message.")

    def output(self, msg : str, tag: str = BMG_INFO) -> None:
        """Output a message to the message queue."""
        if msg is not None and isinstance(msg, str) and len(msg) > 0:
            msg += "\n"
            msg_item = {"msg": msg, "tag": tag}
            self._budman_msg_queue.put(msg_item)