# ---------------------------------------------------------------------------- +
#region bdm_workbook_tree_node.py module
""" bdm_workbook_tree_node.py implements the class BDMWorkbookTreeNode.
"""
#endregion bdm_workbook_tree_node.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging
from typing import Optional, Union, List
# third-party modules and packages
from treelib import Tree, Node
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from budman_namespace import (VALID_WBT_NODE_TYPES)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)  # create logger for the module
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMWorkbookTreeNode(Node):
    # ------------------------------------------------------------------------ +
    #region BDMWorkbookTreeNode class intrinsics
    # ------------------------------------------------------------------------ +
    #region doc string
    """BDM Workbook Tree Node class.

    Represents a node in the BDM workbook tree structure.
    Inherits from treelib.Node and adds BDM-specific attributes.
    """
    #endregion doc string
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self,
                 node_type: str,
                 tag: str,
                 identifier: Optional[Union[str, int]] = None,
                 data: Optional[dict] = None) -> None:
        """Initialize a BDMWorkbookTreeNode instance.

        Args:
            node_type (str): The type of the node (e.g., FI_OBJECT, WF_OBJECT).
            tag (str): The display name of the node.
            identifier (Optional[Union[str, int]]): Unique identifier for the node.
            data (Optional[dict]): Additional data associated with the node.
        """
        super().__init__(tag=tag, identifier=identifier, data=data)
        # Additional initialization can be added here if needed
        self._node_type: str = node_type
        self._name:str = tag
        self._index: int = -1
    #endregion    __init__() method
    # ------------------------------------------------------------------------ +
    #region    Class Properties
    @property
    def node_type(self) -> str:
        """Get the type of the node."""
        return self._node_type
    @node_type.setter
    def node_type(self, value: str) -> None:
        """Set the type of the node."""
        self._node_type = value

    @property
    def name(self) -> str:
        """Get the name of the node."""
        return self._name
    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the node."""
        self._name = value

    @property
    def index(self) -> int:
        """Get the index of the node."""
        return self._index
    @index.setter
    def index(self, value: int) -> None:
        """Set the index of the node."""
        self._index = value
    #endregion Class Properties
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbookTreeNode class intrinsics
    # ------------------------------------------------------------------------ +



