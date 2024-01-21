#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:31
# @Name. Py
# @Author: jialtang
import json
from typing import List, Dict, Tuple

from jinja2 import Template

import cg.utils as utils
from cg.tpl import *
from cg.utils import database_type_to_java_type

# 添加filter到jingja2的环境变量中
tpl = Template("")
tpl.environment.filters['lower_camel_case'] = utils.lower_camel_case
tpl.environment.filters['upper_camel_case'] = utils.upper_camel_case
tpl.environment.filters['to_snake_case'] = utils.to_snake_case


def genereate_entity_in_context(context):
    # 解析JSON数据
    table_name = context['table']['name']
    columns = context['table']['columns']

    # 生成类名，通常是表名首字母大写
    java_name = utils.upper_camel_case(table_name)
    entity_dict = {"name": "", "fields": []}

    # 生成类的字段
    java_fields = []
    for column in columns:
        # 提取字段名和类型
        field_name = utils.lower_camel_case(column['name'])
        field_type = column['type'].upper()

        # 处理字段类型
        java_type = database_type_to_java_type(field_type)

        # 添加到字段列表
        java_fields.append({'name': field_name, 'type': java_type})

    entity_dict["name"] = java_name
    entity_dict["fields"] = java_fields
    context["entity"] = entity_dict


def generate_java_class(context, tpl_str: str) -> Tuple[str, str, List[Dict]]:
    java_name = context["entity"]["name"]
    java_fields = context["entity"]["fields"]
    java_class_template = Template(tpl_str)

    # 使用模板渲染Java类
    java_class = java_class_template.render(
        ctx=context,
    )

    return java_name, java_class, java_fields


# 示例JSON数据
json_data = """
{
    "table": {
        "name": "bs_user",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "constraints": "not null"
            },
            {
                "name": "user_name",
                "type": "VARCHAR(255)",
                "constraints": "not null"
            },
            {
                "name": "email",
                "type": "VARCHAR(255)",
                "constraints": "not null"
            },
            {
                "name": "passwd",
                "type": "TEXT",
                "constraints": "not null"
            }
        ]
    }
}
"""

# 生成Java类
if __name__ == "__main__":
    context = json.loads(json_data)
    genereate_entity_in_context(context)
    java_name, java_class, java_fields = generate_java_class(context, tpls['entity'])
    print(java_name)
    print(java_class)
    print(java_fields)
