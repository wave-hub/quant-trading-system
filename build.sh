#!/usr/bin/env bash
# Render 部署构建脚本
# 安装 Python 后端依赖 + 构建前端静态文件

set -o errexit

echo "=== 安装 Python 依赖 ==="
pip install -r requirements.txt

echo "=== 安装前端依赖 ==="
cd frontend
npm install

echo "=== 构建前端静态文件 ==="
npm run build
cd ..

echo "=== 构建完成 ==="
