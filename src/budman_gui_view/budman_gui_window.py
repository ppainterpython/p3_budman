#-----------------------------------------------------------------------------+
import logging
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# import ttkbootstrap as tb  # tb.Window used for root window only
from .budman_gui_style_registry import StyleRegistry
from .budman_gui_frame import BudManGUIFrame
from .budman_gui_constants import *

logger = logging.getLogger(__name__)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")

class BudManGUIWindow(ttk.Window):
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
    # Class constructor
    def __init__(self, themename: str, datacontext:object = None ):
        # init root window
        super().__init__(themename=themename)
        self.style_registry = StyleRegistry(themename=themename)
        self.title( BMG_WINDOW_TITLE)
        self.geometry(f"{BMG_MIN_WINDOW_WIDTH}x{BMG_MIN_WINDOW_HEIGHT}")
        self.themename: str = themename
        self.budman_gui_frame: ttk.Frame = None
        self.status_bar: ttk.Frame = None
        self.status_label: ttk.Label = None
        self.progress: ttk.Progressbar = None
        self.user_label: ttk.Label = None
        
        # BudMan Application Attributes
        self.datacontext: object = datacontext    # datacontext object

        # Configure main window grid
        self._destroyed: bool = False
        self.minsize(BMG_MIN_WINDOW_WIDTH, BMG_MIN_WINDOW_HEIGHT)
        self.maxsize(BMG_MAX_WINDOW_WIDTH, BMG_MAX_WINDOW_HEIGHT)
        
        # Configure main window grid weights
        self.grid_rowconfigure(0, weight=1)    # Main content area expands
        self.grid_rowconfigure(1, weight=0)    # Status bar fixed height
        self.grid_columnconfigure(0, weight=1) # Full width

        # Create the BudManGUIFrame for the main view (row 0)
        self.budman_gui_frame = BudManGUIFrame(self, self.style_registry, self.datacontext) 
        self.budman_gui_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Create the status bar for the bottom of the window (row 1)
        self._create_status_bar()

        # Set up proper window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Bind event handlers
        self.bind("<Configure>", self.on_resize)

        # All done
        logger.debug("BudManView initialized")

    def _create_status_bar(self):
        """Creates a persistent status bar at the bottom of the window."""
        # Create status bar frame
        self.status_bar = ttk.Frame(self, height=BMG_STATUS_BAR_HEIGHT)
        self.status_bar.configure(style="BMG.TFrame")
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 2))
        self.status_bar.grid_propagate(False)  # Maintain fixed height
        
        # Configure status bar internal grid
        self.status_bar.grid_columnconfigure(1, weight=1)  # Middle section expands
        
        # Left section - Status message
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready", 
            anchor="w"
        )
        self.status_label.configure(style="BMG.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w", padx=(5, 10))

        # Middle section - Progress bar
        self.progress = ttk.Progressbar(
            self.status_bar, 
            length=150, 
            mode="determinate"
        )
        self.progress.grid(row=0, column=1, sticky="w", padx=10)
        self.progress["value"] = 0

        # Middle section - Window size label
        self.window_size = ttk.Label(
            self.status_bar, 
            text="Size: 800x600", 
            anchor="w"
        )
        self.window_size.configure(style="BMG.TLabel")
        self.window_size.grid(row=0, column=1, sticky="w", padx=10)

        # Right section - User info
        self.user_label = ttk.Label(
            self.status_bar, 
            text="User: Paul", 
            anchor="e"
        )
        self.user_label.configure(style="BMG.TLabel")
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
    
    def update_window_size(self, width: int, height: int):
        """Update the window size label"""
        if not self._destroyed and self.window_size.winfo_exists():
            self.window_size.config(text=f"Size: {width}x{height}")

    def update_user(self, user: str):
        """Update the user label"""
        if not self._destroyed and self.user_label.winfo_exists():
            self.user_label.config(text=f"User: {user}")

    #--------------------------------------------------------------------------+
    # Event Handler Methods

    def on_datacontext_changed(self, viewmodel):
        raise NotImplementedError("on_datacontext_change must be implemented in the subclass")
    
    def on_resize(self, event):
        """Handle window resize events"""
        if not self._destroyed:
            width = event.width
            height = event.height
            self.update_window_size(width, height)

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

#------------------------------------------------------------------------------+