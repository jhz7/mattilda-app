from dataclasses import asdict, dataclass

from src.shared.contact.model import Contact
from src.shared.id.generator import IdGenerator
from src.shared.errors.application import AlreadyExistsError
from src.shared.logging.log import Logger
from src.student.domain.repository import ByIdentity, StudentRepository
from src.student.domain.model import Identity, Student

logger = Logger(__name__)


@dataclass
class Request:
    first_name: str
    last_name: str
    age: int
    identity: Identity
    email: str
    phone: str
    address: str


class RegisterStudent:
    def __init__(
        self, student_repository: StudentRepository, id_generator: IdGenerator
    ):
        self.id_generator = id_generator
        self.student_repository = student_repository

    async def execute(self, request: Request) -> Student:
        logger.info(f"About to register student: identity={asdict(request.identity)}")

        query = ByIdentity(identity=request.identity)
        exists_student = await self.student_repository.exists(query=query)

        if exists_student:
            error = AlreadyExistsError(resource="Student", attributes=asdict(request))

            logger.error(error)

            raise error

        contact_id = await self.id_generator.generate()
        contact = Contact(
            id=contact_id,
            email=request.email,
            phone=request.phone,
            address=request.address,
        )
        student_id = await self.id_generator.generate()
        new_student = Student.of(
            id=student_id,
            age=request.age,
            contact=contact,
            identity=request.identity,
            last_name=request.last_name,
            first_name=request.first_name,
        )

        registered_student = await self.student_repository.add(new_student)

        return registered_student
