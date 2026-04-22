# ---------------------------------------------------------------------------- +
#region budman_wf_namespace.py module
""" budman_wf_namespace.py defines symbol constants for budman app worflow
Services."""
#endregion budman_wf_namespace.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages

# third-party modules and packages

# local modules and packages
import budman_namespace as bdm
import p3_mvvm.mvvm_namespace as p3m
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
# BudMan application-specific workflow Constants.

# Standard transaction (txns) workbook column names and order for .csv .xlsx
# A standard budman transactions workbook has ontly the following columns 
# preferrably in this order:
BUDMAN_DATE_COL_NAME = "Date"
BUDMAN_ORIGINAL_DESCRIPTION_COL_NAME = "Original Description"
BUDMAN_AMOUNT_COL_NAME = "Amount"
BUDMAN_ACCOUNT_CODE_COL_NAME = "Account Code" 
BUDMAN_BUDGET_CATEGORY_COL_NAME = "Budget Category"
BUDMAN_LEVEL_1_COL_NAME = "Level1" 
BUDMAN_LEVEL_2_COL_NAME = "Level2" 
BUDMAN_LEVEL_3_COL_NAME = "Level3" 
BUDMAN_DEBIT_CREDIT_COL_NAME = "DebitOrCredit"  
BUDMAN_YEAR_MONTH_COL_NAME = "YearMonth"  
BUDMAN_PAYEE_COL_NAME = "Payee"
BUDMAN_ESSENTIAL_COL_NAME = "Essential" 
BUDMAN_RULE_COL_NAME = "Rule"

BUDMAN_TXNS_WORKBOOK_COL_NAMES = [ 
    BUDMAN_DATE_COL_NAME,
    BUDMAN_ORIGINAL_DESCRIPTION_COL_NAME,
    BUDMAN_AMOUNT_COL_NAME,
    BUDMAN_ACCOUNT_CODE_COL_NAME,
    BUDMAN_BUDGET_CATEGORY_COL_NAME,
    BUDMAN_LEVEL_1_COL_NAME,
    BUDMAN_LEVEL_2_COL_NAME,
    BUDMAN_LEVEL_3_COL_NAME,
    BUDMAN_DEBIT_CREDIT_COL_NAME,
    BUDMAN_YEAR_MONTH_COL_NAME,
    BUDMAN_PAYEE_COL_NAME,
    BUDMAN_ESSENTIAL_COL_NAME,
    BUDMAN_RULE_COL_NAME
]

#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
