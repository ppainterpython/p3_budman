# ---------------------------------------------------------------------------- +
#region    bsm_file_tree.py module
""" Implements BSMFileTree Class.

    The BudMan Data Context uses a "file tree" as a data structure to represent
    folders and files from a storage system. BudMan assumes that files are 
    stored in folders, which might be a cloud storage system, a local file 
    system, or a hybrid of both. Systems downstream from the Data Context 
    handles actual binding to a particular storage system.

    For Views (CLI, GUI or upstream API clients), a file tree is a tree structure
    based on the Treelib module. This module provides a simple API to create 
    and update a file tree for a specified budget domain model based on a url.

    Once initialized, the file_tree is saved in a .json file in the root 
    BDM_FOLDER of BudMan. Other functions are used to look up information from the
    file_tree about folders and files using an int file_index or dir_index. The 
    index values are unique to the entire tree. 
"""
#endregion bsm_file_tree.py module
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
    """
    A file_tree is a treelib.Tree populated from the BSM folders and files. 
    BSMFile objects are stored in the node.data attribute of each node and 
    contain additional information about the file or folder.

    Arguments
    ----------
    folder_url : str - The URL of the root folder for the file tree.
    save_tree : bool - Whether to save the file tree to a .json file.
    valid_prefixes : List[str] - List of valid file prefixes to consider.
    valid_wb_types : List[str] - List of valid workbook types to consider.
    """
    def __init__(self, folder_url:str, save_tree:bool=True,
                 valid_prefixes:List[str]=[], valid_wb_types:List[str]=[]) -> None:
        self.folder_url: str = folder_url
        self.save_tree: bool = save_tree
        self.valid_prefixes: List[str] = valid_prefixes
        self.valid_wb_types: List[str] = valid_wb_types
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
                    if node.data.folder_index > self.max_dir_index:
                        self.max_dir_index = node.data.folder_index
            # Save the file_tree to a .json file
            if self.save_tree and self.file_tree_json_file:
                logger.debug(f"Saving file_tree to {self.file_tree_json_file}")
                self.file_tree.save2file(str(self.file_tree_json_file))
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def construct_file_tree(self) -> Tree:
        """Create a file_tree structure from the url-specified folder's content."""
        p3u.is_not_non_empty_str("folder_url", self.folder_url, raise_error=True)
        folder_abs_path: Path = Path.from_uri(self.folder_url)
        bsm_verify_folder(folder_abs_path, create=False, raise_errors=True)
        file_index:int = 0
        folder_index:int = 0
        file_tree = Tree()
        tag = f"{folder_index:03}:{folder_abs_path.name}"
        # Root node
        bsm_file: BSMFile = BSMFile(BSMFile.BSM_FOLDER, folder_index, -1, self.folder_url,
                                   valid_prefixes=self.valid_prefixes,
                                   valid_wb_types=self.valid_wb_types)
        file_tree.create_node(tag=tag, identifier=self.folder_url,data=bsm_file)

        def add_nodes(current_path: Path, parent_id: str) -> None:
            """Recursive scan folder current_path, depth-first"""
            nonlocal folder_index, file_index
            try:
                if not current_path.is_dir(): # Windows file system specific is_dir()
                    raise ValueError(f"Path is not a folder: {current_path}")
                folder_index += 1
                # iterdir() returns "arbitrary order, may need to sort."
                for item in current_path.iterdir(): # Windows file system sprecific.
                    node_id = item.as_uri() # str(item.resolve())
                    if item.is_dir():
                        # Folder
                        # Apply folder exclude list
                        if item.stem in ["backup", "test", "draft", 
                                        "copies","__pycache__", "personal"]:
                            continue
                        tag = f"{folder_index:03}:{item.name}"
                        folder_bsm_file: BSMFile = BSMFile(BSMFile.BSM_FOLDER, 
                                                           folder_index, 
                                                           -1, 
                                                           node_id,
                                             valid_prefixes=self.valid_prefixes,
                                             valid_wb_types=self.valid_wb_types)
                        file_tree.create_node(tag=tag, identifier=node_id,
                            parent=parent_id,
                            data=folder_bsm_file)
                        add_nodes(item, node_id)
                    else:
                        # File
                        tag = f"{file_index:03}:{item.name}"
                        file_bsm_file: BSMFile = BSMFile(BSMFile.BSM_FILE, folder_index, file_index, item.as_uri(),
                                                        valid_prefixes=self.valid_prefixes,
                                                        valid_wb_types=self.valid_wb_types)
                        file_tree.create_node(tag=tag, identifier=node_id,
                                        parent=parent_id,
                                        data=file_bsm_file)
                        file_index += 1
                return
            except Exception as e:
                logger.error(p3u.exc_err_msg(e))
                raise

        try:
            add_nodes(folder_abs_path, self.folder_url)
            return file_tree
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def get_BSMFile(self, file_index: int) -> Optional[BSMFile]:
        """Get the BSMFile object given file_index."""
        try:
            for node_id in self.file_tree.expand_tree():
                file_node: Node = self.file_tree.get_node(node_id)
                if file_node.is_leaf(): # only look at file nodes, which are leafs
                    if (file_node.data and isinstance(file_node.data, BSMFile)):
                        bsm_file: BSMFile = file_node.data
                        this_index: int = bsm_file.file_index
                        if this_index == file_index:
                            return bsm_file
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def get_sub_file_tree(self, file_url: str) -> Optional[Tree]:
        """Return the sub tree corresponding to a directory at file_url."""
        try:
            p3u.is_not_non_empty_str("file_url", file_url, raise_error=True)
            for node_id in self.file_tree.expand_tree(mode=Tree.WIDTH):
                file_node: Node = self.file_tree.get_node(node_id)
                if not file_node.is_leaf(): # only look at file nodes, which are leafs
                    if (file_node.data and isinstance(file_node.data, BSMFile)):
                        bsm_file: BSMFile = file_node.data
                        if file_url == bsm_file.file_url:
                            # Return a deep copy of the sub tree at file_url
                            sub_tree:Tree = self.file_tree.subtree(node_id)
                            return Tree(sub_tree,deep=True)
            return None
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def validate_file_list(self, file_list: List[int], file_url: Optional[str] = None) -> Optional[List[BSMFile]]:
        """Validate a list of file_index values for a sub tree for file_url.
            Consider leaf files only, no directories."""
        try:
            p3u.is_not_obj_of_type("file_list", file_list, list, raise_error=True)
            if p3u.str_empty(file_url):
                sub_tree = self.file_tree
            else:
                sub_tree: Tree = self.get_sub_file_tree(file_url)
                if sub_tree is None:
                    raise ValueError(f"No sub tree found for file_url: {file_url}")
            bsm_files: List[BSMFile] = []
            for fi in file_list:
                for node_id in sub_tree.expand_tree(mode=Tree.WIDTH):
                    file_node: Node = sub_tree.get_node(node_id)
                    if file_node.is_leaf(): # only look at file nodes, which are leafs
                        if (file_node.data and isinstance(file_node.data, BSMFile) and
                            file_node.data.file_index == fi):
                            # Matched fi to validate
                            bsm_file: BSMFile = file_node.data
                            if not bsm_file.verify_url():
                                err_msg = f"File_index '{fi}' has an invalid URL: {bsm_file.file_url}"
                                logger.error(err_msg)
                                raise RuntimeError(err_msg)
                            bsm_files.append(bsm_file)
            return bsm_files
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def output_all_files(self) -> str:
        """Return a str of all file info in the file_tree."""
        try:
            file_info_list: str = ""
            file_info_list += f"{'in_bdm':<6} "
            file_info_list += f"{'full_filename':<50} "
            file_info_list += f"{'prefix':<15}   "
            file_info_list += f"{'wb_type':<15} "
            file_info_list += f"file_url\n"
            for node_id in self.file_tree.expand_tree():
                file_node: Node = self.file_tree.get_node(node_id)
                if file_node.is_leaf(): # only look at file nodes, which are leafs
                    if (file_node.data and isinstance(file_node.data, BSMFile)):
                        bsm_file: BSMFile = file_node.data
                        file_info_list += f"{str(bsm_file.in_bdm):<6} "
                        file_info_list += f"{bsm_file.full_filename or 'N/A':<50} "
                        file_info_list += f"'{bsm_file.prefix or 'N/A':<15}' "
                        file_info_list += f"'{bsm_file.wb_type or 'N/A':<15}' "
                        file_info_list += f"{bsm_file.file_url}\n"
            return file_info_list
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def all_workbooks(self) -> Generator[BSMFile, None, None]:
        """Generate all the workbooks in the file tree."""
        try:
            file_info_list: str = ""
            for node_id in self.file_tree.expand_tree():
                file_node: Node = self.file_tree.get_node(node_id)
                if file_node.is_leaf(): # only look at file nodes, which are leafs
                    if (file_node.data and isinstance(file_node.data, BSMFile)):
                        bsm_file: BSMFile = file_node.data
                        if bsm_file.wb_type in self.valid_wb_types:
                            yield bsm_file
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def all_files(self) -> Generator[BSMFile, None, None]:
        """Generate all the files in the file tree."""
        try:
            file_info_list: str = ""
            for node_id in self.file_tree.expand_tree():
                file_node: Node = self.file_tree.get_node(node_id)
                if file_node.is_leaf(): # only look at file nodes, which are leafs
                    if (file_node.data and isinstance(file_node.data, BSMFile)):
                        bsm_file: BSMFile = file_node.data
                        yield bsm_file
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise

    def all_folders(self) -> Generator[BSMFile, None, None]:
        """Generate all the folders in the file tree."""
        try:
            file_info_list: str = ""
            for node_id in self.file_tree.expand_tree():
                file_node: Node = self.file_tree.get_node(node_id)
                if not file_node.is_leaf(): # only look at folder nodes, which are not leafs
                    if (file_node.data and isinstance(file_node.data, BSMFile)):
                        bsm_file: BSMFile = file_node.data
                        yield bsm_file
        except Exception as e:
            logger.error(p3u.exc_err_msg(e))
            raise
# ---------------------------------------------------------------------------- +
