from abc import ABCMeta
from abc import abstractmethod


class RateLimiter(metaclass=ABCMeta):
    @abstractmethod
    def is_rate_limited(self) -> bool:
        pass

    @abstractmethod
    def tick(self) -> None:
        """Method that gets triggered whenever the rate limit is passed."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Set the rate limit so that it will be passed on the next try."""
        pass
