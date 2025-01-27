from dataclasses import asdict
from src.shared.errors.application import AlreadyExistsError
from src.shared.logging.log import Logger
from src.student.domain.repository import ByIdentity, StudentRepository
from src.student.domain.model import NewStudent, Student

logger = Logger(__name__)


class RegisterStudent:
    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def execute(self, student: NewStudent) -> Student:
        query = ByIdentity(identity=student.identity)
        exists_student = await self.student_repository.exists(query=query)

        if exists_student:
            error = AlreadyExistsError(
                resource="Student", attributes=asdict(student.identity)
            )

            logger.error(error)

            raise error

        registered_student = await self.student_repository.add(student)

        return registered_student
