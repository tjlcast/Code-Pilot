#!/bin/bash

VERSION=${1:-0.0.1}

# 检查当前目录的名称是否为'docker'，否则直接退出
current_dir=$(basename $(pwd))
if [ "$current_dir" != "docker" ]; then
    echo "当前目录不是'docker'，退出脚本."
    exit 1
fi

# 工程的ROOT路径
PROJECT_PATH=$(dirname $PWD)
# 工程的ROOT名字
PROJECT_NAME=$(basename $(dirname $PWD))

rm -rf ./$PROJECT_NAME
rsync -av --exclude='venv' --exclude='.git' --exclude='.idea' --exclude='.env' --exclude='docker' $PROJECT_PATH ./

docker build --no-cache -t code-pilot:$VERSION .

rm -rf ./$PROJECT_NAME
