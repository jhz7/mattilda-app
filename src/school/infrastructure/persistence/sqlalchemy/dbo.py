from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.contact.model import ContactDbo
from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel
from src.school.domain.model import School, SchoolStatus


class SchoolDbo(BaseSqlModel):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

    # Foreign Key linking to ContactDbo
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), unique=True)

    # Relationship to ContactDbo
    contact: Mapped[ContactDbo] = relationship("ContactDbo", lazy="joined")

    @staticmethod
    def from_domain(school: School, at: datetime = datetime.now()) -> "SchoolDbo":
        return SchoolDbo(
            id=school.id,
            name=school.name,
            status=school.status.name,
            contact_id=school.contact.id,
            created_at=at,
            updated_at=at,
        )

    def as_domain(self) -> School:
        return School(
            id=self.id,
            name=self.name,
            status=SchoolStatus(self.status),
            contact=self.contact.as_domain(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "contact_id": self.contact_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def as_for_update_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "contact_id": self.contact_id,
            "updated_at": self.updated_at,
        }
