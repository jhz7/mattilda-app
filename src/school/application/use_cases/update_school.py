from dataclasses import asdict, dataclass

from src.shared.contact.model import Contact
from src.shared.id.generator import IdGenerator
from src.shared.logging.log import Logger
from src.school.domain.repository import ById, SchoolRepository
from src.school.domain.model import School

logger = Logger(__name__)


@dataclass
class Request:
    id: str
    name: str | None
    email: str | None
    phone: str | None
    address: str | None


class UpdateSchool:
    def __init__(self, schools: SchoolRepository, id_generator: IdGenerator):
        self.schools = schools
        self.id_generator = id_generator

    async def execute(self, request: Request) -> School:
        logger.info(f"About to update a school: request={asdict(request)}")

        query = ById(id=request.id)
        school = await self.schools.get(query=query)

        if request.name is not None:
            school.name = request.name

        contact = await self._build_contact(request)

        if contact is not None:
            school.contact = contact

        updated_school = await self.schools.save(school)

        return updated_school

    async def _build_contact(self, request: Request) -> Contact | None:
        if request.email is None or request.phone is None or request.address is None:
            return None

        contact_id = await self.id_generator.generate()
        contact = Contact(
            id=contact_id,
            email=request.email,
            phone=request.phone,
            address=request.address,
        )

        return contact
