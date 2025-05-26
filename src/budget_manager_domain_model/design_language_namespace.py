# ---------------------------------------------------------------------------- +
#region budman_design_language_namespace.py module
""" BudgetManagerDesignLanguage: a design language for Budget Management.

"""
#endregion budman_design_language_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
# third-party modules and packages
from typing import Dict, List, Tuple, Any
from openpyxl import Workbook



# local modules and packages
# from data.p3_fi_transactions.budget_model import BudgetModel
#endregion Imports
# ---------------------------------------------------------------------------- +

THIS_APP_NAME = "p3_budget_manager"
THIS_APP_SHORT_NAME = "budman"
THIS_APP_VERSION = "0.3.0"
THIS_APP_AUTHOR = "Paul Painter"
THIS_APP_COPYRIGHT = "2025 Paul Painter"

ALL_KEY = "all"
FI_KEY = "fi_key"
WF_KEY = "wf_key"
WB_TYPE = "wb_type"
WB_NAME = "wb_name"
WB_REF = "wb_ref"

WORKBOOK_LIST = List[Tuple[str, str]] 
WORKBOOK_ITEM = Tuple[str, str]
LOADED_WORKBOOK_LIST = List[Tuple[str, Workbook]]
BDM_WORKING_DATA_OBJECT = Dict[str, Any]
DATA_CONTEXT = Dict[str, Any]
