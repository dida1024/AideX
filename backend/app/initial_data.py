import logging

import asyncio

from app.core.db import client,init_mongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_mongo_data() -> None:
    # Placeholder for MongoDB initialization
    await init_mongo(client, db_name="app")

async def main() -> None:
    logger.info("Creating initial data")
    await init_mongo_data()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())  # 这里用 asyncio.run() 运行异步代码
