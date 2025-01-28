from dataclasses import asdict, dataclass

from src.shared.contact.model import Contact
from src.shared.id.generator import IdGenerator
from src.shared.errors.application import AlreadyExistsError
from src.shared.logging.log import Logger
from src.school.domain.repository import ByEmail, SchoolRepository
from src.school.domain.model import School

logger = Logger(__name__)


@dataclass
class Request:
    name: str
    email: str
    phone: str
    address: str


class RegisterSchool:
    def __init__(self, schools: SchoolRepository, id_generator: IdGenerator):
        self.id_generator = id_generator
        self.schools = schools

    async def execute(self, request: Request) -> School:
        logger.info(f"About to register school: email={request.email}")

        query = ByEmail(email=request.email)
        exists_school = await self.schools.exists(query=query)

        if exists_school:
            error = AlreadyExistsError(resource="School", attributes=asdict(request))

            logger.error(error)

            raise error

        contact_id = await self.id_generator.generate()
        contact = Contact(
            id=contact_id,
            email=request.email,
            phone=request.phone,
            address=request.address,
        )
        school_id = await self.id_generator.generate()
        new_school = School.of(
            id=school_id,
            contact=contact,
            name=request.name,
        )

        registered_school = await self.schools.save(new_school)

        return registered_school
