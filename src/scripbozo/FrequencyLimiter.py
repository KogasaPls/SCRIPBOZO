from aiolimiter import AsyncLimiter
from scripbozo.interfaces.RateLimiter import RateLimiter


class FrequencyLimiter(RateLimiter):
    """Limit frequency to once every X seconds."""

    def __init__(self, duration: int) -> None:
        self.limiter: AsyncLimiter = AsyncLimiter(1, duration)

    def is_rate_limited(self) -> bool:
        return not self.limiter.has_capacity()

    async def tick(self) -> None:
        await self.limiter.acquire()

    def reset(self) -> None:
        self.limiter._level = 0
