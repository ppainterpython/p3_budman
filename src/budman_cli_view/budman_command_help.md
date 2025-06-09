# Budget Manager Command Line Interface

## Budget Manager Command Map

When a command is sent from the View to the View Model Command Processing
interface, the full command key is mapped to a method call to implement
the command function. Here is the mapping:

```python
# Use the following cmd_map to dispatch the command for execution.
self.cmd_map = {
    "init_cmd_fin_inst": self.FI_init_cmd,
    "save_cmd_workbooks": self.FI_LOADED_WORKBOOKS_save_cmd,
    "load_cmd_BDM_STORE": self.BDM_STORE_load,
    "save_cmd_BDM_STORE": self.BDM_STORE_save,
}
```

## Budget Manager Help Content

Here is the latest output from the help commands in Budget Manager.

```text
p3budman> load -h
Usage: load [-h] {BDM_STORE, store, bms, BMS, budget_manager_store, workbooks, wb, WB} ...

Load data in the Budget Manager application.

optional arguments:
  -h, --help            show this help message and exit
subcommands:
  {BDM_STORE, store, bms, BMS, budget_manager_store, workbooks, wb, WB}
subcommands:
  {BDM_STORE, store, bms, BMS, budget_manager_store, workbooks, wb, WB}
    BDM_STORE (store, bms, BMS, budget_manager_store, BDM_STORE)
                        Load the Budget Manager Store file.
    workbooks (wb, WB)  Load workbook information.

p3budman> load wb -h
Usage: load workbooks [-h] [-fi [FI_KEY]] [-wf [WF_KEY]] [wb_ref]

positional arguments:
  wb_ref        Workbook reference, name or number from show workbooks.

optional arguments:
  -h, --help    show this help message and exit
  -fi [FI_KEY]  FI key value.
  -wf [WF_KEY]  WF key value.

p3budman> wf -h

Apply a workflow to Budget Manager data.

optional arguments:
  -h, --help            show this help message and exit

Common Arguments:
  Arguments common to all commands.

  --parse-only, -po     Command is only parsed with results returned.
  --validate-only, -vo  Command args are only validated with results returned, but no cmd execution.
  -wi, --what-if        Return details about what the command would do, but don't to any action.

subcommands:
  {check, ch, reload, r, categorization, cat, CAT, c}
    check (ch)          Check some aspect of the workflow data or processing.
    reload (r)          Reload modules.
    categorization (cat, CAT, c)
                        Apply Categorization workflow.
p3budman> wf cat -h
Usage: workflow categorization [-h] [--parse-only] [--validate-only] [-wi] [wb_ref]

positional arguments:
  wb_ref                Workbook reference as either the name or number of a loaded workbook.

optional arguments:
  -h, --help            show this help message and exit

Common Arguments:
  Arguments common to all commands.

  --parse-only, -po     Command is only parsed with results returned.
  --validate-only, -vo  Command args are only validated with results returned, but no cmd execution.
  -wi, --what-if        Return details about what the command would do, but don't to any action.



```
