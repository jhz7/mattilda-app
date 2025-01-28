from dataclasses import asdict
from fastapi import Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.contact.model import Contact, ContactDbo
from src.shared.db.pg_sqlalchemy.connection import get_db
from src.shared.logging.log import Logger
from src.shared.errors.technical import TechnicalError
from src.student.domain.repository import ById, ByIdentity, Query, StudentRepository
from src.student.infrastructure.persistence.sqlalchemy.dbo import StudentDbo
from src.student.domain.model import Student
from sqlalchemy.dialects.postgresql import insert

logger = Logger(__name__)


class SqlAlchemyStudentRepository(StudentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, query: Query) -> bool:
        try:
            stmt = select(exists().where(self.__parse_query(query)))
            result = await self.session.execute(stmt)
            return result.scalar() or False
        except Exception as e:
            error = TechnicalError(
                code="StudentRepositoryError",
                message=f"Fail checking student existing query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def find(self, query: Query) -> Student | None:
        try:
            db_query = select(StudentDbo).where(self.__parse_query(query))
            result = await self.session.execute(db_query)
            result = result.scalar()

            if result is None:
                return None

            return result.as_domain()
        except Exception as e:
            error = TechnicalError(
                code="StudentRepositoryError",
                message=f"Fail finding student query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def list(self) -> list[Student]:
        try:
            result = await self.session.execute(select(StudentDbo))
            result = result.scalars().all()

            return list(map(lambda student_dbo: student_dbo.as_domain(), result))
        except Exception as e:
            error = TechnicalError(
                code="StudentRepositoryError",
                message=f"Fail listing students ",
                attributes={},
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def save(self, student: Student) -> Student:
        try:
            existing_contact_id = await self.__get_or_create_contact(student.contact)

            student_dbo = StudentDbo.from_domain(student)
            student_dbo.contact_id = existing_contact_id

            upsert_student_statement = (
                insert(StudentDbo)
                .values(**student_dbo.as_dict())
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={**student_dbo.as_for_update_dict()},
                )
            )

            await self.session.execute(upsert_student_statement)
            await self.session.commit()

            return student
        except Exception as e:
            error = TechnicalError(
                code="StudentRepositoryError",
                message=f"Fail saving a student {student.id}",
                attributes=asdict(student),
                cause=e,
            )

            logger.error(error)

            raise error from e

    def __parse_query(self, query):
        match query:
            case ById(id):
                return StudentDbo.id == id
            case ByIdentity(identity):
                return (StudentDbo.identity_kind == identity.kind.name) & (
                    StudentDbo.identity_code == identity.code
                )

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


def get_student_repository(
    session: AsyncSession = Depends(get_db),
) -> StudentRepository:
    return SqlAlchemyStudentRepository(session=session)
