from decimal import Decimal
from pydantic import BaseModel

from src.shared.contact.model import ContactDto, PartialContactDto


class CreateSchoolDto(BaseModel):
    name: str
    contact: ContactDto


class UpdateSchoolDto(BaseModel):
    name: str | None
    contact: PartialContactDto | None


class EnrollStudentToSchoolDto(BaseModel):
    student_id: str
    monthly_fee: Decimal
