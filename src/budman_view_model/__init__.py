"""
Budget Manager Data Context Interface Package

"""
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_view_model"
__description__ = "Budget Manager View Model."
__license__ = "MIT"

# Budget Model Domain Working Data
from .budman_view_model import (
    BudManViewModel
)
from .budman_cli_view_datacontext import (
    BudManCLIViewDataContext
)
__all__ = [
    "BudManViewModel",
    "BudManCLIViewDataContext"
]
