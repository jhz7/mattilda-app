from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.school.domain.errors import InvalidSchoolStatusError
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
        if not self.is_active():
            raise InvalidSchoolStatusError(school_id=self.id)

        self.status = SchoolStatus.INACTIVE
        self.updated_at = at

        return self

    def is_active(self) -> bool:
        return self.status == SchoolStatus.ACTIVE
