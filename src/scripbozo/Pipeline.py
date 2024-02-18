import logging

from scripbozo.Channel import Channel
from scripbozo.Config import Config
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
        return (
            OutputBuilder(self._config)
            .with_model(self.model)
            .with_tokenizer(self.tokenizer)
            .with_input(input_tokens)
            .build()
        )
