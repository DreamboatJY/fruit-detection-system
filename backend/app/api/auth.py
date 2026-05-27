from datetime import datetime
import uuid
import logging
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings
from app.models.database import BatchDetectionTask, DetectionRecord, User, get_db
from app.models.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    CurrentUserResponse,
    UserProfileUpdateRequest,
    UserInfo,
    UserLoginRequest,
    UserRegisterRequest,
    UserStats,
    UserStatsResponse,
)
from app.services.minio_service import minio_service

# 创建日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# 转换为uuid类型
def _to_uuid(value):
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


def build_user_info(user: User) -> UserInfo:
    return UserInfo(
        id=str(user.id),
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        role=user.role or "user",
        avatar_url=user.avatar_url,
    )


def _avatar_object_name(avatar_url: str | None) -> str | None:
    if not avatar_url:
        return None

    parsed = urlparse(avatar_url)
    path_parts = [unquote(part) for part in parsed.path.split("/") if part]
    try:
        bucket_index = path_parts.index(settings.minio.avatars_bucket)
    except ValueError:
        return None

    if bucket_index + 1 >= len(path_parts):
        return None
    return path_parts[bucket_index + 1]


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册接口"""
    logger.info(f"收到用户注册请求：username={payload.username}, email={payload.email}")
    
    username = payload.username.strip()
    email = payload.email.strip().lower()
    nickname = payload.nickname.strip() if payload.nickname else None
    
    logger.debug(f"处理后的用户信息：username={username}, email={email}, nickname={nickname}")

    exists = (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )
    if exists:
        logger.warning(f"用户注册失败：用户名或邮箱已被注册 - {username}/{email}")
        raise HTTPException(status_code=400, detail="用户名或邮箱已被注册")

    user = User(
        username=username,
        email=email,
        nickname=nickname or username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"用户注册成功：id={user.id}, username={user.username}")

    return AuthResponse(
        success=True,
        message="注册成功",
        access_token=create_access_token(user.id),
        user=build_user_info(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录接口"""
    logger.info(f"收到用户登录请求：account={payload.username}")
    
    account = payload.username.strip()
    user = (
        db.query(User)
        .filter(or_(User.username == account, User.email == account.lower()))
        .first()
    )

    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(f"用户登录失败：用户名或密码错误 - {account}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        logger.warning(f"用户登录失败：用户已被禁用 - {account}, user_id={user.id}")
        raise HTTPException(status_code=403, detail="用户已被禁用")
    
    logger.info(f"用户登录成功：id={user.id}, username={user.username}")

    return AuthResponse(
        success=True,
        message="登录成功",
        access_token=create_access_token(user.id),
        user=build_user_info(user),
    )

# 获取当前用户信息
@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    logger.debug(f"获取当前用户信息：user_id={current_user.id}, username={current_user.username}")
    
    return CurrentUserResponse(
        success=True,
        message="获取成功",
        user=build_user_info(current_user),
    )

# 更新当前用户信息
@router.put("/me", response_model=CurrentUserResponse)
def update_me(
    # 从请求体中获取更新的用户信息
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前用户信息"""
    logger.info(f"收到用户资料更新请求：user_id={current_user.id}, email={payload.email}")
    
    email = payload.email.strip().lower()
    nickname = payload.nickname.strip() if payload.nickname else None
    
    logger.debug(f"处理后的更新信息：email={email}, nickname={nickname}")

    exists = (
        db.query(User)
        .filter(User.email == email, User.id != current_user.id)
        .first()
    )
    if exists:
        logger.warning(f"用户资料更新失败：邮箱已被其他用户使用 - {email}, user_id={current_user.id}")
        raise HTTPException(status_code=400, detail="邮箱已被其他用户使用")

    current_user.email = email
    current_user.nickname = nickname or current_user.username
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"用户资料更新成功：user_id={current_user.id}, new_email={email}, new_nickname={current_user.nickname}")

    return CurrentUserResponse(
        success=True,
        message="资料更新成功",
        user=build_user_info(current_user),
    )


@router.put("/password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码"""
    logger.info(f"收到用户密码修改请求：user_id={current_user.id}, username={current_user.username}")
    
    if not verify_password(payload.old_password, current_user.password_hash):
        logger.warning(f"用户密码修改失败：旧密码不正确 - user_id={current_user.id}")
        raise HTTPException(status_code=400, detail="旧密码不正确")

    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    
    logger.info(f"用户密码修改成功：user_id={current_user.id}")

    return {"success": True, "message": "密码修改成功"}


@router.get("/me/stats", response_model=UserStatsResponse)
def get_me_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ============================================================
    # 阶段一：统计单图检测数据（batch_id IS NULL 表示非批量任务）
    # ============================================================
    # 单图检测总次数：统计当前用户所有不属于任何批量任务的检测记录
    single_total = (
        db.query(func.count(DetectionRecord.id))
        .filter(DetectionRecord.user_id == current_user.id, DetectionRecord.batch_id.is_(None))
        .scalar()
        or 0
    )
    # 单图检测完成次数：在上面的基础上额外筛选状态为 completed 的记录
    single_completed = (
        db.query(func.count(DetectionRecord.id))
        .filter(
            DetectionRecord.user_id == current_user.id,
            DetectionRecord.batch_id.is_(None),
            DetectionRecord.status == "completed",
        )
        .scalar()
        or 0
    )
    # 单图检测累计目标数：汇总所有单图检测记录识别到的目标总数
    single_targets = (
        db.query(func.coalesce(func.sum(DetectionRecord.total_objects), 0))
        .filter(DetectionRecord.user_id == current_user.id, DetectionRecord.batch_id.is_(None))
        .scalar()
        or 0
    )
    
    # ============================================================
    # 阶段二：统计批量检测任务数据（需用 _to_uuid 转换 ID 类型）
    # ============================================================
    # 批量检测总任务数：统计当前用户创建的所有批量任务
    batch_total = (
        db.query(func.count(BatchDetectionTask.id))
        .filter(BatchDetectionTask.user_id == _to_uuid(current_user.id))
        .scalar()
        or 0
    )
    # 批量检测完成任务数：在上面的基础上额外筛选状态为 completed 的任务
    batch_completed = (
        db.query(func.count(BatchDetectionTask.id))
        .filter(BatchDetectionTask.user_id == _to_uuid(current_user.id), BatchDetectionTask.status == "completed")
        .scalar()
        or 0
    )
    # 批量检测累计目标数：汇总所有批量任务识别到的目标总数
    batch_targets = (
        db.query(func.coalesce(func.sum(BatchDetectionTask.total_objects), 0))
        .filter(BatchDetectionTask.user_id == _to_uuid(current_user.id))
        .scalar()
        or 0
    )

    # ============================================================
    # 阶段三：合并单图和批量数据，计算最终统计指标
    # ============================================================
    # 总检测次数 = 单图检测次数 + 批量任务次数
    total_detections = int(single_total) + int(batch_total)
    # 总完成次数 = 单图完成数 + 批量完成任务数
    completed_detections = int(single_completed) + int(batch_completed)
    # 累计检测目标数 = 单图目标数 + 批量目标数
    total_targets = int(single_targets) + int(batch_targets)
    # 检测成功率 = 完成数 / 总数 × 100（避免除零错误）
    success_rate = round((completed_detections / total_detections) * 100, 1) if total_detections else 0
    # 使用天数 = 从注册日到当前的天数，至少为 1 天
    usage_days = 1
    if current_user.created_at:
        usage_days = max((datetime.now() - current_user.created_at).days + 1, 1)
    
    logger.info(f"用户统计信息计算完成：user_id={current_user.id}, total_detections={total_detections}, success_rate={success_rate}%")

    return UserStatsResponse(
        success=True,
        message="获取成功",
        data=UserStats(
            total_detections=total_detections,
            total_targets=total_targets,
            success_rate=success_rate,
            usage_days=usage_days,
        ),
    )


@router.post("/avatar", response_model=CurrentUserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传用户头像"""
    logger.info(f"收到用户头像上传请求：user_id={current_user.id}, filename={file.filename}, size={file.size}")
    
    try:
        object_name = await minio_service.upload_avatar(file, current_user.id)
        logger.info(f"头像文件上传到 MinIO 成功：user_id={current_user.id}, object_name={object_name}")
    except ValueError as e:
        logger.error(f"头像上传失败：user_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    old_avatar_object = _avatar_object_name(current_user.avatar_url)
    current_user.avatar_url = f"http://localhost:8000/api/detection/files/{settings.minio.avatars_bucket}/{object_name}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    if old_avatar_object and old_avatar_object != object_name:
        deleted = minio_service.delete_object(settings.minio.avatars_bucket, old_avatar_object)
        if deleted:
            logger.info(f"旧头像删除成功：user_id={current_user.id}, object_name={old_avatar_object}")
        else:
            logger.warning(f"旧头像删除失败：user_id={current_user.id}, object_name={old_avatar_object}")
    
    logger.info(f"用户头像上传成功：user_id={current_user.id}, avatar_url={current_user.avatar_url}")

    return CurrentUserResponse(
        success=True,
        message="头像上传成功",
        user=build_user_info(current_user),
    )
