from src.student.domain.repository import Query, StudentRepository
from src.student.domain.model import Student


class StudentQueryHandler:
    def __init__(self, students: StudentRepository):
        self.students = students

    async def get(self, query: Query) -> Student:
        return await self.students.get(query=query)

    async def find(self, query: Query) -> Student | None:
        return await self.students.find(query=query)

    async def list(self) -> list[Student]:
        return await self.students.list()
