from typing import AsyncGenerator
from dataclasses import dataclass
from datetime import date

from src.invoice.application.use_cases.create_invoice import (
    CreateInvoice,
    Request as CreateInvoiceRequest,
)
from src.school.domain.errors import InvalidSchoolStatusError
from src.school.domain.enrollment import (
    ActiveEnrollmentProjection,
    Enrollment,
    EnrollmentRepository,
)
from src.shared.logging.log import Logger
from src.school.domain.repository import ByIdAndActive, SchoolRepository

logger = Logger(__name__)


@dataclass
class Request:
    school_id: str
    period: date


class GenerateInvoices:
    def __init__(
        self,
        schools: SchoolRepository,
        enrollments: EnrollmentRepository,
        create_invoice: CreateInvoice,
    ):
        self.schools = schools
        self.enrollments = enrollments
        self.create_invoice = create_invoice

    async def execute(self, request: Request) -> Enrollment:
        logger.info(
            f"About to generate invoices school: school_id={request.school_id}, period={request.period}"
        )

        school_query = ByIdAndActive(id=request.school_id)
        school = await self.schools.get(query=school_query)

        if not school.is_active():
            error = InvalidSchoolStatusError(school_id=request.school_id)

            logger.error(error.message, error.attributes)

            raise error

        async for _, enrollments in self.list_active_enrollments(school_id=school.id):
            for enrollment in enrollments:
                await self.__generate_invoice(enrollment, request.period)

    async def __generate_invoice(
        self, enrollment: ActiveEnrollmentProjection, period: date
    ):
        create_invoice_request = CreateInvoiceRequest(
            school_id=enrollment.school_id,
            student_id=enrollment.student_id,
            amount=enrollment.monthly_fee,
            period=period,
        )
        await self.create_invoice.execute(request=create_invoice_request)

    async def list_active_enrollments(
        self, school_id: str
    ) -> AsyncGenerator[tuple[str, list[ActiveEnrollmentProjection]], None]:
        cursor = None

        while True:
            next_cursor, enrollments = await self.enrollments.list_active(
                school_id=school_id, cursor=cursor
            )

            yield next_cursor, enrollments

            if not next_cursor:
                break

            cursor = next_cursor
