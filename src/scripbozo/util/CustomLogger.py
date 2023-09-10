import logging
import sys
from logging import Formatter
from logging import Handler
from logging import Logger
from typing import List

import src.scripbozo.Config as Config

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

    @staticmethod
    def make_handlers() -> list[Handler]:
        handlers: List[Handler] = []
        if Config.LOG_FILE:
            handlers.append(CustomLogger.make_file_handler(Config.LOG_FILE))
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
