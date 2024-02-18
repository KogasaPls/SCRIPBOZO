import logging
import random

from scripbozo.Channel import Channel
from scripbozo.Config import Config
from scripbozo.interfaces.LanguageModel import LanguageModel
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.util.CustomLogger import CustomLogger
from scripbozo.util.StringUtils import remove_self_mentions
from scripbozo.util.TensorBuilder import TensorBuilder
from torch import Tensor
from twitchio import Message

log: logging.Logger = CustomLogger(__name__).get_logger()


def roll(p: float) -> bool:
    return random.uniform(0, 1) < p


class Pipeline:
    _config: Config
    model: LanguageModel
    tokenizer: Tokenizer
    channel: Channel

    log: logging.Logger = CustomLogger(__name__).get_logger()

    def __init__(
        self,
        config: Config,
        model: LanguageModel,
        tokenizer: Tokenizer,
        channel: Channel,
    ) -> None:
        self._config = config
        self.model = model
        self.tokenizer = tokenizer
        self.channel = channel

    def reply(self, message: Message) -> str | None:
        self.log_message(message)
        assert message.content

        text_to_encode: str = remove_self_mentions(message.content)[
            : self._config.bot_input_message_max_chars()
        ].strip()
        tokenized_message: Tensor = self.tokenizer.encode(text_to_encode)
        channel_history: Tensor = self.channel.get_tokens(self.tokenizer)

        input_tokens: Tensor = (
            TensorBuilder()
            .append(channel_history)
            .append_n_times(
                tokenized_message, self._config.generation_prompt_duplication_factor()
            )
            .left_trim_to_size(self._config.model().model_max_tokens())
            .build()
        )

        return self.generate(input_tokens)

    def log_message(self, message: Message) -> None:
        self.log.info(
            f"(#{message.channel.name}) {message.author.name}: {message.content}"
        )

    def generate(self, input_tokens: Tensor | None = None) -> str:
        return self.generate_until_valid(input_tokens)

    def is_output_valid(self, line: str) -> bool:
        return (
            len(line) > 0
            and (" " in line or roll(0.5))
            and (len(line) >= 3 or roll(0.25))
            and (len(line) <= self._config.output_max_length() or roll(0.1))
            and ("@" not in line or roll(0.05))
        )

    def generate_until_valid(self, input_tokens: Tensor | None) -> str:
        i: int = 0
        max_retries: int = self._config.bot_max_retries_for_reply()
        while i < max_retries:
            i += 1
            try:
                generated: Tensor = self.model.generate(input_tokens)
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
