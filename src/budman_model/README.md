# p3 Budget Domain Model

Every package has goals, a set of problems to be solved with good code design and implementation. Our Budget Domain Model (BDM) lies in the domain of helping people track their income and spending according to a budget. Input data is obtained from financial institutions, e.g., banks or brockerage firms, as downloaded excel files with transactions. There excel transaction workbooks are read in, the transactions are categorized, and the final output provides a means to collect and analyze inflows and outflows of money against a budget.

## Workflow Process

`p3_budget_model` applies a pattern common to data analytics pipelines. Mutliple workflows can be configured and invoked. Each workflow works in input data from a configurable folder and places results in configurable output folders.

Workflows are triggered by the arrival of a new transaction excel workbook, as a file in a raw_data folder. Workbooks in the raw_data folder are never modified. Ideally, all subsequent processing can be reproduced by applying the workflows to the raw_data input afresh.

Input to a specific workflow is not modified by that workflow. Only results in the output are modified based on the concerns of the workflow applied to the input.

### Workflow Configuration

Where workflows are configured, the workflow (WF) object has the following configurable fields. Here 3 typical workflows are used for illustration.

```python
                    BDM_WF_INTAKE: {
                        # WF Object
                        WF_NAME: BDM_WF_INTAKE,
                        WF_INPUT_FOLDER: "data/new",
                        WF_WORKBOOKS_IN: {},
                        WF_PREFIX_IN: None,
                        WF_OUTPUT_FOLDER: "data/categorized",
                        WF_WORKBOOKS_OUT: {},
                        WF_PREFIX_OUT: "categorized_",
                    },
                    BDM_WF_CATEGORIZATION: {
                        # WF Object
                        WF_NAME: BDM_WF_CATEGORIZATION,
                        WF_INPUT_FOLDER: "data/categorized",
                        WF_WORKBOOKS_IN: {},
                        WF_PREFIX_IN: "categorized_",
                        WF_OUTPUT_FOLDER: "data/processed",
                        WF_WORKBOOKS_OUT: {},
                        WF_PREFIX_OUT: "final_"
                    },
                    BDM_WF_FINALIZATION: {
                        # WF Object
                        WF_NAME: BDM_WF_FINALIZATION,
                        WF_INPUT_FOLDER: "data/processed",
                        WF_WORKBOOKS_IN: {},
                        WF_PREFIX_IN: "final_",
                        WF_OUTPUT_FOLDER: None,
                        WF_WORKBOOKS_OUT: {},
                        WF_PREFIX_OUT: None
                    }

```
