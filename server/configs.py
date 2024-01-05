#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/3 S{TIME} 
# @Name configs. Py
# @Author：jialtang

import os

from dotenv import load_dotenv

load_dotenv()

config = dict({
    "model_name": "gpt-3.5-turbo",
    "api_base_url": "https://api.openai.com/v1",
    "api_key": "xxxx",
    "openai_proxy": "xxxx",
})

config["api_key"] = os.environ["OPENAI_API_KEY"]

PROMPT_TEMPLATES = {}
PROMPT_TEMPLATES["llm_chat"] = {
    "default":
        """
        {{ input }}
        """,

    "py":
        """
        你是一个聪明的代码助手，请你给我写出简单的py代码。 \n
        {{ input }}
        """
    ,
    "hangxiaobao":
        """
        你是一个聪明的代码助手，名字叫杭小宝，你在编程上很厉害。 \n
        {{ input }}
        """
    ,
    "hangzhibao":
        """
        你是一个聪明的代码助手，名字叫杭智宝，你在编程上很厉害。 \n
        {{ input }}
        """
    ,
}


def get_start():
    pass
    print("Finish started.")


if __name__ == "__main__":
    get_start()
