from typing import Any
from typing import Dict


class ChannelConfig:
    _config: Dict[str, Any]
    _channel_name: str

    def __init__(self, config: Dict[str, Any], channel_name: str) -> None:
        self._config = config
        self._channel_name = channel_name

    def name(self):
        return self._channel_name

    def rate_limit_seconds(self) -> int:
        return self._config.get("rate_limit_seconds", 30)

    def rate_limit_volume(self) -> int:
        return self._config.get("rate_limit_volume", 50)

    def offline_only(self) -> bool:
        return self._config.get("offline_only", False)
