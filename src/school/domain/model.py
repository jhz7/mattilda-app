from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.school.domain.errors import InvalidStatusError
from src.shared.contact.model import Contact


class SchoolStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass
class School:
    id: str
    name: str
    contact: Contact
    status: SchoolStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def of(
        id: str,
        name: str,
        contact: Contact,
        at: datetime = datetime.now(),
    ):
        return School(
            id, name, contact, status=SchoolStatus.ACTIVE, created_at=at, updated_at=at
        )

    def deactivate(self, at: datetime = datetime.now()) -> "School":
        if SchoolStatus.ACTIVE != self.status:
            raise InvalidStatusError(student_id=self.id)

        self.status = SchoolStatus.INACTIVE
        self.updated_at = at

        return self
