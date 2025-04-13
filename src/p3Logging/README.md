# p3Logging Package

Brought to you by Paul Painter Python (3p). Created to do hands-on learning about the Python `logging` module.

## Overview

tbd.

## Showing the Logging Configuration

As a visual learner, seeing the visual structure is helpful. So, module `p3LogInfo` has some functions to quickly print a visual, text depiction of the current configuration of loggers, handlers, formatters, etc.

```python
show_logging_setup(config_file:str)
root_logger: Level: DEBUG, Propagate: True, Handlers(1), Filters(0), Formatters(0), Children(1), Parent('None')
  child: PyExcelBudget_logger: Level: NOTSET, Propagate: True, Handlers(0), Filters(0), Formatters(0), Children(0), Parent('root')
  child: PyExcelBudget_logger: Level: NOTSET, Propagate: True, Handlers(0), Filters(0), Formatters(0), Children(0), Parent('root')

root
  |
  +- Handlers
  |     |
  |     +- StreamHandlerType: info
  |     |
  |     +- FileHandlerType: info
  |     |
  |     +- QueueHandlerType: info (inspect listener for Handlers)
  |                |
  |                + Hanlders
  +- Formatters
  |     |
  |     +- formatter: info
  |     |
  |     +- formatter: info
  |
  +- children
  |     |
  |     +- child: info
  |     |
  |     +- child: info

```
