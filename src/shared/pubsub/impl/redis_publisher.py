import json

from src.shared.logging.log import Logger
from src.shared.redis.connection_factory import get_connection
from src.shared.pubsub.publisher import Publisher
from src.shared.errors.technical import TechnicalError

logger = Logger(__name__)


class RedisPublisher(Publisher):
    def __init__(self):
        self.connection = get_connection()

    async def publish(self, subscription: str, data: dict) -> None:
        try:
            logger.info(
                f"About to dispatch a message: subs={subscription}, data={data}"
            )

            await self.connection.publish(subscription, json.dumps(data))
        except Exception as e:
            error = TechnicalError(
                code="RedisPublisherError",
                message=f"Error occured while publishing to {subscription}",
                attributes={"subscription": subscription},
                cause=e,
            )

            logger.error(error)

            raise error from e
