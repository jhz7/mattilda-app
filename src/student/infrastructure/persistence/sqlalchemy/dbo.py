from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.contact.model import ContactDbo
from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel
from src.student.domain.model import Identity, Student, StudentStatus


class StudentDbo(BaseSqlModel):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    identity_kind: Mapped[str] = mapped_column()
    identity_code: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

    # Foreign Key linking to ContactDbo
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), unique=True)

    # Relationship to ContactDbo
    contact: Mapped[ContactDbo] = relationship("ContactDbo", lazy="joined")

    __table_args__ = (
        UniqueConstraint("identity_kind", "identity_code", name="uq_identity_idx"),
    )

    @staticmethod
    def from_domain(student: Student, at: datetime = datetime.now()) -> "StudentDbo":
        return StudentDbo(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            identity_kind=student.identity.kind.name,
            identity_code=student.identity.code,
            age=student.age,
            status=StudentStatus.ACTIVE.value,
            contact_id=student.contact.id,
            created_at=at,
            updated_at=at,
        )

    def as_domain(self) -> Student:
        return Student(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            identity=Identity(kind=self.identity_kind, code=self.identity_code),
            age=self.age,
            status=StudentStatus(self.status),
            contact=self.contact.as_domain(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
