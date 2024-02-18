import tomllib
from os import PathLike
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from scripbozo.ChannelConfig import ChannelConfig
from scripbozo.ModelConfig import ModelConfig


class Config:
    _config: Dict[str, Any]

    def __init__(self, config: Dict[str, Any] | None) -> None:
        self._config = config if config is not None else {}

    @staticmethod
    def from_file(file_path: PathLike[str]):
        file_path = Path(file_path)
        if not (file_path.is_file()):
            raise Exception(f"File does not exist: {file_path}")

        with open(file_path, "r") as f:
            config = tomllib.loads(f.read())

        return Config(config)

    def __get_or_add_section(self, section_name: str) -> Dict[str, Any]:
        if section_name not in self._config:
            self._config[section_name] = {}
        return self._config[section_name]

    def __twitch(self) -> Dict[str, Any]:
        return self.__get_or_add_section("Twitch")

    def __bot(self) -> Dict[str, Any]:
        return self.__get_or_add_section("Bot")

    def __model(self) -> Dict[str, Any]:
        return self.__get_or_add_section("Model")

    def __generation(self) -> Dict[str, Any]:
        return self.__get_or_add_section("Generation")

    def twitch_auth_json(self) -> str:
        return self.__twitch().get("auth_json", "twitch_auth.json").strip(" '\"")

    def bot_input_message_max_chars(self) -> int:
        return self.__bot().get("input_message_max_chars", 200)

    def bot_max_retries_for_reply(self) -> int:
        return self.__bot().get("max_retries_for_reply", 50)

    def bot_output_max_length(self) -> int:
        return self.__bot().get("output_max_length", 255)

    def model_output_max_tokens(self) -> int:
        return self.__model().get("output_max_tokens", 64)

    def channels(self) -> Dict[str, Dict[str, Any]]:
        return self.__get_or_add_section("Channels")

    def channel(self, channel_name: str) -> ChannelConfig:
        channel = self.channels().get(channel_name, {})
        return ChannelConfig(channel, channel_name)

    def model(self) -> ModelConfig:
        return ModelConfig(self.__model())

    def generation_prompt_duplication_factor(self) -> int:
        return self.__generation().get("prompt_duplication_factor", 3)

    def users(self) -> Dict[str, Dict[str, Any]]:
        return self.__get_or_add_section("Users")

    def users_bots(self) -> Dict[str, List[str]]:
        return self.users().get("Bots", [])

    def users_ignored(self) -> Dict[str, List[str]]:
        return self.users().get("Ignored", [])

    def users_privileged(self) -> Dict[str, List[str]]:
        return self.users().get("Privileged", [])
