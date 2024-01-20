#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:31
# @Name. Py
# @Author: jialtang


import json
from typing import List, Dict, Tuple

from jinja2 import Template

from cg.tpl import *
from cg.utils import database_type_to_java_type


def generate_java_class(json_data: str, tpl_str: str) -> Tuple[str, str, List[Dict]]:
    java_class_template = Template(tpl_str)
    # 解析JSON数据
    data = json.loads(json_data)
    table_name = data['table']['table_name']
    columns = data['table']['columns']

    # 生成类名，通常是表名首字母大写
    java_name = table_name.title().replace('_', '')

    # 生成类的字段
    java_fields = []
    for column in columns:
        # 提取字段名和类型
        field_name = column['name']
        field_type = column['type'].upper()

        # 处理字段类型
        java_type = database_type_to_java_type(field_type)

        # 添加到字段列表
        java_fields.append({'name': field_name, 'type': java_type})

    # 使用模板渲染Java类
    java_class = java_class_template.render(
        class_name=java_name,
        fields=java_fields
    )

    return java_name, java_class, java_fields


# 示例JSON数据
json_data = """
{
    "table": {
        "table_name": "bs_user",
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
    java_name, java_class, java_fields = generate_java_class(json_data, tpls['entity'])
    print(java_name)
    print(java_class)
    print(java_fields)
