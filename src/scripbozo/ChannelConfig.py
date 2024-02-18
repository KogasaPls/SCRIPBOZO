import configparser


class ChannelConfig:
    _config: configparser.SectionProxy

    def __init__(self, config: configparser.SectionProxy) -> None:
        self._config = config

    def name(self):
        return self._config.get("DEFAULT", "name")

    def rate_limit_seconds(self) -> int:
        return self._config.getint("rate_limit_seconds", 30)

    def rate_limit_volume(self) -> int:
        return self._config.getint("rate_limit_volume", 50)
