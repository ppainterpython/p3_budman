"""
Budget Manager Data Context Interface Package

"""
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "budman_view_model"
__description__ = "Budget Manager View Model."
__license__ = "MIT"

# Budget Model Domain Working Data
from .budman_cli_parser import (
    BudManCLIParser
)
from .budman_cli_view import (
    BudManCLIView
)
__all__ = [
    "BudManCLIParser",
    "BudManCLIView"
]
