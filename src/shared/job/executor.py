from datetime import datetime
from typing import AsyncGenerator

from src.shared.logging.log import Logger
from src.shared.job.model import JobExecutionResult, JobItemResult, StartedJob
from src.shared.job.repository import JobRepository

logger = Logger(__name__)


class JobExecutor:
    def __init__(self, jobs: JobRepository):
        self.jobs = jobs

    async def run(
        self, job_id: str, job_name: str, generator: AsyncGenerator[JobItemResult, None]
    ) -> JobExecutionResult:
        started_job = StartedJob(
            id=job_id,
            job_name=job_name,
            started_at=datetime.now(),
        )

        collected_items = []

        try:
            async for item in generator:
                collected_items.append(item)

            job_execution_result = started_job.succeeded(
                finished_at=datetime.now(), items=collected_items
            )

        except Exception as error:
            logger.error(f"Error running job: {job_name} {str(error)}", {"error": str(error)})

            job_execution_result = started_job.failed(
                finished_at=datetime.now(), error=str(error)
            )

        finally:
            await self.jobs.save(result=job_execution_result)

        return job_execution_result
