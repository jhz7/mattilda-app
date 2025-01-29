from datetime import datetime
import json
from typing import AsyncGenerator
from src.school.infrastructure.persistence.sqlalchemy.enrolment_repository import (
    SqlAlchemyEnrollmentRepository,
)
from src.shared.db.pg_sqlalchemy.connection import get_db
from src.shared.job.persistence.sqlalchemy.job_repository import SqlAlchemyJobRepository
from src.shared.job.executor import JobExecutor
from src.school.application.use_cases.drop_enrollment import (
    DropEnrollment,
    Request as DropEnrollmentRequest,
)
from src.shared.job.model import JobItemResult, StartedJobItem
from src.school.domain.enrollment import ActiveEnrollmentProjection, ByStudentId
from src.school.application.use_cases.enrollment_query_handler import (
    EnrollmentQueryHandler,
)
from src.shared.pubsub.subscriber import Subscriber
from src.shared.pubsub.impl.redis_subscriber import RedisSubscriber
from src.shared.logging.log import Logger
from src.student.application.use_cases.drop_student import DROP_STUDENT_TOPIC


logger = Logger(__name__)


class DropStudentEnrollmentsSubscriber:
    def __init__(
        self,
        subscriber: Subscriber,
        enrollments: EnrollmentQueryHandler,
        drop_enrollment: DropEnrollment,
        job_executor: JobExecutor,
    ):
        self.subscriber = subscriber
        self.enrollments = enrollments
        self.drop_enrollment = drop_enrollment
        self.job_executor = job_executor

    async def run(self) -> None:
        await self.subscriber.subscribe(DROP_STUDENT_TOPIC, self.__message_handler)

    async def __message_handler(self, message: str) -> None:
        logger.info(f"Message received {message}")

        message_dict = json.loads(message)

        dropped_student_id = message_dict.get("student")

        await self.job_executor.run(
            job_id=f"drop_enrollment|student_id:{dropped_student_id}",
            job_name="DropStudentEnrollments",
            generator=self.__delete_enrollments(student_id=dropped_student_id),
        )

    async def __delete_enrollments(
        self, student_id: str
    ) -> AsyncGenerator[JobItemResult, None]:
        cursor = None

        while True:
            next_cursor, enrollments = await self.enrollments.list(
                query=ByStudentId(student_id=student_id), next_cursor=cursor
            )

            for enrollment in enrollments:
                yield await self.__delete_enrollment(enrollment)

            if not next_cursor:
                break

            cursor = next_cursor

    async def __delete_enrollment(
        self, enrollment: ActiveEnrollmentProjection
    ) -> JobItemResult:
        started_job_item = StartedJobItem(
            id=f"enrollment:{enrollment.id}",
            started_at=datetime.now(),
        )

        try:
            request = DropEnrollmentRequest(
                school_id=enrollment.school_id,
                student_id=enrollment.student_id,
            )
            await self.drop_enrollment.execute(request=request)

            return started_job_item.succeeded(finished_at=datetime.now())
        except Exception as error:
            return started_job_item.failed(finished_at=datetime.now(), error=str(error))


async def dropStudentEnrollmentsSubscriber():
    async for db_session in get_db():
        subscriber = RedisSubscriber()
        job_executor = JobExecutor(jobs=SqlAlchemyJobRepository(db_session))

        enrollments_repository = SqlAlchemyEnrollmentRepository(db_session)
        enrollments = EnrollmentQueryHandler(enrollments=enrollments_repository)
        drop_enrollment = DropEnrollment(enrollments=enrollments_repository)

        return DropStudentEnrollmentsSubscriber(
            subscriber=subscriber,
            enrollments=enrollments,
            drop_enrollment=drop_enrollment,
            job_executor=job_executor,
        )
