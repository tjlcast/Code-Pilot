#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 10:53
# @Name. Py
# @Author: jialtang

from typing import Any

import streamlit as st

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
    template_input = st.text_area("create sql", max_chars=None, height=300, help="Please input create sql",
                                  value=input_help_msg,
                                  on_change=None, args=None, kwargs=None)

    options = st.multiselect(
        'What are your favorite java',
        tpls.keys(),
        tpls.keys())

    if st.button("parse"):
        dict = parser_create_sql(template_input)
        table = dict
        context = {"table": table}
        genereate_entity_in_context(context)

        for k in options:
            v = tpls[k]
            java_name, java_class, java_fields = generate_java_class(context, v)
            with st.expander(label=k + " --- " + java_name):
                st.markdown(utils.file_in_markdown_code(java_class))
