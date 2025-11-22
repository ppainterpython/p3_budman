# ---------------------------------------------------------------------------- +
#region    bdm_workbook_tree.py module
""" Implements BDMWorkbookTree Class.

    The BudMan Data Context uses a "file tree" as a data structure to represent
    wf_folders and workbooks from a budget domain model store (BDM_STORE). 
    BudMan assumes that workbooks are stored in wf_folders, configured for
    a storage system. Folders and workbooks have metadata including a url.

    For Views (CLI, GUI or upstream API clients), a workbook tree is a tree 
    structure based on the Treelib module. This module provides a simple API 
    to create and update a workbook tree for a specified budget domain model 
    passed as an argument.

    Once initialized, the workbook_tree is set in a property. 
"""
#endregion bdm_workbook_tree.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time, toml
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Generator

# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
from treelib import Tree, Node

# local modules and packages
import budman_namespace.design_language_namespace as bdm
from budman_namespace import BDMWorkbook
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region BSMFileTree Class
class BDMWorkbookTree:
    # ======================================================================== +
    #region BudgetDomainModel class intrinsics
    # ======================================================================== +
    #region doc string
    """
    A workbook_tree is a treelib.Tree populated from the BDM. 
    FI_OBJECTs, WF_FOLDER, and BDMWorkbook objects are stored in the 
    node.data attribute of each node and contain additional metadata.

    Arguments
    ----------
    model : BudgetDomainModel - The budget domain model to build the workbook tree from.
    """
    #endregion doc string
    # ------------------------------------------------------------------------ +
    #region __init__()
    def __init__(self, model:object) -> None:
        self._bdm_url: str = ""
        self._id: str = ""
        self._model: object = model
        if self._model is None:
            raise ValueError("BDMWorkbookTree: model cannot be None.")
        if not self.model.bdm_initialized:
            raise ValueError("BDMWorkbookTree: model is not initialized.")
        self._workbook_tree: Tree = model.bdm_workbook_tree if hasattr(model, bdm.BDM_WORKBOOK_TREE) else None
        if self._workbook_tree is None:
            self._workbook_tree = Tree()
        self._bdm_url = self.model.bdm_url
        self._id = self.model.bdm_id
        self.update_workbook_tree()
    #endregion __init__()
    # ------------------------------------------------------------------------ +
    #region class properties
    @property
    def model(self) -> object:
        """Get the BudgetDomainModel."""
        return self._model
    @model.setter
    def model(self, model: object) -> None:
        """Set the BudgetDomainModel."""
        if model is None:
            raise ValueError("BDMWorkbookTree: model cannot be None.")
        self._model = model

    @property
    def workbook_tree(self) -> Tree:
        """Get the workbook_tree."""
        return self._workbook_tree
    @workbook_tree.setter
    def workbook_tree(self, workbook_tree: Tree) -> None:
        """Set the workbook_tree."""
        if workbook_tree is None or not isinstance(workbook_tree, Tree):
            raise ValueError("BDMWorkbookTree: workbook_tree must be a valid Tree object.")
        self._workbook_tree = workbook_tree    

    @property
    def bdm_url(self) -> str:
        """Get the bdm_url."""
        return self._bdm_url
    @property
    def id(self) -> str:
        """Get the id."""
        return self._id
    #endregion class properties
    # ======================================================================== +
    def update_workbook_tree(self) -> None:
        """Update the workbook_tree from the model."""
        try:
            if not self.validate_model_type(self.model):
                return
            self.workbook_tree = self.construct_workbook_tree()
            if self.workbook_tree is None or not isinstance(self.workbook_tree, Tree):
                raise ValueError("workbook_tree is not a valid Tree object.")
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def construct_workbook_tree(self) -> Tree:
        """Update a workbook_tree structure from the model's current content."""
        # Does the tree have nodes yet?
        try:
            root_node_id:str = self.id
            root_node: Node = None
            wb_tree: Tree = self.workbook_tree
            if wb_tree.size() == 0:
                # Root node
                root_node = wb_tree.create_node(tag=F"BDM({self.id})", identifier=root_node_id,data=None)
            else:
                root_node = wb_tree.get_node(root_node_id)
                if root_node is None:
                    raise ValueError(f"Workbook tree root node '{root_node_id}' not found.")
            # Iterate all FIs and the wf_folder configs for each, collect workbooks
            for fi_key, fi_obj in self.model.bdm_fi_collection.items():
                # Each fi_obj needs a node.
                node_data: Dict[str, str] = {}
                fi_node: Node = wb_tree.get_node(fi_key)
                if fi_node is None:
                    # Create the fi_node
                    node_data[bdm.WORKBOOK_TREE_NODE_TYPE_KEY] = bdm.FI_OBJECT
                    node_data[bdm.WORKBOOK_TREE_NODE_FI_KEY] = fi_key
                    fi_node = wb_tree.create_node(tag=f"FI({fi_key})", 
                                                  identifier=fi_key, 
                                                  parent=root_node_id, 
                                                  data=node_data)
                if fi_obj[bdm.FI_WF_FOLDER_CONFIG_COLLECTION] is None:
                    continue
                for wf_key, wfc_list in fi_obj[bdm.FI_WF_FOLDER_CONFIG_COLLECTION].items():
                    # Each wf_key needs a node.
                    wf_key_id = f"{fi_key}::{wf_key}"
                    wf_key_node: Node = wb_tree.get_node(wf_key_id)
                    if wf_key_node is None:
                        node_data = node_data.copy()
                        node_data[bdm.WORKBOOK_TREE_NODE_TYPE_KEY] = bdm.WF_OBJECT
                        node_data[bdm.WORKBOOK_TREE_NODE_FI_KEY] = fi_key
                        node_data[bdm.WORKBOOK_TREE_NODE_WF_KEY] = wf_key
                        wf_key_node = wb_tree.create_node(tag=f"Workflow({wf_key})", 
                                                        identifier=wf_key_id, 
                                                        parent=fi_key, 
                                                        data=node_data)
                    if len(wfc_list) == 0:
                        continue
                    for wfc in wfc_list:
                        # Each wf_purpose:wf_folder needs a node.
                        wf_purpose = wfc.get(bdm.WF_PURPOSE, "")
                        wf_folder = wfc.get(bdm.WF_FOLDER, "")
                        wf_folder_key = f"{wf_key}::{wf_purpose}::{wf_folder}"
                        wf_folder_tag = f"WF_FOLDER({wf_purpose}::{wf_folder})"
                        wf_folder_node = wb_tree.get_node(wf_folder_key)
                        if wf_folder_node is None:
                            node_data = node_data.copy()
                            node_data[bdm.WORKBOOK_TREE_NODE_TYPE_KEY] = bdm.WF_OBJECT
                            node_data[bdm.WORKBOOK_TREE_NODE_FI_KEY] = fi_key
                            node_data[bdm.WORKBOOK_TREE_NODE_WF_KEY] = wf_key
                            node_data[bdm.WORKBOOK_TREE_NODE_WF_FOLDER] = wf_folder_key
                            wf_folder_node = wb_tree.create_node(tag=wf_folder_tag,
                                                                identifier=wf_folder_key,
                                                                parent=wf_key_id,
                                                                data=node_data)
                            if (fi_obj[bdm.FI_WORKBOOK_DATA_COLLECTION] is None or 
                                len(fi_obj[bdm.FI_WORKBOOK_DATA_COLLECTION]) == 0):
                                   continue
                        wb: BDMWorkbook = None
                        for wb_id, wb in fi_obj[bdm.FI_WORKBOOK_DATA_COLLECTION].items():
                            if (wb.wf_purpose == wf_purpose and
                                wb.wf_key == wf_key and
                                wb.wf_folder == wf_folder and
                                wb.fi_key == fi_key ):
                                # This workbook belongs in this wf_folder_node
                                wb_node_id = wb.wb_id
                                wb_node = wb_tree.get_node(wb_node_id)
                                if wb_node is None:
                                    wb_node = wb_tree.create_node(tag=wb.wb_name,
                                                                  identifier=wb_node_id,
                                                                  parent=wf_folder_key,
                                                                  data=wb)
                        # lookup workbooks for fi_key, wf_key, wf_purpose and wf_folder
                        # Add workbook nodes to wf_folder_node
            return wb_tree
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def validate_model_type(self, model: object) -> bool:
        """Validate that the model is a BudgetDomainModel."""
        model_type_name = model.__class__.__name__
        if model_type_name == "BudgetDomainModel":
            return True
        raise TypeError(f"model type '{model_type_name}' is not compatible with 'BudgetDomainModel'.")

# ---------------------------------------------------------------------------- +
