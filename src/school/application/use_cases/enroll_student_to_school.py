from dataclasses import dataclass
from decimal import Decimal

from src.shared.errors.application import AlreadyExistsError
from src.school.domain.errors import InvalidEnrollmentError
from src.school.domain.enrollment import Enrollment, EnrollmentRepository
from src.shared.logging.log import Logger
from src.school.domain.repository import ByIdAndActive, SchoolRepository
from src.student.domain.repository import ById, StudentRepository

logger = Logger(__name__)


@dataclass
class Request:
    school_id: str
    student_id: str
    monthly_fee: Decimal


class EnrollStudentToSchool:
    def __init__(
        self,
        schools: SchoolRepository,
        enrollments: EnrollmentRepository,
        students: StudentRepository,
    ):
        self.schools = schools
        self.students = students
        self.enrollments = enrollments

    async def execute(self, request: Request) -> Enrollment:
        logger.info(
            f"About to enroll student to school: school_id={request.school_id}, student_id={request.student_id}"
        )

        exists_enrollment = await self.enrollments.exists(
            school_id=request.school_id, student_id=request.student_id
        )

        if exists_enrollment:
            error = AlreadyExistsError(
                resource="Enrollment",
                attributes={
                    "school_id": request.school_id,
                    "student_id": request.student_id,
                },
            )

            logger.error(error)

            raise error

        school_query = ByIdAndActive(id=request.school_id)
        school = await self.schools.get(query=school_query)

        student_query = ById(id=request.student_id)
        student = await self.students.get(query=student_query)

        if not school.is_active() or not student.is_active():
            error = InvalidEnrollmentError(
                school_id=request.school_id, student_id=request.student_id
            )

            logger.error(error.message, error.attributes)

            raise error

        enrollment = Enrollment.of(
            school_id=request.school_id,
            student_id=request.student_id,
            monthly_fee=request.monthly_fee,
        )

        return await self.enrollments.save(enrollment)
