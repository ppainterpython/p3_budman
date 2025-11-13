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
                             background=BMG_FAINT_GRAY)
        self.style.configure('BMG.TLabel', 
                             background=BMG_FAINT_GRAY, 
                             font=font_style_bold)
        self.style.configure('BMG.TEntry', 
                             background=BMG_ENTRY_BACKGROUND_ACTIVE, 
                             font=font_style)
        self.style.configure('BMG.TButton', 
                             font=font_style_bold,
                             relief="raised",
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