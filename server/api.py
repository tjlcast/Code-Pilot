#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/3 S{TIME} 
# @Name api. Py
# @Author：jialtang
import argparse

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from server.chat import api_chat
from server.response import BaseResponse


# support swagger
async def document():
    return RedirectResponse(url="/docs")


def create_app():
    app = FastAPI(
        title="API Server",
        version="v0.0.1"
    )

    OPEN_CROSS_DOMAIN = True
    if OPEN_CROSS_DOMAIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.get("/",
            response_model=BaseResponse,
            summary="swagger 文档")(document)

    app.get("/hi",
            response_model=BaseResponse,
            summary="api 信息")(hi)

    app.post("/chat/chat",
             tags=["Chat"],
             summary="与llm模型对话(LLMChain)")(api_chat.chat)

    return app


def hi():
    return BaseResponse.from_msg("hello! This is chat api.")


def get_start():
    pass
    print("Finish started.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("server")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default="9866")

    args = parser.parse_args()
    arg_dict = vars(args)

    app = create_app()
    uvicorn.run(app,
                host=args.host,
                port=args.port)

    get_start()
