from sqlmodel import Session, create_engine, select
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app import crud
from app.core.config import settings
from app.models import User, Item, UserCreate
import logging

logger = logging.getLogger(__name__)

# AsyncIOMotorClient is used for async MongoDB operations
client = AsyncIOMotorClient(str(settings.MONGODB_URI))

 
async def init_mongo(client: AsyncIOMotorClient, db_name: str) -> None:
    try:
        # 确保数据库连接
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # 获取数据库
        database = client[db_name]
        
        # 初始化 Beanie
        await init_beanie(
            database=database,
            document_models=[User, Item],
            allow_index_dropping=True
        )
        logger.info("Successfully initialized Beanie")
        
        # 检查超级用户是否存在
        existing_user = await User.find_one({"email": settings.FIRST_SUPERUSER})
        if not existing_user:
            default_user = UserCreate(
                email=settings.FIRST_SUPERUSER,
                full_name=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = await crud.create_user(user_create=default_user)
            logger.info(f"Created default superuser: {user.email}")
        else:
            logger.info("Default superuser already exists")
            
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {str(e)}")
        raise

