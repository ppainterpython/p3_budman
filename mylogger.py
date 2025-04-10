#------------------------------------------------------------------------------+
# Attribution: Borrowed from James Murphy at mCoding LLC
# https://github.com/mCodingLLC/VideosSampleCode.git
#------------------------------------------------------------------------------+
import datetime as dt
from  dateutil import tz
import json
import logging
from typing import override

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

_ALL =  ('N', 'D', 'I', 'W', 'E', 'C')
ABBREVIATED_LOGGING_LEVELS = _ALL
#------------------------------------------------------------------------------+
#region JSONOutputFormatter class
class JSONOutputFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        # In a logging Formatter, this method conversts the LogRecord 
        # to a string.
        message = self._prepare_log_dict(record) 
        # Convert the extracted message dictionary to a JSON string.
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        # Extract a loggine.LogRecord to a dictionary.
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message
#endregion JSONOutputFormatter class
#------------------------------------------------------------------------------+
#region NonErrorFilter class
class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO
#endregion NonErrorFilter class    
#------------------------------------------------------------------------------+
#region ModuleOrClassFormatter class
class ModuleOrClassFormatter(logging.Formatter):
    '''Format logging messages to include module or class name.'''
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        try:
            super().__init__()
            self.fmt_keys = fmt_keys if fmt_keys is not None else {}
        except Exception as e:
            raise RuntimeError(f"ModuleOrClassFormatter: {e}") from e

    @override
    def format(self, record: logging.LogRecord) -> str:
        # In a logging Formatter, this method conversts the LogRecord 
        # to a string.
        #region Notes about the format string
        # See the section README.md#Logging-Format-Keys for the format keys.
        # "{timestamp}:{levelname}:[{process}:{thread}]: {module}.{funcName}() {message}",
        # "{asctime}.{msecs:03.0f}:{levelname}:[{process}:{thread}]: {class}.{method}() {message}",
        #endregion Notes about the format string
        message = self._prepare_log_dict(record) 
        # Convert the extracted message dictionary to a JSON string.
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        # Extract a loggine.LogRecord to a dictionary.
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(timespec="milliseconds"),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message
#endregion ModuleOrClassFormatter class
#------------------------------------------------------------------------------+
  