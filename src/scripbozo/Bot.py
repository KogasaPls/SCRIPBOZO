import argparse
import logging
import sys
import traceback
from argparse import Namespace

from scripbozo.Command import Command
from scripbozo.CommandHandler import CommandHandler
from scripbozo.Config import Config
from scripbozo.GPT2Model import GPT2Model
from scripbozo.GPT2Tokenizer import GPT2Tokenizer
from scripbozo.MessageHandler import MessageHandler
from scripbozo.TwitchAuth import TwitchAuth
from scripbozo.util.CustomLogger import CustomLogger
from scripbozo.util.EnvDefault import ArgParser
from twitchio import Message
from twitchio.ext import commands
from twitchio.ext import routines

log: logging.Logger = CustomLogger(__name__).get_logger()


def get_args_from_env() -> argparse.Namespace:
    arg_parser: ArgParser = ArgParser()
    arg_parser.add_argument("--config", envvar="CONFIG", default="config.toml")
    arg_parser.add_argument("--nick", envvar="NICK")
    arg_parser.add_argument("--client_id", envvar="CLIENT_ID")
    arg_parser.add_argument("--client_secret", envvar="CLIENT_SECRET")
    arg_parser.add_argument("--initial_channels", envvar="CHANNELS")
    return arg_parser.parse_args()


class Bot(commands.Bot):
    _config: Config
    offline_only_channels: list[str]
    message_handler: MessageHandler
    args: Namespace = get_args_from_env()
    auth: TwitchAuth

    def __init__(self) -> None:
        self._config = Config.from_file(self.args.config)
        self.offline_only_channels = ["moonmoon", "kogasapls"]
        self.message_handler = self.create_message_handler()
        self.auth = TwitchAuth(
            self._config,
            client_id=self.args.client_id,
            client_secret=self.args.client_secret,
        )
        super().__init__(
            client_secret=self.args.client_secret,
            client_id=self.args.client_id,
            nick=self.args.nick,
            initial_channels=[],  # self.args.initial_channels.split(","),
            token=self.auth.get_token(),
            prefix="!",
        )

    def create_message_handler(self) -> MessageHandler:
        model: GPT2Model = GPT2Model(self._config.model())
        tokenizer: GPT2Tokenizer = GPT2Tokenizer()
        model.newline_token_id = tokenizer.wrappedTokenizer.encode("\n")
        return MessageHandler(self._config, model, tokenizer)

    async def event_stream_online(self, data) -> None:
        log.info(f"Stream online: {data}")
        channel: str = data["broadcaster"].lower()
        if channel in self.offline_only_channels:
            self.message_handler.ignore_channel(channel)

    async def event_stream_offline(self, data) -> None:
        log.info(f"Stream offline: {data}")
        channel = data["broadcaster"].lower()
        if channel in self.offline_only_channels:
            self.message_handler.unignore_channel(channel)

    async def event_ready(self) -> None:
        log.info(f"Logged in as {self.nick}")
        await self.ignore_channels()

        channels_to_join = self.args.initial_channels.split(",")
        await self.join_channels(channels_to_join)

    async def ignore_channels(self) -> None:
        live_channels = await self.fetch_streams(
            user_logins=self.offline_only_channels, type="live"
        )

        live_channel_names = [channel.user.name.lower() for channel in live_channels]

        for channel in self.offline_only_channels:
            if channel in live_channel_names:
                log.info(f"Channel {channel} is online")
                self.message_handler.ignore_channel(channel)
            else:
                log.info(f"Channel {channel} is offline")
                self.message_handler.unignore_channel(channel)

    async def event_message(self, message) -> None:
        if self.should_ignore_message(message):
            return

        command: Command = CommandHandler.try_parse_command(message)
        if command is not None:
            await self.handle_command(command, message)
            return

        await self.message_handler.handle_message(message)

    async def handle_command(self, command: Command, message: Message):
        if not self.is_sender_privileged(message):
            return

        log.info(f"Command: {command}")

        match command:
            case Command.HELP:
                await message.channel.send(
                    "Commands: !help, !restart, !sleep, !resume, !quit"
                )
            case Command.RESTART:
                log.info("Restarting...")
                await message.channel.send("NOOO")
                self.message_handler = self.create_message_handler()
            case Command.SLEEP:
                self.message_handler.ignore_channel(message.channel.name)
                await message.channel.send("Bedge")
            case Command.RESUME:
                self.message_handler.unignore_channel(message.channel.name)
                await message.channel.send("Wokege")
            case Command.QUIT | Command.CUM:
                await message.channel.send("moon2CL")
            case Command.MEDS:
                pass
            # new_handler = self.get_new_message_handler()

            case _:
                pass

    async def event_token_expired(self):
        self.auth.refresh_token()
        return self.auth.get_token()

    def is_sender_privileged(self, message: Message) -> bool:
        return (
            message.author.is_mod
            or message.author.is_broadcaster
            or message.author.name in self._config.users_privileged()
        )

    def should_ignore_message(self, message: Message) -> bool:
        return (
            message.echo
            or (not message.content)
            or (message.author.name.lower() == self.nick.lower())
            or (message.author.name in self._config.users_bots())
            or (message.author.name in self._config.users_ignored())
        )

    def run(self):
        super().run()

        @routines.routine(minutes=5, wait_first=True)
        async def ignore_channels():
            await self.ignore_channels()

        @self.event()
        async def event_error(error, data):
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

        @self.event()
        async def event_stream_online(data):
            log.info(f"Stream online: {data}")
            await self.event_stream_online(data)

        @self.event()
        async def event_stream_offline(data):
            log.info(f"Stream offline: {data}")
            await self.event_stream_offline(data)
