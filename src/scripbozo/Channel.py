import logging
from dataclasses import dataclass
from dataclasses import field
from typing import List

import scripbozo.Config as Config
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.MessageStack import MessageStack
from scripbozo.RateLimiterImpl import FrequencyLimiter
from scripbozo.RateLimiterImpl import VolumeLimiter
from scripbozo.util.CustomLogger import CustomLogger
from torch import Tensor
from twitchio import Message


@dataclass
class Channel:
    name: str
    messages: MessageStack = field(default_factory=lambda: MessageStack())
    frequencyLimit: FrequencyLimiter = field(
        default_factory=lambda: FrequencyLimiter(Config.RATE_LIMIT_SECONDS)
    )
    volumeLimit: VolumeLimiter = field(
        default_factory=lambda: VolumeLimiter(Config.RATE_LIMIT_VOLUME)
    )

    log: logging.Logger = CustomLogger(__name__).get_logger()

    def __str__(self) -> str:
        return f"#{self.name}"

    async def add_message(self, message: Message) -> None:
        self.volumeLimit.increment()
        await self.messages.add_message(message)

    def get_tokens(self, tokenizer: Tokenizer) -> Tensor:
        return self.messages.tokenize(tokenizer)


class ChannelList(List[Channel]):
    def __init__(self) -> None:
        super().__init__()

    def contains(self, name: str) -> bool:
        for channel in self:
            if channel.name == name:
                return True
        return False

    def get_channel(self, name: str) -> Channel:
        for channel in self:
            if channel.name == name:
                return channel

        channel = Channel(name)
        self.append(channel)
        return channel

    def get_channel_if_exists(self, name: str) -> Channel | None:
        for channel in self:
            if channel.name == name:
                return channel
        return None

    def add_channel(self, channel: Channel) -> None:
        self.append(channel)

    def remove_channel(self, channel: Channel) -> None:
        self.remove(channel)
