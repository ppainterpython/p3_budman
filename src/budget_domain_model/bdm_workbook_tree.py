# ---------------------------------------------------------------------------- +
#region bdm_workbook_tree.py module
""" bdm_workbook_tree.py implements the class BDMWorkbookTree.
"""
#endregion bdm_workbook_tree.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging
from typing import Optional, Union, List
# third-party modules and packages
from treelib import Tree, Node
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
# local modules and packages
from budman_namespace import (VALID_WBT_NODE_TYPES, BDM)
from .bdm_workbook_tree_node import BDMWorkbookTreeNode
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)  # create logger for the module
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
class BDMWorkbookTree(Tree):
    # ------------------------------------------------------------------------ +
    #region BDMWorkbookTree class intrinsics
    # ------------------------------------------------------------------------ +
    #region doc string
    """BDM Workbook Tree class.

    Represents the BDM workbook tree structure.
    Inherits from treelib.Tree and manages BDM-specific nodes.
    """
    #endregion doc string
    # ------------------------------------------------------------------------ +
    #region    __init__() method
    def __init__(self) -> None:
        """Initialize a BDMWorkbookTree instance.
        """
        super().__init__()
        self._root_node_id: str = None
    #endregion    __init__() method
    # ------------------------------------------------------------------------ +
    #region    Class Properties
    @property
    def root_node_id(self) -> Optional[str]:
        """Get the root node identifier."""
        return self._root_node_id
    #endregion   Class Properties
    # ------------------------------------------------------------------------ +
    #endregion BDMWorkbookTree class intrinsics
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region    BDMWorkbookTree class methods
    def add_tree_node(self,
                 node_type: str,
                 tag: str,
                 identifier: Optional[Union[str, int]] = None,
                 data: Optional[dict] = None,
                 parent_id: Optional[str] = None) -> BDMWorkbookTreeNode:
        """Add a BDMWorkbookTreeNode to the tree.

        Args:
            node_type (str): The type of the node (e.g., FI_OBJECT, WF_OBJECT).
            tag (str): The display name of the node.
            identifier (Optional[Union[str, int]]): Unique identifier for the node.
            data (Optional[dict]): Additional data associated with the node.

        Returns:
            BDMWorkbookTreeNode: The added node.
        """

        # Validate node_type
        if node_type not in VALID_WBT_NODE_TYPES:
            m = f"Invalid node_type '{node_type}'. Must be one of {VALID_WBT_NODE_TYPES}."
            logger.error(m)
            raise ValueError(m)
        # Check if the node already exists
        this_node: Node = self.get_node(identifier) if identifier else None
        if this_node is not None:
            logger.debug(f"Node with identifier '{identifier}' already exists. Skipping add.")
            return this_node  # type: ignore    
        # Create and add the new node
        this_node = BDMWorkbookTreeNode(
            node_type=node_type,
            tag=tag,
            identifier=identifier,
            data=data
        )
        if self.size() == 0:
            if node_type != BDM:
                m = f"root node type must be '{BDM}', not '{node_type}'."
                logger.error(m)
                raise ValueError(m)
            self._root_node_id = identifier
            self.add_node(this_node)  # Add as root node
        else:
            self.add_node(this_node, parent=parent_id)
        return this_node
    #endregion    BDMWorkbookTree class methods
    # ------------------------------------------------------------------------ +