#!/bin/bash
# API 测试运行脚本

set -e

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -q -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，使用默认配置"
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "已从 env.example 创建 .env 文件，请根据需要修改"
    fi
fi

# 创建报告目录
mkdir -p reports

# 运行测试
echo "运行测试..."
pytest "$@"

