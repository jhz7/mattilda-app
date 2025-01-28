from dataclasses import asdict
from fastapi import Depends
from sqlalchemy.orm import aliased
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.contact.model import Contact, ContactDbo
from src.shared.db.pg_sqlalchemy.connection import get_db
from src.shared.logging.log import Logger
from src.shared.errors.technical import TechnicalError
from src.school.domain.repository import (
    ByIdAndActive,
    SchoolRepository,
    ById,
    ByEmail,
    ByStatus,
    SchoolQuery,
    SchoolsQuery,
)
from src.school.infrastructure.persistence.sqlalchemy.dbo import SchoolDbo
from src.school.domain.model import School, SchoolStatus
from sqlalchemy.dialects.postgresql import insert

logger = Logger(__name__)


class SqlAlchemySchoolRepository(SchoolRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, query: SchoolQuery) -> bool:
        try:
            stmt = select(exists(SchoolDbo).where(self.__parse_single_query(query)))
            result = await self.session.execute(stmt)
            return result.scalar() or False
        except Exception as e:
            error = TechnicalError(
                code="SchoolRepositoryError",
                message=f"Fail checking school existing query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def find(self, query: SchoolQuery) -> School | None:
        try:
            db_query = select(SchoolDbo).where(self.__parse_single_query(query))
            result = await self.session.execute(db_query)
            result = result.scalar()

            if result is None:
                return None

            return result.as_domain()
        except Exception as e:
            error = TechnicalError(
                code="SchoolRepositoryError",
                message=f"Fail finding school query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def list(self, query: SchoolsQuery) -> list[School]:
        try:
            db_query = select(SchoolDbo).where(self.__parse_multiple_query(query))
            result = await self.session.execute(db_query)
            result = result.scalars().all()

            return list(map(lambda school_dbo: school_dbo.as_domain(), result))
        except Exception as e:
            error = TechnicalError(
                code="SchoolRepositoryError",
                message=f"Fail listing schools query={(str(query))}",
                attributes={},
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def save(self, school: School) -> School:
        try:
            existing_contact_id = await self.__get_or_create_contact(school.contact)

            school_dbo = SchoolDbo.from_domain(school)
            school_dbo.contact_id = existing_contact_id

            upsert_student_statement = (
                insert(SchoolDbo)
                .values(**school_dbo.as_dict())
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={**school_dbo.as_for_update_dict()},
                )
            )

            await self.session.execute(upsert_student_statement)
            await self.session.commit()

            return school
        except Exception as e:
            error = TechnicalError(
                code="SchoolRepositoryError",
                message=f"Fail saving a school {school.id}",
                attributes=asdict(school),
                cause=e,
            )

            logger.error(error)

            raise error from e

    def __parse_single_query(self, query: SchoolQuery):
        match query:
            case ById(id):
                return SchoolDbo.id == id
            case ByIdAndActive(id):
                return (SchoolDbo.id == id) & (
                    SchoolDbo.status == SchoolStatus.ACTIVE.name
                )
            case ByEmail(email):
                contact_alias = aliased(ContactDbo)
                return (
                    SchoolDbo.contact_id == contact_alias.id
                    and contact_alias.email == email
                )
            case _:
                raise NotImplementedError("Query not implemented")

    def __parse_multiple_query(self, query: SchoolsQuery):
        match query:
            case ByStatus(status):
                return SchoolDbo.status == status.name
            case _:
                raise NotImplementedError("Query not implemented")

    async def __get_or_create_contact(self, contact: Contact) -> str:
        contact_dbo = ContactDbo.from_domain(contact)
        contact_statement = (
            insert(ContactDbo).values(**contact_dbo.as_dict()).on_conflict_do_nothing()
        )

        await self.session.execute(contact_statement)
        await self.session.commit()

        existing_contact_id = await self.session.execute(
            select(ContactDbo.id).filter_by(email=contact.email)
        )
        existing_contact_id = existing_contact_id.scalar_one_or_none()

        return existing_contact_id


def get_school_repository(
    session: AsyncSession = Depends(get_db),
) -> SchoolRepository:
    return SqlAlchemySchoolRepository(session=session)
