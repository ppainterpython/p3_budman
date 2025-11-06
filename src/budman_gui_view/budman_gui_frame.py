# ---------------------------------------------------------------------------- +
#region budman_gui_frame.py module
""" budman_gui_frame.py implements the class BudManGuiFrame.
"""
#endregion budman_gui_app.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging
from typing import Optional
import tkinter as tk
import tkinter.font as tkFont
from tkinter import EventType, scrolledtext, StringVar, BooleanVar
from tkinter import ttk
import ttkbootstrap as tb  # tb.Window used for root window only
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from .budman_gui_style_registry import StyleRegistry
from budman_gui_view.budman_gui_constants import *
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(BMG_WINDOW_TITLE)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUIFrame(ttk.Frame, 
                      BudManAppDataContext_Binding,
                      p3m.CommandProcessor_Binding):
    #--------------------------------------------------------------------------+
    #region BudManViewFrame class intrinsics
    #--------------------------------------------------------------------------+
    #region BudMagGUIFram doc string
    """ Budget Manager View Frame class.
        The BudManViewFrame class is a subclass of the ttkbootstrap class and 
        implements the primary user interface for the application.

        Frame Layout
        ------------
        BudManGUIFrame(ttk.Frame)
            3 rows, 5 columns
            Row 0: Filepath label, entry, autosave checkbox
            Row 1: Button frame with Save, Load, Quit buttons
            Row 2: Paned window with workbook treeview and text area. This
            enables the treeview and text area to be resized vertically together.

        Properties
        ----------
        datacontext : object
            The data context for the view, typically a ViewModel object. 
            Just maintain a reference to the datacontext from root.
    """
    #endregion BudMagGUIFram doc string
    #--------------------------------------------------------------------------+
    #region __init__() 
    def __init__(self, 
                 parent:tb.Window, 
                 style_registry: StyleRegistry, 
                 command_processor : Optional[p3m.CommandProcessor_Binding] = None,
                 data_context : Optional[BudManAppDataContext_Binding] = None,
                 ) -> None:
        # init super class (tk.Frame)
        super().__init__(parent,style="BMG.TFrame")
        self._dc_binding:bool = False
        self._cp_binding:bool = False
        try:
            # Setup DataContext_Binding
            if data_context is not None:
                self.DC = data_context
                self.dc_binding = True
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            logger.debug("BudManGUIFrame configured with no DataContext.")

        try:
            # Setup CommandProcessor_Binding
            if command_processor is not None:
                self.CP = command_processor
                self.cp_binding = True
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            logger.debug("BudManGUIFrame configured with no CommandProcessor.")

        # BudMan Application Attributes
        self._filepath_value = tk.StringVar(self,value="default")  # file path for the budget manager data file
        self._autosave_value = tk.BooleanVar(self) # auto save flag for the budget manager data
        self._autosave_value.set(False) # default for autosave

        # tkinter configuration
        self.parent = parent   # reference to the root window
        self.filepath_label: ttk.Label = None
        self.filepath_entry: tk.Entry = None
        self.autosave_checkbutton: ttk.Checkbutton = None
        self.button_frame: ttk.Frame = None
        self.save_button : tk.Button = None
        self.load_button : tk.Button = None
        self.quit_button: tk.Button = None
        self.paned_window: ttk.Panedwindow = None
        self.file_tree: ttk.Treeview = None
        self.text_frame : tk.Frame = None
        self.text_area: scrolledtext.ScrolledText = None

        # init widgets in BudManGUIFrame
        self.configure(style="BMG.TFrame")
        self.create_BudManGUIFrame_widgets() # setup BudManGUIFrame widgets
        self.layout_BudManGUIFrame_widgets() # layout BudManGUIFrame widgets
        self.bind_BudManGUIFrame_widgets()   # bind BudManGUIFrame widgets to events
    #endregion __init__()
    #--------------------------------------------------------------------------+
    #region BudManGUIFrame properties
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
    def filepath(self) -> str:
        """Get the filepath property."""
        return self._filepath_value.get()

    @filepath.setter
    def filepath(self, filepath: str) -> None:
        """Set the filepath property."""
        self._filepath_value.set(filepath)

    @property
    def autosave(self) -> bool:
        """Get the autosave property."""
        return self._autosave_value.get()
    @autosave.setter
    def autosave(self, autosave: bool) -> None:
        """Set the autosave property."""
        self._autosave_value.set(autosave)
    #endregion BudManGUIFrame properties
    #--------------------------------------------------------------------------+
    #endregion BudManGUIFrame class intrinsics
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame class methods
    def initialize(self) -> None:
        """Initialize the BudManGUIView class."""
        try:
            # Setup the file tree here from self.DC.model.bsm_file_tree
            logger.debug(f"BudManGUIFrame: Initializing BudManGUIFrame widgets.")
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise

    def create_BudManGUIFrame_widgets(self):
        '''Create the BudManGUIFrame widgets with minimal configuration,
        applying any style overrides.'''

        # Construct the widgets
        # Basic design: root window -> BudManGUIFrame -> BudManGUIFrame widgets
        # button frame holds the buttons arranged horizontally
        self.filepath_label = ttk.Label(self, text="BDM Store URL:")
        self.filepath_label.configure(style='BMG.TLabel') # set style for label
        # entry_font = tkFont.Font(family="Segoe UI", size=12)
        self.filepath_entry = ttk.Entry(self, textvariable=self._filepath_value) #,font=entry_font) 
        self.filepath_entry.configure(style='BMG.TEntry')  # set style for entry
        self.autosave_checkbutton = \
            ttk.Checkbutton(self,text="Auto Save",offvalue=False,onvalue=True, \
                           variable=self._autosave_value,style='BMG.TCheckbutton')
        self.autosave_checkbutton.configure(style='BMG.TCheckbutton')  
        self.button_frame = ttk.Frame(self)
        self.button_frame.configure(style='BMG.TFrame')  # set style for button frame
        self.save_button = ttk.Button(self.button_frame,text="Save")
        self.save_button.configure(style='BMG.TButton')  # set style for button
        self.load_button = ttk.Button(self.button_frame,text="Load")
        self.load_button.configure(style='BMG.TButton')  # set style for button 
        self.quit_button = ttk.Button(self.button_frame,text="Quit")
        self.quit_button.configure(style='BMG.TButton')  # set style for button

        self.paned_window = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.paned_window.configure(style='BMG.TPanedwindow')  # set style for panedwindow
        self.file_tree = ttk.Treeview(self.paned_window, 
                                    columns=('file_index', 'wf_key', 'Status'), 
                                    show='tree headings')
        self.file_tree.configure(style='BMG.Treeview')
        self.paned_window.add(self.file_tree, weight=2)
        self.file_tree.heading('#0', text='Name', anchor='w')
        self.file_tree.column('#0', anchor='w', width=200)
        self.file_tree.heading('file_index', text='File Index', anchor='w')
        self.file_tree.column('file_index', anchor='w', width=40)
        self.file_tree.heading('wf_key', text='wf_key', anchor='w')
        self.file_tree.column('wf_key', anchor='w', width=80)
        self.file_tree.heading('Status', text='Status', anchor='w')
        self.file_tree.column('Status', anchor='w', width=80)
        self.text_frame = tk.Frame(self.paned_window)
        self.text_frame.configure(bg=BMG_FAINT_GRAY)
        self.text_area = scrolledtext.ScrolledText(self.text_frame,wrap=tk.WORD, 
                                                   width=40, height=10)
        self.paned_window.add(self.text_frame, weight=3)

    def layout_BudManGUIFrame_widgets(self):
        '''Configure the BudManGUIFrame child widgets layout grid configuration'''
        # Use Pack layout for the BudManGUIFrame in the root window
        # The BudManGUIFrame should expand to fill the root window
        self.configure(style='BMG.TFrame') # set style for the frame
        # self.pack(side='top',  fill="both", expand=True,ipady=20) # pack layout for the frame

        # Configure the grid layout for the frame: 4 rows by 5 columns,
        # equal weight for all rows and columns.
        self.columnconfigure(0, minsize=100)
        self.columnconfigure((1,2,3), weight=1)
        self.columnconfigure(4, minsize=50)
        self.rowconfigure(2, weight=1, uniform="b")
        # self.rowconfigure(3, weight=2,uniform="b")

        # Layout the widgets in the grid
        # row 0: filepath label, entry, autosave checkbutton
        self.filepath_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filepath_entry.grid(row=0, column=1, columnspan=3, sticky="ew")
        self.autosave_checkbutton.grid(row=0, column=4, padx=5, pady=5, \
                                       sticky="e")

        # row 1: button frame with save, load, quit buttons
        self.button_frame.grid(row=1, column=0, columnspan=5, sticky="nse")
        self.quit_button.pack(side="right", padx=5, pady=5)
        self.load_button.pack(side="right", padx=5, pady=5)
        self.save_button.pack(side="right", padx=5, pady=5)

        # row 2: paned window with workbook treeview and text area
        self.paned_window.grid(row=2, column=0, columnspan=5, sticky="nsew")
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        self.text_area.grid(row=0, column=0, sticky="nsew")

    def bind_BudManGUIFrame_widgets(self):
        ''' Bind the widgets in the frame to their respective event handlers.
        A set up specific key bindings.'''
        # bind event handlers
        self.quit_button.configure(command=self.parent.destroy) # close the app
        self.autosave_checkbutton.configure(command=self.on_autosave_changed)
        self.save_button.configure(command=self.on_save_button_clicked)
        self.load_button.configure(command=self.on_load_button_clicked)

        # do key bindings
        self.filepath_entry.bind("<Return>", self.on_filepath_changed)
        self.filepath_entry.bind("<Tab>", self.on_filepath_changed)
        self.filepath_entry.bind("<FocusOut>", self.on_filepath_changed)
    #endregion BudManGUIFrame class methods
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame event handlers
    #--------------------------------------------------------------------------+
    def on_filepath_changed(self, event):
        """ Event handler for when the user presses the Enter key in the filepath entry. """
        # for <Return> key event, event.keysym = 'Return'
        # for <Tab> key event, event.keysym = 'Tab'
        # for <FocusOut> event, event.type = 'EventType.FocusOut'
        v = self.filepath
        s = "<Return> key event" if event.keysym == 'Return' else \
            "<Tab> key event" if event.keysym == 'Tab' else \
            "<FocusOut> event" if event.type == EventType.FocusOut else "Unknown event"
        # TODO: how to signal event to ViewModel?
        #self.datacontext.ativity_store_uri.set(v) # signal ViewModel of change
        print(f"BudManGUIWindow.BudManGUIFrame.filepath changed to: {v} after: {s}")

    def on_save_button_clicked(self):
        """ Event handler for when the user clicks the save button. """
        v = self.filepath
        print(f"BudManGUIWindow.BudManGUIFrame.save_button clicked with filepath: {v}")

    def on_load_button_clicked(self):
        """ Event handler for when the user clicks the load button. """
        v = self.filepath
        if self.button_is_enabled(self.save_button):
            self.disable_button(self.save_button)
        else:   
            self.enable_button(self.save_button)
        print(f"BudManGUIWindow.BudManGUIFrame.load_button clicked with filepath: {v}")

    def on_autosave_changed(self):
        """ Event handler for when the user checks or unchecks the 
        autosave checkbox. """
        # v = self.autosave_value.get()
        print(f"BudManView.BudManViewFrame.autosave_value is to: {self.autosave}" + \
              f" with autosave_checkbutton.state(): {self.autosave_checkbutton.state()}")
    #endregion BudManViewFrame event handlers
    #--------------------------------------------------------------------------+
    
    #------------------------------------------------------------------------------+
    #region BudManGUIFrame support methods
    def disable_button(self, button:ttk.Button) -> None:
        """Disable a button widget."""
        button.state(["disabled"])
    def enable_button(self, button:ttk.Button) -> None:
        """Enable a button widget."""
        button.state(["!disabled"])
    def button_is_enabled(self, button:ttk.Button) -> bool:
        """Check if a button widget is enabled."""
        return button.instate(["!disabled"])    
    #endrgion BudManGUIFrame support methods
#------------------------------------------------------------------------------+