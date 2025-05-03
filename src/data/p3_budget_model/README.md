# p3 Budget Domain Model

Every package has goals, a set of problems to be solved with good code design and implementation. Our Budget Domain Model (BDM) lies in the domain of helping people track their income and spending according to a budget. Input data is obtained from financial institutions, e.g., banks or brockerage firms, as downloaded excel files with transactions. There excel transaction workbooks are read in, the transactions are categorized, and the final output provides a means to collect and analyze inflows and outflows of money against a budget.

## Workflow Process

`p3_budget_model` applies a pattern common to data analytics pipelines. Mutliple workflows can be configured and invoked. Each workflow works in input data from a configurable folder and places results in configurable output folders.

Workflows are triggered by the arrival of a new transaction excel workbook, as a file in a raw_data folder. Workbooks in the raw_data folder are never modified. Ideally, all subsequent processing can be reproduced by applying the workflows to the raw_data input afresh.

Input to a specific workflow is not modified by that workflow. Only results in the output are modified based on the concerns of the workflow applied to the input.

### Workflow Configuration

Where workflows are configured, the workflow (WF) object has the following configurable fields. Here 3 typical workflows are used for illustration.

```python
                    BM_WF_INTAKE: {
                        # WF Object
                        WF_NAME: BM_WF_INTAKE,
                        WF_FOLDER_IN: "data/new",
                        WF_WORKBOOKS_IN: {},
                        WF_IN_PREFIX: None,
                        WF_FOLDER_OUT: "data/categorized",
                        WF_WORKBOOKS_OUT: {},
                        WF_OUT_PREFIX: "categorized_",
                    },
                    BM_WF_CATEGORIZATION: {
                        # WF Object
                        WF_NAME: BM_WF_CATEGORIZATION,
                        WF_FOLDER_IN: "data/categorized",
                        WF_WORKBOOKS_IN: {},
                        WF_IN_PREFIX: "categorized_",
                        WF_FOLDER_OUT: "data/processed",
                        WF_WORKBOOKS_OUT: {},
                        WF_OUT_PREFIX: "final_"
                    },
                    BM_WF_FINALIZATION: {
                        # WF Object
                        WF_NAME: BM_WF_FINALIZATION,
                        WF_FOLDER_IN: "data/processed",
                        WF_WORKBOOKS_IN: {},
                        WF_IN_PREFIX: "final_",
                        WF_FOLDER_OUT: None,
                        WF_WORKBOOKS_OUT: {},
                        WF_OUT_PREFIX: None
                    }

```
