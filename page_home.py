#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/2 S{TIME} 
# @Name page_home. Py
# @Author：jialtang

import streamlit as st
from streamlit_option_menu import option_menu

from webui.page_prompt import page_prompt
from webui.page_cg import page_cg
from webui.page_code import page_code
from webui.page_maven import page_maven
from webui.page_openai import page_openai
from webui.web_utils.api_client import ApiRequest
from webui.web_utils.cg_api_client import create_cg_api_client
from webui.web_utils.openai_client import OpenAiApiRequest

VERSION = "0.0.1"


@st.cache_resource(ttl=10800)  # 3小时过期
def getOpenApiRequest():
    return OpenAiApiRequest()


@st.cache_resource(ttl=10800)  # 3小时过期
def getApiRequest():
    return ApiRequest()


@st.cache_resource(ttl=10800)  # 3小时过期
def getCgApiClient():
    return create_cg_api_client()


def get_start():
    st.set_page_config(
        "Pilots WebUI",
        # os.path.join("img", "chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/chatchat-space/Langchain-Chatchat',
            'Report a bug': "https://github.com/chatchat-space/Langchain-Chatchat/issues",
            'About': f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！"""
        }
    )

    pages = {
        "Chat Pilot": {
            "icon": "chat",
            "func": page_openai,
        },
        "Prompt Pilot": {
            "icon": "hdd-stack",
            "func": page_prompt,
        }
    }

    with st.sidebar:
        st.title('_Nice_ :blue[pilot] :sunglasses:')
        # st.title(':blue[HzBank Smart Pilot]')
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
        if selected_page == 'Openai Pilot':
            api = getOpenApiRequest()
            pages[selected_page]["func"](api)
        elif selected_page == 'Prompt Pilot':
            api = getOpenApiRequest()
            pages[selected_page]["func"](api)
        else:
            pass
    else:
        st.toast(f"{selected_page} 还在施工中...尽情期待")


if __name__ == "__main__":
    get_start()
