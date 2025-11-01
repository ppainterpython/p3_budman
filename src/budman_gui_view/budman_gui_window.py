#-----------------------------------------------------------------------------+
import logging
import tkinter as tk
import tkinter.ttk as ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb  # tb.Window used for root window only
from .budman_gui_frame import BudManGUIFrame
from .constants import *

logger = logging.getLogger(__name__)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")

class BudManGUIWindow(tb.Window):
    """ Budget Manager GUI Window class.
        The BudManGUIWindow class is a subclass of the tb.Window class and 
        implements the entire GUI user interface for the Budget Manager 
        application.

        Window Layout
        -------------
        BudManGUIWindow(tb.Window)
            2 rows, 1 column
            Row 0: BudManGUIFrame (main content area)
            Row 1: Status Bar (persistent at bottom)

        Properties
        ----------
        title : str
            The title of the window.
        themename : str
            The ttkbootstrap theme name for the window.
            Default is 'cosmo'.
        datacontext : object
            The data context object for the view. 
    """
    #region ATView class
    #--------------------------------------------------------------------------+
    # Public Property attributes
    budman_gui_frame: tk.Frame = None
    status_bar: tk.Frame = None

    # Private attributes
    __width: int = BMV_MIN_WINDOW_WIDTH
    __height: int = BMV_MIN_WINDOW_HEIGHT
    __geometry: str = f"{__width}x{__height}"
    
    # Class constructor
    def __init__(self, title=BMV_WINDOW_TITLE, themename='cosmo', 
                 datacontext:object = None ):
        # init root window
        super().__init__(title, themename)
        self.title: str = title
        self.themename: str = themename
        
        # BudMan Application Attributes
        self.datacontext: object = datacontext    # datacontext object

        # Configure main window grid
        self._destroyed: bool = False
        style: tk.ttk.Style = self.configure_styles()
        self.configure(bg=BMV_FAINT_GRAY)
        self.geometry(self.__geometry)
        self.minsize(BMV_MIN_WINDOW_WIDTH, BMV_MIN_WINDOW_HEIGHT)
        self.maxsize(BMV_MAX_WINDOW_WIDTH, BMV_MAX_WINDOW_HEIGHT)
        
        # Configure main window grid weights
        self.grid_rowconfigure(0, weight=1)    # Main content area expands
        self.grid_rowconfigure(1, weight=0)    # Status bar fixed height
        self.grid_columnconfigure(0, weight=1) # Full width

        # Create the BudManGUIFrame for the main view (row 0)
        self.budman_gui_frame = BudManGUIFrame(self, self, self.datacontext) 
        self.budman_gui_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Create the status bar for the bottom of the window (row 1)
        self._create_status_bar()

        # Set up proper window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # All done
        logger.debug("BudManView initialized")

    def _create_status_bar(self):
        """Creates a persistent status bar at the bottom of the window."""
        # Create status bar frame
        self.status_bar = tk.Frame(
            self, 
            relief="sunken", 
            bd=1, 
            bg="lightgray", 
            height=30
        )
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 2))
        self.status_bar.grid_propagate(False)  # Maintain fixed height
        
        # Configure status bar internal grid
        self.status_bar.grid_columnconfigure(1, weight=1)  # Middle section expands
        
        # Left section - Status message
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready", 
            anchor="w", 
            relief="flat"
        )
        self.status_label.configure(style="AT.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w", padx=(5, 10))

        # Middle section - Progress bar
        self.progress = ttk.Progressbar(
            self.status_bar, 
            length=150, 
            mode="determinate"
        )
        self.progress.grid(row=0, column=1, sticky="w", padx=10)
        self.progress["value"] = 0

        # Right section - User info
        self.user_label = ttk.Label(
            self.status_bar, 
            text="User: Paul", 
            anchor="e", 
            relief="flat"
        )
        self.user_label.configure(style="AT.TLabel")
        self.user_label.grid(row=0, column=2, sticky="e", padx=(10, 5))

    #--------------------------------------------------------------------------+
    # Status bar utility methods
    
    def update_status(self, message: str):
        """Update the status message"""
        if not self._destroyed and self.status_label.winfo_exists():
            self.status_label.config(text=message)
    
    def update_progress(self, value: int):
        """Update the progress bar (0-100)"""
        if not self._destroyed and self.progress.winfo_exists():
            self.progress["value"] = max(0, min(100, value))
    
    def update_user(self, user: str):
        """Update the user label"""
        if not self._destroyed and self.user_label.winfo_exists():
            self.user_label.config(text=f"User: {user}")

    #--------------------------------------------------------------------------+
    # Event Handler Methods

    def on_datacontext_changed(self, viewmodel):
        raise NotImplementedError("on_datacontext_change must be implemented in the subclass")
    
    def on_closing(self):
        """Handle application closing properly"""
        self._destroyed = True
        # Cancel any pending after() calls
        if hasattr(self, '_after_jobs'):
            for job in self._after_jobs:
                self.after_cancel(job)
        # Destroy the window
        self.destroy()
    
    def safe_after(self, delay, callback):
        """Safe wrapper for after() calls"""
        if not self._destroyed:
            job = self.after(delay, callback)
            if not hasattr(self, '_after_jobs'):
                self._after_jobs = []
            self._after_jobs.append(job)
            return job

    def configure_styles(self) -> ttk.Style:
        """Configure custom styles for the GUI components."""
        # Configure some style overrides for BudManViewFrame
        style = ttk.Style(self)
        font_style = ('Segoe UI', 12)
        style.configure('TFrame', background=BMV_FAINT_GRAY, font=font_style)
        style.configure('AT.TCheckbutton', background=BMV_FAINT_GRAY, font=font_style)
        style.configure('AT.TLabel', background=BMV_FAINT_GRAY, font=font_style)
        style.configure('AT.TEntry', background=BMV_FAINT_GRAY, font=font_style)
        style.configure("Treeview.Heading", font=('Segoe UI', 12,'bold'))
        return style
#------------------------------------------------------------------------------+