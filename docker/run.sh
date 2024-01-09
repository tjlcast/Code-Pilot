#!/bin/sh

docker rm -f code-pilot

PROJECT_PATH=$(dirname $PWD)
echo $PROJECT_PATH

docker run -itd \
  --name code-pilot \
  -v $PROJECT_PATH/.env:/app/Code-Pilot/.env \
  -v $PROJECT_PATH/mydatabase.db:/app/Code-Pilot/mydatabase.db \
  -p 9966:9966 \
  code-pilot:0.0.1
