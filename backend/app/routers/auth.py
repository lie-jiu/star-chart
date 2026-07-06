"""
认证路由
"""
import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from app.database import get_db
from app.models import User
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserCreate(BaseModel):
    username: str
    password: str

    @validator('username')
    def username_must_be_english(cls, v):
        if not re.match(r'^[a-zA-Z]+$', v):
            raise ValueError('Username must contain only English letters')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool = False

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_admin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """获取管理员用户，非管理员禁止访问"""
    user = get_current_user(token, db)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
    return user


@router.post("/set-admin/{user_id}")
async def set_admin(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """设置用户为管理员（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    db.commit()
    return {"message": f"User {user.username} is now admin"}


@router.post("/unset-admin/{user_id}")
async def unset_admin(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """取消管理员权限（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = False
    db.commit()
    return {"message": f"User {user.username} admin removed"}


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 生成 token（保留 is_admin 状态）
    access_token = create_access_token(data={"sub": user.username}, is_admin=user.is_admin)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "is_admin": user.is_admin},
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """登录"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成 token（保留 is_admin 状态）
    access_token = create_access_token(data={"sub": user.username}, is_admin=user.is_admin)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "is_admin": user.is_admin},
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
    }


@router.get("/check")
async def check_auth(current_user: User = Depends(get_current_user)):
    """检查认证状态"""
    return {"authenticated": True, "username": current_user.username}


@router.patch("/me")
async def update_me(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改用户名"""
    new_username = data.get("username", "").strip()
    if not new_username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    if not re.match(r'^[a-zA-Z]+$', new_username):
        raise HTTPException(status_code=400, detail="用户名必须是纯英文")
    if len(new_username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少3个字符")

    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == new_username, User.id != current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    current_user.username = new_username
    db.commit()
    return {"message": "用户名修改成功", "username": new_username}


@router.post("/change-password")
async def change_password(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码（需要旧密码）"""
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="旧密码和新密码不能为空")

    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="旧密码错误")

    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.delete("/me")
async def delete_self(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """注销当前账号"""
    db.delete(current_user)
    db.commit()
    return {"message": "账号已删除"}


@router.get("/users")
async def list_users(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """列出所有用户（仅管理员）"""
    users = db.query(User).order_by(User.id).all()
    return [{"id": u.id, "username": u.username, "is_admin": u.is_admin, "created_at": u.created_at} for u in users]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """删除用户（仅管理员）"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
