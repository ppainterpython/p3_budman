"""
Budget Manager - p3_budman package

budman_command_processor - the Command Processor pattern for p3_budman.
"""
__version__ = "0.3.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_command_processor"
__description__ = "Command Processor pattern implementation for BudMan."
__license__ = "MIT"

from .budman_cp_namespace import *
from .budman_commands import *

# target for 'from budman_app import *'
__all__ = [
    "BudManApp"
]

