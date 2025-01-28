from pydantic import BaseModel

from src.shared.contact.model import ContactDto


class CreateSchoolDto(BaseModel):
    name: str
    contact: ContactDto


class PartialContactDto(BaseModel):
    email: str | None
    phone: str | None
    address: str | None


class UpdateSchoolDto(BaseModel):
    name: str | None
    contact: PartialContactDto | None
