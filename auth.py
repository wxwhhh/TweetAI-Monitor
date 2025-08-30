import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session, redirect, url_for, flash

class AuthManager:
    def __init__(self, db_path='data/auth.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建session表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 检查是否需要创建默认用户
        self.create_default_user()
    
    def create_default_user(self):
        """创建默认用户"""
        if not self.user_exists('admin'):
            # 生成随机密码
            import random
            import string
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # 保存密码到文件供用户查看
            with open('data/default_password.txt', 'w', encoding='utf-8') as f:
                f.write(f"默认账号: admin\n默认密码: {password}\n\n请妥善保管密码，如需修改请直接操作数据库。")
            
            self.create_user('admin', password)
            print(f"✅ 默认用户已创建 - 用户名: admin, 密码: {password}")
            print(f"📝 密码已保存到 data/default_password.txt")
    
    def create_user(self, username, password):
        """创建新用户"""
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                         (username, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def user_exists(self, username):
        """检查用户是否存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def verify_user(self, username, password):
        """验证用户凭据"""
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?', 
                     (username, password_hash))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def create_session(self, user_id):
        """创建新的session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)  # 24小时过期
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)',
                     (session_id, user_id, expires_at))
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id):
        """验证session是否有效"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM sessions 
            WHERE session_id = ? AND expires_at > ?
        ''', (session_id, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def delete_session(self, session_id):
        """删除session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    def cleanup_expired_sessions(self):
        """清理过期的session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE expires_at <= ?', (datetime.now(),))
        conn.commit()
        conn.close()

# 全局认证管理器实例
auth_manager = AuthManager()

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        
        if not session_id:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
        
        user_id = auth_manager.validate_session(session_id)
        if not user_id:
            # session过期，清除session
            session.pop('session_id', None)
            flash('登录已过期，请重新登录', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    """获取当前登录用户ID"""
    session_id = session.get('session_id')
    if session_id:
        return auth_manager.validate_session(session_id)
    return None
