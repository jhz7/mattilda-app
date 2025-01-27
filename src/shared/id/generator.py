from abc import ABC, abstractmethod


class IdGenerator(ABC):
    @abstractmethod
    async def generate(self) -> str:
        pass
