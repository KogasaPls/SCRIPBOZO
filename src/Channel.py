import logging
from dataclasses import dataclass
from dataclasses import field
from typing import List

from torch import Tensor

import src.Config as Config
from src.interfaces.Tokenizer import Tokenizer
from src.MessageQueue import MessageQueue
from src.RateLimiterImpl import FrequencyLimiter
from src.RateLimiterImpl import VolumeLimiter
from src.util.CustomLogger import CustomLogger
from twitchio import Message

log: logging.Logger = CustomLogger(__name__).get_logger()


@dataclass
class Channel:
    name: str
    messages: MessageQueue = field(default_factory=lambda: MessageQueue())
    frequencyLimit: FrequencyLimiter = field(
        default_factory=lambda: FrequencyLimiter(Config.RATE_LIMIT_SECONDS)
    )
    volumeLimit: VolumeLimiter = field(
        default_factory=lambda: VolumeLimiter(Config.RATE_LIMIT_VOLUME)
    )

    def __str__(self) -> str:
        return f"#{self.name}"

    async def add_message(self, message: Message) -> None:
        self.volumeLimit.increment()
        await self.messages.add_message(message)

    def get_tokens(self, tokenizer: Tokenizer) -> Tensor:
        return self.messages.tokenize(tokenizer)

    def log(self, message: str) -> None:
        log.info(f"({self}) {message}")

    def debug(self, message: str) -> None:
        log.debug(f"({self}) {message}")


class ChannelList(List[Channel]):
    def __init__(self) -> None:
        super().__init__()

    def get_channel(self, name: str) -> Channel:
        for channel in self:
            if channel.name == name:
                return channel
        return self.add_channel(name)

    def add_channel(self, name: str) -> Channel:
        channel: Channel = Channel(name)
        self.append(channel)
        return channel
