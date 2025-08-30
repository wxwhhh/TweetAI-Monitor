#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证系统测试脚本
"""

import os
import sys
import sqlite3

def test_database():
    """测试数据库连接和表结构"""
    print("🔍 测试数据库连接...")
    
    try:
        conn = sqlite3.connect('data/auth.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ 数据库连接成功")
        print(f"📊 发现表: {[table[0] for table in tables]}")
        
        # 检查用户表
        if ('users',) in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 用户数量: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT username, created_at FROM users")
                users = cursor.fetchall()
                print("📝 用户列表:")
                for user in users:
                    print(f"  - {user[0]} (创建时间: {user[1]})")
        
        # 检查session表
        if ('sessions',) in tables:
            cursor.execute("SELECT COUNT(*) FROM sessions")
            session_count = cursor.fetchone()[0]
            print(f"🔑 活跃session数量: {session_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_password_file():
    """测试默认密码文件"""
    print("\n🔍 测试默认密码文件...")
    
    password_file = 'data/default_password.txt'
    if os.path.exists(password_file):
        try:
            with open(password_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print("✅ 默认密码文件存在")
            print("📝 文件内容:")
            print(content)
            return True
        except Exception as e:
            print(f"❌ 读取密码文件失败: {e}")
            return False
    else:
        print("❌ 默认密码文件不存在")
        return False

def test_auth_module():
    """测试认证模块"""
    print("\n🔍 测试认证模块...")
    
    try:
        from auth import auth_manager
        
        # 测试用户验证
        if auth_manager.user_exists('admin'):
            print("✅ admin用户存在")
        else:
            print("❌ admin用户不存在")
            return False
        
        # 测试session管理
        print("✅ 认证模块加载成功")
        return True
        
    except Exception as e:
        print(f"❌ 认证模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("    🔐 认证系统测试")
    print("=" * 50)
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    tests = [
        ("数据库连接", test_database),
        ("默认密码文件", test_password_file),
        ("认证模块", test_auth_module),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！认证系统工作正常")
        print("\n💡 下一步:")
        print("1. 运行 python start.py 启动系统")
        print("2. 查看控制台输出的默认密码")
        print("3. 访问 http://localhost:5000 进行登录")
    else:
        print("⚠️  部分测试失败，请检查配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
