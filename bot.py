import argparse
import logging
from argparse import Namespace

from src.GPT2Model import GPT2Model
from src.GPT2Tokenizer import GPT2Tokenizer
from src.MessageHandler import MessageHandler
from src.util.CustomLogger import CustomLogger
from src.util.EnvDefault import ArgParser
from src.util.TwitchAuth import TwitchAuth
from twitchio.ext import commands

log: logging.Logger = CustomLogger(__name__).get_logger()


def get_args_from_env() -> argparse.Namespace:
    arg_parser: ArgParser = ArgParser()
    arg_parser.add_argument("--nick", envvar="NICK")
    arg_parser.add_argument("--client_id", envvar="CLIENT_ID")
    arg_parser.add_argument("--client_secret", envvar="CLIENT_SECRET")
    arg_parser.add_argument("--initial_channels", envvar="CHANNELS")
    return arg_parser.parse_args()


class Bot(commands.Bot):
    args: Namespace = get_args_from_env()
    handler: MessageHandler
    auth: TwitchAuth = TwitchAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
    )

    def __init__(self, message_handler: MessageHandler) -> None:
        self.handler = message_handler
        super().__init__(
            client_secret=self.args.client_secret,
            client_id=self.args.client_id,
            nick=self.args.nick,
            initial_channels=self.args.initial_channels.split(","),
            token=self.auth.get_token(),
            prefix="!",
        )

    async def event_ready(self) -> None:
        log.info(f"Logged in as {self.nick}")

    async def event_message(self, message) -> None:
        await handler.handle_message(message)


if __name__ == "__main__":
    handler: MessageHandler = MessageHandler(GPT2Model(), GPT2Tokenizer())
    bot: Bot = Bot(handler)
    bot.run()
