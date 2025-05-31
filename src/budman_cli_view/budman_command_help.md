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
