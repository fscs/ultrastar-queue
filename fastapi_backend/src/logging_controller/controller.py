import atexit
import json
import logging.config
import pathlib


def setup_logging() -> None:
    config_file = pathlib.Path("fastapi_backend/src/logging_controller/config.json")
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
