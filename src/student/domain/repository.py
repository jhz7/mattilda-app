from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from src.shared.errors.application import NotFoundError
from src.student.domain.model import Identity, NewStudent, Student


class Query(ABC):
    pass


@dataclass
class ById(Query):
    id: str


@dataclass
class ByIdentity(Query):
    identity: Identity


class StudentRepository(ABC):
    async def get(self, query: Query) -> Student:
        found_student = await self.find(query)

        if found_student is None:
            raise NotFoundError(resource="Student", attributes=asdict(query))

        return found_student

    @abstractmethod
    async def find(self, query: Query) -> Student | None:
        pass

    @abstractmethod
    async def list(self) -> list[Student]:
        pass

    @abstractmethod
    async def add(self, student: NewStudent) -> Student:
        pass
