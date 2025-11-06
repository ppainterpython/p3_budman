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
        font_style = ('Segoe UI', 12)
        font_style_bold = ('Segoe UI', 12, 'bold')
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
                             font=font_style, rowheight=25)
        self.style.configure("BMG.Treeview.Heading", font=('Segoe UI', 12, 'bold'))

    def get_style(self) -> Style:
        """Get the ttk.Style object for the BudMan GUI application."""
        return self.style