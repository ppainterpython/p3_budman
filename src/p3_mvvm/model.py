# ---------------------------------------------------------------------------- +
#region model.py module
""" Model class concrete implementation of a basic p3_mvvm model. 

    This module implements the CommandProcessor class, which is a concrete
    implementation of the CommandProcessor_Base abstract base class. It provides
    the necessary methods and properties to process commands in a p3_mvvm
    application.

    The CommandProcessor class is designed to be subclassed by applications to
    enable application-specific capability. With the p3_mvvm design pattern,
    access to a DataContext is a basic provision, either through inheritance or 
    binding.

    A critical aspect of the CommandProcessor is the CMD_OBJECT. Here, a 
    dictionary is used to contain the key attributes of a p3_mvvm command. A
    valid CMD_OBJECT may have a variable number of attributes, based on the
    need of the command. But, there are some required attributes and several
    common attributes which may be in any valid CMD_OBJECT. Constants are
    defined for these attribute keys and values, as appropriate. Note, these
    are the basic requirements used in the Command Processor for functional
    operation and are not specific to any application.

    Required CMD_OBJECT Attributes:
    - 'cmd_name': "name string"  The unique name of the command.
    - 'cmd_key': "key string"    A unique key for the command, derived from the
        command name by appending the CMD_KEY_SUFFIX, e.g., "_cmd".
    - 'cmd_exec_func': Callable  A callable function to execute the command.
        Constants:
            CMD_KEY_SUFFIX = "_cmd"
            CK_CMD_NAME = "cmd_name"
            CK_CMD_KEY = "cmd_key"
            CK_CMD_EXEC_FUNC = "cmd_exec_func"
        Notes: A cmd_key is constructed by appending the CMD_KEY_SUFFIX to
        the cmd_name. For example: cmd_name = 'list' has cmd_key = 'list_cmd'.

    Optional common CMD_OBJECT Attributes:
    - 'subcmd_name': "name string"  The name of a sub-command, if applicable.
    - 'subcmd_key': "key string"    A unique key for the sub-command, derived from
        the sub-command name by appending the CMD_KEY_SUFFIX, e.g., "_cmd".
        Constants:
            CK_SUBCMD_NAME = "subcmd_name"
            CK_SUBCMD_KEY = "subcmd_key"
        Notes: A subcmd_key is constructed by appending the CMD_KEY with
        underscore '_' and the subcmd_name. For example: cmd_key = 'list_cmd'
        and subcmd_name = 'workbooks' results in 
        subcmd_key = 'list_cmd_workbooks'.
    - 'cmd_exec_func': Callable  A callable function to execute the sub-command.

    Command_Processor provides a general purpost CMD_RESULT dictionary returned
    by a command or sub-command EXEC_FUNC. The CMD_RESULT dictionary
    contains the following keys:
    - 'cmd_result_status': bool  The status of the command execution, True if
        successful, False if an error occurred.
    - 'cmd_result_content_type': str A symbol reflecting the type of the result
      returned by the command. This will be application function specific for
      each command implemented.
    - 'cmd_result_content': Any  The content returned by the command execution. 
      If cmd_result_success is True, this can be any type of object. If False,
      this is typically a string error message.

    Command_Processor supports builtin parameter flags which can be added to any
    cmd string or possibly set as flags affecting all cmds.
    - parse_only: bool - If True, the command will only be parsed, the resulting
    attributes are displayed, but the cmd is not executed. WHen parse_only 
    is used, the cp_execute_cmd() method will construct a CMD_RESULT_TYPE object
    with a simple string out showing the content of the CMD_OBJECT_TYPE object
    and return it prior to any other actions in the Command_Processor
    pipeline interface.
    - validate_only : bool - If True, the command will be fully validated, but 
    not executed. The cmd parameters with possible validation messages is 
    displayed. Command_Processor pipeline stops after calling the 
    cp_validate_cmd_object() method in the Command_Processor pipeline interface.
    - what_if : bool - If True, the command will be executed in a "what if"
    mode, where the effects of the command are simulated but not applied. Output
    about possible impact of the cmd is displayed. Not supported by all cmds.

    Command_Processor includes optional support for building CMD_OBJECTs from
    command lines parsed by cmd2, arparse for convenience.
"""
#endregion command_processor.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import logging
from typing import List, Type, Union, Dict, Tuple, Any, Callable, Optional
# third-party modules and packages
import p3_utils as p3u, pyjson5, p3logging as p3l
# local modules and packages
import budman_namespace.design_language_namespace as bdm
from .mvvm_namespace import *
from .model_base_ABC import Model_Base
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals
# ---------------------------------------------------------------------------- +
#region    Model class
class Model(Model_Base):
    # ------------------------------------------------------------------------ +
    #region    Model class instrisics - override for app-specific
    # ------------------------------------------------------------------------ +
    #region Model class doc string
    """Concrete Class for Model_Base."""
    #endregion CommandProcessor class doc string
    # ------------------------------------------------------------------------ +
    #region __init__() constructor method
    def __init__(self) -> None:
        self._model_id = __class__.__name__ + "-" + p3u.gen_unique_hex_id()
    #endregion __init__() constructor method
    # ------------------------------------------------------------------------ +
    #endregion Model class instrisics 
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region    Model_Base Properties
    @property
    def model_id(self) -> str:
        """Return the model ID."""
        return self._model_id

    #endregion Model_Base Properties

# ---------------------------------------------------------------------------- +
#endregion Model class
# ---------------------------------------------------------------------------- +