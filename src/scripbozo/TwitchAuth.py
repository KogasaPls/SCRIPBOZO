import logging
import os
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from math import ceil
from typing import Any

import requests
import ujson
from scripbozo.Config import Config
from scripbozo.util.CustomLogger import CustomLogger
from typing_extensions import Self

TWITCH_OAUTH_URL: str = "https://id.twitch.tv/oauth2/token"

log: logging.Logger = CustomLogger(__name__).get_logger()


@dataclass
class TwitchAuthData:
    """Data type for the response from the Twitch API."""

    data: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        return ujson.dumps(self.data)

    def save_to_file(self, path: str) -> None:
        with open(path, "w") as f:
            ujson.dump(self.data, f, indent=4)

    def from_json(self, data: str) -> Self:
        self.data = ujson.loads(data)
        return self

    def get_auth_token(self) -> str:
        return self.data["auth_token"]

    def get_expiration_time(self) -> int:
        return self.data["creation_time"] + self.data["expires_in"]

    def get_refresh_token(self) -> str:
        return self.data["refresh_token"]

    def from_response(self, response: requests.Response) -> Self:
        self.data["auth_token"] = response.json()["access_token"]
        self.data["expires_in"] = response.json()["expires_in"]
        self.data["refresh_token"] = response.json()["refresh_token"]
        self.data["creation_time"] = ceil(datetime.now().timestamp())
        return self

    def is_expired(self) -> bool:
        log.debug(
            "Refresh token expires at"
            f" {datetime.fromtimestamp(self.get_expiration_time())}."
        )
        return self.get_expiration_time() < ceil(datetime.now().timestamp())


class TwitchAuth:
    _config: Config
    client_id: str
    client_secret: str
    data: TwitchAuthData

    def __init__(self, config: Config, client_id: str, client_secret: str) -> None:
        self._config = config
        self.client_id = client_id
        self.client_secret = client_secret
        self.setup_refresh_token()

    def setup_refresh_token(self) -> None:
        try:
            file_path: str = self._config.twitch_auth_json()
            if os.path.exists(file_path):
                self.data = self.__load_from_file(file_path)
            else:
                self.data = self.__load_from_env()
        except Exception as e:
            log.exception(e)
            self.data = TwitchAuthData()

        if self.data.is_expired():
            self.refresh_token()

    @staticmethod
    def __load_from_file(file_path: str) -> TwitchAuthData:
        log.info(f"Loading auth data from {file_path}")
        with open(file_path, "r") as f:
            file: str = f.read()
            data: TwitchAuthData = TwitchAuthData().from_json(file)
            if not data:
                raise Exception("No Twitch auth data found in file.")
            return data

    @staticmethod
    def __load_from_env() -> TwitchAuthData:
        log.info("Loading auth data from environment variables.")
        data: TwitchAuthData = TwitchAuthData()
        data.data["auth_token"] = os.environ["TWITCH_AUTH_TOKEN"]
        data.data["expires_in"] = os.environ["TWITCH_AUTH_EXPIRES_IN"]
        data.data["refresh_token"] = os.environ["TWITCH_AUTH_REFRESH_TOKEN"]
        data.data["creation_time"] = os.environ["TWITCH_AUTH_CREATION_TIME"]
        return data

    def save_to_file(self) -> None:
        file_path = self._config.twitch_auth_json()
        log.info(f"Saving new auth data to {file_path}")
        self.data.save_to_file(file_path)

    def request_new_token_using_refresh(self) -> Any:
        log.info("Requesting new token using refresh token.")
        url: str = TWITCH_OAUTH_URL
        params: dict[str, str] = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.data.get_refresh_token(),
        }
        response: requests.Response = requests.post(url, params=params)
        return TwitchAuthData().from_response(response)

    def request_new_token(self) -> Any:
        log.info("Requesting new auth and refresh tokens.")

        {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.data.get_refresh_token(),
        }

    def update_data(self, data: TwitchAuthData) -> None:
        self.data = data
        self.save_to_file()

    def refresh_token(self) -> None:
        try:
            if self.refresh_token:
                log.info("Refreshing token.")
                data: TwitchAuthData = self.request_new_token_using_refresh()
                self.update_data(data)
            else:
                log.info("No refresh token, manual intervention required")

        except Exception as e:
            log.exception(e)

    def get_token(self) -> str:
        if not self.data or self.data.is_expired():
            self.refresh_token()
        return self.data.get_auth_token()
