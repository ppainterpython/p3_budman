# ---------------------------------------------------------------------------- +
#region budman_gui_window.py module
""" budman_gui_window.py implements the class BudManGuiWindow.
"""
#endregion budman_gui_app.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging, getpass
from typing import Optional
import tkinter as tk
import tkinter.font as tkFont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
import budman_settings as bdms
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
# bugman_gui_view modules and packages
from .budman_gui_style_registry import StyleRegistry
from .budman_gui_frame import BudManGUIFrame
from .budman_gui_msg import BudManGUIMsg
from .budman_gui_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)  # create logger for the module
budman_msg = BudManGUIMsg()  # Singleton instance of BudManGuiMsg
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUIWindow(ttk.Window, 
                      BudManAppDataContext_Binding,
                      p3m.CommandProcessor_Binding):
    #--------------------------------------------------------------------------+
    #region BudManGUIWindow class Intrinsics
    #--------------------------------------------------------------------------+
    #region BudManGUIWindow doc string
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
    #endregion BudManGUIWindow doc string
    #--------------------------------------------------------------------------+
    #region __init__() 
    def __init__(self, 
                 themename: str,
                 budman_settings : Optional[bdms.BudManSettings] = None,
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 data_context : Optional[BudManAppDataContext_Binding] = None,
                 ) -> None:
        # init root GUI application Window.
        super().__init__(themename=themename)
        # Application attributes.
        self._settings : bdms.BudManSettings = budman_settings if budman_settings else bdms.BudManSettings()
        self._dc_binding:bool = False
        self._cp_binding:bool = False
        self._store_url: str = ""
        self._tk_windowing_system: str = self.tk.call('tk', 'windowingsystem')

        try:
            # Setup DataContext_Binding
            if data_context is not None:
                self.DC = data_context
                self.dc_binding = True
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            logger.debug("BudManGUIWindow configured with no DataContext.")
        try:
            # Setup CommandProcessor_Binding
            if command_processor is not None:
                self.CP = command_processor
                self.cp_binding = True
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            logger.debug("BudManGUIWindow configured with no CommandProcessor.")

        # Widget value variable attributes.
        self._status_value: tk.StringVar = tk.StringVar(value=BMG_APP_READY_STATUS)
        self._user_value: tk.StringVar = tk.StringVar(value="un-set")
        self._window_size: tk.StringVar = tk.StringVar(value=f"{BMG_MIN_WINDOW_WIDTH}x{BMG_MIN_WINDOW_HEIGHT}")
        self._destroyed: bool = False
        self._progress_value: tk.IntVar = tk.IntVar(value=0)

        # Attributes for other widgets in the GUI.
        self.style_registry = StyleRegistry(themename=themename)
        self.themename: str = themename # Styles for the window and all widgets
        self.budman_gui_frame: BudManGUIFrame = None
        self.status_bar: ttk.Frame = None
        self.status_label: ttk.Label = None
        self.status_value: ttk.Label = None
        self.progress_label: ttk.Label = None
        self.progress_bar: ttk.Progressbar = None
        self.window_size_label: ttk.Label = None
        self.window_size_value: ttk.Label = None
        self.user_label: ttk.Label = None
        self.user_value: ttk.Label = None

        # Configure the root window properties
        self.configure_root_window()
        # Create the BudManGUIFrame for the main view (row 0)
        self.create_budman_gui_frame(command_processor, data_context)
        # Create the status bar for the bottom of the window (row 1)
        self._create_status_bar()
        # Bind event handlers
        self.bind_event_handlers()
        
        # All done
        logger.debug("BudManView initialized")
    #endregion __init__() 
    # -------------------------------------------------------------------------- +
    #region   BudManGUIWindow class properties
    @property
    def dc_binding(self) -> bool:
        """Get the dc_binding property."""
        return self._dc_binding
    @dc_binding.setter
    def dc_binding(self, value: bool) -> None:
        """Set the dc_binding property."""
        if not isinstance(value, bool):
            raise TypeError("dc_binding must be a boolean.")
        self._dc_binding = value
    @property
    def cp_binding(self) -> bool:
        """Get the cp_binding property."""
        return self._cp_binding
    @cp_binding.setter
    def cp_binding(self, value: bool) -> None:
        """Set the cp_binding property."""
        if not isinstance(value, bool):
            raise TypeError("cp_binding must be a boolean.")
        self._cp_binding = value
    @property
    def settings(self) -> bdms.BudManSettings:
        """Get the settings property."""
        return self._settings
    @settings.setter
    def settings(self, value: bdms.BudManSettings) -> None:
        """Set the settings property."""
        if not isinstance(value, bdms.BudManSettings):
            raise TypeError("settings must be a BudManSettings instance.")
        self._settings = value
        logger.debug(f"Settings updated: {self._settings}")
    @property
    def store_url(self) -> str:
        """Get the store_url property."""
        return self._store_url  
    @store_url.setter
    def store_url(self, value: str) -> None:
        """Set the store_url property."""
        if not isinstance(value, str):
            raise TypeError("store_url must be a string.")
        self._store_url = value
    @property
    def app_status(self) -> str:
        """Get the app_status property."""
        return self._status_value.get()
    @app_status.setter
    def app_status(self, value: str) -> None:
        """Set the app_status property."""
        if not isinstance(value, str):
            raise TypeError("app_status must be a string.")
        self._status_value.set(value)
    @property
    def window_size(self) -> str:  
        """Get the window_size property."""
        return self._window_size.get()
    @window_size.setter
    def window_size(self, value: str) -> None:
        """Set the window_size property."""
        if not isinstance(value, str):
            raise TypeError("window_size must be a string.")
        self._window_size.set(value)
    @property
    def app_user(self) -> str:  
        """Get the app_user property."""
        return self._user_value.get()
    @app_user.setter
    def app_user(self, value: str) -> None:
        """Set the app_user property."""
        if not isinstance(value, str):
            raise TypeError("app_user must be a string.")
        self._user_value.set(value)

    #endregion   BudManGUIWindow class properties
    # ------------------------------------------------------------------------ +
    #endregion BudManGUIWindow class Intrinsics
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region    BudManGUIView class methods
    def initialize(self) -> None:
        """Initialize the BudManGUIView class."""
        try:
            logger.debug(f"BudManGUIWindow: Initializing BudManGUIFrame widgets.")
            self.budman_gui_frame.filepath = self.store_url
            self.budman_gui_frame.initialize()
            budman_msg.msg_widget = self.budman_gui_frame.msg_area
            budman_msg.root = self
            budman_msg.msg_handler()
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def configure_root_window(self):
        """Configure the root window properties."""
        self.title(BMG_WINDOW_TITLE)
        self.geometry(f"{BMG_MIN_WINDOW_WIDTH}x{BMG_MIN_WINDOW_HEIGHT}")
        self.minsize(BMG_MIN_WINDOW_WIDTH, BMG_MIN_WINDOW_HEIGHT)
        self.maxsize(BMG_MAX_WINDOW_WIDTH, BMG_MAX_WINDOW_HEIGHT)

        # Configure main window grid 2x1 (rows x columns)
        self.grid_rowconfigure(0, weight=1)    # Main content area expands
        self.grid_rowconfigure(1, weight=0)    # Status bar fixed height
        self.grid_columnconfigure(0, weight=1) # Full width

        # Setup for Menu use later
        self.option_add('*tearOff', FALSE)


    def create_budman_gui_frame(self, command_processor, data_context):
        """Create the BudManGUIFrame widget."""
        self.budman_gui_frame = BudManGUIFrame(self, 
                                               self.style_registry, 
                                               command_processor=command_processor,
                                               data_context=data_context) 
        self.budman_gui_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    def _create_status_bar(self):
        """Creates a persistent status bar at the bottom of the window."""
        # Create status bar frame
        self.status_bar = ttk.Frame(self, 
                                    height=BMG_STATUS_BAR_HEIGHT)
        self.status_bar.configure(style="BMG.TFrame")
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,10))
        # self.status_bar.grid_propagate(False)  # Maintain fixed height
        
        # Configure status bar internal grid
        # self.status_bar.grid_columnconfigure(0, weight=0)  # Middle section expands
        
        # First from left - Status message
        self.status_label = ttk.Label(
            self.status_bar, 
            text=BMG_APP_STATUS_LABEL, 
            anchor="w"
        )
        self.status_label.configure(style="BMG.TLabel")
        self.status_label.pack(side="left", padx=(2,0), pady=5)
        self.status_value = ttk.Label(
            self.status_bar, 
            text=BMG_APP_READY_STATUS, 
            anchor="w",
            textvariable=self._status_value
        )
        self.status_value.configure(style="BMG.Value.TLabel")
        self.status_value.pack(side="left", padx=0, pady=5)

        # Vertical separator
        sep1 = ttk.Separator(self.status_bar, orient='vertical')
        sep1.pack(side="left", padx=(2,2), pady=5)

        # Second from left - Progress bar
        self.progress_label = ttk.Label(
            self.status_bar, 
            text=BMG_APP_PROGRESS_LABEL, 
            anchor="w"
        )
        self.progress_label.configure(style="BMG.TLabel")
        self.progress_label.pack(side="left", padx=0, pady=5)
        self.progress_bar = ttk.Progressbar(
            self.status_bar, 
            length=150, 
            variable=self._progress_value,
            mode="determinate"
        )
        self.progress_bar.configure(style="BMG.Horizontal.TProgressbar")
        self.progress_bar.pack(side="left", padx=(0,2), pady=5)
        self.progress_bar["value"] = 0

        # Vertical separator
        sep2 = ttk.Separator(self.status_bar, orient='vertical')
        sep2.pack(side="left", padx=(5,2), pady=5)

        # Third from left - Window size label
        self.window_size_label = ttk.Label(
            self.status_bar, 
            text=BMG_APP_WINDOW_SIZE_LABEL, 
            anchor="w"
        )
        self.window_size_label.configure(style="BMG.TLabel")
        self.window_size_label.pack(side="left", padx=0, pady=5)
        initialize_size: str = f"{BMG_MIN_WINDOW_WIDTH}x{BMG_MIN_WINDOW_HEIGHT}"
        initialize_width: int = int(BMG_MIN_WINDOW_WIDTH)
        initialize_height: int = int(BMG_MIN_WINDOW_HEIGHT)
        self.window_size_value = ttk.Label(
            self.status_bar, 
            text=f"Size: {initialize_size}", 
            anchor="w",
            textvariable=self._window_size
        )
        self.window_size_value.configure(style="BMG.Value.TLabel")
        self.window_size_value.pack(side="left", padx=0, pady=5)
        self.update_window_size(initialize_width, initialize_height)
        # self.window_size_value.grid(row=0, column=0, sticky="w",  padx=5, pady=5)

        # Vertical separator
        sep3 = ttk.Separator(self.status_bar, orient='vertical')
        sep3.pack(side="left", padx=(2,2), pady=5)

        # Far right - User info
        self.app_user = getpass.getuser()
        self.user_value = ttk.Label(
            self.status_bar, 
            text=self.app_user, 
            anchor="e",
            textvariable=self._user_value
        )
        self.user_value.configure(style="BMG.Value.TLabel")
        self.user_value.pack(side="right", padx=(0,2), pady=5)
        self.user_label = ttk.Label(
            self.status_bar, 
            text=BMG_APP_USER_LABEL, 
            anchor="e"
        )
        self.user_label.configure(style="BMG.TLabel")
        self.user_label.pack(side="right", padx=0, pady=5)

    def bind_event_handlers(self):
        """Bind event handlers for the BudManGUIWindow."""
        # Set up proper window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Bind event handlers
        self.bind("<Button-1>", self.on_quit_button_clicked)  # Focus on click anywhere
        self.bind("<Configure>", self.on_resize)
    #endregion BudManGUIView class methods
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region    BudManGUIWindow Event Handler Methods
    def on_datacontext_changed(self, viewmodel):
        raise NotImplementedError("on_datacontext_change must be implemented in the subclass")
    
    def on_resize(self, event):
        """Handle window resize events"""
        if not self._destroyed and type(event.widget).__name__ == "BudManGUIWindow":
            width = event.width
            height = event.height
            self.update_window_size(width, height)

    def on_quit_button_clicked(self, event):
        """ Event handler for when the user clicks the quit button. """
        # bubble up to the parent
        logger.info("BudManGUIWindow.BudManGUIFrame.quit_button clicked. Exiting application.")
        # Dispatch the Button-1 event depending on which child widget passed it.
        if event.widget == self.budman_gui_frame.quit_button:
            self.on_closing()

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
    #endregion BudManGUIWindow Event Handler Methods
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region    Status bar utility methods
    
    def update_status(self, message: str):
        """Update the status message"""
        if not self._destroyed and self.status_label.winfo_exists():
            self.status_label.config(text=message)
    
    def update_progress(self, value: int):
        """Update the progress bar (0-100)"""
        if not self._destroyed and self.progress_bar.winfo_exists():
            self.progress_bar["value"] = max(0, min(100, value))
    
    def update_window_size(self, width: int, height: int):
        """Update the window size label"""
        if not self._destroyed :
            self.window_size = f"{width}x{height}"

    def update_user(self, user: str):
        """Update the user label"""
        if not self._destroyed and self.user_label.winfo_exists():
            self.app_user=user

    def load_sample_data(self):
        '''Load sample data into the BudManGUIFrame widgets for testing purposes.'''
        gui_frame: BudManGUIFrame = self.budman_gui_frame
        root_folder = gui_frame.file_treeview.insert('', 'end', text="  0 budget", values=("Folder", "root", "n/a"))
        file0_entry = gui_frame.file_treeview.insert(root_folder, 'end', text="  0 .bdm_file_tree.json", values=("File", "n/a", "n/a"))
        file1_entry = gui_frame.file_treeview.insert(root_folder, 'end', text="  1 2025Budget.xlsx", values=("File", "n/a", "n/a"))
        folder1_entry = gui_frame.file_treeview.insert(root_folder, 'end', text="  1 boa", values=('Folder', 'Financial Institution', 'FI_FOLDER'))
        folder2_entry = gui_frame.file_treeview.insert(folder1_entry, 'end', text="  2 budget", values=('Folder', 'Budget', 'Working'))
        gui_frame.file_treeview.insert(folder2_entry, 'end', text="  7 Manual-BOAChecking2023.slxs", values=('File', 'n/a', 'User-defined'))

        gui_frame.msg_area.insert(tk.END, "Line 1:\n")
        gui_frame.msg_area.insert(tk.END, "Line 2:\n")
        gui_frame.msg_area.insert(tk.END, "Line 3:\n")
        gui_frame.msg_area.yview(tk.END)
        bdm_store_url = self.settings[bdms.BDM_STORE_URL]
        gui_frame.filepath = bdm_store_url  
        print("pause")

    #endregion Status bar utility methods
    #--------------------------------------------------------------------------+


#------------------------------------------------------------------------------+