"""图片上传接口。

课程作业用本地磁盘存储，路径按年月分目录，避免单目录几十万文件导致
文件系统查找变慢。生产环境应换成对象存储（OSS/S3），
接口签名不用变，只换 save_image 的实现。

安全要点：
1. 不信任客户端文件名，用 uuid 重命名（防目录穿越、防重名覆盖）
2. 校验扩展名白名单，不校验 MIME（MIME 可以伪造）
3. 限制大小，避免被人当网盘刷爆磁盘
"""
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user
from app.core.exceptions import BusinessError
from app.models.user import User
from app.schemas.common import ApiResponse

router = APIRouter(tags=["上传"])

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

# backend/uploads
UPLOAD_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "uploads"


@router.post("/image", response_model=ApiResponse[dict], summary="上传图片")
async def upload_image(
    file: UploadFile = File(..., description="图片文件，最大 5MB"),
    _: User = Depends(get_current_user),
) -> ApiResponse[dict]:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise BusinessError(f"不支持的图片格式：{ext or '未知'}，仅支持 jpg/png/gif/webp")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise BusinessError("图片超过 5MB，请压缩后再上传")
    if not content:
        raise BusinessError("文件内容为空")

    month_dir = datetime.now().strftime("%Y%m")
    target_dir = UPLOAD_ROOT / month_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    (target_dir / filename).write_bytes(content)

    # 返回相对路径，前端拼上服务地址即可访问
    url = f"/static/uploads/{month_dir}/{filename}"
    return ApiResponse[dict](
        message="上传成功", data={"url": url, "filename": filename}
    )
