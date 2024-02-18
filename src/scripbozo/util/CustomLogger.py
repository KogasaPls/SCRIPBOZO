import logging
import sys
from logging import Formatter
from logging import Handler
from logging import Logger
from typing import List

LOG_FORMAT: str = "[%(asctime)s] (%(levelname)s) %(name)s: %(message)s"
DATE_FORMAT: str = "%H:%M:%S"


class CustomLogger:
    name: str
    level: str
    log_file: str | None

    def __init__(
        self, name: str, level: str = "INFO", log_file: str | None = None
    ) -> None:
        self.name = name
        self.level = level
        self.log_file = log_file
        self.setup(level)

    def setup(self, level: str) -> None:
        logger: Logger = logging.getLogger()
        handlers: List[Handler] = self.make_handlers()

        logging.Formatter(LOG_FORMAT)
        logger.setLevel(level)

        self.set_handlers_if_not_set(handlers)

        logger.info("Started logger.")

    def get_logger(self) -> Logger:
        return logging.getLogger(self.name)

    def clear_handlers(self) -> None:
        logging.getLogger(self.name).handlers.clear()

    def set_handlers_if_not_set(self, handlers: List[Handler]) -> None:
        current_handlers: list[Handler] = logging.getLogger(self.name).handlers
        if current_handlers != handlers:
            self.clear_handlers()
            self.set_handlers(handlers)

    def set_handlers(self, handlers: List[Handler]) -> None:
        for handler in handlers:
            logging.getLogger(self.name).addHandler(handler)

    def make_handlers(self) -> list[Handler]:
        handlers: List[Handler] = []
        if self.log_file:
            handlers.append(CustomLogger.make_file_handler(self.log_file))
        handlers.append(CustomLogger.make_stdout_handler())
        return handlers

    @staticmethod
    def make_stdout_handler() -> Handler:
        handler: Handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(Formatter(LOG_FORMAT, DATE_FORMAT))
        return handler

    @staticmethod
    def make_file_handler(filename: str) -> Handler:
        handler: Handler = logging.FileHandler(filename)
        handler.setFormatter(Formatter(LOG_FORMAT, DATE_FORMAT))
        return handler
