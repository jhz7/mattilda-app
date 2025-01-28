from fastapi import APIRouter, Depends

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
from src.school.infrastructure.api.http.dto import CreateSchoolDto, UpdateSchoolDto


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
