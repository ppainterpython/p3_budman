# ---------------------------------------------------------------------------- +
import sys, os, re, glob
from pathlib import Path

# import pandas as pd
# ---------------------------------------------------------------------------- +
#region Initializations
# me = f"{Path(__file__).name}: "
# cwd = os.getcwd(); 
# print(f"{me}cwd: '{cwd}'")
# print(f"{me}sys.path: '{sys.path}'")

# xlsx = ".xlsx"
# csv = ".csv"
# file_actual_folder = "~\\OneDrive\\budget\\boa\\data"
# file_actual_name = "BOAChecking2025"
# try:
#     file_name_path = Path(f"{file_actual_name}{xlsx}")
#     folder_path = Path(file_actual_folder).expanduser() 
#     abs_path = folder_path / file_name_path
#     abs_path.touch()
#     # if not abs_path.exists():
#     #     print(f"{me}File does not exist: {abs_path}") 
#     #     exit()
# except Exception as e:
#     print(f"{me}Error: {repr(e)}")
#     exit()
# # Opening a single Excel file
# df = pd.read_excel(
#     abs_path
#     , parse_dates=[1] 
#     # , index_col=[1]
# )
#endregion Initializations
# ---------------------------------------------------------------------------- +
# Transform data
# ---------------------------------------------------------------------------- +
# Remove some columns from the original excel import
# df.drop(['Status'], inplace=True, axis=1)
# df.drop(['Split Type'], inplace=True, axis=1)
# df.drop(['Currency'], inplace=True, axis=1)
# df.drop(['User Description'], inplace=True, axis=1)
# df.drop(['Memo'], inplace=True, axis=1)
# df.drop(['Classification'], inplace=True, axis=1)

# # Format the columns of interest
# df["Date"] = pd.to_datetime(df["Date"])
# df["Date"] = df["Date"].dt.strftime("%m/22/%Y")
# # For column ['Account Name'], Replace the string with just the third part, to
# # shorten it, i.e., "Bank of America - Bank - Primary Checking Acct" becomes
# # "Primary Checking Acct".
# df['Account Name'] = df['Account Name'].str.replace(
#     r'^[^-]+-\s*[^-]+-\s*(.+)$',  # Regular expression
#     r'\1',                        # Replace w/ group 1, 1st capturing group (the third part)
#     regex=True                    # Enable regex mode
# )
# df.head(5)
# # Map values to column ['Category'] by re pattern-matching to 
# # column ['Original Description'].
# # This list of patterns will be quite long. 
# # TODO: How to use data to train an LLM or ML model to do this?
# category_mapping = {
#     r'(?i)\bamazon\b': 'Amazon Prime',
#     r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'Home Owners Association',
# }

# def map_category(description):
#     for pattern, category in category_mapping.items():
#         if re.search(pattern, str(description), re.IGNORECASE):
#             return category
#     return 'Other'  # Default category if no match is found

# category_mapping = {
#     r'(?i)\bamazon\b': 'Amazon Prime',
#     r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'Home Owners Association',
# }



# df['Category'] = df['Original Description'].apply(map_category)

# _ = "pause"


# df = df.drop(["sensor_15"], axis=1)

# ---------------------------------------------------------------------------- +
# Combining multiple Excel files
# ---------------------------------------------------------------------------- +

# path = "../../data/raw/pump_sensor_data"
# files = sorted(glob(path + "/*.xlsx"))

# df_combined = pd.concat(
#     [
#         pd.read_excel(f, parse_dates=[0], index_col=[0]).drop(["sensor_15"], axis=1)
#         for f in files
#     ]
# )

# df_combined["sensor_00"].plot()

# # ---------------------------------------------------------------------------- +
# # Export to .xlsx
# # ---------------------------------------------------------------------------- +

# df_combined.to_excel("../../data/interim/data_combined.xlsx")

# # ---------------------------------------------------------------------------- +
# # Export to .csv
# # ---------------------------------------------------------------------------- +

# df_combined.to_csv("../../data/interim/data_combined.csv")
