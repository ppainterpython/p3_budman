# ---------------------------------------------------------------------------- +
#region budman_gui_app.py module
""" budman_gui_app.py implements the class BudManGuiApp.

"""
#endregion budman_gui_app.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import cmd
import logging, os, getpass, time, copy
from typing import List, Optional, Type, Generator, Dict, Tuple, Any, TYPE_CHECKING
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
import budman_command_processor as cp
from .budman_gui_window  import BudManGUIWindow

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BudManGUIApp:
    """ Budget Manager GUI Application class.
        The BudManGuiApp class sets up and runs the BudManGuiView.
    """
    #region BudManGuiApp class
    #--------------------------------------------------------------------------+
    # Public Property attributes
    app_name: str = "P3 Budget Manager GUI Application"

    # Class constructor
    def __init__(self):
        bmv: BudManGUIWindow = None
        logger.info(f"Initializing BudMan GUI Application")

        # Create the BudManView for a UX
        self.bmv = BudManGUIWindow()
        logger.debug(f"BudManView created")

    def run(self) -> p3m.CMD_RESULT_TYPE:
        """Run the BudManView application loop"""
        self.bmv.mainloop()
        cmd_result: p3m.CMD_RESULT_TYPE = p3m.create_CMD_RESULT_OBJECT(
            cmd_result_status=True,
            result_content_type=p3m.CMD_STRING_OUTPUT,
            result_content=f"BudManGuiApp run completed.",
            cmd_object=None
        )
        logger.debug(f"Finished BudManGuiApp.run()") # pragma: no cover
        return cmd_result
    #--------------------------------------------------------------------------+
    # Property attributes

    #--------------------------------------------------------------------------+
    # Event Handler Methods