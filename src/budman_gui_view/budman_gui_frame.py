# ---------------------------------------------------------------------------- +
#region budman_gui_frame.py module
""" budman_gui_frame.py implements the class BudManGuiFrame.
"""
#endregion budman_gui_app.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging
from typing import Optional, Union, List
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
                              FILE_TREE_NODE_WF_PURPOSE, P2, P4, P6)
from budman_data_context import BudManAppDataContext_Binding
import budman_command_processor as cp
from .budman_gui_style_registry import StyleRegistry
from .budman_gui_msg import BudManGUIMsg
from .budman_gui_constants import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(BMG_WINDOW_TITLE)  # create logger for the module
budman_msg = BudManGUIMsg()  # Singleton instance of BudManGuiMsg
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
        BudManGUIFrame(ttk.Frame) 4x5 grid
            4 rows, 5 columns
            Row 0: Filepath label, entry
            Row 1: Button frame with Save, Load, Quit buttons
            Row 2: dc_info_frame(ttk.Frame) 3x4 grid
            Row 3: Paned window with workbook treeview and text area. This
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
        # Application attributes
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
        self._dc_FI_KEY = tk.StringVar(self,value="")  # DataContext FI_KEY
        self._dc_workflow = tk.StringVar(self,value="")  # DataContext workflow
        self._dc_purpose = tk.StringVar(self,value="")  # DataContext purpose
        self._dc_workbook = tk.StringVar(self,value="")  # DataContext workbook
        self._dc_WF_FOLDER = tk.StringVar(self,value="")  # DataContext WF_FOLDER
        self._dc_WB_TYPE = tk.StringVar(self,value="")  # DataContext WB_TYPE

        # tkinter configuration
        self.parent = parent   # reference to the root window
        self.style_registry = style_registry  # reference to the style registry
        # widgets
        self.bdm_store_url_label: ttk.Label = None
        self.bdm_store_url_entry: tk.Entry = None
        self.budman_cmd_button_frame: ttk.Frame = None
        self.save_button : tk.Button = None
        self.load_button : tk.Button = None
        self.quit_button: tk.Button = None
        self.dc_info_frame: ttk.Frame = None
        self.dc_FI_KEY_label: ttk.Label = None
        self.dc_FI_KEY_value: ttk.Label = None
        self.dc_workflow_label: ttk.Label = None
        self.dc_workflow_value: ttk.Label = None
        self.dc_purpose_label: ttk.Label = None
        self.dc_purpose_value: ttk.Label = None
        self.dc_workbook_label: ttk.Label = None
        self.dc_workbook_value: ttk.Label = None
        self.dc_WF_FOLDER_label: ttk.Label = None
        self.dc_WF_FOLDER_value: ttk.Label = None
        self.dc_WB_TYPE_label: ttk.Label = None
        self.dc_WB_TYPE_value: ttk.Label = None
        self.paned_window_frame: ttk.Frame = None
        self.paned_window: ttk.Panedwindow = None
        self.tree_notebook_frame: ttk.Frame = None
        self.tree_notebook: ttk.Notebook = None
        self.workbook_treeview_frame: ttk.Frame = None
        self.workbook_treeview: ttk.Treeview = None
        self.file_treeview_frame: ttk.Frame = None
        self.file_treeview: ttk.Treeview = None
        self.text_frame : tk.Frame = None
        self.msg_area: scrolledtext.ScrolledText = None
        self.treeview_context_menu: tk.Menu = None

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
    def file_tree(self) -> Optional[Tree]:
        """Get the file_tree property."""
        return self._file_tree
    @file_tree.setter
    def file_tree(self, file_tree: Optional[Tree]) -> None:
        """Set the file_tree property."""
        if not isinstance(file_tree, (Tree, type(None))):
            raise TypeError("file_tree must be a Tree or None.")
        self._file_tree = file_tree

    @property
    def dc_FI_KEY(self) -> str:
        """Get the dc_FI_KEY property."""
        return self._dc_FI_KEY.get()
    @dc_FI_KEY.setter
    def dc_FI_KEY(self, value: str) -> None:
        """Set the dc_FI_KEY property."""
        self._dc_FI_KEY.set(value)

    @property
    def dc_workflow(self) -> str:
        """Get the dc_workflow property."""
        return self._dc_workflow.get()
    @dc_workflow.setter
    def dc_workflow(self, value: str) -> None:
        """Set the dc_workflow property."""
        self._dc_workflow.set(value)

    @property
    def dc_purpose(self) -> str:
        """Get the dc_purpose property."""
        return self._dc_purpose.get()
    @dc_purpose.setter
    def dc_purpose(self, value: str) -> None:
        """Set the dc_purpose property."""
        self._dc_purpose.set(value)

    @property
    def dc_workbook(self) -> str:
        """Get the dc_workbook property."""
        return self._dc_workbook.get()
    @dc_workbook.setter
    def dc_workbook(self, value: str) -> None:
        """Set the dc_workbook property."""
        self._dc_workbook.set(value)

    @property
    def dc_WF_FOLDER(self) -> str:
        """Get the dc_WF_FOLDER property."""
        return self._dc_WF_FOLDER.get()
    @dc_WF_FOLDER.setter
    def dc_WF_FOLDER(self, value: str) -> None:
        """Set the dc_WF_FOLDER property."""
        self._dc_WF_FOLDER.set(value)

    @property
    def dc_WB_TYPE(self) -> str:
        """Get the dc_WB_TYPE property."""
        return self._dc_WB_TYPE.get()
    @dc_WB_TYPE.setter
    def dc_WB_TYPE(self, value: str) -> None:
        """Set the dc_WB_TYPE property."""
        self._dc_WB_TYPE.set(value)
    #endregion BudManGUIFrame properties
    #--------------------------------------------------------------------------+
    #endregion BudManGUIFrame class intrinsics
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame class methods
    def initialize(self) -> None:
        """Initialize the BudManGUIView class."""
        try:
            # Initialize the dc_info_frame values from the data context
            if not self.dc_binding:
                self.dc_FI_KEY = BMG_UNINITIALIZED
                self.dc_workflow = BMG_UNINITIALIZED
                self.dc_purpose = BMG_UNINITIALIZED
                self.dc_WF_FOLDER = BMG_UNINITIALIZED
                self.dc_WB_TYPE = BMG_UNINITIALIZED
                self.dc_workbook = BMG_UNINITIALIZED
                return

            self.dc_FI_KEY = self.DC.dc_FI_KEY
            self.dc_workflow = self.DC.dc_WF_KEY
            self.dc_purpose = self.DC.dc_WF_PURPOSE
            if self.DC.dc_WORKBOOK is not None:
                self.dc_WF_FOLDER = self.DC.dc_WORKBOOK.wf_folder
                self.dc_WB_TYPE = self.DC.dc_WB_TYPE
                self.dc_workbook = self.DC.dc_WB_NAME
            else:
                self.dc_WF_FOLDER = BMG_UNBOUND_WORKBOOK
                self.dc_WB_TYPE = BMG_UNBOUND_WORKBOOK
                self.dc_workbook = BMG_UNBOUND_WORKBOOK
            # Initialize values for the file tree here
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
        '''Create and configure the BudManGUIFrame widgets with minimal 
        configuration, including style and grid configuration.'''

        # Configure the BudManGUIFrame settings, grid, and style.
        # 4 rows by 5 columns.
        self.columnconfigure(0, minsize=100)
        self.columnconfigure((1,2,3), weight=1)
        self.columnconfigure(4, minsize=50)
        self.rowconfigure((0,1,2), weight=0)
        self.rowconfigure(3, weight=1)
        self.configure(style='BMG.TFrame') # set style for the frame

        # Construct and configure the widgets
        # bdm_store_url label and entry, children of the BudManGUIFrame.
        self.bdm_store_url_label = ttk.Label(self, text="BDM Store URL:")
        self.bdm_store_url_label.configure(style='BMG.TLabel') # set style for label
        self.bdm_store_url_entry = ttk.Entry(self, textvariable=self._filepath_value) #,font=entry_font) 
        self.bdm_store_url_entry.configure(style='BMG.TEntry')  # set style for entry

        # Command button frame as child of the BudManGUIFrame.
        # Has child button widgets for Save, Load, and Quit.
        self.budman_cmd_button_frame = ttk.Frame(self)
        self.budman_cmd_button_frame.configure(style='BMG.TFrame')  # set style for button frame
        self.save_button = ttk.Button(self.budman_cmd_button_frame,text="Save")
        self.save_button.configure(style='BMG.TButton')  # set style for button
        self.load_button = ttk.Button(self.budman_cmd_button_frame,text="Load")
        self.load_button.configure(style='BMG.TButton')  # set style for button 
        self.quit_button = ttk.Button(self.budman_cmd_button_frame,text="Quit")
        self.quit_button.configure(style='BMG.TButton')  # set style for button

        # dc_info_frame as child of BudMangGUIFrame.
        self.dc_info_frame = self.create_dc_info_frame(self)

        # create the paned_window_frame
        self.paned_window_frame = self.create_paned_window_frame(self)  

        # Create the tree_notebook_frame and child widgets
        self.tree_notebook_frame = self.create_tree_notebook_frame(self.paned_window)
        # Text frame and area
        self.text_frame = self.create_text_frame(self.paned_window)

        # Create file treeview frame and widget
        self.file_treeview_frame = self.create_file_treeview_frame(self.tree_notebook)
        # Create workbook treeview frame and widget
        self.workbook_treeview_frame = self.create_workbook_treeview_frame(self.tree_notebook)
        # Create treeview_context_menu
        self.treeview_context_menu = tk.Menu(self, tearoff=0)
        self.treeview_context_menu.add_command(label="workflow categorize", 
                                      command=self.on_workflow_categorize)
        self.treeview_context_menu.add_command(label="workflow transfer file", 
                                      command=self.on_workflow_transfer_file)

    def create_dc_info_frame(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Frame:
        """Create the dc_info_frame widget."""
        dc_info_frame = ttk.Frame(parent)
        # 3 rows x 4 columns
        dc_info_frame.rowconfigure((0,1,2), weight=1, uniform="b")
        dc_info_frame.columnconfigure((0,2), weight=0)
        dc_info_frame.columnconfigure((1,3), weight=0)
        dc_info_frame.configure(style='BMG.TFrame')  # set style for dc_info_frame
        # dc_info_frame widgets
        self.dc_FI_KEY_label = ttk.Label(dc_info_frame, text="FI_KEY:")
        self.dc_FI_KEY_label.configure(style='BMG.TLabel')  # set style for label
        self.dc_FI_KEY_value = ttk.Label(dc_info_frame, text="",
                                         textvariable=self._dc_FI_KEY)
        self.dc_FI_KEY_value.configure(style='BMG.Value.TLabel')  # set style for value label
        self.dc_workflow_label = ttk.Label( dc_info_frame, text="Workflow:")
        self.dc_workflow_label.configure(style='BMG.TLabel')  # set style for label
        self.dc_workflow_value = ttk.Label(dc_info_frame, text="",
                                            textvariable=self._dc_workflow)
        self.dc_workflow_value.configure(style='BMG.Value.TLabel')  # set style for value label
        self.dc_purpose_label = ttk.Label(dc_info_frame, text="Purpose:")
        self.dc_purpose_label.configure(style='BMG.TLabel')  # set style for label
        self.dc_purpose_value = ttk.Label(dc_info_frame, text="",
                                                    textvariable=self._dc_purpose)
        self.dc_purpose_value.configure(style='BMG.Value.TLabel')  # set style for value label
        self.dc_workbook_label = ttk.Label(dc_info_frame, text="Workbook:")
        self.dc_workbook_label.configure(style='BMG.TLabel')  # set style for label
        self.dc_workbook_value = ttk.Label(dc_info_frame, text="",
                                            textvariable=self._dc_workbook)
        self.dc_workbook_value.configure(style='BMG.Value.TLabel')  # set style for value label
        self.dc_WF_FOLDER_label = ttk.Label(dc_info_frame, text="WF Folder:")
        self.dc_WF_FOLDER_label.configure(style='BMG.TLabel')  # set style for label
        self.dc_WF_FOLDER_value = ttk.Label(dc_info_frame, text="",
                                             textvariable=self._dc_WF_FOLDER)
        self.dc_WF_FOLDER_value.configure(style='BMG.Value.TLabel')  # set style for value label
        self.dc_WB_TYPE_label = ttk.Label(dc_info_frame, text="WB Type:")
        self.dc_WB_TYPE_label.configure(style='BMG.TLabel')  # set style for label
        self.dc_WB_TYPE_value = ttk.Label(dc_info_frame, text="",
                                           textvariable=self._dc_WB_TYPE)
        self.dc_WB_TYPE_value.configure(style='BMG.Value.TLabel')  # set style for value label
        return dc_info_frame

    def create_paned_window_frame(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Frame:
        """Create the paned_window_frame widget along with its child widgets."""
        paned_window_frame = ttk.Frame(parent)
        paned_window_frame.configure(style='BMG.TFrame')  # set style for frame
        paned_window_frame.rowconfigure(0, weight=1)
        paned_window_frame.columnconfigure(0, weight=1)
        self.paned_window = ttk.Panedwindow(paned_window_frame, orient=tk.VERTICAL)
        self.paned_window.configure(style='BMG.TPanedwindow')  # set style
        return paned_window_frame

    def create_tree_notebook_frame(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Frame:
        """Create the tree_notebook_frame widget."""
        tree_notebook_frame = ttk.Frame(parent)
        tree_notebook_frame.configure(style='BMG.TFrame')  # set style for frame
        tree_notebook_frame.rowconfigure(0, weight=1)
        tree_notebook_frame.columnconfigure(0, weight=1)
        # Create the workbook_treeview_frame.
        self.tree_notebook = self.create_tree_notebook(tree_notebook_frame)
        self.paned_window.add(tree_notebook_frame, weight=2) # Pos 1
        return tree_notebook_frame

    def create_tree_notebook(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Notebook:    
        """Create the tree_notebook widget."""
        tree_notebook = ttk.Notebook(parent)
        tree_notebook.configure(style='BMG.TNotebook')  # set style for frame
        return tree_notebook
    
    def create_workbook_treeview_frame(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Frame:
        """Create the workbook_treeview_frame widget with its child widgets."""
        workbook_treeview_frame = ttk.Frame(parent)
        # 1x1 grid
        workbook_treeview_frame.rowconfigure(0, weight=1)
        workbook_treeview_frame.columnconfigure(0, weight=1)
        workbook_treeview_frame.configure(style='BMG.TFrame')  # set style for frame
        self.workbook_treeview = self.create_workbook_treeview(workbook_treeview_frame)
        self.tree_notebook.add(workbook_treeview_frame, text=BMG_TREEVIEW_WORKBOOKS_TAB_LABEL) # Pos 1
        return workbook_treeview_frame
    
    def create_workbook_treeview(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Treeview:
        """Create a workbook treeview widget."""
        try:
            workbook_treeview = ttk.Treeview(parent, 
                                    columns=(FILE_TREE_NODE_TYPE_KEY,
                                             FILE_TREE_NODE_WF_KEY, 
                                             FILE_TREE_NODE_WF_PURPOSE), 
                                    show='tree headings')
            workbook_treeview.configure(style='BMG.Treeview')
            # workbook_treeview config: headings and columns
            workbook_treeview.heading('#0', text='Index:Name', anchor='w')
            workbook_treeview.column('#0', anchor='w', width=200)
            workbook_treeview.heading(FILE_TREE_NODE_TYPE_KEY, text='Type', anchor='w')
            workbook_treeview.column(FILE_TREE_NODE_TYPE_KEY, anchor='w', width=40)
            workbook_treeview.heading(FILE_TREE_NODE_WF_KEY, text='Workflow', anchor='w')
            workbook_treeview.column(FILE_TREE_NODE_WF_KEY, anchor='w', width=80)
            workbook_treeview.heading(FILE_TREE_NODE_WF_PURPOSE, text='Purpose', anchor='w')
            workbook_treeview.column(FILE_TREE_NODE_WF_PURPOSE, anchor='w', width=80)
            return workbook_treeview
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def create_file_treeview_frame(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Frame:
        """Create the file_treeview_frame widget with its child widgets."""
        file_treeview_frame = ttk.Frame(parent)
        # 1x1 grid
        file_treeview_frame.rowconfigure(0, weight=1)
        file_treeview_frame.columnconfigure(0, weight=1)
        file_treeview_frame.configure(style='BMG.TFrame')  # set style for frame
        self.file_treeview = self.create_file_treeview(file_treeview_frame)
        self.tree_notebook.add(file_treeview_frame, text=BMG_TREEVIEW_FILES_TAB_LABEL) # Pos 1
        return file_treeview_frame

    def create_file_treeview(self, parent:Union[tk.Widget, ttk.Widget]) -> ttk.Treeview:
        """Create a file treeview widget."""
        try:
            file_treeview = ttk.Treeview(parent, 
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

    def create_text_frame(self, parent:Union[tk.Widget, ttk.Widget]) -> tk.Frame:
        """Create a text frame widget."""
        try:
            text_frame = ttk.Frame(parent)
            text_frame.rowconfigure(0, weight=1)
            text_frame.columnconfigure(0, weight=1)
            text_frame.configure(style='BMG.TFrame')
            self.msg_area = self.create_msg_area_widget(text_frame)
            self.paned_window.add(text_frame, weight=3) # Pos 2
            return text_frame
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def create_msg_area_widget(self,parent:Union[tk.Widget,ttk.Widget]) -> scrolledtext.ScrolledText:
        """Create a scrolled text area widget."""
        try:
            msg_area = scrolledtext.ScrolledText(parent,wrap=tk.WORD, 
                                                  width=40, height=10)
            msg_area.configure(bg=BMG_FAINT_GRAY, fg=BMG_DARK_TEXT,
                                font=BMG_BASIC_FIXED_FONT)
            self.style_registry.configure_tags_text(msg_area)
            return msg_area
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def layout_BudManGUIFrame_widgets(self):
        '''Configure the BudManGUIFrame child widgets layout grid configuration'''
        # The BudManGUIFrame should expand to fill the root window
        # self.configure(style='BMG.TFrame') # set style for the frame

        # Layout the widgets in the grid
        # row 0: filepath label, entry
        self.bdm_store_url_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.bdm_store_url_entry.grid(row=0, column=1, columnspan=3, sticky="ew")

        # row 1: button frame with save, load, quit buttons
        self.budman_cmd_button_frame.grid(row=1, column=0, columnspan=5, 
                                          sticky="nse", padx=5, pady=5)
        self.quit_button.pack(side="right", padx=5, pady=5)
        self.load_button.pack(side="right", padx=5, pady=5)
        self.save_button.pack(side="right", padx=5, pady=5)

        # row 2: dc_info_frame with labels and values, grow ew only
        self.dc_info_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        self.dc_FI_KEY_label.grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.dc_FI_KEY_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.dc_workflow_label.grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.dc_workflow_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.dc_purpose_label.grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.dc_purpose_value.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.dc_workbook_label.grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.dc_workbook_value.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        self.dc_WF_FOLDER_label.grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.dc_WF_FOLDER_value.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        self.dc_WB_TYPE_label.grid(row=2, column=2, sticky="e", padx=5, pady=2)
        self.dc_WB_TYPE_value.grid(row=2, column=3, sticky="w", padx=5, pady=2)

        # row 3: paned window with workbook treeview and text area.
        self.paned_window_frame.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.paned_window.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        # Layout the two frames in the paned window.
        self.file_treeview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.workbook_treeview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.msg_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def bind_BudManGUIFrame_widgets(self):
        ''' Bind the widgets in the frame to their respective event handlers.
        A set up specific key bindings.'''
        # bind event handlers
        self.quit_button.bind("<Button-1>", self.on_quit_button_clicked) # close the app
        self.save_button.configure(command=self.on_save_button_clicked)
        self.load_button.configure(command=self.on_load_button_clicked)
        # do key bindings
        self.bdm_store_url_entry.bind("<Return>", self.on_filepath_changed)
        self.bdm_store_url_entry.bind("<Tab>", self.on_filepath_changed)
        self.bdm_store_url_entry.bind("<FocusOut>", self.on_filepath_changed)

        # Treeview selection event binding
        self.file_treeview.tag_bind(BMG_FTVOBJECT, "<<TreeviewSelect>>", self.on_file_treeview_select)
        # Right mouse click support
        self.file_treeview.bind("<Button-3>", self.on_right_click)

    #endregion BudManGUIFrame class methods
    #--------------------------------------------------------------------------+

    #--------------------------------------------------------------------------+
    #region BudManGUIFrame event handlers
    #--------------------------------------------------------------------------+
    def on_quit_button_clicked(self, event):
        """ Event handler for when the user clicks the quit button. """
        # bubble up to the parent
        logger.info("BudManGUIWindow.BudManGUIFrame.quit_button clicked. Exiting application.")

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

    def on_file_treeview_select(self, event):
        """ Event handler for when the user selects an item in the file treeview. """
        count = len(self.file_treeview.selection())
        if count == 0:
            return
        budman_msg.output(f"File treeview selection changed. {count} item(s) selected.", BMG_DEBUG)
        selected_items = self.file_treeview.selection()
        for item in selected_items:
            item_text = self.file_treeview.item(item, "text")
            budman_msg.output(f"{P2}Selected item: {item_text} (ID: {item})", BMG_DEBUG)
    
    def on_right_click(self, event):
        """ Event handler for right mouse click on the file treeview. """
        selected_items: List[str] = []
        # Identify the item clicked on
        clicked_item_id = self.file_treeview.identify_row(event.y)
        if not clicked_item_id:
            # Nothin right clicked on the treeview
            return
        self.file_treeview.selection_add(clicked_item_id)
        selected_count = len(self.file_treeview.selection())
        budman_msg.output(f"Right-click. {selected_count} item(s) are selected.", BMG_DEBUG)
        selected_items = self.file_treeview.selection()
        for item in selected_items:
            item_text = self.file_treeview.item(item, "text")
            budman_msg.output(f"{P2}Selected item: {item_text} (ID: {item})", BMG_DEBUG)
        self.treeview_context_menu.post(event.x_root, event.y_root)

    def on_workflow_categorize(self):
        """ Event handler for workflow categorize context menu item. """
        budman_msg.output("Workflow categorize context menu item selected.", BMG_DEBUG)

    def on_workflow_transfer_file(self):
        """ Event handler for workflow transfer file context menu item. """
        budman_msg.output("Workflow transfer file context menu item selected.", BMG_DEBUG)
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
                self.paned_window.forget(1) # Treeview is at pos 1
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
                    item_type = "unknown"
                    workflow_value = "unknown"
                    purpose_value = "unknown"
                    if self.dc_binding:
                        item_info = self.dc_FILE_TREE_node_info(file_tree_node)
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
    #endregion BudManGUIFrame support methods
#------------------------------------------------------------------------------+