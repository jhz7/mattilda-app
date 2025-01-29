from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.shared.errors.application import NotFoundError
from src.school.domain.errors import InvalidEnrollmentError


@dataclass(frozen=True)
class Enrollment:
    id: str
    student_id: str
    school_id: str
    monthly_fee: Decimal
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @staticmethod
    def of(
        student_id: str,
        school_id: str,
        monthly_fee: Decimal,
        at: datetime = datetime.now(),
    ):
        return Enrollment(
            id=f"school:{school_id}/student:{student_id}",
            student_id=student_id,
            school_id=school_id,
            monthly_fee=monthly_fee,
            created_at=at,
            updated_at=at,
        )

    def adjust_fee(
        self,
        new_fee: Decimal,
        at: datetime = datetime.now(),
    ):
        if not self.is_active():
            raise InvalidEnrollmentError(
                school_id=self.school_id,
                student_id=self.student_id,
            )

        return Enrollment(
            id=self.id,
            student_id=self.student_id,
            school_id=self.school_id,
            monthly_fee=new_fee,
            created_at=self.created_at,
            updated_at=at,
        )

    def delete(
        self,
        at: datetime = datetime.now(),
    ):
        if not self.is_active():
            raise InvalidEnrollmentError(
                school_id=self.school_id,
                student_id=self.student_id,
            )

        return Enrollment(
            id=self.id,
            student_id=self.student_id,
            school_id=self.school_id,
            monthly_fee=self.monthly_fee,
            created_at=self.created_at,
            updated_at=at,
            deleted_at=at,
        )

    def is_active(self):
        return self.deleted_at is None


@dataclass(frozen=True)
class ActiveEnrollmentProjection:
    id: str
    student_id: str
    school_id: str
    monthly_fee: Decimal


class EnrollmentRepository(ABC):
    async def get(self, school_id: str, student_id: str) -> Enrollment:
        found_enrollment = await self.find(school_id=school_id, student_id=student_id)

        if found_enrollment is None:
            raise NotFoundError(
                resource="Enrollment",
                attributes={"school_id": school_id, "student_id": student_id},
            )

        return found_enrollment

    @abstractmethod
    async def exists(self, school_id: str, student_id: str) -> bool:
        pass

    @abstractmethod
    async def find(self, school_id: str, student_id: str) -> Enrollment:
        pass

    @abstractmethod
    async def list_ids(self, school_id: str) -> list[str]:
        pass

    @abstractmethod
    async def list_active(
        self, school_id: str, cursor: str | None
    ) -> tuple[str, list[ActiveEnrollmentProjection]]:
        pass

    @abstractmethod
    async def save(self, school: Enrollment) -> Enrollment:
        pass
