import atexit
import sys
import json
import logging.config
from pathlib import Path


def setup_logging() -> None:
    config_file = Path(__file__).parent / "config.json"
    with open(config_file, "r") as f:
        config = json.load(f)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def get_db_logger() -> logging.Logger:
    logger = logging.getLogger("db_population")
    logger.setLevel(logging.DEBUG)
    return logger
