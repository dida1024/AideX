import logging

from sqlmodel import Session
import asyncio

from app.core.db import engine, client, init_db, init_mongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)

async def init_mongo_data() -> None:
    # Placeholder for MongoDB initialization
    await init_mongo(client, db_name="app")

async def main() -> None:
    logger.info("Creating initial data")
    # init()
    await init_mongo_data()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())  # 这里用 asyncio.run() 运行异步代码
