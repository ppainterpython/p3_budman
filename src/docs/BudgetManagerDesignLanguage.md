# Budget Manager Application Design Language

An application for managing a budget is the outcome here. Budgets are about tracking income versus spending and managing that to goals. Budget goals including limiting spending in defined categories, savings for categories, etc. These are the words for the Design Language of the Budget Manager (BudMan) application.

Words mean something. Much is written about a design language, but what I have in mind is, first, to tell the narrative story of the applications purpose and value to its users. Then, establish a vocabulary that will be consistent when describing the design and implementation of the applications. Here is the BudMan narrative. Key words are placed in __bold__, nouns and verbs.

## Managing to a Budget

All people, families, businesses and organizations have a budget, managed or not. The budget is a framework and practices to know how much money is coming in and going out. Most budgets are related to income and spending, making money and spending money. Our __Budget Model__ is straight-forward. Money is tracked by by transactions occurring with __Financial Institutions (FI)__ such as banks and brokerage firms. Typically, one uses __Accounts__ with an FI and can obtain a record of all transactions for each account either by a statement document, online banking, or downloading a file. BudMan refers to such data collections as __Workbooks (WB)__ , specifically, Excel workbooks or csv files. A workbook is from a specific FI and contains rows of transaction information, such as date, amount, description, etc.

Tracking income and expenses over time is critical to the value of a budget. Often, FI's will update account status on a monthly basis, issuing statements, or workbooks in the BudMan narrative. There will be workbooks from each FI, at least for each month, and perhaps separately for each account. Gathering the new input into the budget for user benefit requires processing the workbooks, and hence, a means to manage that processing. BudMan uses __Workflows (WF)__ to handle the processing. A workflow is a series of tasks performed on the workbooks. A task uses input, produces output, and may utilize working copies of data for a time.

## Design for the MVVM Pattern

Managing a budget with an application is the goal. I chose to make it a command line application to handle excel __Workbooks__, doing the tedious stuff and let the user use Excel for the actual user experience regarding the numbers. Hence, the __View__ in our design is a simple command line interface (__CLI__). But, the __View Model__, __Data Context__, and __Model__ designs do not have knowledge of that.

## Technical Design Overview

Having written a story, the narrative embodied in the design language of an application, it remains to create a technical design to implement the narrative. Several key factors are considered for the design. First, the concept of managing to a budget presents several domains of interest. As I am a fan of domain-driven design, the Budget Domain Model design is a critical influencer. Another influence is applying the MVVM design pattern for software applications.

### Budget Domain Model (BDM)

Notes: Information (data) is separated by Financial Institution (FI) and Workflow (WF). Application users are familiar with the storage model of PCs, that of folders and files, so we can leverage that vernacular and later map it to the storage sub-domain, or Budget Storage Model (BSM).

In the BDM, data is mapped to files as storage units. Files are organized into folders, a container of files. A folder contains both other folders and files. In our initial focus, files are more often excel workbooks, referred to as workbooks for brevity (although it is conceivable that .csv files will have a role as well, since many FIs provide download data in csv files.)

Workflows process files with tasks in a sequence. A general view is a task knows what folder will contain the files it must work with. Files are loosely considered to be used as input, working, or output data. Hence, a folder is designated as input, working, or output as a container type. In the BDM, files are kept in collections, each with a unique filename and filetype the union of which is referred to as the full filename (e.g., filename='March2025', filetype='.xlsx', full filename='March2025.xlsx'). Workflows may configure prefixes aligned to workflow input, working or output state.

In our design language, files are Data Files (DF) and WorkBooks (WB) with another type designation of DF_TYPE or WB_TYPE (synonyms). This type maps to the input, working, output state concept. A __DATA_COLLECTION__ is a set of lists of files/workbooks (__WORKBOOK_DATA_LIST__ or __FILE_LIST__).

### MVVM Command Pattern Technical Design

Our MVVM design includes a sub-pattern for Command Processing (CP) as well as a Data Context (DC). Early on, I learned the .NET MVVM framework and that has no doubt influenced my thinking as I design one in python. Because I can, I decided to include the CP and DC in an uber-DC pattern.

View -> ViewDataContext(bindings for CP, DC) -> ViewModel(bindings for CP, DC) -> uber-DC -> Model

The ViewModel CP methods to execute individual cmds should use the DC_interface plus a model-specific interface to simplify the model_interface for use in the context of the DC_interface. Cmds take action on data, hence, the DC has to involve mapping cmd actions in the ViewModel to an abstraction that will ultimately access the Model and do real work on real data.

### Model Technical Design

Using MVVM, the Model is concerned with data and storage. Our design here factors the Model into two component concepts, one for data referred to as the __Budget Domain Model__ (BDM), and one for storage, the __Budget Storage Model__ (BSM). The BDM is a domain model concerning with the data and behavior (code) associated with it. A package named `budget_domain_model` defines classes and modules with the major class for the BDM named __BudgetDomainModel__. At present, the BSM resides in the package `budget_storage_model`.

For flexibility and code reuse, the MVVM pattern encourages loose-coupling through lazy, run-time binding  to specific concrete implementations of the components through Dependency Injection. For the Model, a key differences between concrete implementations is how data is stored. A storable object used for BDM data is referred to as the __BDM_STORE__ object, a dictionary with absolute mapping to/from json. A __BDM_STORE__ is a data object that is stored using a __URL__ for reference. It is not an explicit _type_, has a defined schema of attributes representable in json, and defines an abstract interface implemented by concrete classes or functions. The __URL__ to a __BDM_STORE__ object is referred to as the __BDM_URL__. With a __BDM_URL__, the model can move the data back and forth from storage depending on the _scheme_ of the __BDM_URL__.

In the beginning, the local filesystem is used. But the design couples through a __URL__ specified for the __BDM_STORE__. This value may be configurable, but the Model design does not know anything about how the configuration is maintained in other layers of an application. When the BudgetDomainModel() is accessed, it will be through the __URL__. A file://-type __URL__ indicates the local filesystem and the pathname is extracted from the __URL__.

When dealing with data and storage in a Model, there is always functionality devoted to loading and storing existing data objects as well as creation of new data objects, how to specify default values, etc. With this design, a __BDM_STORE__ object begins with a creation function. A __BDM_CONFIG__ object is used to specify initial values used when instantiating a new object. Great effort has been devoted to maintain the same _schema_ for both __BDM_STORE__ and __BDM_CONFIG__ object data content. In the `budget_domain_model` package, the `BDMConfig` class has the job to provide __BDM_CONFIG__ objects used to instantiate `BudgetDomainModel` instances from __BDM_CONFIG__ objects. Two scenarios are provided. First, the `BDMConfig` class can load a __BDM_STORE__ object from a __BDM_URL__ and provide it as a __BDM_CONFIG__ object. Second, the `BDMConfig` class can provide a pristine __BDM_CONFIG__ object based on internal default values. Applications can further modify the __BDM_CONFIG__ object in other ways prior to providing it to instantiate a `BudgetDomainModel` class instance.

Keep application settings and configuration out of the Model design. Do not use outside config/settings objects to initialize the model. The BDMConfig is used as a default object to create a new __BDM_STORE__ object which can then be modified and used to initialize a new BUDMAN_MODEL_STORE before saving it the first time.

### Budget Storage Model

__BDM_STORE__ and __BDM_CONFIG__ are dictionaries in memory and json files in storage. The BSM treats them accordingly. Storage is referenced by __URL__. BSM does no validation beyond json encode and decode. Exceptions are raised for error conditions.

__WORKBOOKS__ are files which are also moved to and from storage. Only the local filesystem is supported as a storage service. __WORKBOOKS__ are referenced by their absolute path string (__abs_path__).

BSM maps a __folder__ path, a __filename__ and a __filetype__ into an __abs_path__ for filesystem operations. The combined __filename__ appended to __filetype__ is referred to as the __full_filename__.

### View Model

The __View Model__ is created first, as the application starts. It is the responsibility of the __View Model__ to create the other components. It has access to the application settings, but the __Data Context__ and __Model__ have no dependency on those.

In the __View Model__ initialization, it loads the __BDM_STORE__ and applies the appropriate state assignments to the __Data Context__ to prime it for the application.

### Data Context Technical Design

The concept of __Workbook__ is expanding. Need to change __WB_TYPE__ to __WF_PURPOSE__, to model the intended use by a __Workflow__ of a __Workbook__ and the __Folder__ containing it both in the __BDM__ and __BSM__. So __WB_TYPE__ is redefined to cover excel workbooks and csv workbooks of differing types. We have the most common case of a workbook in excel holding financial transaction data, typically downloaded from an institution. But these begin life as .csv files and become .xlsx files, one aspect of the type. The other is that now we have the __Check Register__ workbook, which is a csv file.

### Workflow Processing Technical Design

We started with mapping the Budget_Category field by using regex patterns to match the Original Description field of a workbook to a Budget Category. Later, we added the Level1, Level2, Level3 fields to split the budget category on '.' and populate 3 columns in the workbook, added by BudMan. That was done in the `map_budget_category` task function. Even later, that task function was modified further to support other new column values. These additional columns are for convenience back in excel pivot tables.

Now, the design needs expansion and refactoring. Here are some notes:

```python

    # A workflow is composed of workflow task functions.
    # The Budget Category workflow has the following tasks:
    #   - Perform transformations on workbooks.
    #   - Move workbooks from one wf folder to another.
    #   - Apply transformation in-place to "working" files in one folder.
    #   - budget_category_process_workbook(): runs a series of 
    #     common tasks on a workbook. It can be run anytime and the
    #     tasks will do their work additively.
    #   - map_budget_category() - applies the category_map patterns to a 
    #     specified column and returns a Budget #     Category.
    #   - map_check_register() reads a CheckRegister .csv file 
    #     and applies the category to the indicated 'check' transactions, 
    #     replacing the Original Description field.
    #   - set_account_code() - applies the transform to the 
    #     Account Name field and stores in the Account Code field.
    #   - Set DebitOrCredit
    # A worklow and its tasks run under a wf_key and a wb_type.
```

### Workflow Data Collection Transition Notes

I have evolved this aspect of the BDM several times, but I have converged on a data model that has two parts. Originally, the BDM had __FI_DATA_COLLECTION__ which stored references to __WORKBOOK_ITEMS__ containing bits of information about workbooks in the context of a workflow process. This is workflow-centric, and helps achieve the goal of clean separation of the FI's data as it proceeds through a set of workflow tasks. That is still in the design.

In addition to that view of an FI's workbook data, the __FI_OBJECT__ now has a __FI_WORKBOOK_COLLECTION__ containing all known workbooks for an FI. Each workbook object contains all the meta data known about a workbook, giving a workbook-centric data view.

To add clarity, I am refactoring some type definitions:

- __WORKFLOW_DATA_COLLECTION__ to organize the workbooks in the workflow-centric view.

- __WORKBOOK_DATA_COLLECTION__ for the workbook-centric view.

### Making BudManViewModel a subclass of BudManDataContext_Binding

To keep it simple, and keep an eye on a clean, and simple Dependency Injection pattern, I am making all bindings happen after object instantiation. Using initialize methods, the *_binding classes are configured with the reference to their concrete objects at initialization time, not object instantiation time.

## Change Journal

| Date       | Description                                                      |
|------------|------------------------------------------------------------------|
| 06/17/2025 | Removed bdm_initialize_from_BDM_STORE(self) from budget_domain_model.py|
|06/17/2025|Modified BDMWorkbook class and WORKBOOK_DATA_COLLECTION to be use the wb_id as the key, not a list index. The wb_index used in layers above BDM, not persisted in BDMWorkbook.|
|6/19/2025|Making BudManViewModel a subclass of BudManDataContext_Binding finally.|
