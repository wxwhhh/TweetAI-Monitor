#!/bin/bash

echo "===================================="
echo "    Twitter AI 监控系统"
echo "===================================="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7或更高版本"
    exit 1
fi

# 安装依赖
echo "正在安装依赖包..."
pip3 install -r requirements.txt

# 启动应用
echo
echo "启动应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo
python3 app.py 