#!/bin/sh

# 默认版本号
VERSION=${1:-0.0.1}

docker save code-pilot:$VERSION > Docker-code-pilot-$VERSION.tar.gz
