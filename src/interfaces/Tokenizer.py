from abc import ABCMeta
from abc import abstractmethod
from typing import Any


class Tokenizer(metaclass=ABCMeta):
    @abstractmethod
    def encode(self, message: str) -> Any:
        pass

    @abstractmethod
    def decode(self, tokenized: Any) -> str:
        pass
