from dataclasses import asdict
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.job.model import (
    JobExecutionResult,
    SuccessJobExecution,
    FailureJobExecution,
)
from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel


class JobExecutionDbo(BaseSqlModel):
    __tablename__ = "job_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    items: Mapped[dict] = mapped_column(JSONB, nullable=True)
    error: Mapped[str] = mapped_column(String, nullable=True)
    succeed_items: Mapped[int] = mapped_column(nullable=True)
    failed_items: Mapped[int] = mapped_column(nullable=True)
    started_at: Mapped[datetime] = mapped_column()
    finished_at: Mapped[datetime] = mapped_column()

    @staticmethod
    def from_domain(job: JobExecutionResult) -> "JobExecutionDbo":
        dbo = JobExecutionDbo(
            id=job.id,
            name=job.job_name,
            kind=job.kind,
            started_at=job.started_at,
            finished_at=job.finished_at,
        )

        match job:
            case SuccessJobExecution():
                dbo.items = [asdict(item) for item in job.items]
                dbo.succeed_items = job.succeed_items
                dbo.failed_items = job.failed_items
            case FailureJobExecution():
                dbo.error = job.error

        return dbo
