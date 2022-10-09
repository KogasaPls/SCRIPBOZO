from abc import ABCMeta
from abc import abstractmethod
from typing import Any


class LanguageModel(metaclass=ABCMeta):
    """
    Abstract class for a language model. Contains abstract methods that must
    be overridden by the implementations.
    """

    model: Any

    @abstractmethod
    def generate(self, input: Any) -> Any:
        pass
