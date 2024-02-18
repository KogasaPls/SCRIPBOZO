from scripbozo.interfaces.RateLimiter import RateLimiter


class VolumeLimiter(RateLimiter):
    """Limit frequency to once every X increments."""

    counter: int = 0
    maxVolume: int = 0

    def __init__(self, max_volume: int) -> None:
        self.maxVolume = max_volume
        self.reset()

    def tick(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.counter = self.maxVolume

    def is_rate_limited(self) -> bool:
        return self.counter < self.maxVolume

    def increment(self) -> None:
        self.counter += 1
