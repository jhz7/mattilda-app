from dataclasses import asdict
from fastapi import Depends
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.school.infrastructure.persistence.sqlalchemy.enrollment_dbo import (
    EnrollmentDbo,
)
from src.school.domain.enrollment import (
    ActiveEnrollmentProjection,
    Enrollment,
    EnrollmentRepository,
)
from src.shared.db.pg_sqlalchemy.connection import get_db
from src.shared.logging.log import Logger
from src.shared.errors.technical import TechnicalError

logger = Logger(__name__)


class SqlAlchemyEnrollmentRepository(EnrollmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, school_id: str, student_id: str) -> bool:
        try:
            stmt = select(exists(EnrollmentDbo)).filter(
                EnrollmentDbo.school_id == school_id,
                EnrollmentDbo.student_id == student_id,
            )
            result = await self.session.execute(stmt)
            return result.scalar() or False
        except Exception as e:
            error = TechnicalError(
                code="EnrollmentRepositoryError",
                message=f"Fail checking existing schools/students enrollment school_id={school_id} student_id={student_id}",
                attributes={"school_id": school_id, "student_id": student_id},
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def find(self, school_id: str, student_id: str) -> Enrollment:
        try:
            db_query = select(EnrollmentDbo).filter(
                EnrollmentDbo.school_id == school_id,
                EnrollmentDbo.student_id == student_id,
            )
            result = await self.session.execute(db_query)
            found_dbo = result.scalars().one_or_none()

            if found_dbo is None:
                return None

            return found_dbo.as_domain()
        except Exception as e:
            error = TechnicalError(
                code="EnrollmentRepositoryError",
                message=f"Fail finding schools/students enrollment school_id={school_id} student_id={student_id}",
                attributes={"school_id": school_id, "student_id": student_id},
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def list_active(
        self, school_id: str, cursor: str | None
    ) -> tuple[str, list[ActiveEnrollmentProjection]]:
        with_cursor = (
            select(EnrollmentDbo)
            .filter(
                EnrollmentDbo.school_id == school_id,
                EnrollmentDbo.deleted_at.is_(None),
                EnrollmentDbo.id > cursor,
            )
            .order_by(EnrollmentDbo.id)
            .limit(50)
        )
        without_cursor = (
            select(EnrollmentDbo)
            .filter(
                EnrollmentDbo.school_id == school_id,
                EnrollmentDbo.deleted_at.is_(None),
            )
            .order_by(EnrollmentDbo.id)
            .limit(50)
        )

        db_query = without_cursor if not cursor else with_cursor

        result = await self.session.execute(db_query)
        result = result.scalars().all()
        next_cursor = result[-1].id if result else None

        return next_cursor, [dbo.as_read_projection() for dbo in result]

    async def list_ids(self, school_id: str) -> list[str]:
        try:
            db_query = select(EnrollmentDbo.id).filter(
                EnrollmentDbo.school_id == school_id, EnrollmentDbo.deleted_at.is_(None)
            )
            result = await self.session.execute(db_query)
            result = result.scalars().all()

            return list(result)
        except Exception as e:
            error = TechnicalError(
                code="EnrollmentRepositoryError",
                message=f"Fail listing schools/students enrollments school_id={school_id}",
                attributes={"school_id": school_id},
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def save(self, school: Enrollment) -> Enrollment:
        try:
            enrollment_dbo = EnrollmentDbo.from_domain(school)

            upsert_enrollment_statement = (
                insert(EnrollmentDbo)
                .values(**enrollment_dbo.as_dict())
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={**enrollment_dbo.as_for_update_dict()},
                )
            )

            await self.session.execute(upsert_enrollment_statement)
            await self.session.commit()

            return school
        except Exception as e:
            error = TechnicalError(
                code="EnrollmentRepositoryError",
                message=f"Fail saving a school/student enrollment {school.id}",
                attributes=asdict(school),
                cause=e,
            )

            logger.error(error)

            raise error from e


def get_enrollment_repository(
    session: AsyncSession = Depends(get_db),
) -> EnrollmentRepository:
    return SqlAlchemyEnrollmentRepository(session=session)
