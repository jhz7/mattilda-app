from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from src.shared.errors.application import NotFoundError
from src.school.domain.model import School, SchoolStatus


class SchoolQuery(ABC):
    pass


class SchoolsQuery(ABC):
    pass


@dataclass
class ById(SchoolQuery):
    id: str


@dataclass
class ByEmail(SchoolQuery):
    email: str


@dataclass
class ByStatus(SchoolsQuery):
    status: SchoolStatus


class SchoolRepository(ABC):
    async def get(self, query: SchoolQuery) -> School:
        found_school = await self.find(query)

        if found_school is None:
            raise NotFoundError(resource="School", attributes=asdict(query))

        return found_school

    @abstractmethod
    async def exists(self, query: SchoolQuery) -> bool:
        pass

    @abstractmethod
    async def find(self, query: SchoolQuery) -> School | None:
        pass

    @abstractmethod
    async def list(self, query: SchoolsQuery) -> list[School]:
        pass

    @abstractmethod
    async def save(self, school: School) -> School:
        pass
