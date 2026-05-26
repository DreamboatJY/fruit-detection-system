from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.database import User, get_db
from app.models.schemas import (
    AuthResponse,
    CurrentUserResponse,
    UserInfo,
    UserLoginRequest,
    UserRegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def build_user_info(user: User) -> UserInfo:
    return UserInfo(
        id=str(user.id),
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        role=user.role or "user",
        avatar_url=user.avatar_url,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip()
    email = payload.email.strip().lower()
    nickname = payload.nickname.strip() if payload.nickname else None

    exists = (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )
    if exists:
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

    return AuthResponse(
        success=True,
        message="注册成功",
        access_token=create_access_token(user.id),
        user=build_user_info(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    account = payload.username.strip()
    user = (
        db.query(User)
        .filter(or_(User.username == account, User.email == account.lower()))
        .first()
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")

    return AuthResponse(
        success=True,
        message="登录成功",
        access_token=create_access_token(user.id),
        user=build_user_info(user),
    )


@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return CurrentUserResponse(
        success=True,
        message="获取成功",
        user=build_user_info(current_user),
    )
