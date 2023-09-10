from abc import ABCMeta
from abc import abstractmethod
from typing import Any


class LanguageModel(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, model_input: Any) -> Any:
        pass
