from abc import ABCMeta
from abc import abstractmethod
from logging import Logger
from typing import Any

from src.util.CustomLogger import CustomLogger

log: Logger = CustomLogger(__name__).get_logger()


class Tokenizer(metaclass=ABCMeta):
    def __init__(self) -> None:
        log.debug("init")

    @abstractmethod
    def encode(self, message: str) -> Any:
        pass

    @abstractmethod
    def decode(self, tokenized: Any) -> str:
        pass
