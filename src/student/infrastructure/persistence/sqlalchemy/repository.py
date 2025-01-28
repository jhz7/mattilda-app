from dataclasses import asdict
from fastapi import Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.contact.model import ContactDbo
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
            db_query = self.__parse_query(query)
            result = await self.session.execute(db_query)
            r = result.scalar()
            logger.info(r)

            if r is None:
                return None

            return r.all()
        except Exception as e:
            error = TechnicalError(
                code="StudentRepositoryError",
                message=f"Fail finding student query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def list(self):
        return self.session.query(self.model).all()

    async def add(self, student: Student) -> Student:
        try:
            contact_dbo = ContactDbo.from_domain(student.contact)
            contact_statement = (
                insert(ContactDbo)
                .values(**contact_dbo.as_dict())
                .on_conflict_do_nothing()
            )

            await self.session.execute(contact_statement)
            await self.session.commit()

            existing_contact_id = await self.session.execute(
                select(ContactDbo.id).filter_by(email=student.contact.email)
            )
            existing_contact_id = existing_contact_id.scalar_one_or_none()
            student_dbo = StudentDbo.from_domain(student)
            student_dbo.contact_id = existing_contact_id

            self.session.add(student_dbo)
            await self.session.commit()

            return student
        except Exception as e:
            error = TechnicalError(
                code="StudentRepositoryError",
                message="Fail adding a student",
                attributes=asdict(student),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def update(self, student):
        self.session.add(student)
        self.session.commit()
        return student

    def __parse_query(self, query):
        match query:
            case ById(id):
                return StudentDbo.id == id
            case ByIdentity(identity):
                return (StudentDbo.identity_kind == identity.kind.name) & (
                    StudentDbo.identity_code == identity.code
                )


def get_student_repository(
    session: AsyncSession = Depends(get_db),
) -> StudentRepository:
    return SqlAlchemyStudentRepository(session=session)
