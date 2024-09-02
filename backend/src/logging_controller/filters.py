import logging
from typing import override


class OnlyInfoFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno == logging.INFO
