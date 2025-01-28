from src.shared.errors.business import BusinessError
from src.shared.logging.log import Logger
from src.student.domain.repository import ById, StudentRepository
from src.student.domain.model import Student

logger = Logger(__name__)


class DropStudent:
    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def execute(self, student_id: str) -> Student:
        logger.info(f"About to drop a student: id={student_id}")

        query = ById(id=student_id)
        student = await self.student_repository.get(query=query)

        try:
            dropped_student = student.deactivate()
        except BusinessError as error:
            logger.error(error)
            raise error

        await self.student_repository.save(student=dropped_student)

        return dropped_student
