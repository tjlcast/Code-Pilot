#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/24 S{TIME} 
# @Name page_cg. Py
# @Author：jialtang
import os
import typing
import time
from typing import Tuple, Dict, Literal, List

import pandas as pd
import streamlit as st
from st_aggrid import JsCode, AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_chatbox import *
from streamlit_modal import Modal

from webui.commands.cg_commands import hit_command, check_error_msg
from webui.web_utils.cg_api_client import CgApiClient

# 定义展示对话框
my_modal = Modal(title="", key="modal_key", max_width=800)

chat_box = ChatBox(
    chat_name="cg_chat_bot",
    session_key="cg_chat_bot",
    assistant_avatar=os.path.join(
        "./img",
        "chatchat_icon_hangzhibao.png"
    ),
    user_avatar=os.path.join(
        "./img",
        "chatchat_icon_user.png"
    ),
)


def page_cg(api_client: CgApiClient):
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
                                     ["Proj Talk",
                                      "Proj Manage",
                                      ],
                                     index=0,
                                     key="dialogue_mode",
                                     on_change=chat_model_selector,
                                     )

        if dialogue_mode == "Proj Talk":
            if st.button("清空所有对话", use_container_width=True):
                chat_box.reset_history()

    if dialogue_mode == "Proj Manage":
        proj_manage_page(api_client)
    elif dialogue_mode == "Proj Talk":
        if not chat_box.chat_inited:
            chat_box.init_session()
        chat_box.output_messages()
        chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter "

        # talk
        if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
            history = get_messages_history(3)
            params = {
                "prompt": prompt,
                "history": history,
                "api": api_client,
            }

            chat_box.user_say(prompt)

            command = hit_command(prompt)
            if command:
                chat_box.ai_say("正在思考...")
                res = command(params)
                if isinstance(res, typing.Generator):
                    resp = ""
                    for msg in res:
                        if error_msg := check_error_msg(msg):  # check whether error occured
                            st.error(error_msg)
                            return
                        resp += str(msg)
                        chat_box.update_msg(resp)  # 更新最终的字符串，去除光标
                        time.sleep(1)
                    chat_box.update_msg(resp, streaming=False)  # 更新最终的字符串，去除光标
                elif isinstance(res, dict):
                    if error_msg := check_error_msg(res):  # check whether error occured
                        st.error(error_msg)
                        return
                    chat_box.update_msg(res["msg"], streaming=False)  # 更新最终的字符串，去除光标
                else:
                    if error_msg := check_error_msg(res):  # check whether error occured
                        st.error(error_msg)
                        return
                    res = str(res)
                    chat_box.update_msg(res, streaming=False)  # 更新最终的字符串，去除光标

            else:
                chat_box.ai_say("Unknown command.Please input /h for more info.")


def proj_manage_page(api_client: CgApiClient):
    with st.expander(
            "创建",
            expanded=True,
    ):
        table_names = api_client.list_db_tables()
        table_name = st.selectbox(
            "table_name",
            table_names,
            index=0
        )
        row1 = st.columns(2)
        project_name = row1[0].text_input("project_name")
        entity_name = row1[1].text_input("entity_name")
        row2 = st.columns(3)
        bussi_package = row2[0].text_input("bussi_package")
        entity_package_name = row2[1].text_input("entity_package_name")
        project_desc = row2[2].text_input("project_desc")

        def generate_cg_project():
            msg = ""
            if len(project_name) == 0:
                msg += "project_name is empty"
            if len(entity_name) == 0:
                msg += "entity_name is empty"
            if len(project_name) == 0:
                msg += "project_name is empty"
            if len(bussi_package) == 0:
                msg += "bussi_package is empty"
            if len(entity_package_name) == 0:
                msg += "entity_package_name is empty"

            if len(msg) != 0:
                st.toast(msg)
                return

            api_client.generate_cg_project(
                table_name,
                entity_name,
                project_name,
                bussi_package,
                entity_package_name,
                project_desc
            )
            st.toast("Create successfully.")

        st.button(label="生成", on_click=generate_cg_project)

    projects = api_client.list_cg_projects()
    for key in projects.keys():
        projects[key]["projectName"] = key
    projects = pd.DataFrame(data=projects.values())
    if not len(projects):
        st.info(f"There is no projects")
    else:
        st.write(f"代码库中已有文件:")
        st.info("代码库中包含源文件与配置，请从下表中选择文件后操作")

        gb = config_aggrid(
            projects,
            {
                ("projectName", "生成代码的工程名"): {},
                ("tableName", "生成源表表名"): {},
                ("entityName", "生成代码的实体名"): {},
                ("projectName", "生成代码的工程名"): {},
                ("bussiPackage", "生成代码的包前缀"): {},
                ("bussiPackage", "生成代码的包前缀"): {},
                ("entityPackageName", "生成代码的包名"): {},
                ("projectDesc", "描述"): {},
                # ("in_folder", "源文件"): {"cellRenderer": cell_renderer},
                # ("in_db", "向量库"): {"cellRenderer": cell_renderer},
            },
            "single",
        )

        project_grid = AgGrid(
            projects,
            gb.build(),
            columns_auto_size_mode="FIT_CONTENTS",
            theme="alpine",
            custom_css={
                "#gridToolBar": {"display": "none"},
            },
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False
        )

        selected_rows = project_grid.get("selected_rows", [])

        def deleteProj():
            deleteProjectName = selected_rows[0]["projectName"]
            api_client.delete_cg_project(deleteProjectName)

        cols = st.columns(4)
        if cols[0].button(
                "删除",
                disabled=not (selected_rows),
                use_container_width=True,
                on_click=deleteProj
        ):
            pass

        if cols[1].button(
                "查看Proj",
                disabled=not (selected_rows),
                use_container_width=True,
        ):
            with my_modal.container():
                showProjectName = selected_rows[0]["projectName"]
                proj_info = api_client.show_cg_project(showProjectName)
                st.markdown(f"""
                                     {showProjectName} \r\n
                                     ---\r\n
                                     {proj_info}
                                     """.format(showProjectName=showProjectName, proj_info=proj_info))  # 这里的t[1]为用例名称
                # 定义一个确定按钮，注意key值为指定的session_state，on_click调用回调函数改session_state的值
                st.button("确定", key="confirm")

        showProjectName = selected_rows[0]["projectName"] if len(selected_rows) != 0 else None
        if showProjectName:
            content = api_client.download_proj_zip(showProjectName).content
            cols[2].download_button(
                "下载",
                content,
                file_name=showProjectName + ".zip",
                use_container_width=True, )
        else:
            cols[2].download_button(
                "下载",
                "",
                disabled=True,
                use_container_width=True, )


cell_renderer = JsCode("""function(params) {if(params.value==true){return '✓'}else{return '×'}}""")


def config_aggrid(
        df: pd.DataFrame,
        columns: Dict[Tuple[str, str], Dict] = {},
        selection_mode: Literal["single", "multiple", "disabled"] = "single",
        use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("No", width=40)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    return gb


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


def get_start():
    pass
    print("Finish started.")


if __name__ == "__main__":
    get_start()
