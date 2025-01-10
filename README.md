## Run

运行
``` sh
nohup ./run_webui.ps1 &
```


## DevEnv

创建python虚拟环境
```python
python -m venv .env
```

激活虚拟环境
```python
source .env/bin/activate
```

安装依赖（从清华源）
```python
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Config
数据库路径为运行时目录中的`./mydatabase.db`

配置文件拷贝 `.env.sample` 为 `.env`，修改其中的LLM配置项

- OPENAI_API_KEY= "xxxx"
  - LLM的key
- OPENAI_API_ADDR = "http://xxx.xxx:80"
  - LLM的endpoint
- OPENAI_API_URL = "/v1/chat/completions"
  - LLM的请求路径
- OPENAI_MODEL_NAME="qwen-72b"
  - LLM的模型参数

