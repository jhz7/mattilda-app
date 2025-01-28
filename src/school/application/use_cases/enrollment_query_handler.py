from src.school.domain.enrollment import Enrollment, EnrollmentRepository


class EnrollmentQueryHandler:
    def __init__(self, enrollments: EnrollmentRepository):
        self.enrollments = enrollments

    async def get(self, school_id: str, student_id: str) -> Enrollment:
        return await self.enrollments.get(student_id=student_id, school_id=school_id)

    async def find(self, school_id: str, student_id: str) -> Enrollment | None:
        return await self.enrollments.find(student_id=student_id, school_id=school_id)

    async def list(self, school_id: str) -> list[str]:
        return await self.enrollments.list_ids(school_id=school_id)
