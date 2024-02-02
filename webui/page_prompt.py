#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Time 2023/11/2 S{TIME} 
# @Name page_code. Py
# @Author：jialtang

import json
import os

import pandas as pd
import streamlit as st
from webui.crypt.crypt import KEY
from webui.crypt.crypt import encrypt_integer
from webui.crypt.crypt import decrypt_string
from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField, DateTimeField, ForeignKeyField
from streamlit_tree_select import tree_select

from webui.web_utils.openai_client import OpenAiApiRequest
from webui.web_utils.template_engine import TemplateEngine


@st.cache_resource(ttl=10800)  # 3小时过期
def getDb():
    db = SqliteDatabase('./mydatabase.db', pragmas={'foreign_keys': 1})
    db.connect(True)
    return db


db = getDb()


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
                                     )
        if dialogue_mode == "删除分组":
            group_ids = [x.get("value") for x in node_root]
            delete_group_id = st.selectbox("选择一个分组", options=group_ids, format_func=lambda x: entity_dict.get(x).name)

            def delete_group():
                UserPrompt.delete().where(UserPrompt.parent_id == delete_group_id).execute()
                UserPrompt.delete().where(UserPrompt.id == delete_group_id).execute()
                # 这里通过在表格中设置级联删除，当UserPrompt删除时，会自动删除属于该提示词的历史记录
                st.toast("成功删除!")

            st.button("删除", on_click=lambda: delete_group())

        elif dialogue_mode == "创建提示词":
            group_ids = [x.get("value") for x in node_root]
            select_group_id = st.selectbox("选择一个分组", options=group_ids, format_func=lambda x: entity_dict.get(x).name)

            prompt_name = st.text_input("请输入提示词名称")
            public_name = st.text_input("请输入分享码")
            button_val = st.button("创建")
            if button_val:
                if public_name != "":
                    id = decrypt_string(public_name, KEY)
                    where = UserPrompt.select().where(UserPrompt.id == id).first()
                    if where.is_public==0:
                        st.error("该分享码已经失效！")
                        return
                    prompt_name = prompt_name if prompt_name!="" else where.name
                    UserPrompt.create(name=prompt_name, parent_id=select_group_id, template=where.template,
                                      user_id=user_id, params=where.params)
                    st.toast("成功创建提示词：" + prompt_name)
                else:
                    UserPrompt.create(name=prompt_name, parent_id=select_group_id, template="",
                                  user_id=user_id, params="{}")
                    st.toast("成功创建提示词：" + prompt_name)

        elif dialogue_mode == "创建分组":
            group_name = st.text_input("输入分组名称")
            if st.button("创建"):
                UserPrompt.create(name=group_name, user_id=user_id, parent_id=-1)
                st.toast("成功创建分组：" + group_name)
    # end st.siderbar

    for select_id_str in return_select.get("checked"):
        with st.expander(entity_dict.get(int(select_id_str)).name):
            select_id = int(select_id_str)
            name = prompt_dict.get(select_id).get("name")
            template = prompt_dict.get(select_id).get("template")
            params = prompt_dict.get(select_id).get("params")
            is_public = prompt_dict.get(select_id).get("is_public")
            is_public = False if is_public == 0 else True
            params = json.loads(params)

            template_flag_select_str = st.selectbox("选项占位符", ["{}", "$"],
                                                    index=0,
                                                    key=select_id_str + "template_flag_select"
                                                    )
            template_flag_select = 0 if template_flag_select_str == "{}" else 1

            template_input = st.text_area(name + "--提示词模版", value=template, max_chars=None,
                                          key=select_id_str + "--提示词模版",
                                          help=None, on_change=None, args=None, kwargs=None)

            params_extract = TemplateEngine(template_input, template_flag_select).extract_params()
            params_extract = json.loads(params_extract)

            for key, val in params_extract.items():
                save_val = params.get(key, "")
                input_val = st.text_area(key + "_--提示词参数", value=save_val, max_chars=None,
                                         key=select_id_str + "_" + key + "--提示词参数",
                                         help=None, on_change=None, args=None, kwargs=None)
                params_extract[key] = input_val

            cols = st.columns(3)

            # start update button
            if cols[0].button(
                    "保存",
                    help="保存当前的提示词模版和提示词参数",
                    use_container_width=True,
                    type="primary",
                    key="save" + select_id_str,
            ):
                prompt_entity = entity_dict.get(select_id)
                prompt_entity.template = template_input
                prompt_entity.params = json.dumps(params_extract, ensure_ascii=False)
                prompt_entity.save()
                st.toast("保存成功！")
            # end update button

            # start delete button
            if cols[1].button(
                    "删除",
                    help="删除本提示词以及其历史执行记录",
                    use_container_width=True,
                    type="primary",
                    key="delete" + select_id_str
            ):
                prompt_entity = entity_dict.get(select_id)
                prompt_entity.delete_instance()
                st.rerun()
            # end delete button

            is_public_cols = st.columns(2)
            def change_public(args):
                prompt_entity = entity_dict.get(select_id)
                if st.session_state[args]!=prompt_entity.is_public:
                    prompt_entity.is_public = st.session_state[args]
                    prompt_entity.save()
            is_public_input = is_public_cols[0].checkbox("是否公开", key="is_public" + select_id_str, value=is_public, on_change=change_public, args=("is_public" + select_id_str,))
            if is_public_input:
                is_public_cols[1].markdown("```\n" + encrypt_integer(select_id, KEY) + "\n```")


            # start execute button
            is_markdown = st.checkbox("是否输出markdown格式", key="is_markdown" + select_id_str)
            cols1 = st.columns(3)
            if cols1[0].button(
                    "执行",
                    use_container_width=True,
                    type="primary",
                    key="execute" + select_id_str
            ):
                with st.spinner("Waiting for pilot thinking"):
                    params_dict = params_extract
                    tpl_rendered = TemplateEngine(template_input, template_flag_select).render(params_dict)

                    r = api.chat_completion_v1(tpl_rendered,
                                               history=[],
                                               model=os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
                                               temperature=0.0,
                                               stream=False,
                                               as_json=True)
                    for t in r:
                        # 解析openai返回的json数据，获取其中返回msg
                        print(t)
                        try:
                            assistant_message = t.get("choices", [{}])[0].get("message", {}).get("content", "")
                            st.write("下面是LLM结论：")
                            if is_markdown:
                                assistant_message = "```\n\n" + assistant_message + "\n\n```"
                            st.info(assistant_message)
                            # 记录执行结果
                        except Exception as e:
                            st.error("LLM occurs error: " + str(e) + " reply: " + json.dumps(t))

                    def mark_history(arg_select_id_str):
                        select_id_cur = int(arg_select_id_str)
                        create_prompt_history(user_id=st.session_state.login_id,
                                              user_name=st.session_state.login_name,
                                              prompt_id=select_id_cur, ask=tpl_rendered,
                                              reply=assistant_message)

                    st.button("记录执行结果", key="mark_prompt_history_" + select_id_str, on_click=mark_history,
                              args=(select_id_str,))

        st.divider()
        with st.expander(entity_dict.get(int(select_id_str)).name + "--history"):
            if st.button("删除全部记录", key="delete_all_prompt_history_" + select_id_str):
                delete_all_prompt_history(st.session_state.login_id, select_id)
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
    is_public = IntegerField(column_name="is_public")

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


def delete_all_prompt_history(user_id: int, prompt_id: int):
    BsUserPromptExecuteHistory.delete().where(BsUserPromptExecuteHistory.user_id == user_id,
                                              prompt_id == prompt_id).execute()


def prompt_execute_history(user_id: int, prompt_id: int):
    history = list_prompt_execute_history(user_id, prompt_id)
    l = list(history.dicts())
    df = pd.DataFrame(l, columns=["ask", "reply", "create_time"])
    md = df.to_html()
    st.markdown(md, unsafe_allow_html=True)
    # st.table(df)


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
                                                     BsUserPromptExecuteHistory.prompt_id == prompt_id).order_by(BsUserPromptExecuteHistory.create_time.desc())


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
