#-----------------------------------------------------------------------------+
import logging
import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb  # tb.Window used for root window only
from .budman_gui_frame import BudManGUIFrame
from .constants import *

logger = logging.getLogger(__name__)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")

class BudManGUIWindow(tb.Window):
    """ Budget Manager View class.
        The BudManView class is a subclass of the tkinter.Tk class and implements 
        the entire GUI user interface for the Budget Manager application.

        Properties
        ----------
        datacontext : object
            The data context for the view, typically a ViewModel object. 
            For ATView class, the datacontext should be a ATViewModel object.
    """
    #region ATView class
    #--------------------------------------------------------------------------+
    # Public Property attributes
    datacontext: object = None    # ATViewModel object used as datacontext
    tkview_frame: tk.Frame = None

    # Private attributes
    __width: int = BMV_MIN_WINDOW_WIDTH
    __height: int = BMV_MIN_WINDOW_HEIGHT
    __geometry: str = f"{__width}x{__height}"
    # Class constructor
    def __init__(self, title=BMV_WINDOW_TITLE, themename='cosmo'):
        # init root window
        super().__init__(title,themename)
        self.configure(bg=BMV_FAINT_GRAY)
        self.geometry(self.__geometry)
        self.minsize(BMV_MIN_WINDOW_WIDTH, BMV_MIN_WINDOW_HEIGHT)
        self.maxsize(BMV_MAX_WINDOW_WIDTH, BMV_MAX_WINDOW_HEIGHT)
        # init properties
        self.bmview_frame = BudManGUIFrame(self) # create the view frame
        logger.debug("BudManView initialized")

    #--------------------------------------------------------------------------+
    # Property attributes

    #--------------------------------------------------------------------------+
    # Event Handler Methods

    def on_datacontext_changed(self, viewmodel):
        raise NotImplementedError("on_datacontext_change must be implemented in the subclass")
    

#------------------------------------------------------------------------------+