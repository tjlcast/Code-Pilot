#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/6 S{TIME} 
# @Name api_chat. Py
# @Author：jialtang

import asyncio
# from configs import LLM_MODEL, TEMPERATURE
# from server.utils import wrap_done, get_ChatOpenAI
from typing import AsyncIterable
from typing import List

from fastapi import Body
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate

import server.utils
from server.chat.utils import History

LLM_MODEL = "OpenAI"
TEMPERATURE = 0.7


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               history: List[History] = Body([],
                                             description="历史对话",
                                             examples=[[
                                                 {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                 {"role": "assistant", "content": "虎头虎脑"}]]
                                             ),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
               max_tokens: int = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               ):
    history = [History.from_data(h) for h in history]

    return StreamingResponse(chat_iterator(
        temperature=temperature,
        query=query,
        history=history,
        model_name=model_name,
        prompt_name=prompt_name,
        stream=stream,
        max_tokens=max_tokens,
    ), media_type="text/event-stream")


async def chat_iterator(
        temperature: float,
        query: str,
        history: List[History] = [],
        model_name: str = LLM_MODEL,
        prompt_name: str = 'default',
        max_tokens: int = None,
        stream: bool = False,
) -> AsyncIterable[str]:
    handler = AsyncIteratorCallbackHandler()
    model = server.utils.get_ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens,
                                        callbacks=[handler], )

    prompt_template = server.utils.get_prompt_template("llm_chat", prompt_name)
    # prompt_template = '{{ input }}'
    input_msg = History(role="user", content=prompt_template).to_msg_template(False)
    combine_history_query = [i.to_msg_template() for i in history] + [input_msg]
    chat_prompt = ChatPromptTemplate.from_messages(combine_history_query)
    '''Below is an example for chat_prompt.format(input="hi"):
    user: hi
    assistant: Hello! How can I assist you today?
    user: hello
    assistant: Hello! How can I assist you today?
    '''

    # Build a chain.
    chain = LLMChain(prompt=chat_prompt, llm=model, verbose=True)

    # Start a task that runs in the background.
    task = asyncio.create_task(
        server.utils.wrap_done(
            chain.acall({"input": query}),
            handler.done,
        )
    )

    if stream:
        async for token in handler.aiter():
            yield token
    else:
        answer = ""
        async for token in handler.aiter():
            answer += token
        yield answer

    await task


async def get_start():
    iterator = chat_iterator(temperature=0.7, query="hi",
                             history=[History.from_human_data("hello"), History.from_assistant_data("hi"), ],
                             model_name="OpenAI", stream=True, )
    async for line in iterator:
        print(f"line: {line}")

    print("Finish")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_start())
    loop.stop()
