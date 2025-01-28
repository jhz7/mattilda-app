from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal

from src.invoice.domain.errors import InvalidInvoicePartiesError
from src.school.domain.repository import ByIdAndActive, SchoolRepository
from src.shared.errors.application import AlreadyExistsError
from src.shared.logging.log import Logger
from src.invoice.domain.repository import ById, InvoiceRepository
from src.invoice.domain.model import Invoice
from src.student.domain.repository import ById as StudentById, StudentRepository

logger = Logger(__name__)


@dataclass
class Request:
    school_id: str
    student_id: str
    amount: Decimal
    due_date: date


class CreateInvoice:
    def __init__(
        self,
        students: StudentRepository,
        schools: SchoolRepository,
        invoices: InvoiceRepository,
    ):
        self.schools = schools
        self.students = students
        self.invoices = invoices

    async def execute(self, request: Request) -> Invoice:
        logger.info(f"About to create an invoice: request={asdict(request)}")

        invoice_id = Invoice.build_id(
            school_id=request.school_id,
            student_id=request.student_id,
            due_date=request.due_date,
        )
        exists_invoice = await self.invoices.exists(query=ById(id=invoice_id))

        if exists_invoice:
            error = AlreadyExistsError(
                resource="Invoice",
                attributes={
                    "school_id": request.school_id,
                    "student_id": request.student_id,
                    "due_date": request.due_date,
                },
            )

            logger.error(error)

            raise error

        school_query = ByIdAndActive(id=request.school_id)
        school = await self.schools.get(query=school_query)

        student_query = StudentById(id=request.student_id)
        student = await self.students.get(query=student_query)

        if not school.is_active() or not student.is_active():
            error = InvalidInvoicePartiesError(
                school_id=request.school_id, student_id=request.student_id
            )

            logger.error(error.message, error.attributes)

            raise error

        event, new_invoice = Invoice.of(
            student_id=student.id,
            school_id=school.id,
            amount=request.amount,
            due_date=request.due_date,
        )

        await self.invoices.update(event)

        return new_invoice
