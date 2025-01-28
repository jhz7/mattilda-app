from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.shared.contact.model import Contact
from src.student.domain.errors import InvalidStatusError


class IdentityKind(Enum):
    CURP = "CURP"
    PASSPORT = "PASSPORT"


@dataclass
class Identity:
    kind: IdentityKind
    code: str


class StudentStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass
class Student:
    id: str
    first_name: str
    last_name: str
    age: int
    contact: Contact
    identity: Identity
    status: StudentStatus
    created_at: datetime
    updated_at: datetime

    def deactivate(self, at: datetime = datetime.now()) -> "Student":
        if not self.is_active():
            raise InvalidStatusError(student_id=self.id)

        self.status = StudentStatus.INACTIVE
        self.updated_at = at

        return self

    def is_active(self) -> bool:
        return StudentStatus.ACTIVE == self.status

    @staticmethod
    def of(
        id: str,
        first_name: str,
        last_name: str,
        age: int,
        contact: Contact,
        identity: Identity,
        at: datetime = datetime.now(),
    ) -> "Student":
        return Student(
            id=id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            contact=contact,
            identity=identity,
            status=StudentStatus.ACTIVE,
            created_at=at,
            updated_at=at,
        )
