from sqlmodel import Session, create_engine, select
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app import crud
from app.core.config import settings
from app.models import User, Item, UserCreate
import logging

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
# AsyncIOMotorClient is used for async MongoDB operations
client = AsyncIOMotorClient(str(settings.MONGODB_URI))

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # user = session.exec(
    #     select(User).where(User.email == settings.FIRST_SUPERUSER)
    # ).first()
    # if not user:
    #     user_in = UserCreate(
    #         email=settings.FIRST_SUPERUSER,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         is_superuser=True,
    #     )
    #     user = crud.create_user(session=session, user_create=user_in)
    return None
 
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

