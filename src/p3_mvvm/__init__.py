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
from .data_context_binding import (
    DataContext_Binding
)
from .data_context_base_ABC import (
    DataContext_Base
)
from .data_context import (
    DataContext
)
from .command_processor_Binding import (
    CommandProcessor_Binding
)
from .command_processor_Base_ABC import (
    CommandProcessor_Base
)
from .command_processor import (
    CommandProcessor
)
# target for 'from budman_app import *'
__all__ = [
    "Model_Binding",
    "Model_Base",
    "DataContext_Binding",
    "DataContext_Base",
    "DataContext",
    "CommandProcessor_Binding",
    "CommandProcessor_Base",
    "CommandProcessor"
]

