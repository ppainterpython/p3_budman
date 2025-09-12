# ---------------------------------------------------------------------------- +
#region    bsm_file_tree.py module
""" Implements BSMFileTree Class.

    The BDM uses a "file tree" as a shortcut to locate files in the budget
    domain model. BDM assumes that files are stored in folders in a storage 
    system, which might be a cloud storage system, a local file system, or
    a hybrid of both. The Budget Storage Model handles actual binding to a
    a particular storage system.

    For CLI and other simple user interfaces, a file tree is a tree structure
    based on the Treelib module. This module provides a simple API to create 
    and update a file tree for a specified budget domain model based on a url.

    Once initialized, the file_tree is saved in a .json file in the root of the
    bdm_store folder. Other functions are used to look up information from the
    file_tree about folders and files using an int file_index or dir_index. The 
    index values are unique to the entire tree. 
"""
#endregion bsm_file_tree.py module
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard library modules and packages
import logging, os, time, toml
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
from treelib import Tree, Node
# local modules and packages
from budget_storage_model.bsm_file import BSMFile
import budman_namespace.design_language_namespace as bdm
from budget_storage_model import (bsm_verify_folder, bsm_URL_verify_file_scheme,)
#endregion Imports
# ---------------------------------------------------------------------------- +
#region    Globals and Constants
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------- +
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region BSMFileTree Class
class BSMFileTree:
    def __init__(self, folder_url:str, save_tree:bool=True) -> None:
        self.folder_url: str = folder_url
        self.save_tree: bool = save_tree
        self.folder_path: Path = bsm_URL_verify_file_scheme(folder_url, test_exists=True)
        self.file_tree: Tree = None
        self.max_file_index: int = -1
        self.max_dir_index: int = -1
        if save_tree:
            self.file_tree_json_file: Path = self.folder_path / ".bdm_file_tree.json"
        else:
            self.file_tree_json_file = None
        self.update_file_tree()

    def update_file_tree(self) -> None:
        """Update the file_tree from the folder_url."""
        try:
            p3u.is_not_non_empty_str("folder_url", self.folder_url, raise_error=True)
            self.file_tree = self.construct_file_tree()
            if self.file_tree is None or not isinstance(self.file_tree, Tree):
                raise ValueError("file_tree is not a valid Tree object.")
            # Update max file_index and dir_index
            self.max_file_index = -1
            self.max_dir_index = -1
            for node in self.file_tree.all_nodes():
                if isinstance(node.data, BSMFile):
                    if node.data.file_index > self.max_file_index:
                        self.max_file_index = node.data.file_index
                    if node.data.dir_index > self.max_dir_index:
                        self.max_dir_index = node.data.dir_index
            # Save the file_tree to a .json file
            if self.save_tree and self.file_tree_json_file:
                logger.debug(f"Saving file_tree to {self.file_tree_json_file}")
                # self.file_tree.save2file(str(self.file_tree_json_file))
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def construct_file_tree(self) -> Tree:
        """Create a file_tree structure from a folder's content specified by URL."""
        p3u.is_not_non_empty_str("folder_url", self.folder_url, raise_error=True)
        folder_abs_path: Path = Path.from_uri(self.folder_url)
        bsm_verify_folder(folder_abs_path, create=False, raise_errors=True)
        file_index:int = 0
        dir_index:int = 0
        file_tree = Tree()
        tag = f"{dir_index:2} {folder_abs_path.name}"
        # Root node
        file_tree.create_node(tag=tag, identifier=str(folder_abs_path),
                            data=BSMFile(BSMFile.BSM_FOLDER, dir_index, -1, self.folder_url))

        def add_nodes(current_path: Path, parent_id: str) -> None:
            """Recursive scan directory current_path. Depth-first, using Path.iterdir()"""
            nonlocal dir_index, file_index
            try:
                if not current_path.is_dir():
                    raise ValueError(f"Path is not a directory: {current_path}")
                dir_index += 1
                # iterdir() returns "arbitrary order, may need to sort."
                for item in current_path.iterdir():
                    node_id = str(item.resolve())
                    if item.is_dir():
                        # Folder
                        if item.stem in ["backup", "test", "draft", 
                                        "copies","__pycache__", "personal"]:
                            continue
                        tag = f"{dir_index:2} {item.name}"
                        file_tree.create_node(tag=tag, identifier=node_id, 
                            parent=parent_id, 
                            data=BSMFile(BSMFile.BSM_FOLDER, dir_index, 
                                        -1, item.as_uri()))
                        add_nodes(item, node_id)
                    else:
                        # File
                        tag = f"{file_index:2} {item.name}"
                        file_tree.create_node(tag=tag, identifier=node_id, 
                                        parent=parent_id, 
                                        data=BSMFile(BSMFile.BSM_FILE, dir_index, 
                                                    file_index, item.as_uri()))
                        file_index += 1
                return
            except Exception as e:
                logger.error(p3u.exc_err_msg(e))
                raise

        try:
            add_nodes(folder_abs_path, str(folder_abs_path))
            return file_tree
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
#endregion BUDMAN_CMD_FILE_SERVICE_file_tree()
# ---------------------------------------------------------------------------- +
