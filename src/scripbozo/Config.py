import configparser
from os import PathLike
from pathlib import Path

from scripbozo.ChannelConfig import ChannelConfig
from scripbozo.ModelConfig import ModelConfig


class Config:
    _config: configparser.ConfigParser

    def __init__(self, config: configparser.ConfigParser) -> None:
        self._config = config

    @staticmethod
    def default():
        return Config(configparser.ConfigParser())

    @staticmethod
    def from_file(file_path: PathLike[str]):
        file_path = Path(file_path)
        if not (file_path.is_file()):
            raise Exception(f"File does not exist: {file_path}")

        config = configparser.ConfigParser()
        config.read(file_path)

        return Config(config)

    def __logging(self) -> configparser.SectionProxy:
        if not self._config.has_section("Logging"):
            self._config.add_section("Logging")
        return self._config["Logging"]

    def __twitch(self) -> configparser.SectionProxy:
        if not self._config.has_section("Twitch"):
            self._config.add_section("Twitch")
        return self._config["Twitch"]

    def __bot(self) -> configparser.SectionProxy:
        if not self._config.has_section("Bot"):
            self._config.add_section("Bot")
        return self._config["Bot"]

    def __model(self) -> configparser.SectionProxy:
        if not self._config.has_section("Model"):
            self._config.add_section("Model")
        return self._config["Model"]

    def __generation(self) -> configparser.SectionProxy:
        if not self._config.has_section("Generation"):
            self._config.add_section("Generation")
        return self._config["Generation"]

    def logging_default_log_level(self) -> str:
        return self.__logging().get("default_log_level", "INFO")

    def logging_log_file(self) -> str:
        return self.__logging().get("log_file", "log.txt")

    def twitch_auth_json(self) -> str:
        return self.__twitch().get("auth_json", "twitch_auth.json")

    def bot_input_message_max_chars(self) -> int:
        return self.__bot().getint("input_message_max_chars", 200)

    def bot_client_timeout(self) -> int:
        return self.__bot().getint("client_timeout", 10)

    def bot_max_retries_for_reply(self) -> int:
        return self.__bot().getint("max_retries_for_reply", 50)

    def output_max_length(self):
        return self.__bot().getint("output_max_length", 255)

    def model_output_max_tokens(self) -> int:
        return self.__model().getint("output_max_tokens", 64)

    def channel(self, channel_name: str) -> ChannelConfig:
        if not self._config.has_section(f"Channels.{channel_name}"):
            self._config.add_section(f"Channels.{channel_name}")
        return ChannelConfig(self._config[f"Channels.{channel_name}"])

    def model(self) -> ModelConfig:
        return ModelConfig(self.__model())

    def generation_prompt_duplication_factor(self) -> int:
        return self.__generation().getint("prompt_duplication_factor", 3)
