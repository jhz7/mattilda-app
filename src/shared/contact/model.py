from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel


class ContactDto(BaseModel):
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    address: Annotated[str, Field(min_length=5, max_length=255)]


class PartialContactDto(BaseModel):
    email: str | None
    phone: str | None
    address: str | None


@dataclass
class Contact:
    id: str
    email: str
    phone: str
    address: str


class ContactDbo(BaseSqlModel):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

    def as_domain(self) -> Contact:
        return Contact(
            id=self.id,
            email=self.email,
            phone=self.phone,
            address=self.address,
        )

    @staticmethod
    def from_domain(domain: Contact, at: datetime = datetime.now()) -> "ContactDbo":
        return ContactDbo(
            id=domain.id,
            email=domain.email,
            phone=domain.phone,
            address=domain.address,
            created_at=at,
            updated_at=at,
        )
    
    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
