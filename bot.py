import argparse
import logging
import sys
import traceback
from argparse import Namespace

from src.Command import Command
from src.CommandHandler import CommandHandler
from src.GPT2Model import GPT2Model
from src.GPT2Tokenizer import GPT2Tokenizer
from src.MessageHandler import MessageHandler
from src.MessageIgnorer import MessageIgnorer
from src.TwitchAuth import TwitchAuth
from src.util.CustomLogger import CustomLogger
from src.util.EnvDefault import ArgParser
from twitchio import Message
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
    message_handler: MessageHandler
    auth: TwitchAuth = TwitchAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
    )

    def get_new_message_handler(self) -> MessageHandler:
        model: GPT2Model = GPT2Model()
        tokenizer: GPT2Tokenizer = GPT2Tokenizer()
        return MessageHandler(model, tokenizer)

    def __init__(self) -> None:
        self.message_handler = self.get_new_message_handler()
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
        if MessageIgnorer(message).should_ignore():
            return

        command: Command = CommandHandler.try_parse_command(message)
        if command is not None:
            await self.handle_command(command, message)
            return

        await self.message_handler.handle_message(message)

    async def handle_command(self, command: Command, message: Message):
        if not self.is_sender_privileged(message):
            return

        print(f"Command: {command}")

        match command:
            case Command.HELP:
                await message.channel.send("Commands: !help, !restart, !sleep, !resume, !quit")
            case Command.RESTART:
                log.info("Restarting...")
                await message.channel.send("NOOO")
                self.message_handler = self.get_new_message_handler()
            case Command.SLEEP:
                self.message_handler.ignore_channel(message.channel.name)
                await message.channel.send("Bedge")
            case Command.RESUME:
                self.message_handler.unignore_channel(message.channel.name)
                await message.channel.send("Wokege")
            case Command.QUIT | Command.CUM:
                await message.channel.send("moon2CL")
            case _:
                pass

    async def event_token_expired(self):
        self.auth.refresh_token()
        return self.auth.get_token()

    def is_sender_privileged(self, message: Message) -> bool:
        return message.author.name.lower() == "kogasapls" or message.author.is_mod or message.author.is_broadcaster


if __name__ == "__main__":
    bot: Bot = Bot()
    bot.run()


    @bot.event()
    async def event_error(error, data):
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
