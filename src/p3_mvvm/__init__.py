"""
p3_MVVM - a simple MVVM framework for Python.

MVVM - Model-View-ViewModelA - is a design pattern framework for a
software application.
"""
__version__ = "0.1.0"
__author__ = "Paul Painter"
__copyright__ = "2025 Paul Painter"
__name__ = "p3_mvvm"
__description__ = "p3_MVVM - a simple MVVM framework for Python."
__license__ = "MIT"

from .model_binding_ABC import (
    Model_Binding
)
from .model_base_ABC import (
    Model_Base
)
# target for 'from budman_app import *'
__all__ = [
    "Model_Binding",
    "Model_Base"
]

