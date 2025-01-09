FROM python:3.10.6

# 设置code文件夹是工作目录
WORKDIR /app/Code-Pilot

# 复制代码到工作目录
COPY ./Code-Pilot /app/Code-Pilot

# 禁用缓存并批量安装包(后面的链接是利用豆瓣源安装，速度会加快) pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN  pip install --no-cache-dir --upgrade -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
