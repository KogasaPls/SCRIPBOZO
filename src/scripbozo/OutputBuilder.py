import random
from logging import Logger

from scripbozo.Channel import Channel
from scripbozo.Config import Config
from scripbozo.interfaces.LanguageModel import LanguageModel
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.util.CustomLogger import CustomLogger
from torch import Tensor
from typing_extensions import Self

log: Logger = CustomLogger(__name__).get_logger()


def roll(p: float) -> bool:
    return random.uniform(0, 1) < p


class OutputBuilder:
    _config: Config
    channel: Channel
    model: LanguageModel
    tokenizer: Tokenizer
    input: Tensor

    def __init__(self, config: Config):
        self._config = config

    def is_output_valid(self, line: str) -> bool:
        """Require a series of conditions with a specified chance of ignoring a failed check."""
        return (
            len(line) > 0
            and (" " in line or roll(0.5))
            and (len(line) >= 3 or roll(0.25))
            and (len(line) <= self._config.output_max_length() or roll(0.1))
            and ("@" not in line or roll(0.05))
        )

    def with_channel(self, channel: Channel) -> Self:
        self.channel = channel
        return self

    def with_model(self, model: LanguageModel) -> Self:
        self.model = model
        return self

    def with_tokenizer(self, tokenizer: Tokenizer) -> Self:
        self.tokenizer = tokenizer
        return self

    def with_input(self, input_tokens: Tensor | None = None) -> Self:
        if input_tokens is not None:
            self.input = input_tokens
        return self

    def build(self) -> str:
        return self.generate_until_valid()

    def generate_until_valid(self) -> str:
        i: int = 0
        max_retries: int = self._config.bot_max_retries_for_reply()
        while i < max_retries:
            i += 1
            try:
                generated: Tensor = self.model.generate(self.input)
                decoded: str = (
                    self.tokenizer.decode(generated)
                    .replace("\n", "")
                    .replace("<|endoftext|>", "")
                    .strip()
                )
                if self.is_output_valid(decoded):
                    return decoded
            except Exception as e:
                log.info(f"Error while generating: {e}")
                pass

        return "I don't know what to say!"
