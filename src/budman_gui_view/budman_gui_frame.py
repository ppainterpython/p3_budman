#------------------------------------------------------------------------------+
import logging
import tkinter as tk
from tkinter import EventType, scrolledtext, StringVar, BooleanVar
from tkinter import ttk
import ttkbootstrap as tb  # tb.Window used for root window only
from budman_gui_view.constants import *

ATV_DEFAULT_FILEPATH = "~/activity.json"  # default filename for saving

logger = logging.getLogger(BMV_WINDOW_TITLE)  # create logger for the module
logger.debug(f"Imported module: {__name__}")
logger.debug(f"{__name__} Logger name: {logger.name}, Level: {logger.level}")

class BudManGUIFrame(ttk.Frame):
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
    #--------------------------------------------------------------------------+
    #region BudManViewFrame class
    #--------------------------------------------------------------------------+

    def __init__(self, parent_frame:tk.Frame, root_window:tb.Window, datacontext:object=None): # self is tk.Tk root window
        # init super class (tk.Frame)
        super().__init__()

        # BudMan Application Attributes
        self.datacontext = datacontext    # BudManViewModel object used as datacontext
        self.filepath_value = tk.StringVar(self,value=ATV_DEFAULT_FILEPATH)  # file path for the budget manager data file
        self.autosave_value = tk.BooleanVar(self) # auto save flag for the budget manager data
        self.autosave_value.set(False) # default for autosave

        # tkinter configuration
        self.parent = parent_frame # reference to the parent frame
        self.root = root_window   # reference to the root window
        self.filepath_label: ttk.Label = None
        self.filepath_entry: tk.Entry = None
        self.autosave_checkbutton: ttk.Checkbutton = None
        self.button_frame: ttk.Frame = None
        self.save_button : tk.Button = None
        self.load_button : tk.Button = None
        self.quit_button: tk.Button = None
        self.paned_window: ttk.Panedwindow = None
        self.wb_tree: ttk.Treeview = None
        self.text_frame : tk.Frame = None
        self.text_area: scrolledtext.ScrolledText = None
        # init widgets in BudManGUIFrame
        self.create_BudManGUIFrame_widgets() # setup BudManGUIFrame widgets
        self.layout_BudManGUIFrame_widgets() # layout BudManGUIFrame widgets
        self.bind_BudManGUIFrame_widgets()   # bind BudManGUIFrame widgets to events
        self.load_sample_data()              # load sample data into widgets for testing

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame class methods
    #--------------------------------------------------------------------------+
    def create_BudManGUIFrame_widgets(self):
        '''Create the BudManGUIFrame widgets with minimal configuration,
        applying any style overrides.'''

        # Construct the widgets
        # Basic design: root window -> BudManGUIFrame -> BudManGUIFrame widgets
        # button frame holds the buttons arranged horizontally
        self.filepath_label = ttk.Label(self, text="BDM Store URL:")
        self.filepath_label.configure(style='AT.TLabel') # set style for label
        self.filepath_entry = tk.Entry(self,textvariable=self.filepath_value) 
        # self.filepath_entry.configure(style='AT.TEntry')  # set style for entry
        self.autosave_checkbutton = \
            ttk.Checkbutton(self,text="Auto Save",offvalue=False,onvalue=True, \
                           variable=self.autosave_value,style='AT.TCheckbutton')
        self.autosave_checkbutton.configure(style='AT.TCheckbutton')  
        self.button_frame = ttk.Frame(self)
        self.save_button = tk.Button(self.button_frame,text="Save", width=10)
        self.load_button = tk.Button(self.button_frame,text="Load", width=10)
        self.quit_button = tk.Button(self.button_frame,text="Quit", width=10)
        self.paned_window = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.wb_tree = ttk.Treeview(self.paned_window, 
                                    columns=('wb_index', 'wf_key', 'Status'), 
                                    show='tree headings')
        # self.wb_tree.configure(style='AT.Treeview')  # set style for treeview
        self.paned_window.add(self.wb_tree, weight=2)
        self.wb_tree.heading('#0', text='Workbook/Folder Name', anchor='w')
        self.wb_tree.heading('wb_index', text='wb_index', anchor='w')
        self.wb_tree.heading('wf_key', text='wf_key', anchor='w')
        self.wb_tree.heading('Status', text='Status', anchor='w')
        self.text_frame = tk.Frame(self.paned_window)
        self.text_area = scrolledtext.ScrolledText(self.text_frame,wrap=tk.WORD, 
                                                   width=40, height=10)
        self.paned_window.add(self.text_frame, weight=3)

    def load_sample_data(self):
        '''Load sample data into the BudManGUIFrame widgets for testing purposes.'''
        fi_entry = self.wb_tree.insert('', 'end', text="boa", values=("", "", ""))
        wf_entry = self.wb_tree.insert(fi_entry, 'end', text="new", values=("", "", ""))
        self.wb_tree.insert(wf_entry, 'end', text="workbook 1", values=('0', 'Input', 'Loaded'))
        self.wb_tree.insert(wf_entry, 'end', text="workbook 2", values=('1', 'Working', 'Not Loaded'))

        self.text_area.insert(tk.END, "Line 1:\n")
        self.text_area.insert(tk.END, "Line 2:\n")
        self.text_area.insert(tk.END, "Line 3:\n")
        self.text_area.yview(tk.END)

    def layout_BudManGUIFrame_widgets(self):
        '''Configure the BudManGUIFrame child widgets layout grid configuration'''
        # Use Pack layout for the BudManGUIFrame in the root window
        # The BudManGUIFrame should expand to fill the root window
        self.configure(style='TFrame') # set style for the frame
        # self.pack(side='top',  fill="both", expand=True,ipady=20) # pack layout for the frame

        # Configure the grid layout for the frame: 4 rows by 5 columns,
        # equal weight for all rows and columns.
        self.columnconfigure((0,1,2,3,4), weight=1)
        self.rowconfigure(2, weight=1,uniform="b")
        # self.rowconfigure(3, weight=2,uniform="b")

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

        # row 2: paned window with workbook treeview and text area
        self.paned_window.grid(row=2, column=0, columnspan=5, sticky="nsew")
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        self.text_area.grid(row=0, column=0, sticky="nsew")

    def bind_BudManGUIFrame_widgets(self):
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
    #endregion BudManGUIFrame class methods
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame properties
    def set_datacontext(self, datacontext: object):
        self.datacontext = datacontext

    def get_filepath(self):
        return self.filepath_value.get()

    def set_filepath(self, filepath: str):
        self.filepath_value.set(filepath)
    #endregion BudManGUIFrame properties
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame event handlers
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
        print(f"BudManGUIWindow.BudManGUIFrame.filepath changed to: {v} after: {s}")

    def on_save_button_clicked(self):
        """ Event handler for when the user clicks the save button. """
        v = self.filepath_value.get()
        print(f"BudManGUIWindow.BudManGUIFrame.save_button clicked with filepath: {v}")

    def on_load_button_clicked(self):
        """ Event handler for when the user clicks the load button. """
        v = self.filepath_value.get()
        print(f"BudManGUIWindow.BudManGUIFrame.load_button clicked with filepath: {v}")

    def on_autosave_changed(self):
        """ Event handler for when the user checks or unchecks the 
        autosave checkbox. """
        # v = self.autosave_value.get()
        print(f"BudManView.BudManViewFrame.autosave_value is to: {self.autosave_value.get()}" + \
              f" with autosave_checkbutton.state(): {self.autosave_checkbutton.state()}")
    #endregion BudManViewFrame event handlers
    #--------------------------------------------------------------------------+
    
#------------------------------------------------------------------------------+