import logging

from torch import Tensor
from twitchio import Message

import src.Config as Config
from src.Channel import Channel
from src.interfaces.LanguageModel import LanguageModel
from src.interfaces.Tokenizer import Tokenizer
from src.OutputBuilder import OutputBuilder
from src.util.CustomLogger import CustomLogger
from src.util.StringUtils import remove_self_mentions
from src.util.TensorBuilder import TensorBuilder

log: logging.Logger = CustomLogger(__name__).get_logger()


class Pipeline:
    model: LanguageModel
    tokenizer: Tokenizer
    channel: Channel

    log: logging.Logger = CustomLogger(__name__).get_logger()

    def __init__(
        self, model: LanguageModel, tokenizer: Tokenizer, channel: Channel
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.channel = channel

    def reply(self, message: Message) -> str | None:
        self.log_message(message)
        assert message.content

        text_to_encode: str = remove_self_mentions(message.content)
        tokenized_message: Tensor = self.tokenizer.encode(text_to_encode)
        channel_history: Tensor = self.channel.get_tokens(self.tokenizer)

        input_tokens: Tensor = (
            TensorBuilder()
            .append(channel_history)
            .append_n_times(tokenized_message, Config.PROMPT_DUPLICATION_FACTOR)
            .left_trim_to_size(Config.MODEL_MAX_TOKENS)
            .build()
        )

        return self.generate(input_tokens)

    def log_message(self, message: Message) -> None:
        self.log.info(
            f"(#{message.channel.name}) {message.author.name}: {message.content}"
        )

    def generate(self, input_tokens: Tensor | None = None) -> str:
        return (
            OutputBuilder()
            .with_model(self.model)
            .with_tokenizer(self.tokenizer)
            .with_input(input_tokens)
            .build()
        )
