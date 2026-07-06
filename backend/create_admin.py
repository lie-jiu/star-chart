#!/usr/bin/env python3
"""
创建管理员用户脚本
用法: python create_admin.py <用户名> <密码>
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

from app.database import SessionLocal, init_db
from app.models import User
from app.auth import get_password_hash
import re

def validate_username(username):
    if not re.match(r'^[a-zA-Z]+$', username):
        return "用户名必须是纯英文"
    if len(username) < 3:
        return "用户名至少3个字符"
    return None

def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("密码至少8位")
    if not re.search(r'[A-Z]', password):
        errors.append("需要大写字母")
    if not re.search(r'[a-z]', password):
        errors.append("需要小写字母")
    if not re.search(r'[0-9]', password):
        errors.append("需要数字")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("需要特殊字符")
    return errors if errors else None

def main():
    if len(sys.argv) != 3:
        print("用法: python create_admin.py <用户名> <密码>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    err = validate_username(username)
    if err:
        print(f"用户名错误: {err}")
        sys.exit(1)

    errs = validate_password(password)
    if errs:
        print(f"密码强度不足: {', '.join(errs)}")
        sys.exit(1)

    init_db()

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"用户 {username} 已存在")
            sys.exit(1)

        user = User(
            username=username,
            password_hash=get_password_hash(password),
            is_admin=True
        )
        db.add(user)
        db.commit()
        print(f"管理员 {username} 创建成功")
    except Exception as e:
        db.rollback()
        print(f"创建失败: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
