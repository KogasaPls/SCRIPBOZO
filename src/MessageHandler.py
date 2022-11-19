import logging

from src.interfaces.LanguageModel import LanguageModel
from src.interfaces.Tokenizer import Tokenizer
from src.MessageIgnorer import MessageIgnorer
from src.Pipeline import Pipeline
from src.util.Channel import Channel
from src.util.Channel import ChannelList
from src.util.CustomLogger import CustomLogger
from src.util.StringUtils import contains_self_mention
from twitchio import Message

log: logging.Logger = CustomLogger(__name__).get_logger()


def should_reply(message: Message) -> bool:
    if not message.content:
        return False

    return contains_self_mention(message.content)


class MessageHandler:
    """
    Receives input from a chat server, tokenizes it, passes it to the model,
    then sends a reply if one is generated.
    """

    model: LanguageModel
    tokenizer: Tokenizer
    channels: ChannelList = ChannelList()

    def __init__(self, model: LanguageModel, tokenizer: Tokenizer) -> None:
        self.model: LanguageModel = model
        self.tokenizer: Tokenizer = tokenizer

    async def handle_message(self, message: Message) -> None:
        if MessageIgnorer(message).should_ignore():
            return

        channel: Channel = self.channels.get_channel(message.channel.name)
        channel.debug(f"{message.author.name}: {message.content}")

        await channel.add_message(message)

        if should_reply(message):
            await self.handle_reply(message, channel)

    async def handle_reply(self, message: Message, channel: Channel) -> None:
        if channel.frequencyLimit.is_rate_limited():
            log.info("Rate limited, ignoring message.")
            return

        await channel.frequencyLimit.tick()
        response: str | None = Pipeline(self.model, self.tokenizer, channel).reply(message)

        if response is not None:
            channel.log(f"Replying to {message.author.name}: {response}")
            await message.channel.send(response)
            channel.volumeLimit.tick()
