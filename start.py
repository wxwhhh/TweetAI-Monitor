#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter AI 监控系统启动脚本
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖包是否已安装"""
    try:
        import flask
        import requests
        import openai
        print("✓ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ['data', 'templates', 'static/css', 'static/js']
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
    print("✓ 目录结构检查完成")

def main():
    """主函数"""
    print("=" * 50)
    print("    Twitter AI 监控系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建目录
    create_directories()
    
    # 启动Flask应用
    print("\n启动Flask应用...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务\n")
    
    try:
        # 导入并运行Flask应用
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")
        print("请检查配置是否正确")

if __name__ == "__main__":
    main() 