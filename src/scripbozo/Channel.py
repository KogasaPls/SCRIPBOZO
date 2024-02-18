import logging
from dataclasses import dataclass

from scripbozo.ChannelConfig import ChannelConfig
from scripbozo.Config import Config
from scripbozo.FrequencyLimiter import FrequencyLimiter
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.MessageStack import MessageStack
from scripbozo.util.CustomLogger import CustomLogger
from scripbozo.VolumeLimiter import VolumeLimiter
from torch import Tensor
from twitchio import Message


@dataclass
class Channel:
    _config: ChannelConfig
    frequencyLimit: FrequencyLimiter
    volumeLimit: VolumeLimiter
    messages: MessageStack
    log: logging.Logger = CustomLogger(__name__).get_logger()

    def __init__(self, config: Config, channel_name: str):
        self._config = config.channel(channel_name)
        self.name = channel_name
        self.frequencyLimit = FrequencyLimiter(self._config.rate_limit_seconds())
        self.volumeLimit = VolumeLimiter(self._config.rate_limit_volume())
        self.messages = MessageStack(config.model_output_max_tokens())

    def __str__(self) -> str:
        return f"#{self._config.name()}"

    async def add_message(self, message: Message) -> None:
        self.volumeLimit.increment()
        await self.messages.add_message(message)

    def get_tokens(self, tokenizer: Tokenizer) -> Tensor:
        return self.messages.tokenize(tokenizer)
