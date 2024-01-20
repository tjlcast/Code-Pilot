#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 10:53
# @Name. Py
# @Author: jialtang

from typing import Any

import streamlit as st

import cg.utils as utils
from cg.generator import *
from cg.parse_creata_sql import parser_create_sql

input_help_msg = """
create table bs_user
(
    id        INTEGER      not null,
    user_name VARCHAR(255) not null,
    email     VARCHAR(255) not null,
    passwd    TEXT not null,
);
"""


def page_cg(api: Any):
    template_input = st.text_area("create sql", max_chars=None, height=300, help=input_help_msg,
                                  on_change=None, args=None, kwargs=None)
    if st.button("parse"):
        dict = parser_create_sql(template_input)
        table = dict
        context = {"table": table}
        msg = "```\n" + json.dumps(context, indent=4) + "\n```"
        with st.expander(label="context", expanded=True):
            st.markdown(msg)

        for k, v in tpls.items():
            java_name, java_class, java_fields = generate_java_class(json.dumps(context), v)
            with st.expander(label=k + " --- " + java_name):
                st.markdown(utils.file_in_markdown_code(java_class))
