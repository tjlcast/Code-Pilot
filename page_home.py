#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/2 S{TIME} 
# @Name page_home. Py
# @Author：jialtang

import streamlit as st
import os

# 这个配置需要在最开始就进行配置
VERSION = "0.0.1"
st.set_page_config(
    "Pilots WebUI",
    os.path.join("img", "chatchat_icon_hangxiaobao.png"),
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/chatchat-space/Langchain-Chatchat',
        'Report a bug': "https://github.com/chatchat-space/Langchain-Chatchat/issues",
        'About': f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！"""
    }
)


from streamlit_option_menu import option_menu
from webui.page_openai import page_openai
from webui.page_prompt import page_prompt, check_user, register_user
from cg.webui import page_cg
from webui.page_file_2_md import page_file_2_md
from webui.web_utils.api_client import ApiRequest
from webui.web_utils.cg_api_client import create_cg_api_client
from webui.web_utils.openai_client import OpenAiApiRequest


@st.cache_resource(ttl=10800)  # 3小时过期
def getOpenApiRequest():
    return OpenAiApiRequest(base_url=os.environ.get("OPENAI_API_ADDR", "http://121.40.102.152:9966"))


@st.cache_resource(ttl=10800)  # 3小时过期
def getApiRequest():
    return ApiRequest()


@st.cache_resource(ttl=10800)  # 3小时过期
def getCgApiClient():
    return create_cg_api_client()


def get_start():
    pages = {
        "Chat Pilot": {
            "icon": "chat",
            "func": page_openai,
        },
        "Prompt Pilot": {
            "icon": "hdd-stack",
            "func": page_prompt,
        },
        "CG Pilot": {
            "icon": "app-indicator",
            "func": page_cg,
        },
        "File_to_MD": {
            "icon": "folder",
            "func": page_file_2_md,
        }
    }

    with st.sidebar:
        st.title('_Nice_ :blue[pilot] :sunglasses:')
        st.caption(
            f"""<p align="right">当前版本：{VERSION}</p>""",
            unsafe_allow_html=True,
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            default_index=0,
        )
        # End of sidebar
        pass

    # according to selected_page
    if selected_page in pages and selected_page != 'Maven Pilot':
        if selected_page == 'Chat Pilot':
            api = getOpenApiRequest()
            pages[selected_page]["func"](api)
        elif selected_page == 'Prompt Pilot':
            api = getOpenApiRequest()
            pages[selected_page]["func"](api)
        else:
            api = getOpenApiRequest()
            pages[selected_page]["func"](api)
    else:
        st.toast(f"{selected_page} 还在施工中...尽情期待")


def login():
    username = st.text_input("用户名", key="user_name")
    password = st.text_input("密码", type="password", key="password")
    submit_button = st.button("登录", key="login")
    if submit_button:
        # 验证用户名和密码
        user = check_user(username, password)
        if user:
            # 登录成功
            st.session_state.login_id = user.id
            st.session_state.login_name = user.name
            st.toast("欢迎， {}!".format(st.session_state.login_name))
            st.rerun()
        else:
            # 登录失败
            st.error("用户名或密码错误，请重试。")


# 注册页面
def register():
    with st.expander("注册"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit_button = st.button("注册", key="register")
        if submit_button:
            # 将新用户添加到数据库
            register_user(username, password)
            st.write("注册成功！")


from dotenv import load_dotenv

# 加载.env文件
load_dotenv(override=True)

if __name__ == "__main__":

    if not st.session_state.get("login_id"):
        login()
        register()
    else:
        # 用户已登录，显示应用内容
        get_start()
