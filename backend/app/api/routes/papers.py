import logging

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser
from app.api.deps.papers import get_paper_form
from app.models.papers import Paper, PaperCreate, PaperPublic, PapersPublic, PaperCreateForm
from app.models.response import ApiResponse, PaginatedResponse
from app.utils.file_helper import FileHelper
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/", response_model=ApiResponse[list[PapersPublic]])
async def read_items(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> PaginatedResponse:
    """
    Retrieve items.
    """
    # 获取项目总数
    count = await Paper.count()
    
    # 获取分页项目列表
    papers = await Paper.find().skip(skip).limit(limit).to_list()
    
    # 将 Item 转换为 ItemPublic
    papers_public = []
    for paper in papers:
        try:
            paper_public = await PaperPublic.from_item(paper)
            papers_public.append(paper_public)
        except Exception as e:
            logger.error(f"Error processing item {paper.id}: {str(e)}")
            continue
    
    # 返回分页响应
    return PaginatedResponse.create(
        items=papers_public,
        total=count,
        page=skip // limit + 1 if limit else 1,
        page_size=limit
    )

@router.post("/", response_model=ApiResponse[PaperPublic])
async def create_paper(
    current_user: CurrentUser,
    form_data: PaperCreateForm = Depends(get_paper_form)
) -> ApiResponse[PaperPublic]:
    """
    create paper.
    """
    # 创建Paper数据模型
    paper_create = form_data.to_paper_create()
    paper_data = paper_create.model_dump()
    paper_data["owner"] = current_user
    
    # 处理文件上传
    file_helper = FileHelper(settings.DOWNLOAD_DIR)
    saved_file_name = await file_helper.save_from_upload_file(form_data.file)
    saved_file_url = file_helper.gen_down_url(saved_file_name)
    paper_data["url"] = saved_file_url
    
    # 创建并保存数据库记录
    paper = Paper.model_validate(paper_data)
    await paper.insert()
    
    paper_public = await paper.to_public()
    return ApiResponse.success_response(data=paper_public)