from abc import ABC, abstractmethod

from src.shared.job.model import JobExecutionResult


class JobRepository(ABC):
    @abstractmethod
    async def save(self, result: JobExecutionResult) -> None:
        pass
