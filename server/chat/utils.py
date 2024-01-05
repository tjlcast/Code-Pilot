#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/6 S{TIME} 
# @Name utils. Py
# @Author：jialtang

from typing import List, Union, Tuple, Dict

from langchain.prompts.chat import ChatMessagePromptTemplate
from pydantic import BaseModel, Field


class History(BaseModel):
    """
    对话历史
    可从dict生成，如
    h = History(**{"role":"user","content":"你好"})
    也可转换为tuple，如
    h.to_msy_tuple = ("human", "你好")
    """
    role: str = Field(...)
    content: str = Field(...)

    def to_msg_tuple(self):
        return "ai" if self.role == "assistant" else "human", self.content

    def to_msg_template(self, is_raw=True) -> ChatMessagePromptTemplate:
        role_maps = {
            "ai": "assistant",
            "human": "user",
        }
        role = role_maps.get(self.role, self.role)
        if is_raw:  # 当前默认历史消息都是没有input_variable的文本。
            content = "{% raw %}" + self.content + "{% endraw %}"
        else:
            content = self.content

        return ChatMessagePromptTemplate.from_template(
            content,
            "jinja2",
            role=role,
        )

    @classmethod
    def from_data(cls, h: Union[List, Tuple, Dict]) -> "History":
        if isinstance(h, (list, tuple)) and len(h) >= 2:
            h = cls(role=h[0], content=h[1])
        elif isinstance(h, dict):
            h = cls(**h)

        return h

    @classmethod
    def from_assistant_data(cls, h: str) -> "History":
        h = cls(role="assistant", content=h)
        return h

    @classmethod
    def from_human_data(cls, h: str) -> "History":
        h = cls(role="user", content=h)
        return h


def get_start():
    pass
    print("Finish started.")


if __name__ == "__main__":
    get_start()
