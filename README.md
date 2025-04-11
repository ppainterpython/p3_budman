<!-- markdownlint-disable MD033 -->

# PyExcelBudget

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
