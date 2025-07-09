# Diff Details

Date : 2025-07-08 00:00:55

Directory c:\\Users\\ppain\\repos\\python\\p3_budman

Total : 41 files,  3001 codes, 643 comments, 92 blanks, all 3736 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [budget\_model\_logging\_config.jsonc](/budget_model_logging_config.jsonc) | JSON with Comments | 1 | 0 | 0 | 1 |
| [level\_2\_categories.csv](/level_2_categories.csv) | CSV | 248 | 0 | 1 | 249 |
| [main.py](/main.py) | Python | 4 | 0 | 0 | 4 |
| [pyrightconfig.json](/pyrightconfig.json) | JSON | 1 | 0 | 0 | 1 |
| [settings.toml](/settings.toml) | TOML | 2 | 0 | 1 | 3 |
| [src/budget\_domain\_model/README.md](/src/budget_domain_model/README.md) | Markdown | -40 | 0 | -10 | -50 |
| [src/budget\_domain\_model/budget\_domain\_model.py](/src/budget_domain_model/budget_domain_model.py) | Python | -538 | -300 | -34 | -872 |
| [src/budget\_domain\_model/budget\_domain\_model\_config.py](/src/budget_domain_model/budget_domain_model_config.py) | Python | -14 | 7 | -1 | -8 |
| [src/budget\_domain\_model/get\_budget\_model\_template.py](/src/budget_domain_model/get_budget_model_template.py) | Python | -4 | -24 | -3 | -31 |
| [src/budget\_storage\_model/\_\_init\_\_.py](/src/budget_storage_model/__init__.py) | Python | 2 | 0 | 0 | 2 |
| [src/budget\_storage\_model/budget\_storage\_model.py](/src/budget_storage_model/budget_storage_model.py) | Python | 50 | 33 | 2 | 85 |
| [src/budget\_storage\_model/csv\_data\_collection.py](/src/budget_storage_model/csv_data_collection.py) | Python | -9 | 5 | 0 | -4 |
| [src/budman\_app/budman\_app.py](/src/budman_app/budman_app.py) | Python | 62 | 41 | 9 | 112 |
| [src/budman\_cli\_view/budman\_cli\_parser.py](/src/budman_cli_view/budman_cli_parser.py) | Python | 69 | 17 | 13 | 99 |
| [src/budman\_cli\_view/budman\_cli\_view.py](/src/budman_cli_view/budman_cli_view.py) | Python | 17 | 48 | 1 | 66 |
| [src/budman\_command\_processor/\_\_init\_\_.py](/src/budman_command_processor/__init__.py) | Python | 10 | 6 | 4 | 20 |
| [src/budman\_command\_processor/budman\_cp\_namespace.py](/src/budman_command_processor/budman_cp_namespace.py) | Python | 61 | 44 | 11 | 116 |
| [src/budman\_command\_processor/workflow\_commands.py](/src/budman_command_processor/workflow_commands.py) | Python | 26 | 15 | 4 | 45 |
| [src/budman\_data\_context/budget\_domain\_model\_working\_data.py](/src/budman_data_context/budget_domain_model_working_data.py) | Python | 15 | 2 | -1 | 16 |
| [src/budman\_data\_context/budman\_data\_context.py](/src/budman_data_context/budman_data_context.py) | Python | 30 | 10 | 3 | 43 |
| [src/budman\_data\_context/budman\_data\_context\_base\_ABC.py](/src/budman_data_context/budman_data_context_base_ABC.py) | Python | 14 | 4 | 3 | 21 |
| [src/budman\_data\_context/budman\_data\_context\_binding\_class.py](/src/budman_data_context/budman_data_context_binding_class.py) | Python | 21 | 12 | 5 | 38 |
| [src/budman\_namespace/\_\_init\_\_.py](/src/budman_namespace/__init__.py) | Python | 2 | 0 | 0 | 2 |
| [src/budman\_namespace/bdm\_workbook\_class.py](/src/budman_namespace/bdm_workbook_class.py) | Python | 74 | 26 | -2 | 98 |
| [src/budman\_namespace/design\_language\_namespace.py](/src/budman_namespace/design_language_namespace.py) | Python | 11 | 1 | 0 | 12 |
| [src/budman\_settings/budman\_settings.py](/src/budman_settings/budman_settings.py) | Python | 15 | 7 | 0 | 22 |
| [src/budman\_settings/budman\_settings\_constants.py](/src/budman_settings/budman_settings_constants.py) | Python | 1 | 1 | 1 | 3 |
| [src/budman\_view\_model/budman\_view\_model.py](/src/budman_view_model/budman_view_model.py) | Python | -53 | 138 | -2 | 83 |
| [src/budman\_workflows/\_\_init\_\_.py](/src/budman_workflows/__init__.py) | Python | 62 | 4 | 0 | 66 |
| [src/budman\_workflows/budget\_categorization.py](/src/budman_workflows/budget_categorization.py) | Python | -26 | -82 | -2 | -110 |
| [src/budman\_workflows/budget\_category\_mapping.py](/src/budman_workflows/budget_category_mapping.py) | Python | -21 | 61 | 11 | 51 |
| [src/budman\_workflows/budget\_intake.py](/src/budman_workflows/budget_intake.py) | Python | 127 | 76 | 16 | 219 |
| [src/budman\_workflows/txn\_category.py](/src/budman_workflows/txn_category.py) | Python | 107 | 117 | 9 | 233 |
| [src/budman\_workflows/workflow\_utils.py](/src/budman_workflows/workflow_utils.py) | Python | 266 | 135 | 6 | 407 |
| [src/docs/Architecture V4.drawio](/src/docs/Architecture%20V4.drawio) | Draw.io | 2,135 | 0 | 0 | 2,135 |
| [src/docs/BudgetManagerDesignLanguage.md](/src/docs/BudgetManagerDesignLanguage.md) | Markdown | 20 | 0 | 8 | 28 |
| [src/scripts/bdm\_store.py](/src/scripts/bdm_store.py) | Python | 72 | 19 | -1 | 90 |
| [src/scripts/doit.py](/src/scripts/doit.py) | Python | 27 | 3 | 6 | 36 |
| [src/scripts/fooey.py](/src/scripts/fooey.py) | Python | -12 | 40 | 5 | 33 |
| [src/scripts/show\_categories.py](/src/scripts/show_categories.py) | Python | 4 | 1 | 1 | 6 |
| [src/scripts/txn\_cats.py](/src/scripts/txn_cats.py) | Python | 162 | 176 | 28 | 366 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details