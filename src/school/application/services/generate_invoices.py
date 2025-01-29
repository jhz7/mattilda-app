from typing import AsyncGenerator
from dataclasses import dataclass
from datetime import date, datetime

from src.shared.job.model import JobItemResult, StartedJobItem
from src.shared.job.executor import JobExecutor
from src.invoice.application.use_cases.create_invoice import (
    CreateInvoice,
    Request as CreateInvoiceRequest,
)
from src.school.domain.errors import InvalidSchoolStatusError
from src.school.domain.enrollment import (
    ActiveEnrollmentProjection,
    BySchoolId,
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
        job_executor: JobExecutor,
    ):
        self.schools = schools
        self.enrollments = enrollments
        self.create_invoice = create_invoice
        self.job_executor = job_executor

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

        await self.job_executor.run(
            job_id=f"generate-invoices|school:{request.school_id}|period:{request.period}",
            job_name="GenerateInvoices",
            generator=self.__generate_invoices(request),
        )

    async def __generate_invoices(
        self, request: Request
    ) -> AsyncGenerator[JobItemResult, None]:
        cursor = None

        while True:
            next_cursor, enrollments = await self.enrollments.list_active(
                query=BySchoolId(request.school_id), cursor=cursor
            )

            for enrollment in enrollments:
                yield await self.__generate_invoice(enrollment, request.period)

            if not next_cursor:
                break

            cursor = next_cursor

    async def __generate_invoice(
        self, enrollment: ActiveEnrollmentProjection, period: date
    ) -> JobItemResult:
        started_job_item = StartedJobItem(
            id=f"erollment:{enrollment.id}|period:{period}",
            started_at=datetime.now(),
        )

        try:
            create_invoice_request = CreateInvoiceRequest(
                school_id=enrollment.school_id,
                student_id=enrollment.student_id,
                amount=enrollment.monthly_fee,
                due_date=period,
            )
            await self.create_invoice.execute(request=create_invoice_request)

            return started_job_item.succeeded(finished_at=datetime.now())
        except Exception as error:
            return started_job_item.failed(finished_at=datetime.now(), error=str(error))
