#------------------------------------------------------------------------------+
import logging
import tkinter as tk
from tkinter import EventType, scrolledtext, StringVar, BooleanVar
from tkinter import ttk
from budman_gui_view.constants import *

ATV_DEFAULT_FILEPATH = "~/activity.json"  # default filename for saving

logger = logging.getLogger(BMV_WINDOW_TITLE)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")

class BudManGUIFrame(ttk.Frame):
    """ Budget Manager View Frame class.
        The BudManViewFrame class is a subclass of the ttkbootstrap class and 
        implements the primary user interface for the application.

        Properties
        ----------
        datacontext : object
            The data context for the view, typically a ViewModel object. 
            Just maintain a reference to the datacontext from root.
    """
    #--------------------------------------------------------------------------+
    #region BudManViewFrame class
    #--------------------------------------------------------------------------+
    # DataContext property
    datacontext: object = None    # BudManViewModel object used as datacontext

    # Widget value binding properties
    # These properties are bound to the UI widgets in the frame
    filepath_value: tk.StringVar  # file path for the budget manager data file
    autosave_value: tk.BooleanVar # auto save flag for the budget manager data

    # UI widgets in the frame
    root : object = None # root window
    filepath_label: ttk.Label = None
    filepath_entry: tk.Entry = None
    autosave_checkbutton: ttk.Checkbutton = None
    button_frame: ttk.Frame = None
    save_button : tk.Button = None
    load_button : tk.Button = None
    quit_button: tk.Button = None
    text_frame : tk.Frame = None
    text_area: scrolledtext.ScrolledText = None

    def __init__(self, root): # self is tk.Tk root window
        # init super class (tk.Frame)
        super().__init__()

        # init value properties
        self.root = root # reference to the root window
        self.datacontext = root.datacontext # reference to the datacontext
        self.filepath_value = tk.StringVar(self,value=ATV_DEFAULT_FILEPATH)
        self.autosave_value = tk.BooleanVar(self)
        self.autosave_value.set(False) # default for autosave

        # init widgets in ATViewFrame
        self.create_atviewframe_widgets() # setup atviewframe widgets
        self.layout_atviewframe_widgets() # layout atviewframe widgets
        self.bind_atviewframe_widgets()   # bind atviewframe widgets to events

        # ...existing code...
        self._destroyed = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    #endregion ATViewFrame class

    def on_closing(self):
        """Handle application closing properly"""
        self._destroyed = True
        # Cancel any pending after() calls
        if hasattr(self, '_after_jobs'):
            for job in self._after_jobs:
                self.root.after_cancel(job)
        # Destroy the window
        self.root.destroy()
    
    def safe_after(self, delay, callback):
        """Safe wrapper for after() calls"""
        if not self._destroyed:
            job = self.root.after(delay, callback)
            if not hasattr(self, '_after_jobs'):
                self._after_jobs = []
            self._after_jobs.append(job)
            return job
    #--------------------------------------------------------------------------+
    #region ATViewFrame class methods
    #--------------------------------------------------------------------------+
    def create_atviewframe_widgets(self):
        '''Create the ATViewFrame widgets with minimal configuration,
        applying any style overrides.'''
        # Configure some style overrides for ATViewFrame
        style = ttk.Style(self)
        font_style = ('Segoe UI', 12)
        style.configure('TFrame', background=BMV_FAINT_GRAY, font=font_style)
        style.configure('AT.TCheckbutton', background=BMV_FAINT_GRAY, font=font_style)
        style.configure('AT.TLabel', background=BMV_FAINT_GRAY, font=font_style)
        style.configure('AT.TEntry', background=BMV_FAINT_GRAY, font=font_style)


        # Construct the widgets
        # Basic design: root window -> ATViewFrame -> ATViewFrame widgets
        # button frame holds the buttons arranged horizontally
        self.filepath_label = ttk.Label(self, text="File Path:")
        self.filepath_label.configure(style='AT.TLabel') # set style for label
        self.filepath_entry = tk.Entry(self,textvariable=self.filepath_value, font=font_style) 
        self.autosave_checkbutton = \
            ttk.Checkbutton(self,text="Auto Save",offvalue=False,onvalue=True, \
                           variable=self.autosave_value,style='AT.TCheckbutton')
        self.autosave_checkbutton.configure(style='AT.TCheckbutton')  
        self.button_frame = ttk.Frame(self)
        self.save_button = tk.Button(self.button_frame,text="Save", width=10)
        self.load_button = tk.Button(self.button_frame,text="Load", width=10)
        self.quit_button = tk.Button(self.button_frame,text="Quit", width=10)
        self.text_frame = tk.Frame(self)
        self.text_area = scrolledtext.ScrolledText(self.text_frame,wrap=tk.WORD, 
                                                   width=40, height=10)
        self.text_area.insert(tk.END, "Line 1:\n")
        self.text_area.insert(tk.END, "Line 2:\n")
        self.text_area.insert(tk.END, "Line 3:\n")
        self.text_area.yview(tk.END)

        self.wb_tree = ttk.Treeview(self)
        self.wb_tree['columns'] = ('wb_index', 'wf_key', 'Status')
        self.wb_tree.heading('#0', text='Workbook Name', anchor='w')
        self.wb_tree.heading('wb_index', text='wb_index')
        self.wb_tree.heading('wf_key', text='wf_key')
        self.wb_tree.heading('Status', text='Status')
        self.wb_tree.insert('', 'end', text='Workbook 1', values=('0', 'Input', 'Loaded'))
        self.wb_tree.insert('', 'end', text='Workbook 2', values=('1', 'Working', 'Not Loaded'))
        #debug layout
        # tk.Label(self, text="Cell 3,0").grid(row=3, column=0, columnspan=1, \
        #                                      sticky="nsew", padx=5, pady=5)
        # tk.Label(self, text="Cell 3,1").grid(row=3, column=1, columnspan=1, \
        #                                      sticky="nsew", padx=5, pady=5)
        # tk.Label(self, text="Cell 3,2").grid(row=3, column=2, columnspan=1, \
        #                                      sticky="nsew", padx=5, pady=5)
        # tk.Label(self, text="Cell 3,3").grid(row=3, column=3, columnspan=1, \
        #                                      sticky="nsew", padx=5, pady=5)
        # tk.Label(self, text="Cell 3,4").grid(row=3, column=4, columnspan=1, \
        #                                      sticky="nsew", padx=5, pady=5)

    def layout_atviewframe_widgets(self):
        '''Configure the ATViewFrame child widgets layout grid configuration'''
        # Use Pack layout for the ATViewFrame in the root window
        # The ATViewFrame should expand to fill the root window
        self.configure(style='TFrame') # set style for the frame
        self.pack(side='top',  fill="both", expand=True,ipady=20) # pack layout for the frame

        # Configure the grid layout for the frame: 4 rows by 5 columns,
        # equal weight for all rows and columns.
        self.columnconfigure((0,1,2,3,4), weight=1)
        self.rowconfigure(3, weight=2,uniform="b")

        # Layout the widgets in the grid
        # row 0: filepath label, entry, autosave checkbutton
        self.filepath_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filepath_entry.grid(row=0, column=1, columnspan=3, sticky="ew")
        self.autosave_checkbutton.grid(row=0, column=4, padx=5, pady=5, \
                                       sticky="w")

        # row 1: button frame with save, load, quit buttons
        self.button_frame.grid(row=1, column=0, columnspan=5, sticky="nse")
        self.quit_button.pack(side="right", padx=5, pady=5)
        self.load_button.pack(side="right", padx=5, pady=5)
        self.save_button.pack(side="right", padx=5, pady=5)

        # row 2: text area for activity entries
        self.text_frame.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)

        # row 3: workbook treeview
        self.wb_tree.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
    def bind_atviewframe_widgets(self):
        ''' Bind the widgets in the frame to their respective event handlers.
        A set up specific key bindings.'''
        # bind event handlers
        self.quit_button.configure(command=self.root.destroy) # close the app
        self.autosave_checkbutton.configure(command=self.on_autosave_changed)
        self.save_button.configure(command=self.on_save_button_clicked)
        self.load_button.configure(command=self.on_load_button_clicked)

        # do key bindings
        self.filepath_entry.bind("<Return>", self.on_filepath_changed)
        self.filepath_entry.bind("<Tab>", self.on_filepath_changed)
        self.filepath_entry.bind("<FocusOut>", self.on_filepath_changed)
    #endregion ATViewFrame class methods
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region ATViewFrame properties
    def set_datacontext(self, datacontext: object):
        self.datacontext = datacontext

    def get_filepath(self):
        return self.filepath_value.get()

    def set_filepath(self, filepath: str):
        self.filepath_value.set(filepath)
    #endregion ATViewFrame properties
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region ATViewFrame event handlers
    #--------------------------------------------------------------------------+
    def on_filepath_changed(self, event):
        """ Event handler for when the user presses the Enter key in the filepath entry. """
        # for <Return> key event, event.keysym = 'Return'
        # for <Tab> key event, event.keysym = 'Tab'
        # for <FocusOut> event, event.type = 'EventType.FocusOut'
        v = self.filepath_value.get()
        s = "<Return> key event" if event.keysym == 'Return' else \
            "<Tab> key event" if event.keysym == 'Tab' else \
            "<FocusOut> event" if event.type == EventType.FocusOut else "Unknown event"
        # TODO: how to signal event to ViewModel?
        #self.datacontext.ativity_store_uri.set(v) # signal ViewModel of change
        print(f"ATView.ATVFrame.filepath changed to: {v} after: {s}")

    def on_save_button_clicked(self):
        """ Event handler for when the user clicks the save button. """
        v = self.filepath_value.get()
        print(f"ATView.ATVFrame.save_button clicked with filepath: {v}")

    def on_load_button_clicked(self):
        """ Event handler for when the user clicks the load button. """
        v = self.filepath_value.get()
        print(f"ATView.ATVFrame.load_button clicked with filepath: {v}")

    def on_autosave_changed(self):
        """ Event handler for when the user checks or unchecks the 
        autosave checkbox. """
        # v = self.autosave_value.get()
        print(f"BudManView.BudManViewFrame.autosave_value is to: {self.autosave_value.get()}" + \
              f" with autosave_checkbutton.state(): {self.autosave_checkbutton.state()}")
    #endregion BudManViewFrame event handlers
    #--------------------------------------------------------------------------+
    
#------------------------------------------------------------------------------+