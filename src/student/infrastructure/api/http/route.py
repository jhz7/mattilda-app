from fastapi import APIRouter, Depends

from src.shared.id.generator import IdGenerator
from src.shared.id.ulid_generator import get_id_generator
from src.student.domain.repository import ById, StudentRepository
from src.student.infrastructure.persistence.sqlalchemy.repository import (
    get_student_repository,
)
from src.student.application.use_cases.register_student import (
    RegisterStudent,
    Request as RegisterStudentRequest,
)
from src.student.domain.model import Identity
from src.student.application.use_cases.student_query_handler import StudentQueryHandler
from src.student.application.use_cases.drop_student import DropStudent
from src.student.application.use_cases.update_student import (
    UpdateStudent,
    Request as UpdateStudentRequest,
)
from src.student.infrastructure.api.http.dto import CreateStudentDto, UpdateStudentDto


router = APIRouter()


def get_register_student_use_case(
    id_generator: IdGenerator = Depends(get_id_generator),
    student_repository: StudentRepository = Depends(get_student_repository),
) -> RegisterStudent:
    return RegisterStudent(
        student_repository=student_repository, id_generator=id_generator
    )


def get_drop_student_use_case(
    student_repository: StudentRepository = Depends(get_student_repository),
) -> RegisterStudent:
    return DropStudent(student_repository=student_repository)


def get_update_student_use_case(
    id_generator: IdGenerator = Depends(get_id_generator),
    student_repository: StudentRepository = Depends(get_student_repository),
) -> RegisterStudent:
    return UpdateStudent(
        student_repository=student_repository, id_generator=id_generator
    )


def get_student_query_handler(
    student_repository: StudentRepository = Depends(get_student_repository),
) -> StudentQueryHandler:
    return StudentQueryHandler(student_repository=student_repository)


@router.post("/students")
async def create_student(
    dto: CreateStudentDto,
    use_case: RegisterStudent = Depends(get_register_student_use_case),
):
    request = RegisterStudentRequest(
        first_name=dto.first_name,
        last_name=dto.last_name,
        age=dto.age,
        identity=Identity(kind=dto.identity_kind, code=dto.identity_code),
        email=dto.contact.email,
        phone=dto.contact.phone,
        address=dto.contact.address,
    )
    registered_student = await use_case.execute(request)

    return registered_student


@router.delete("/students/{id}")
async def delete_student(
    id: str,
    use_case: DropStudent = Depends(get_drop_student_use_case),
):
    registered_student = await use_case.execute(student_id=id)

    return registered_student


@router.patch("/students/{id}")
async def update_student(
    id: str,
    dto: UpdateStudentDto,
    use_case: UpdateStudent = Depends(get_update_student_use_case),
):
    request = UpdateStudentRequest(
        id=id,
        age=dto.age,
        first_name=dto.first_name,
        last_name=dto.last_name,
        email=dto.contact.email,
        phone=dto.contact.phone,
        address=dto.contact.address,
    )
    updated_student = await use_case.execute(request)

    return updated_student


@router.get("/students/{id}")
async def get_student(
    id: str,
    query_handler: StudentQueryHandler = Depends(get_student_query_handler),
):
    student = await query_handler.get(query=ById(id=id))

    return student


@router.get("/students")
async def get_students(
    query_handler: StudentQueryHandler = Depends(get_student_query_handler),
):
    students = await query_handler.list()

    return students
