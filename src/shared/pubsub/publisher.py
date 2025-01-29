from abc import ABC, abstractmethod


class Publisher(ABC):
    @abstractmethod
    async def publish(self, subscription: str, data: dict) -> None:
        pass
