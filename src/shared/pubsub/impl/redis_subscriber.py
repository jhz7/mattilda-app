from src.shared.logging.log import Logger
from src.shared.redis.connection_factory import get_connection
from src.shared.pubsub.subscriber import Subscriber, AsyncCallbackType
from src.shared.errors.technical import TechnicalError

logger = Logger(__name__)


class RedisSubscriber(Subscriber):
    def __init__(self):
        self.connection = get_connection()

    async def subscribe(self, subscription: str, process: AsyncCallbackType) -> None:
        try:
            pubsub = self.connection.pubsub()

            await pubsub.subscribe(subscription)

            async for message in pubsub.listen():
                if message["type"] == "message" and message["channel"] == subscription:
                    data = message["data"]

                    logger.info(
                        f"About to process a message: subs={subscription}, data={data}"
                    )

                    await process(data)
        except Exception as e:
            error = TechnicalError(
                code="RedisSubscriberError",
                message=f"Error occured while subscribing to {subscription}",
                attributes={"subscription": subscription},
                cause=e,
            )

            logger.error(error)

            raise error from e
