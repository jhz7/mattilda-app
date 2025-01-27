from src.student.domain.repository import Query, StudentRepository
from src.student.domain.model import Student


class StudentQueryHandler:
    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def get(self, query: Query) -> Student:
        return await self.student_repository.get(query=query)

    async def find(self, query: Query) -> Student | None:
        return await self.student_repository.find(query=query)

    async def list(self) -> list[Student]:
        return await self.student_repository.list()
