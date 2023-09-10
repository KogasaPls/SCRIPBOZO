import logging

from twitchio import Message

from src.Channel import Channel
from src.Channel import ChannelList
from src.interfaces.LanguageModel import LanguageModel
from src.interfaces.Tokenizer import Tokenizer
from src.Pipeline import Pipeline
from src.util.CustomLogger import CustomLogger
from src.util.StringUtils import contains_self_mention


class MessageHandler:
    """
    Receives input from a chat server, tokenizes it, passes it to the model,
    then sends a reply if one is generated.
    """

    model: LanguageModel
    tokenizer: Tokenizer
    channels: ChannelList = ChannelList()
    ignored_channels: ChannelList = ChannelList()
    log: logging.Logger = CustomLogger(__name__).get_logger()

    def __init__(self, model: LanguageModel, tokenizer: Tokenizer) -> None:
        self.model: LanguageModel = model
        self.tokenizer: Tokenizer = tokenizer

    def should_reply(self, message: Message) -> bool:
        if not message.content:
            self.log.debug("Message has no content, ignoring.")
            return False
        if self.ignored_channels.contains(message.channel.name):
            self.log.debug("Channel is ignored, ignoring message.")
            return False

        return contains_self_mention(message.content)

    def ignore_channel(self, channel_name: str) -> None:
        channel: Channel = self.channels.get_channel(channel_name)
        self.log.info(f"Ignoring channel {channel_name}")
        self.ignored_channels.add_channel(channel)

    def unignore_channel(self, channel_name: str) -> None:
        channel: Channel | None = self.ignored_channels.get_channel_if_exists(
            channel_name
        )
        if channel and self.ignored_channels.contains(channel_name):
            self.log.info(f"Unignoring channel {channel_name}")
            self.ignored_channels.remove_channel(channel)

    async def handle_message(self, message: Message) -> None:
        self.log.debug(
            f"(#{message.channel.name}) {message.author.name}: {message.content}"
        )

        channel: Channel = self.channels.get_channel(message.channel.name)
        await channel.add_message(message)

        if self.should_reply(message):
            await self.handle_reply(message, channel)

    async def handle_reply(self, message: Message, channel: Channel) -> None:
        if channel.frequencyLimit.is_rate_limited():
            self.log.info(f"(#{message.channel}) Rate limited, ignoring message.")
            return

        await channel.frequencyLimit.tick()
        response: str | None = Pipeline(self.model, self.tokenizer, channel).reply(
            message
        )

        if response is not None:
            self.log.info(
                f"(#{message.channel.name}) Replying to {message.author.name}:"
                f" {response}"
            )
            await message.channel.send(response)
            channel.volumeLimit.tick()
