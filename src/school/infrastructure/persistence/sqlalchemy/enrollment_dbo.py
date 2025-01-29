from datetime import datetime
from decimal import Decimal
from sqlalchemy import DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.school.domain.enrollment import ActiveEnrollmentProjection, Enrollment
from src.school.infrastructure.persistence.sqlalchemy.dbo import SchoolDbo
from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel
from src.student.infrastructure.persistence.sqlalchemy.dbo import StudentDbo


class EnrollmentDbo(BaseSqlModel):
    __tablename__ = "enrollments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), nullable=False)
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), nullable=False)
    monthly_fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

    # Relationships
    student: Mapped[StudentDbo] = relationship("StudentDbo", lazy="joined")
    school: Mapped[SchoolDbo] = relationship("SchoolDbo", lazy="joined")

    @staticmethod
    def from_domain(enrollment: Enrollment) -> "EnrollmentDbo":
        return EnrollmentDbo(
            id=enrollment.id,
            student_id=enrollment.student_id,
            school_id=enrollment.school_id,
            monthly_fee=enrollment.monthly_fee,
            deleted_at=enrollment.deleted_at,
            created_at=enrollment.created_at,
            updated_at=enrollment.updated_at,
        )

    def as_domain(self) -> Enrollment:
        return Enrollment(
            id=self.id,
            student_id=self.student_id,
            school_id=self.school_id,
            monthly_fee=self.monthly_fee,
            deleted_at=self.deleted_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def as_read_projection(self) -> ActiveEnrollmentProjection:
        return ActiveEnrollmentProjection(
            id=self.id,
            student_id=self.student_id,
            school_id=self.school_id,
            monthly_fee=self.monthly_fee,
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "school_id": self.school_id,
            "monthly_fee": self.monthly_fee,
            "deleted_at": self.deleted_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def as_for_update_dict(self) -> dict:
        return {
            "id": self.id,
            "monthly_fee": self.monthly_fee,
            "deleted_at": self.deleted_at,
            "updated_at": self.updated_at,
        }
