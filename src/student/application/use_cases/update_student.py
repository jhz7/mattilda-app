from dataclasses import asdict, dataclass

from src.shared.contact.model import Contact
from src.shared.id.generator import IdGenerator
from src.shared.logging.log import Logger
from src.student.domain.repository import ById, StudentRepository
from src.student.domain.model import Student

logger = Logger(__name__)


@dataclass
class Request:
    id: str
    first_name: str | None
    last_name: str | None
    age: int | None
    email: str | None
    phone: str | None
    address: str | None


class UpdateStudent:
    def __init__(self, students: StudentRepository, id_generator: IdGenerator):
        self.id_generator = id_generator
        self.students = students

    async def execute(self, request: Request) -> Student:
        logger.info(f"About to update a student: request={asdict(request)}")

        query = ById(id=request.id)
        student = await self.students.get(query=query)

        if request.first_name is not None:
            student.first_name = request.first_name

        if request.last_name is not None:
            student.last_name = request.last_name

        if request.age is not None:
            student.age = request.age

        contact = await self._build_contact(request)

        if contact is not None:
            student.contact = contact

        updated_student = await self.students.save(student)

        return updated_student

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
