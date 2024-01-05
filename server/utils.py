#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/3 S{TIME} 
# @Name utils. Py
# @Author：jialtang
import asyncio
from typing import Callable, Any, Optional
from typing import List, Awaitable

from langchain.chat_models import ChatOpenAI

from server.configs import config


# 由Langchain原生支持的模型，这些模型不会走Fschat封装
def get_ChatOpenAI(
        model_name: str,
        temperature: float,
        max_tokens: int = None,
        streaming: bool = True,
        callbacks: List[Callable] = [],
        verbose: bool = True,
        **kwargs: Any,
) -> ChatOpenAI:
    # config = config_models["langchain"][model_name]
    openai_api_key = config.get("api_key")
    model = ChatOpenAI(
        streaming=streaming,
        verbose=verbose,
        callbacks=callbacks,
        model_name=config.get("model_name"),
        # openai_api_base=config.get("api_base_url"),
        openai_api_key=config.get("api_key"),
        # openai_proxy=config.get("openai_proxy"),
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return model


async def wrap_done(fn: Awaitable, event: asyncio.Event):
    """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
    try:
        await fn
    except Exception as e:
        msg = f"Caught exception: {e}"
        # logger.error(f'{e.__class__.__name__}: {msg}',
        #              exc_info=e if log_verbose else None)
    finally:
        event.set()


def get_current_module_name():
    return __name__


def test_get_current_module_name():
    return get_current_module_name()


def get_prompt_template(type: str, name: str) -> Optional[str]:
    '''
    从prompt_config中加载模板内容
    type: "llm_chat","agent_chat","knowledge_base_chat","search_engine_chat"的其中一种，如果有新功能，应该进行加入。
    '''
    from server.configs import PROMPT_TEMPLATES
    # import importlib
    # importlib.reload(PROMPT_TEMPLATES)  # TODO: 检查configs/prompt_config.py文件有修改再重新加载
    return PROMPT_TEMPLATES[type].get(name)


def get_start():
    pass
    print("Finish started.")


if __name__ == "__main__":
    get_start()
