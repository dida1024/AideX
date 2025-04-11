from beanie import Document
from app.models.base import TimestampMixin

# 先导入用户模型，再导入项目模型
from app.models.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    User,
    UserPublic,
    UsersPublic,
)

from app.models.item import (
    ItemBase,
    ItemCreate,
    ItemUpdate,
    Item,
    ItemPublic,
    ItemsPublic,
)

from app.models.papers import (
    PaperBase,
    PaperCreate,
    PaperUpdate,
    Paper,
    PaperPublic,
    PaperPublic,
)

# 导入依赖于两者的模型
from app.models.user import UserWithItems

from app.models.auth import (
    Token,
    TokenData,
    PasswordResetRequest,
    PasswordResetConfirm,
)

from app.models.response import (
    PaginatedResults,
    MessageResponse,
)

# 重建模型
User.model_rebuild()
Item.model_rebuild() 
Paper.model_rebuild()

models = [cls for cls in Document.__subclasses__()]
