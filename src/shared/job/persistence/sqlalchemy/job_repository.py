from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.job.model import JobExecutionResult
from src.shared.job.persistence.sqlalchemy.dbo import JobExecutionDbo
from src.shared.job.repository import JobRepository


from src.shared.db.pg_sqlalchemy.connection import get_db
from src.shared.logging.log import Logger
from src.shared.errors.technical import TechnicalError

logger = Logger(__name__)


class SqlAlchemyJobRepository(JobRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, result: JobExecutionResult) -> None:
        try:
            job_execution_dbo = JobExecutionDbo.from_domain(result)
            self.session.add(job_execution_dbo)
            await self.session.commit()
        except Exception as e:
            error = TechnicalError(
                code="JobRepositoryError",
                message=f"Fail saving job execution result {result.id}",
                attributes=result.__dict__,
                cause=e,
            )

            logger.error(error)

            raise error from e


def get_job_repository(
    session: AsyncSession = Depends(get_db),
) -> JobRepository:
    return SqlAlchemyJobRepository(session=session)
