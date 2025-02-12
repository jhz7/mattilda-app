from fastapi import APIRouter, Depends

from src.shared.job.executor import JobExecutor
from src.shared.job.persistence.sqlalchemy.job_repository import get_job_repository
from src.shared.job.repository import JobRepository
from src.invoice.application.use_cases.create_invoice import CreateInvoice
from src.invoice.domain.repository import InvoiceRepository
from src.invoice.infrastructure.persistence.sqlalchemy.repository import (
    get_invoice_repository,
)
from src.school.application.services.generate_invoices import (
    GenerateInvoices,
    Request as GenerateInvoicesRequest,
)
from src.school.application.use_cases.enroll_student_to_school import (
    EnrollStudentToSchool,
    Request as EnrollStudentToSchoolRequest,
)
from src.school.domain.enrollment import EnrollmentRepository
from src.school.infrastructure.persistence.sqlalchemy.enrolment_repository import (
    get_enrollment_repository,
)
from src.school.domain.model import SchoolStatus
from src.shared.id.generator import IdGenerator
from src.shared.id.ulid_generator import get_id_generator
from src.school.domain.repository import ById, ByStatus, SchoolRepository
from src.school.infrastructure.persistence.sqlalchemy.repository import (
    get_school_repository,
)
from src.school.application.use_cases.register_school import (
    RegisterSchool,
    Request as RegisterSchoolRequest,
)
from src.school.application.use_cases.school_query_handler import SchoolQueryHandler
from src.school.application.use_cases.drop_school import DropSchool
from src.school.application.use_cases.update_school import (
    UpdateSchool,
    Request as UpdateSchoolRequest,
)
from src.school.infrastructure.api.http.dto import (
    BillPeriodDto,
    CreateSchoolDto,
    EnrollStudentToSchoolDto,
    UpdateSchoolDto,
)
from src.student.domain.repository import StudentRepository
from src.student.infrastructure.persistence.sqlalchemy.repository import (
    get_student_repository,
)


router = APIRouter()


def get_register_school_use_case(
    id_generator: IdGenerator = Depends(get_id_generator),
    schools_repository: SchoolRepository = Depends(get_school_repository),
) -> RegisterSchool:
    return RegisterSchool(schools=schools_repository, id_generator=id_generator)


def get_drop_school_use_case(
    schools_repository: SchoolRepository = Depends(get_school_repository),
) -> RegisterSchool:
    return DropSchool(schools=schools_repository)


def get_update_school_use_case(
    id_generator: IdGenerator = Depends(get_id_generator),
    schools_repository: SchoolRepository = Depends(get_school_repository),
) -> RegisterSchool:
    return UpdateSchool(schools=schools_repository, id_generator=id_generator)


def get_school_query_handler(
    schools_repository: SchoolRepository = Depends(get_school_repository),
) -> SchoolQueryHandler:
    return SchoolQueryHandler(schools=schools_repository)


def get_enroll_student_to_school_use_case(
    schools_repository: SchoolRepository = Depends(get_school_repository),
    students_repository: StudentRepository = Depends(get_student_repository),
    enrollment_repository: EnrollmentRepository = Depends(get_enrollment_repository),
) -> SchoolQueryHandler:
    return EnrollStudentToSchool(
        schools=schools_repository,
        enrollments=enrollment_repository,
        students=students_repository,
    )


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


def get_job_executor(
    jobs: JobRepository = Depends(get_job_repository),
) -> JobExecutor:
    return JobExecutor(jobs=jobs)


def get_generate_invoices_service(
    schools_repository: SchoolRepository = Depends(get_school_repository),
    enrollment_repository: EnrollmentRepository = Depends(get_enrollment_repository),
    create_invoice: CreateInvoice = Depends(get_create_invoice_use_case),
    job_executor: JobExecutor = Depends(get_job_executor),
) -> GenerateInvoices:
    return GenerateInvoices(
        schools=schools_repository,
        enrollments=enrollment_repository,
        create_invoice=create_invoice,
        job_executor=job_executor,
    )


@router.post("/schools")
async def create_school(
    dto: CreateSchoolDto,
    use_case: RegisterSchool = Depends(get_register_school_use_case),
):
    request = RegisterSchoolRequest(
        name=dto.name,
        email=dto.contact.email,
        phone=dto.contact.phone,
        address=dto.contact.address,
    )

    registered_school = await use_case.execute(request)

    return registered_school


@router.post("/schools/{id}/enrollments/")
async def create_enrollment(
    id: str,
    dto: EnrollStudentToSchoolDto,
    use_case: EnrollStudentToSchool = Depends(get_enroll_student_to_school_use_case),
):
    request = EnrollStudentToSchoolRequest(
        school_id=id,
        student_id=dto.student_id,
        monthly_fee=dto.monthly_fee,
    )

    enrollment = await use_case.execute(request)

    return enrollment


@router.post("/schools/{id}/invoices/")
async def create_invoices(
    id: str,
    dto: BillPeriodDto,
    use_case: GenerateInvoices = Depends(get_generate_invoices_service),
):
    request = GenerateInvoicesRequest(
        school_id=id,
        period=dto.period,
    )

    await use_case.execute(request)

    return None


@router.delete("/schools/{id}")
async def delete_school(
    id: str,
    use_case: DropSchool = Depends(get_drop_school_use_case),
):
    dropped_school = await use_case.execute(school_id=id)

    return dropped_school


@router.patch("/schools/{id}")
async def update_school(
    id: str,
    dto: UpdateSchoolDto,
    use_case: UpdateSchool = Depends(get_update_school_use_case),
):
    request = UpdateSchoolRequest(
        id=id,
        name=dto.name,
        email=dto.contact.email,
        phone=dto.contact.phone,
        address=dto.contact.address,
    )
    updated_school = await use_case.execute(request)

    return updated_school


@router.get("/schools/{id}")
async def get_school(
    id: str,
    query_handler: SchoolQueryHandler = Depends(get_school_query_handler),
):
    school = await query_handler.get(query=ById(id=id))

    return school


@router.get("/schools")
async def get_schools(
    query_handler: SchoolQueryHandler = Depends(get_school_query_handler),
):
    students = await query_handler.list(query=ByStatus(status=SchoolStatus.ACTIVE))

    return students
