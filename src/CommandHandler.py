from src.Command import Command
from twitchio import Channel
from twitchio import Message


class CommandHandler:
    """
    Handles commands sent to the bot.
    """

    @staticmethod
    def try_parse_command(message: Message) -> Command | None:
        if not (message.content.startswith("!")):
            return None

        key: str = message.content.split(" ")[0][1:]
        try:
            return Command(key)
        except ValueError:
            return None
