#-----------------------------------------------------------------------------+
import logging
from ttkbootstrap import Style
# from ttkbootstrap.constants import *
from .budman_gui_constants import *

class StyleRegistry:
    """ Style Manager for BudMan GUI Application.
        The StyleManager class manages the styles for the BudMan GUI application
        using ttkbootstrap styles.
    """
    #region StyleManager class
    #--------------------------------------------------------------------------+
    # Public Property attributes

    # Class constructor
    def __init__(self, themename="cosmo"):
        self.style = Style(theme=themename)
        self._define_styles()

    def _define_styles(self):
        """Define the styles for the BudMan GUI application."""
        font_style = BMG_BASIC_FIXED_FONT
        font_style_bold = BMG_BASIC_FIXED_FONT_BOLD
        self.style.configure('BMG.TFrame', 
                             background=BMG_FAINT_GRAY,
                             padding=(BMG_TFRAME_PADDING,
                                      BMG_TFRAME_PADDING,
                                      BMG_TFRAME_PADDING,
                                      BMG_TFRAME_PADDING),
                             relief="solid",
                             bordercolor='red',
                             borderwidth=3)
        self.style.configure('BMG.TNotebook', 
                             background=BMG_FAINT_GRAY,
                             padding=(BMG_TNOTEBOOK_PADDING,
                                      BMG_TNOTEBOOK_PADDING,
                                      BMG_TNOTEBOOK_PADDING,
                                      BMG_TNOTEBOOK_PADDING),
                             relief="solid",
                             bordercolor='blue',
                             borderwidth=3)
        self.style.configure('BMG.TLabel', 
                             background=BMG_FAINT_GRAY, 
                             padding=(2,2,2,2),
                             relief="flat",
                             borderwidth=3,
                             font=font_style_bold)
        self.style.configure('BMG.Value.TLabel', 
                             background=BMG_FAINT_GRAY, 
                             foreground=BMG_TEXT_VALUE_COLOR,
                             padding=(2,2,2,2),
                             relief="flat",
                             borderwidth=3,
                             font=font_style)
        self.style.configure('BMG.TEntry', 
                             background=BMG_ENTRY_BACKGROUND_ACTIVE, 
                             foreground=BMG_TEXT_VALUE_COLOR,
                             padding=(2,2,2,2),
                             relief="sunken",
                             font=font_style)
        self.style.configure('BMG.TButton', 
                             font=font_style_bold,
                             padding=(2,2,2,2),
                             width=10)
        self.style.map("BMG.TButton",
                       foreground=[('disabled', BMG_BUTTON_FOREGROUND_DISABLED)],
                       background=[('disabled', BMG_BUTTON_BACKGROUND_DISABLED)],
                       relief=[('pressed', 'sunken'), ('!pressed', 'raised'),
                               ('disabled', 'raised')]
            )
        self.style.configure('BMG.TCheckbutton', background=BMG_FAINT_GRAY, font=font_style)
        self.style.configure('BMG.TPanedwindow', background=BMG_FAINT_GRAY)
        self.style.configure('BMG.Treeview', background=BMG_FAINT_GRAY,
                             font=font_style, rowheight=30)
        self.style.configure("BMG.Treeview.Heading", font=BMG_BASIC_FIXED_FONT_BOLD)
        self.style.configure("BMG.Horizontal.TProgressbar", length=150, borderwidth=2,
                             troughcolor=BMG_LIGHT_GRAY)

    def configure_tags_text(self, widget):
        """Configure the tags for a scrolled text widget."""
        widget.tag_configure(BMG_INFO, foreground=BMG_DARK_TEXT)
        widget.tag_configure(BMG_DEBUG, foreground="blue")
        widget.tag_configure(BMG_WARNING, foreground="orange")
        widget.tag_configure(BMG_ERROR, foreground="red")
        widget.tag_configure(BMG_CRITICAL, foreground="red", underline=1)

    def get_style(self) -> Style:
        """Get the ttk.Style object for the BudMan GUI application."""
        return self.style