#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理脚本 - 用于查看和修改用户信息
"""

import sqlite3
import hashlib
import sys

def connect_db():
    """连接数据库"""
    try:
        conn = sqlite3.connect('data/auth.db')
        return conn
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        return None

def list_users():
    """列出所有用户"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, created_at FROM users')
    users = cursor.fetchall()
    
    if not users:
        print("📝 暂无用户")
        return
    
    print("\n👥 用户列表:")
    print("-" * 50)
    print(f"{'ID':<5} {'用户名':<15} {'创建时间':<20}")
    print("-" * 50)
    
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<20}")
    
    conn.close()

def change_password(username, new_password):
    """修改用户密码"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 检查用户是否存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ 用户 '{username}' 不存在")
        conn.close()
        return
    
    # 更新密码
    password_hash = hashlib.md5(new_password.encode()).hexdigest()
    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', 
                  (password_hash, username))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 用户 '{username}' 密码已更新")

def add_user(username, password):
    """添加新用户"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        print(f"❌ 用户 '{username}' 已存在")
        conn.close()
        return
    
    # 创建新用户
    password_hash = hashlib.md5(password.encode()).hexdigest()
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                  (username, password_hash))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 用户 '{username}' 创建成功")

def delete_user(username):
    """删除用户"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 检查用户是否存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ 用户 '{username}' 不存在")
        conn.close()
        return
    
    # 删除用户相关的session
    cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user[0],))
    
    # 删除用户
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 用户 '{username}' 已删除")

def show_help():
    """显示帮助信息"""
    print("""
🔐 用户管理脚本

用法:
  python manage_users.py [命令] [参数]

命令:
  list                    - 列出所有用户
  change-password <用户名> <新密码>  - 修改用户密码
  add <用户名> <密码>     - 添加新用户
  delete <用户名>         - 删除用户
  help                    - 显示此帮助信息

示例:
  python manage_users.py list
  python manage_users.py change-password admin newpassword123
  python manage_users.py add user1 password123
  python manage_users.py delete user1
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_users()
    
    elif command == 'change-password':
        if len(sys.argv) != 4:
            print("❌ 用法: python manage_users.py change-password <用户名> <新密码>")
            return
        change_password(sys.argv[2], sys.argv[3])
    
    elif command == 'add':
        if len(sys.argv) != 4:
            print("❌ 用法: python manage_users.py add <用户名> <密码>")
            return
        add_user(sys.argv[2], sys.argv[3])
    
    elif command == 'delete':
        if len(sys.argv) != 3:
            print("❌ 用法: python manage_users.py delete <用户名>")
            return
        delete_user(sys.argv[2])
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()
