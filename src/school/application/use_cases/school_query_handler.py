from src.school.domain.repository import SchoolRepository, SchoolQuery, SchoolsQuery
from src.school.domain.model import School


class SchoolQueryHandler:
    def __init__(self, schools: SchoolRepository):
        self.schools = schools

    async def get(self, query: SchoolQuery) -> School:
        return await self.schools.get(query=query)

    async def find(self, query: SchoolQuery) -> School | None:
        return await self.schools.find(query=query)

    async def list(self, query: SchoolsQuery) -> list[School]:
        return await self.schools.list(query=query)
