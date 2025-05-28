# Budget Manager Application Design Language

An application for managing a budget is the outcome here. Budgets are about tracking income versus spending and managing that to goals. Budget goals including limiting spending in defined categories, savings for categories, etc. These are the words for the Design Language of the Budget Manager (BudMan) application.

Words mean something. Much is written about a design language, but what I have in mind is, first, to tell the narrative story of the applications purpose and value to its users. Then, establish a vocabulary that will be consistent when describing the design and implementation of the applications. Here is the BudMan narrative. Key words are placed in __bold__, nouns and verbs.

## Managing to a Budget

All people, families, businesses and organizations have a budget, managed or not. The budget is a framework and practices to know how much money is coming in and going out. Most budgets are related to income and spending, making money and spending money. Our __Budget Model__ is straight-forward. Money is tracked by by transactions occurring with __Financial Institutions (FI)__ such as banks and brokerage firms. Typically, one uses __Accounts__ with an FI and can obtain a record of all transactions for each account either by a statement document, online banking, or downloading a file. BudMan refers to such data collections as __Workbooks (WB)__ , specifically, Excel workbooks or csv files. A workbook is from a specific FI and contains rows of transaction information, such as date, amount, description, etc.

Tracking income and expenses over time is critical to the value of a budget. Often, FI's will update account status on a monthly basis, issuing statements, or workbooks in the BudMan narrative. There will be workbooks from each FI, at least for each month, and perhaps separately for each account. Gathering the new input into the budget for user benefit requires processing the workbooks, and hence, a means to manage that processing. BudMan uses __Workflows (WF)__ to handle the processing. A workflow is a series of tasks performed on the workbooks. A task uses input, produces output, and may utilize working copies of data for a time.

