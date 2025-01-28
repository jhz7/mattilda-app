from src.shared.errors.business import BusinessError
from src.shared.logging.log import Logger
from src.school.domain.repository import SchoolRepository, ById
from src.school.domain.model import School

logger = Logger(__name__)


class DropSchool:
    def __init__(self, schools: SchoolRepository):
        self.schools = schools

    async def execute(self, school_id: str) -> School:
        logger.info(f"About to drop a school: id={school_id}")

        query = ById(id=school_id)
        school = await self.schools.get(query=query)

        try:
            dropped_school = school.deactivate()
        except BusinessError as error:
            logger.error(error)
            raise error

        await self.schools.save(school=dropped_school)

        return dropped_school
