import logging
import sys
from logging import Formatter
from logging import Handler
from logging import Logger

import src.Config as Config

LOG_FORMAT: str = "[%(asctime)s] (%(levelname)s) %(name)s: %(message)s"
DATE_FORMAT: str = "%H:%M:%S"


class CustomLogger:
    name: str
    level: str

    def __init__(self, name: str, level: str = Config.DEFAULT_LOG_LEVEL) -> None:
        self.name = name
        self.level = level
        self.setup(level)

    def setup(self, level: str) -> None:
        logger: Logger = logging.getLogger()
        stream_handler: Handler = self.make_handler()

        logging.Formatter(LOG_FORMAT)
        logger.setLevel(level)

        self.set_handler_if_not_set(stream_handler)

        logger.info("Started logger.")

    def get_logger(self) -> Logger:
        return logging.getLogger(self.name)

    def clear_handlers(self) -> None:
        logging.getLogger(self.name).handlers.clear()

    def set_handler_if_not_set(self, handler: Handler) -> None:
        current_handlers: list[Handler] = logging.getLogger(self.name).handlers
        desired_handlers: list[Handler] = [handler]
        if current_handlers != desired_handlers:
            self.clear_handlers()
            logging.getLogger(self.name).addHandler(handler)

    @staticmethod
    def make_handler() -> Handler:
        handler: Handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(Formatter(LOG_FORMAT, DATE_FORMAT))
        return handler
