from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, create_access_token,
    get_current_user, hash_password, require_admin,
)
from app.models.user import User
from app.schemas.user import UserLogin, TokenOut, UserOut, UserCreate

router = APIRouter()


class UserUpdate(BaseModel):
    username:  Optional[str] = None
    full_name: Optional[str] = None
    role:      Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    password: str


# ── 登录 ───────────────────────────────────────────────────

@router.post("/auth/login", response_model=TokenOut, summary="用户登录")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_pw):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/auth/me", response_model=UserOut, summary="获取当前用户信息")
def me(current_user=Depends(get_current_user)):
    return current_user


# ── 用户管理（管理员专用）────────────────────────────────

@router.get("/auth/users", response_model=list[UserOut], summary="用户列表（仅管理员）")
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.id).all()


@router.post("/auth/users", response_model=UserOut, status_code=201, summary="新建用户（仅管理员）")
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")
    user = User(
        username=data.username,
        hashed_pw=hash_password(data.password),
        full_name=data.full_name,
        role=data.role or "viewer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/auth/users/{uid}", response_model=UserOut, summary="修改用户信息（仅管理员）")
def update_user(uid: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 用户名修改时检查重复
    if data.username and data.username != user.username:
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(status_code=400, detail="用户名已被占用")
        user.username = data.username
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user


@router.put("/auth/users/{uid}/password", summary="修改密码（管理员可改任意人，普通用户只改自己）")
def change_password(
    uid: int,
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != uid and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限修改他人密码")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.hashed_pw = hash_password(data.password)
    db.commit()
    return {"message": "密码已更新"}


@router.delete("/auth/users/{uid}", status_code=204, summary="删除用户（仅管理员）")
def delete_user(uid: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if uid == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员账号")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
