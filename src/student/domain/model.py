from dataclasses import dataclass, field
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
    contact: list[Contact]
    identity: Identity
    status: StudentStatus = StudentStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    def deactivate(self, at: datetime = datetime.now()) -> "Student":
        if StudentStatus.ACTIVE != self.status:
            raise InvalidStatusError(student_id=self.id)

        self.status = StudentStatus.INACTIVE
        self.updated_at = at

        return self


@dataclass
class NewStudent(Student):
    id: str = field(init=False)
    status: StudentStatus = field(init=False)
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
