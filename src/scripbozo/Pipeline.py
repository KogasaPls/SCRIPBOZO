import logging

import scripbozo.Config as Config
from scripbozo.Channel import Channel
from scripbozo.interfaces.LanguageModel import LanguageModel
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.OutputBuilder import OutputBuilder
from scripbozo.util.CustomLogger import CustomLogger
from scripbozo.util.StringUtils import remove_self_mentions
from scripbozo.util.TensorBuilder import TensorBuilder
from torch import Tensor
from twitchio import Message

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
