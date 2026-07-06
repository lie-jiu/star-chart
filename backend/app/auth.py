"""
用户认证服务
算法：Argon2id（2015 年 PHC 密码哈希竞赛冠军，目前业界最先进方案）
配置：t=3, m=64MB, p=4（OWASP 推荐最低参数）
安全性：抗 GPU 暴力破解、抗 ASIC 专用硬件、抗侧信道攻击、抗彩虹表
"""
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from argon2.low_level import Type

# Argon2id 配置（OWASP 推荐最低参数）
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)

# JWT 配置
SECRET_KEY = "mo_jiu_dashboard_secret_key_change_me_in_production_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


class TokenData(BaseModel):
    username: str
    is_admin: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def get_password_hash(password: str) -> str:
    return ph.hash(password)


def create_access_token(data: dict, is_admin: bool = False, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if is_admin:
        to_encode.update({"admin": True})
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username, is_admin=payload.get("admin", False))
    except JWTError:
        return None
