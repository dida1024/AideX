# 从子模块导入并重新导出依赖
from .auth import (
    CurrentUser,
    CurrentSuperuser,
    get_current_user,
    get_current_active_superuser,
    TokenDep,
    reusable_oauth2
)

from .papers import (
    get_paper_form,
    validate_paper_file,
    PAPER_ALLOWED_TYPES
)

# 导出这些名称，使它们可以从app.api.deps导入
__all__ = [
    # 认证相关
    "CurrentUser",
    "CurrentSuperuser",
    "get_current_user",
    "get_current_active_superuser",
    "TokenDep",
    "reusable_oauth2",
    
    # 论文相关
    "get_paper_form",
    "validate_paper_file",
    "PAPER_ALLOWED_TYPES"
]
