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
from treelib import Tree, Node
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from budman_namespace import (FILE_TREE_NODE_TYPE_KEY, FILE_TREE_NODE_WF_KEY,
                              FILE_TREE_NODE_WF_PURPOSE)
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
from .budman_gui_style_registry import StyleRegistry
from .budman_gui_msg import BudManGuiMsg
from .budman_gui_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(BMG_WINDOW_TITLE)  # create logger for the module
budman_msg = BudManGuiMsg()  # Singleton instance of BudManGuiMsg
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
        self._file_tree: Optional[Tree] = None
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
        self.style_registry = style_registry  # reference to the style registry
        self.filepath_label: ttk.Label = None
        self.filepath_entry: tk.Entry = None
        self.autosave_checkbutton: ttk.Checkbutton = None
        self.button_frame: ttk.Frame = None
        self.save_button : tk.Button = None
        self.load_button : tk.Button = None
        self.quit_button: tk.Button = None
        self.paned_window: ttk.Panedwindow = None
        self.file_treeview: ttk.Treeview = None
        self.text_frame : tk.Frame = None
        self.msg_area: scrolledtext.ScrolledText = None

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

    @property 
    def file_tree(self) -> Optional[Tree]:
        """Get the file_tree property."""
        return self._file_tree
    @file_tree.setter
    def file_tree(self, file_tree: Optional[Tree]) -> None:
        """Set the file_tree property."""
        if not isinstance(file_tree, (Tree, type(None))):
            raise TypeError("file_tree must be a Tree or None.")
        self._file_tree = file_tree
    #endregion BudManGUIFrame properties
    #--------------------------------------------------------------------------+
    #endregion BudManGUIFrame class intrinsics
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame class methods
    def initialize(self) -> None:
        """Initialize the BudManGUIView class."""
        try:
            # Setup the file tree here 
            self.initialize_file_tree()
            logger.debug(f"BudManGUIFrame: Initializing BudManGUIFrame widgets.")
            return self
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
    
    def initialize_file_tree(self) -> None:
        """Initialize the file treeview widget from the data context."""
        try:
            logger.debug(f"BudManGUIFrame: Initializing file treeview widget.")
            if self.dc_binding:
                # User the dc_FILE_TREE from the data context
                self.file_tree = self.dc_FILE_TREE
                self.refresh_file_treeview()
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

        # Paned window with TreeView and Frame:ScrolledText widget
        self.paned_window = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.paned_window.configure(style='BMG.TPanedwindow')  # set style for panedwindow
        self.file_treeview = self.create_file_treeview()
        self.paned_window.add(self.file_treeview, weight=2)
        # Text frame and area
        self.text_frame = tk.Frame(self.paned_window)
        self.text_frame.configure(bg=BMG_FAINT_GRAY)
        self.msg_area = self.create_msg_area_widget()
        self.paned_window.add(self.text_frame, weight=3)

    def create_msg_area_widget(self) -> scrolledtext.ScrolledText:
        """Create a scrolled text area widget."""
        try:
            msg_area = scrolledtext.ScrolledText(self.text_frame,wrap=tk.WORD, 
                                                  width=40, height=10)
            msg_area.configure(bg=BMG_FAINT_GRAY, fg=BMG_DARK_TEXT,
                                font=BMG_BASIC_FIXED_FONT)
            self.style_registry.configure_tags_text(msg_area)
            return msg_area
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
    def create_file_treeview(self) -> ttk.Treeview:
        """Create a file treeview widget."""
        try:
            file_treeview = ttk.Treeview(self.paned_window, 
                                    columns=(FILE_TREE_NODE_TYPE_KEY,
                                             FILE_TREE_NODE_WF_KEY, 
                                             FILE_TREE_NODE_WF_PURPOSE), 
                                    show='tree headings')
            file_treeview.configure(style='BMG.Treeview')
            # file_treeview config: headings and columns
            file_treeview.heading('#0', text='Index:Name', anchor='w')
            file_treeview.column('#0', anchor='w', width=200)
            file_treeview.heading(FILE_TREE_NODE_TYPE_KEY, text='Type', anchor='w')
            file_treeview.column(FILE_TREE_NODE_TYPE_KEY, anchor='w', width=40)
            file_treeview.heading(FILE_TREE_NODE_WF_KEY, text='Workflow', anchor='w')
            file_treeview.column(FILE_TREE_NODE_WF_KEY, anchor='w', width=80)
            file_treeview.heading(FILE_TREE_NODE_WF_PURPOSE, text='Purpose', anchor='w')
            file_treeview.column(FILE_TREE_NODE_WF_PURPOSE, anchor='w', width=80)
            return file_treeview
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

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
        self.msg_area.grid(row=0, column=0, sticky="nsew")

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

        # Treeview selection event binding
        self.file_treeview.tag_bind(BMG_FTVOBJECT, "<<TreeviewSelect>>", self.on_file_treeview_select)
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
        budman_msg.output(f"Load button clicked with filepath: {v}", BMG_DEBUG)
        print(f"BudManGUIWindow.BudManGUIFrame.load_button clicked with filepath: {v}")

    def on_autosave_changed(self):
        """ Event handler for when the user checks or unchecks the 
        autosave checkbox. """
        # v = self.autosave_value.get()
        print(f"BudManView.BudManViewFrame.autosave_value is to: {self.autosave}" + \
              f" with autosave_checkbutton.state(): {self.autosave_checkbutton.state()}")
    
    def on_file_treeview_select(self, event):
        """ Event handler for when the user selects an item in the file treeview. """
        selected_items = self.file_treeview.selection()
        for item in selected_items:
            item_text = self.file_treeview.item(item, "text")
            print(f"BudManGUIFrame: Selected file treeview item: {item_text} (ID: {item})")
    #endregion BudManViewFrame event handlers
    #--------------------------------------------------------------------------+
    
    #------------------------------------------------------------------------------+
    #region BudManGUIFrame support methods
    def refresh_file_treeview(self) -> None:
        """Refresh the file treeview widget from the file_tree property."""
        try:
            if self.file_tree is None:
                logger.debug("BudManGUIFrame: No file_tree to refresh.")
                return
            # Update the file_treeview. If one exists with content, then remove
            # it and replace with a new one with updated content.
            if len(self.file_treeview.children) > 0:
                new_treeview = self.create_file_treeview()
                self.paned_window.forget(1)
                self.paned_window.add(1, new_treeview, weight=2)
                self.file_treeview = new_treeview
            # Traverse the file_tree and add items to file_treeview
            root_file_tree_node_id: str = self.file_tree.root
            root_file_tree_node: Node = self.file_tree[root_file_tree_node_id]
            # Setup the root file_treeview item
            root_file_treeview_id = self.file_treeview.insert(
                '', 
                tk.END, 
                text=root_file_tree_node.tag,
                iid=root_file_tree_node_id,
                tags=(BMG_FTVOBJECT,),
                values=("BDM_FOLDER", "root", "All"))

            # # Populate the file_treeview with items from the file_tree
            def add_tree_nodes(file_tree: Tree, 
                               parent_file_tree_node_id: str,
                               parent_file_treeview_node_id: str) -> None:
                # for node_id in self.file_tree.expand_tree():
                #     node = self.file_tree.get_node(node_id)
                # node.identifier = full path of folder or file
                # node.tag = "nnn name" where nnn is the file or folder index
                #            and name is the file or folder name.
                for file_tree_node in file_tree.children(parent_file_tree_node_id):
                    item_info = self.dc_FILE_TREE_node_info(file_tree_node)
                    item_type = "unknown"
                    workflow_value = "unknown"
                    purpose_value = "unknown"
                    if item_info is not None:
                        item_type = item_info.get(FILE_TREE_NODE_TYPE_KEY, item_type)
                        workflow_value = item_info.get(FILE_TREE_NODE_WF_KEY, workflow_value)
                        purpose_value = item_info.get(FILE_TREE_NODE_WF_PURPOSE, purpose_value)
                    item_id = self.file_treeview.insert(
                        parent_file_treeview_node_id,
                        tk.END,
                        iid=file_tree_node.identifier,
                        text=file_tree_node.tag,
                        tags=(BMG_FTVOBJECT,),
                        values=(item_type, workflow_value, purpose_value)
                    )
                    add_tree_nodes(self.file_tree, file_tree_node.identifier, item_id)


            add_tree_nodes(self.file_tree, 
                           root_file_tree_node_id, 
                           root_file_treeview_id)
            logger.debug("BudManGUIFrame: File treeview refreshed.")
        except Exception as e:
            logger.exception(p3u.exc_err_msg(e))
            raise
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