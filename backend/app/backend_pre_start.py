import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.db import client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_mongo(client: AsyncIOMotorClient) -> None:
    try:
        # Try to create session to check if DB is awake
        client.admin.command("ping")
    except Exception as e:
        logger.error(e)
        raise e

def main() -> None:
    logger.info("Initializing service")
    # init(engine)
    init_mongo(client)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
