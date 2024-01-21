#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:18
# @Name. Py
# @Author: jialtang

import re
from typing import List


def split_string(s: str) -> List[str]:
    result = []
    word = ''
    for char in s:
        if char.isupper():
            if word:  # 如果word非空，则添加到结果列表中
                result.append(word)
                word = ''
        elif char == '_' or char == '-' or char == ' ':
            if word:
                result.append(word)
                word = ''
                continue
        word += char
    if word:  # 处理最后一个可能的单词
        result.append(word)
    return result


def to_snake_case(name):
    # 将驼峰命名转换为蛇形命名
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    # 将帕斯卡命名转换为蛇形命名
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name).lower()
    # 将下划线命名转换为蛇形命名
    name = re.sub(r'_+', '_', name).lower()
    # 将空格命名转换为蛇形命名
    name = re.sub(r'\s+', '_', name).lower()
    # 将连字符命名转换为蛇形命名
    name = re.sub(r'-+', '_', name).lower()
    return name


def lower_camel_case(name: str) -> str:
    # replace = name.title().replace("_", "")
    # return replace[0].lower() + replace[1:]
    # 将下划线命名、帕斯卡命名、蛇形命名、空格命名和连字符命名转换为小驼峰命名
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    s1 = re.sub('_+', '_', s1)
    components = s1.split('_')
    # 我们保留第一个单词的原始大小写格式
    return components[0] + ''.join(x.title() for x in components[1:])


def upper_camel_case(s: str):
    words = split_string(s)
    join = "".join(word.title() for word in words if word)
    return join


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

    print(upper_camel_case("camelCase"))  # 输出: CamelCase
    print(upper_camel_case("PascalCase"))  # 输出: PascalCase
    print(upper_camel_case("snake_case"))  # 输出: SnakeCase
    print(upper_camel_case("kebab-case"))  # 输出: KebabCase
    print(upper_camel_case("space case"))  # 输出: SpaceCase


    def split_string(s):
        result = []
        word = ''
        for char in s:
            if char.isupper():
                if word:  # 如果word非空，则添加到结果列表中
                    result.append(word)
                    word = ''
            elif char == '_' or char == '-' or char == ' ':
                if word:
                    result.append(word)
                    word = ''
                    continue
            word += char
        if word:  # 处理最后一个可能的单词
            result.append(word)
        return result


    s = "HelloIAmTjl"
    print(split_string(s))

    s = "helloIAmTjl"
    print(split_string(s))

    s = "camelCase"
    print(split_string(s))

    s = "snake_case"
    print(split_string(s))

    s = "kebab-case"
    print(split_string(s))

    s = "space case"
    print(split_string(s))
