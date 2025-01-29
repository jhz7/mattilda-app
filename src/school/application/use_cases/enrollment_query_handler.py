from src.school.domain.enrollment import (
    ActiveEnrollmentProjection,
    Enrollment,
    EnrollmentRepository,
    EnrollmentsQuery,
)


class EnrollmentQueryHandler:
    def __init__(self, enrollments: EnrollmentRepository):
        self.enrollments = enrollments

    async def get(self, school_id: str, student_id: str) -> Enrollment:
        return await self.enrollments.get(student_id=student_id, school_id=school_id)

    async def find(self, school_id: str, student_id: str) -> Enrollment | None:
        return await self.enrollments.find(student_id=student_id, school_id=school_id)

    async def list(
        self, query: EnrollmentsQuery, next_cursor: str | None
    ) -> tuple[str | None, list[ActiveEnrollmentProjection]]:
        return await self.enrollments.list_active(query=query, cursor=next_cursor)
