import logging
from typing import Dict
from typing import Set

from scripbozo.Channel import Channel
from scripbozo.Config import Config
from scripbozo.interfaces.LanguageModel import LanguageModel
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.Pipeline import Pipeline
from scripbozo.util.CustomLogger import CustomLogger
from scripbozo.util.StringUtils import contains_self_mention
from twitchio import Message


class MessageHandler:
    """
    Receives input from a chat server, tokenizes it, passes it to the model,
    then sends a reply if one is generated.
    """

    _config: Config
    model: LanguageModel
    tokenizer: Tokenizer
    channels: Dict[str, Channel] = {}
    ignored_channels: Set[str] = set()
    log: logging.Logger = CustomLogger(__name__).get_logger()

    def __init__(
        self, config: Config, model: LanguageModel, tokenizer: Tokenizer
    ) -> None:
        self._config = config
        self.model: LanguageModel = model
        self.tokenizer: Tokenizer = tokenizer

    def should_reply(self, message: Message) -> bool:
        if not message.content:
            self.log.debug("Message has no content, ignoring.")
            return False

        if message.channel.name in self.ignored_channels:
            self.log.info("Channel is ignored, ignoring message.")
            return False

        if not contains_self_mention(message.content):
            return False

        channel: Channel = self.get_channel(message.channel.name)
        if channel.is_offline_only() and channel.is_online:
            self.log.info("Channel is online, ignoring message.")
            return False

        if channel.frequencyLimit.is_rate_limited():
            self.log.info("Rate limited, ignoring message.")
            return False

        return True

    def ignore_channel(self, channel_name: str) -> None:
        self.log.info(f"Ignoring channel {channel_name}")
        self.ignored_channels.add(channel_name)

    def unignore_channel(self, channel_name: str) -> None:
        if channel_name in self.ignored_channels:
            self.log.info(f"Unignoring channel {channel_name}")
            self.ignored_channels.remove(channel_name)

    def get_channel(self, channel_name: str) -> Channel:
        if channel_name not in self.channels:
            self.channels[channel_name] = Channel(self._config, channel_name)

        return self.channels[channel_name]

    async def handle_message(self, message: Message) -> None:
        channel: Channel = self.get_channel(message.channel.name)
        await channel.add_message(message)

        if self.should_reply(message):
            await self.handle_reply(message, channel)

    async def handle_reply(self, message: Message, channel: Channel) -> None:
        response: str | None = Pipeline(
            self._config, self.model, self.tokenizer, channel
        ).reply(message)

        if response is not None:
            self.log.info(
                f"(#{message.channel.name}) Replying to {message.author.name}:"
                f" {response}"
            )

            await channel.frequencyLimit.tick()
            channel.volumeLimit.tick()

            await message.channel.send(response)
