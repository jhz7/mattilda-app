from fastapi import APIRouter, Depends

from src.invoice.infrastructure.api.http.dto import (
    AddInvoicePaymentDto,
    CreateInvoiceDto,
)
from src.invoice.application.use_cases.add_invoice_payment import AddInvoicePayment
from src.invoice.application.use_cases.cancel_invoice import (
    CancelInvoice,
    Request as CancelInvoiceRequest,
)
from src.invoice.application.use_cases.fail_invoice_payment import (
    FailInvoicePayment,
    Request as FailInvoicePaymentRequest,
)
from src.invoice.application.use_cases.invoice_query_handler import InvoiceQueryHandler
from src.invoice.application.use_cases.succeed_invoice_payment import (
    SucceedInvoicePayment,
    Request as SucceedInvoicePaymentRequest,
)
from src.invoice.application.use_cases.create_invoice import CreateInvoice
from src.invoice.domain.repository import (
    All,
    ById,
    BySchoolId,
    ByStudentId,
    InvoiceRepository,
)
from src.invoice.infrastructure.persistence.sqlalchemy.repository import (
    get_invoice_repository,
)
from src.school.domain.repository import SchoolRepository
from src.school.infrastructure.persistence.sqlalchemy.repository import (
    get_school_repository,
)
from src.shared.id.generator import IdGenerator
from src.shared.id.ulid_generator import get_id_generator
from src.student.domain.repository import StudentRepository
from src.student.infrastructure.persistence.sqlalchemy.repository import (
    get_student_repository,
)


router = APIRouter()


def get_create_invoice_use_case(
    student_repository: StudentRepository = Depends(get_student_repository),
    school_repository: SchoolRepository = Depends(get_school_repository),
    invoice_repository: InvoiceRepository = Depends(get_invoice_repository),
) -> CreateInvoice:
    return CreateInvoice(
        students=student_repository,
        schools=school_repository,
        invoices=invoice_repository,
    )


def get_add_invoice_payment_use_case(
    id_generator: IdGenerator = Depends(get_id_generator),
    invoice_repository: InvoiceRepository = Depends(get_invoice_repository),
) -> AddInvoicePayment:
    return AddInvoicePayment(
        id_generator=id_generator,
        invoices=invoice_repository,
    )


def get_cancel_invoice_use_case(
    invoice_repository: InvoiceRepository = Depends(get_invoice_repository),
) -> CancelInvoice:
    return CancelInvoice(invoices=invoice_repository)


def get_succeed_invoice_payment_use_case(
    invoice_repository: InvoiceRepository = Depends(get_invoice_repository),
) -> SucceedInvoicePayment:
    return SucceedInvoicePayment(invoices=invoice_repository)


def get_fail_invoice_payment_use_case(
    invoice_repository: InvoiceRepository = Depends(get_invoice_repository),
) -> FailInvoicePayment:
    return FailInvoicePayment(invoices=invoice_repository)


def get_invoice_query_handler(
    invoice_repository: InvoiceRepository = Depends(get_invoice_repository),
) -> InvoiceQueryHandler:
    return InvoiceQueryHandler(invoices=invoice_repository)


@router.post("/invoices")
async def create_invoice(
    dto: CreateInvoiceDto,
    use_case: CreateInvoice = Depends(get_create_invoice_use_case),
):
    request = dto.as_create_invoice_request()
    created_invoice = await use_case.execute(request)

    return created_invoice


@router.post("/invoices/{id}/payments/")
async def create_payment(
    id: str,
    dto: AddInvoicePaymentDto,
    use_case: AddInvoicePayment = Depends(get_add_invoice_payment_use_case),
):
    request = dto.as_add_invoice_payment_request(invoice_id=id)

    invoice = await use_case.execute(request)

    return invoice


@router.patch("/invoices/{invoice_id}/payments/{payment_id}/succeed")
async def update_payment_succeed(
    invoice_id: str,
    payment_id: str,
    use_case: SucceedInvoicePayment = Depends(get_succeed_invoice_payment_use_case),
):
    request = SucceedInvoicePaymentRequest(
        id=invoice_id,
        payment_id=payment_id,
    )
    invoice = await use_case.execute(request)

    return invoice


@router.patch("/invoices/{invoice_id}/payments/{payment_id}/fail")
async def update_payment_failed(
    invoice_id: str,
    payment_id: str,
    use_case: FailInvoicePayment = Depends(get_fail_invoice_payment_use_case),
):
    request = FailInvoicePaymentRequest(
        id=invoice_id,
        payment_id=payment_id,
    )
    invoice = await use_case.execute(request)

    return invoice


@router.delete("/invoices/{id}")
async def delete_invoice(
    id: str,
    use_case: CancelInvoice = Depends(get_cancel_invoice_use_case),
):
    request = CancelInvoiceRequest(id=id)
    canceled_invoice = await use_case.execute(request)

    return canceled_invoice


@router.get("/invoices/{id}")
async def get_invoice(
    id: str,
    query_handler: InvoiceQueryHandler = Depends(get_invoice_query_handler),
):
    invoice = await query_handler.find(query=ById(id=id))

    return invoice


@router.get("/invoices")
async def get_invoices(
    school_id: str | None = None,
    student_id: str | None = None,
    query_handler: InvoiceQueryHandler = Depends(get_invoice_query_handler),
):
    query = (
        BySchoolId(school_id=school_id)
        if school_id
        else ByStudentId(student_id=student_id) if student_id else None
    )

    if query is None:
        raise ValueError("School id or student id is required")

    return await query_handler.account_statement(query=query)
