from abc import ABC, abstractmethod
from typing import Callable, Coroutine

AsyncCallbackType = Callable[[str], Coroutine[None, None, None]]
"""A callback type which receives a str and returns a Coroutine of None, so, it is awaitable"""


class Subscriber(ABC):
    @abstractmethod
    async def subscribe(self, subscription: str, process: AsyncCallbackType) -> None:
        pass
