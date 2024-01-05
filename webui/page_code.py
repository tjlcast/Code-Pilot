#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/2 S{TIME} 
# @Name page_code. Py
# @Author：jialtang
import os
from datetime import datetime
from typing import List, Dict, Union

import streamlit as st
from streamlit_chatbox import *

from webui.web_utils.api_client import ApiRequest

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "./img",
        "chatchat_icon_hangzhibao.png"
    ),
    user_avatar=os.path.join(
        "./img",
        "chatchat_icon_user.png"
    )
)


def page_code(api: ApiRequest):
    if not chat_box.chat_inited:
        # default_model = get_default_llm_model(api)[0]
        st.toast(
            f"欢迎使用! \n\n"
            # f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    with st.sidebar:
        def chat_model_selector():
            dialogue_mode = st.session_state["dialogue_mode"]
            if dialogue_mode == "知识库问答":
                st.toast(
                    f"还在施工中...尽情期待"
                )
            else:
                st.toast(
                    f"当前运行的模型`{dialogue_mode}`, 您可以开始提问了."
                )

        dialogue_mode = st.selectbox("请选择对话模式：",
                                     ["LLM 对话",
                                      "知识库问答",
                                      ],
                                     index=0,
                                     key="dialogue_mode",
                                     on_change=chat_model_selector,
                                     )

        if dialogue_mode == "知识库问答":
            return

        # default temperature is 0.7
        temperature = st.slider("Temperature：", 0.0, 1.0, 0.7, 0.05)

        # default history is 3
        history_len = st.number_input("历史对话轮数：", 0, 20, 3)

    now = datetime.now()
    with st.sidebar:
        columns = st.columns(2)
        export_button = columns[0]
        if columns[1].button("清空所有对话", use_container_width=True):
            chat_box.reset_history()
            # st.experimental_rerun()

        export_button.download_button(
            "导出记录",
            "".join(chat_box.export2md()),
            file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Display chat messages from history on app rerun
    chat_box.output_messages()
    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter "

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        history = get_messages_history(history_len)
        chat_box.user_say(prompt)
        chat_box.ai_say("正在思考...")

        text = ""
        # text: string
        # history:[
        #   {'role': 'user', 'content': 'hi'},
        #   {'role': 'assistant', 'content': ''},]
        r = api.chat_chat(prompt,
                          history=history,
                          temperature=temperature)
        for t in r:
            if error_msg := check_error_msg(t):  # check whether error occured
                st.error(error_msg)
                break
            text += t
            chat_box.update_msg(text)
        chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标
        # print(f"<>text: {text}")

        # text = f"321 {prompt} 123"
        # chat_box.update_msg(text)
        # chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标

    # print("Finish started.")


def check_error_msg(data: Union[str, dict, list], key: str = "errorMsg") -> str:
    '''
    return error message if error occured when requests API
    '''
    if isinstance(data, dict):
        if key in data:
            return data[key]
        if "code" in data and data["code"] != 200:
            return data["msg"]
    return ""


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


if __name__ == "__main__":
    page_code()
