#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:18
# @Name. Py
# @Author: jialtang


def file_in_markdown_code(code: str) -> str:
    return "```\n" + code + "\n````"


def database_type_to_java_type(db_type):
    # 定义一个映射字典，将数据库类型映射到Java类型
    type_mapping = {
        'int': 'Integer',
        'integer': 'Integer',
        'smallint': 'short',
        'bigint': 'Long',
        'float': 'Float',
        'double': 'Double',
        'decimal': 'java.math.BigDecimal',
        'varchar': 'String',
        'char': 'String',
        'text': 'String',
        'date': 'java.util.Date',
        'datetime': 'java.util.Date',
        'timestamp': 'java.sql.Timestamp',
        'boolean': 'Boolean',
        'bit': 'Boolean'
    }

    # 检查是否为varchar类型，并提取长度信息
    if db_type.lower().startswith('varchar'):
        # 假设格式为varchar(30)，提取长度信息
        length_start = db_type.find('(')
        length_end = db_type.find(')')
        if length_start != -1 and length_end != -1:
            length_str = db_type[length_start + 1:length_end]
            try:
                length = int(length_str)
                # 对于varchar类型，我们返回String，因为Java中没有varchar类型
                return 'String'
            except ValueError:
                pass

    # 如果不是varchar类型，或者提取长度信息失败，则使用映射字典
    db_type_lower = db_type.lower()
    return type_mapping.get(db_type_lower, 'Object')


if __name__ == '__main__':
    # 示例使用
    print(database_type_to_java_type('varchar'))  # 输出: String
    print(database_type_to_java_type('varchar(30)'))  # 输出: String
    print(database_type_to_java_type('int'))  # 输出: int
    print(database_type_to_java_type('datetime'))  # 输出: java.util.Date
