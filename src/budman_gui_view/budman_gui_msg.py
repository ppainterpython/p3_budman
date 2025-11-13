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
class BudManGuiMsg(metaclass=BDMSingletonMeta):
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
                msg = self._budman_msg_queue.get_nowait()
                if msg is None:
                    break  # Exit signal
                self.update_msg_widget(msg)
        except queue.Empty:
            pass  # No message, continue waiting
        self.root.after(100, self.msg_handler)

    def update_msg_widget(self, msg : str) -> None:
        """Append a message to the message widget."""
        if self._msg_widget:
            self._msg_widget.insert(tk.END, msg)
            self._msg_widget.see(tk.END)  # Scroll to the end
        else:
            logger.warning("Message widget is not set. Cannot append message.")

    def output(self, msg : str) -> None:
        """Output a message to the message queue."""
        self._budman_msg_queue.put(msg+'\n')