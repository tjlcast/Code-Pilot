#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Time 2023/11/2 S{TIME} 
# @Name page_code. Py
# @Author：jialtang

import json
import os
import pandas as pd
import streamlit as st
from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField, DateTimeField, ForeignKeyField
from streamlit_tree_select import tree_select

from webui.web_utils.openai_client import OpenAiApiRequest
from webui.web_utils.template_engine import TemplateEngine

db = SqliteDatabase('./mydatabase.db', pragmas={'foreign_keys': 1})


@st.cache_resource(ttl=10800)  # 3小时过期
def getDb():
    db.connect(True)
    return


def page_prompt(api: OpenAiApiRequest):
    # 查询用户
    user_id = st.session_state.get("login_id")
    user_name = st.session_state.get("login_name")
    entity_dict = {}
    prompt_dict = {}
    with st.sidebar:
        select = UserPrompt.select().where(UserPrompt.user_id == user_id)
        for i in range(select.count()):
            entity_dict[select[i].id] = select[i]
        dicts = select.dicts()
        user_prompts = list(dicts)
        node_map = {}
        node_root = []
        for user_prompt in user_prompts:
            prompt_dict[user_prompt.get("id")] = user_prompt
            node_map[user_prompt.get("id")] = {"label": user_prompt.get("name"), "value": user_prompt.get("id")}

        for user_prompt in user_prompts:
            id = user_prompt.get("id")
            parent_id = user_prompt.get("parent_id", -1)
            node = node_map.get(id)
            if parent_id != -1:
                parent_node = node_map.get(parent_id, {})
                parent_node_children = parent_node.get("children", [])
                parent_node_children.append(node)
                parent_node["children"] = parent_node_children
            else:
                node.setdefault("children", [])
                node_root.append(node)

        st.write("您的提示词分组如下：")
        return_select = tree_select(nodes=node_root, only_leaf_checkboxes=True, no_cascade=True, expand_on_click=True,
                                    check_model="leaf")

        dialogue_mode = st.selectbox("请选择操作模式：",
                                     [
                                         "创建提示词",
                                         "删除分组",
                                         "创建分组",
                                     ],
                                     index=0,
                                     key="dialogue_mode",
                                     # on_change=chat_model_selector,
                                     )
        if dialogue_mode == "删除分组":
            group_ids = [x.get("value") for x in node_root]
            delete_group_id = st.selectbox("选择一个分组", options=group_ids, format_func=lambda x: entity_dict.get(x).name)

            def delete_group():
                UserPrompt.delete().where(UserPrompt.parent_id == delete_group_id).execute()
                UserPrompt.delete().where(UserPrompt.id == delete_group_id).execute()
                # BsUserPromptExecuteHistory.delete().where(BsUserPromptExecuteHistory.prompt_id == delete_group_id).execute()
                st.toast("成功删除!")

            st.button("删除", on_click=lambda: delete_group())

        elif dialogue_mode == "创建提示词":
            group_ids = [x.get("value") for x in node_root]
            select_group_id = st.selectbox("选择一个分组", options=group_ids, format_func=lambda x: entity_dict.get(x).name)

            prompt_name = st.text_input("请输入提示词名称")
            button_val = st.button("创建")
            if button_val:
                UserPrompt.create(name=prompt_name, parent_id=select_group_id,
                                  user_id=1, params="{}")
                st.toast("成功创建提示词：" + prompt_name)

        elif dialogue_mode == "创建分组":
            group_name = st.text_input("输入分组名称")
            if st.button("创建"):
                UserPrompt.create(name=group_name, group_id=0, parent_id=-1, user_id=1)
                st.toast("成功创建分组：" + group_name)
        st.write(return_select)
    # end st.siderbar

    for select_id_str in return_select.get("checked"):
        with st.expander(entity_dict.get(int(select_id_str)).name):
            select_id = int(select_id_str)
            name = prompt_dict.get(select_id).get("name")
            template = prompt_dict.get(select_id).get("template")
            params = prompt_dict.get(select_id).get("params")

            template_flag_select_str = st.selectbox("选项占位符", ["{}","$"],
                                                index=0,
                                                key=select_id_str+"template_flag_select"
                                                )
            template_flag_select = 0 if template_flag_select_str == "{}" else 1

            template_input = st.text_area(name + "--提示词模版", value=template, max_chars=None,
                                          key=select_id_str + "--提示词模版",
                                          help=None, on_change=None, args=None, kwargs=None)

            cols_mid = st.columns(3)
            # start extract button
            if cols_mid[0].button(
                    "提取参数",
                    # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                    use_container_width=True,
                    type="primary",
                    key="extract_params" + select_id_str
            ):
                params_extract = TemplateEngine(template_input, template_flag_select).extract_params()
                # params = params_extract
                st.info(params_extract)
            # end extract button
            # start origin button
            if cols_mid[1].button(
                    "显示原值",
                    # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                    use_container_width=True,
                    type="primary",
                    key="show_origin" + select_id_str
            ):
                pass
            # end origin button

            try:
                params_json = json.loads(params)
                params = json.dumps(params_json, indent=4, ensure_ascii=False)
            except Exception as e:
                st.error("该params格式不对，不是json")
            params_input = st.text_area(name + "--提示词参数", value=params, max_chars=None,
                                        key=select_id_str + "--提示词参数",
                                        help=None, on_change=None, args=None, kwargs=None)

            cols = st.columns(3)

            # start update button
            if cols[0].button(
                    "保存",
                    # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                    use_container_width=True,
                    type="primary",
                    key="save" + select_id_str,
            ):
                prompt_entity = entity_dict.get(select_id)
                prompt_entity.template = template_input
                prompt_entity.params = params_input
                prompt_entity.save()
                st.toast("保存成功！")

            # end update button

            # start delete button
            if cols[1].button(
                    "删除",
                    # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                    use_container_width=True,
                    type="primary",
                    key="delete" + select_id_str
            ):
                prompt_entity = entity_dict.get(select_id)
                prompt_entity.delete_instance()
                st.rerun()
            # end delete button

            # start execute button
            cols1 = st.columns(3)
            if cols1[0].button(
                    "执行",
                    # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                    use_container_width=True,
                    type="primary",
                    key="execute" + select_id_str
            ):
                params_dict = json.loads(params_input)
                tpl_rendered = TemplateEngine(template_input, template_flag_select).render(params_dict)
                r = api.chat_completion_v1(tpl_rendered,
                                           history=[],
                                           model=os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
                                           temperature=0.7,
                                           stream=False,
                                           as_json=True)
                for t in r:
                    # 解析openai返回的json数据，获取其中返回msg
                    print(t)
                    try:
                        assistant_message = t.get("choices", [{}])[0].get("message", {}).get("content", "")
                        st.write("下面是LLM结论：")
                        st.info(assistant_message)
                        # 记录执行结果
                        st.button("记录执行结果", on_click=lambda: create_prompt_history(user_id=st.session_state.login_id,
                                                                                   user_name=st.session_state.login_name,
                                                                                   prompt_id=select_id,
                                                                                   ask=tpl_rendered,
                                                                                   reply=assistant_message))
                    except Exception as e:
                        st.error("LLM occurs error: " + str(e) + " reply: " + json.dumps(t))
            # end execute button
            # start render button
            if cols1[1].button(
                    "渲染",
                    # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                    use_container_width=True,
                    type="primary",
                    key="render" + select_id_str
            ):
                params_dict = json.loads(params_input)
                tpl_rendered = TemplateEngine(template_input, template_flag_select).render(params_dict)
                print(tpl_rendered)
                st.write("下面是渲染结果：")
                st.info(tpl_rendered)
            # end render button
        st.divider()
        with st.expander(entity_dict.get(int(select_id_str)).name + "--history"):
            prompt_execute_history(st.session_state.login_id, select_id)
        st.divider()


class BaseModel(Model):
    class Meta:
        database = db


class UserPrompt(BaseModel):
    id = IntegerField(unique=True, column_name="id")
    user_id = IntegerField(column_name="user_id")
    name = CharField(column_name="name")
    template = CharField(column_name="template")
    params = CharField(column_name="params")
    parent_id = IntegerField(column_name="parent_id")

    class Meta:
        table_name = 'bs_user_prompt'  # 这里可以自定义表名


class User(BaseModel):
    id = IntegerField(unique=True, column_name="id")
    name = CharField(column_name="user_name")
    email = CharField(column_name="email")
    passwd = CharField(column_name="passwd")

    class Meta:
        table_name = 'bs_user'  # 这里可以自定义表名


def check_user(user_name, passwd):
    first = User.select().where(User.name == user_name, User.passwd == passwd).first()
    return first


def register_user(user_name, passwd):
    user = User(name=user_name, passwd=passwd, email="")
    user.save()


def prompt_execute_history(user_id: int, prompt_id: int):
    history = list_prompt_execute_history(user_id, prompt_id)
    l = list(history.dicts())
    df = pd.DataFrame(l, columns=["ask", "reply", "create_time"])
    st.table(df)


class BsUserPromptExecuteHistory(BaseModel):
    id = IntegerField(unique=True, column_name="id")
    prompt_id = ForeignKeyField(UserPrompt, column_name="prompt_id", on_delete='cascade')
    ask = TextField(column_name="ask")
    reply = TextField(column_name="reply")
    model = TextField(column_name="model")
    url = TextField(column_name="url")
    request = TextField(column_name="request")
    response = TextField(column_name="response")
    create_time = DateTimeField(column_name="create_time")
    user_id = IntegerField(column_name="user_id")
    user_name = TextField(column_name="user_name")

    class Meta:
        table_name = 'bs_user_prompt_execute_history'  # 这里可以自定义表名


def list_prompt_execute_history(user_id: int, prompt_id: int):
    return BsUserPromptExecuteHistory.select().where(BsUserPromptExecuteHistory.user_id == user_id,
                                                     BsUserPromptExecuteHistory.prompt_id == prompt_id)


def create_prompt_history(user_id: int, prompt_id: int, ask: str, reply: str, model: str = "", url: str = "",
                          request: str = "",
                          response: str = "", user_name: str = ""):
    BsUserPromptExecuteHistory.create(
        user_id=user_id,
        user_name=user_name,
        prompt_id=prompt_id,
        ask=ask,
        reply=reply,
        model=model,
        url=url,
        request=request,
        response=response,
    )


if __name__ == "__main__":
    db = getDb()
    # register_user("tjl", "123")
    check_user("tjl", "123")
    print("finish")
