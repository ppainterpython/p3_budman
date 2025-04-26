<!-- markdownlint-disable MD033 -->

# PyExcelBudget

## Introduction

This project began with the goal of learning about `pandas`, `Jupyter` in `VS Code` and the `python interactive mode`. At the same time, I was working on [pppActivityTracker](https://github.com/ppainterpython/pppActivityTracker.git) project. There I learned much about `Python logging` and and building a gui with `tkinter`.

**Goal:** the goal of `PyExcelBudget` is to analyze excel and csv files downloaded from the bank and use `pandas` to perform data analysis on the transactions producing budget visualizations and insights (to find out where all the money has gone.)
   > **Note**
   > Begun in the winter of 2025, this was my first exerience with python, in VS Code and the current version of GitHub Copilot. I tried to spend a lot of time with GHC, to really understand what it can help with, and what it screws up.

## Notes about p3_excel_budget Project

While getting this project off the ground, I started learning how to build python packacges for various subcompents. Although a bit of a learning curve, the structure has come together as follows. 

```python
p3_excel_budget/
├── .vscode/
│   ├── launch.json
│   ├── settings.json
│   └── tasks.json
├── logs/
│   ├── p3ExcelBudget.log
│   └── p3loggingDefault-file.log
├── src/
│   ├── data/
│   │   ├── p3_banking_transactions/
│   │   │   ├── __init__.py
│   │   │   ├── apply_mapping_to_excel_file.py
│   │   │   ├── budget_transactions.py
│   │   │   └── transaction_files.py
│   │   ├── p3_interactive_notebooks/
│   │   │   ├── apply_mapping_to_excel_file.py
│   │   │   └── read_excel_file.py
│   │   └── __init__.py
│   ├── experiments/
│   │   └── fooey.py
│   ├── utility/
│   │   ├── __init__.py
│   │   └── plot_settings.py
│   ├── __init__.py
│   ├── main.py
│   └── p3_excel_budget_constants.py
├── tests/
│   └── test_main.py
├── .coveragerc
├── .env
├── .gitignore
├── README.md
├── p3_excel_budget.code-workspace
├── pytest.ini
└── requirements.txt

9 directories, 26 files
```

## Learning about Pandas with openpyxl

```python
pip install pandas
pip install openpyxl
pip install matplotlib
pip install ipykernel # This is needed for Python 3.13.2+ to run jupyter cells
> git clone https://github.com/daveebbelaar/pandas-tutorials.git
> start vscode
_ open folder for project
_ in vscode, save as workspace in the project root folder, now open the workspace to work on the project. User level defaults and Workspace level settings. Workspace overrides User settings. 
_ add vscode extensions: python, pylance, python extension pack, Jupyter
# research extensions: CodeSnap, Path Intellisense, Atom One Dark Theme
# file icon themes are also available. Material Icon Theme
# vscode settings: Jupyter > Interactive Window > Text Editor: Execute Selection  <<<<---- should be checked
# The above seems to override: PythonREPL: Enable REPLSmart Send


```

## Learning more about Python logging.Logger

A project to learn about Python logging capabilities. Thanks to James Murphy for  his great [Modern Python Logging](https://www.youtube.com/watch?v=9L77QExPmI0) video with the [125_moder_loggin](https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/135_modern_logging) example code.

## Notes on support for JSONC in Python

I want to be able to comment JSON config files. I don't know why python json still ignores that, but it does. So, I will try the solution found in [stackoverflow: How to parse json file with c-style comments?](https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments) The recommendation there is to use a cpython implementation for JSON5 called [PyJSON5](https://pyjson5.readthedocs.io/en/latest/) documented [here](https://pyjson5.readthedocs.io/en/latest/).

## Logging Format Keys

In the custom log Formatter class ```ModuleOrClassFormatter```, I have taken some liberties to have logs appear the way I want them. First, I use fixed width names for the log level corresponding to the standard ones:

```python
# Standard Name   Abbrv   Custom Name   Value
# NOTSET            N     'NOTST'        0
# DEBUG             D     'DEBUG'       10 
# INFO              I     'INFO '       20
# WARNING           W     'WARN '       30
# ERROR             E     'ERROR'       40
# CRITICAL          C     'CRIT '       50
#
```

DateTime formats are ISO Format both with UTC time or with the UTC offset for the user's local timezone.

A text log entry will be like this:

```text
2025-04-10T01:03:39.727+00:00:E:[pidxxx:tidxxx]:modORclass:funcORmeth() message 
```

On occasion, as an option, the logger, handler and formatter names will be appended to the message, as in:

```text
<loggername:handlername:formattername>
<ActivityTracker:file:ModuleOrClassFormatter>
```

## Python Regular Expressions (re)

With some help from GitHub Copilot, I did a regex refresher. Here are some of the patterns being used. I wanted to record this as it was one of my initial sessions with GHC and `pandas`.

### Modifying the `'Account Name'` Column

For data from a bank holding transactions, the provided value of the Account Name is long and redundant. So, this pattern is used to reduce it to minimalist form. The original values are like:

```python
"ACME Bank of Awesome - Credit Card - Visa Signature"
"ACME Bank of Awesome - Bank - Primary Checking Acct"
```

and are transformed to:

```python
"Visa Signature"
"Primary Checking Acct"
```

The data is contained in a `pandas.dataframe` object. Here is the code to do the reduction.

```python
df['Account Name'] = df['Account Name'].str.replace(
    r'^[^-]+-\s*[^-]+-\s*(.+)$',  # Regular expression
    r'\1',                        # Replace w/ group 1, 1st capturing group (the third part)
    regex=True                    # Enable regex mode
)
```

Explanation (direct quote from GitHub Copilot)

1. `^[^-]+`
   - Matches the first part of the string (e.g., `'ACME Bank of Awesome'`), which is everything up to the first `-`.
   - `^` asserts the start of the string.
   - `[^-]+` matches one or more characters that are not a hyphen (`-`).
1. `-\s*`
   - Matches the hyphen (`-`) and any surrounding whitespace.
1. `[^-]+`
   - Matches the second part of the string (e.g., 'Bank' or 'Credit Card'), which is everything up to the next `-`
1. `-\s*(.+)$`
   - Matches the hyphen (`-`) and any surrounding whitespace, followed by the third part of the string.
   - `(.+)$` captures the third part (e.g., `'Primary Checking Acct'` or `'Visa Signature'`) until the end of the string (`$`).

### Mapping the `'Category'` Column

When banking data is downloaded, the `'Original Description'` column is filled with varying different text drawn from the transaction processings. Our effort is to map those to a smaller, simpler set of values in the `'Category'` column. GitHub Copil was asked to write the python for this action when the data is contained in a `pandas.dataframe` object. Part of the prompt used, in several back and forth sequences, was:

```text
I want all the words to be present in order but with variable whitespace and perhaps other characters in between. 
And the other characters could abut one of the words, like "DES:HOA"
```

Here is what GHC recommended:

To match all the specified words in order, allowing for variable whitespace or other characters (e.g., punctuation) between them, and to handle cases where other characters might abut one of the words (like `"DES:HOA"`), you can use a regular expression with the following features:

1. **Word Matching in Order**:
   - Use `.*?` between the words to allow for any characters (including whitespace or punctuation) between them.
1. **Word Boundaries**:
   - Use `\b` to ensure that the words are matched as whole words, but allow for cases where characters might abut one of the words.
1. **Case Insensitivity**:
   - Use the `(?i)` flag to make the pattern case-insensitive.
1. **Optional Characters Around Words**:
   - Use optional non-word characters (`\W*`) to allow for characters like `:` or `-` to abut the words.

#### Regular Expression

Here’s the regular expression to match all the words in order:

```python
r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b'
```

#### Explanation

1. `(?i)`:
   - Makes the pattern case-insensitive.
1. `\bavery`:
   - Matches the word `"avery"` as a whole word.
1. `\W*`:
   - Matches zero or more non-word characters (e.g., `:`, `-`, or whitespace).
1. `.*?`:
   - Matches zero or more of any characters (non-greedy), allowing for variable whitespace or other characters between the words.
1. `\branch`:
   - Matches the word `"ranch"` as a whole word.
1. `\bHOA`:
   - Matches the word `"HOA"` as a whole word.
1. `\bdues\b`:
   - Matches the word "dues" as a whole word.

#### Example Usage

Here’s how you can use this pattern in your `category_mapping` dictionary and apply it to a `pandas DataFrame`:

```python
import re
import pandas as pd

# Example DataFrame
data = pd.DataFrame({
    'description': [
        'avery ranch HOA dues',
        'avery-ranch HOA:dues',
        'avery ranch dues HOA',
        'DES:avery ranch HOA dues',
        'amazon purchase',
        'avery ranch HOAdues'
    ]
})

# Category mapping
category_mapping = {
    r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'HOA Dues',
    r'(?i)\bamazon\b': 'Amazon',
}

# Function to categorize descriptions
def categorize(description):
    for pattern, category in category_mapping.items():
        if re.search(pattern, description):  # Match using the regex
            return category
    return 'Other'

# Apply the function to the DataFrame
data['category'] = data['description'].apply(categorize)

print(data)
```

#### Output

```python
  Original Description      Category
0 avery ranch HOA dues      HOA Dues
1 avery-ranch HOA:dues      HOA Dues
2 avery ranch dues HOA      HOA Dues
3 DES:avery ranch HOA dues  HOA Dues
4 amazon purchase           Amazon
5 avery ranch HOAdues       HOA Dues
```

#### Key Points

1. **Handles Variable Whitespace and Characters**:
   - The `.*?` and `\W*` parts of the regex allow for any characters (including whitespace, punctuation, or none) between the words.
1. **Matches Words in Order**:
   - The words `"avery,"` `"ranch,"` `"HOA,"` and `"dues"` must appear in the specified order.
1. **Case-Insensitive Matching**:
   - The `(?i)` flag ensures that the matching is not affected by letter casing.
1. **Handles Abutting Characters**:
   - The `\W*` ensures that characters like `:` or `-` can abut the words without breaking the match.

#### Summary

The regular expression `r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b'` ensures that all specified words are matched in order, with flexibility for variable whitespace, punctuation, or other characters in between. It also handles cases where characters abut the words, such as `"DES:HOA"`. This approach is robust for categorizing text data in your `DataFrame`.

## Learning about Python Packages

```python
pip install -e ../p3Logging

# wsl
wsl.exe  -d Ubuntu


# TODO List
# p3logging - enable/disable loggers by dictConfig Handler Id
# p3logging - clean up Queue_Handler thread issues

```
