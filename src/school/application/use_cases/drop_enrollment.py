from dataclasses import dataclass

from src.school.domain.enrollment import Enrollment, EnrollmentRepository
from src.shared.logging.log import Logger

logger = Logger(__name__)


@dataclass
class Request:
    school_id: str
    student_id: str


class DropEnrollment:
    def __init__(
        self,
        enrollments: EnrollmentRepository,
    ):
        self.enrollments = enrollments

    async def execute(self, request: Request) -> Enrollment:
        logger.info(
            f"About to drop enrollment: school_id={request.school_id}, student_id={request.student_id}"
        )

        enrollment = await self.enrollments.get(
            school_id=request.school_id, student_id=request.student_id
        )

        enrollment = enrollment.delete()

        return await self.enrollments.save(enrollment)
