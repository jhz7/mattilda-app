from pydantic import BaseModel

from src.shared.contact.model import ContactDto
from src.student.domain.model import IdentityKind


class CreateStudentDto(BaseModel):
    first_name: str
    last_name: str
    age: int
    identity_kind: IdentityKind
    identity_code: str
    contact: ContactDto


class PartialContactDto(BaseModel):
    email: str | None
    phone: str | None
    address: str | None


class UpdateStudentDto(BaseModel):
    first_name: str | None
    last_name: str | None
    age: int | None
    contact: PartialContactDto