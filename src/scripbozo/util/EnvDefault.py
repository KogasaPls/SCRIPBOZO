import argparse
import os

import dotenv


class EnvDefault(argparse.Action):
    """Allow argparse to use environment variables as defaults."""

    def __init__(self, envvar, required=True, default=None, **kwargs) -> None:
        current_path = os.getcwd()
        dotenv.load_dotenv(dotenv_path=f"{current_path}/.env")

        default_or_env: str | None = default or os.environ[envvar]
        is_still_required: bool = required and not default_or_env
        super(EnvDefault, self).__init__(
            default=default_or_env, required=is_still_required, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        setattr(namespace, self.dest, values)


class ArgParser(argparse.ArgumentParser):
    """Set defaults from environment variables."""

    def add_argument(self, *args, **kwargs) -> None:
        if "envvar" in kwargs:
            kwargs["action"] = EnvDefault
        super().add_argument(*args, **kwargs)
