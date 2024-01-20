#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2024/1/19 S{TIME} 
# @Name parse_creata_sql. Py
# @Author：jialtang


import re


def parse_create_table(sql_statement):
    # 使用正则表达式匹配CREATE TABLE语句
    pattern = r"CREATE TABLE\s+(?P<table_name>\w+)\s*\((?P<columns>.*?)\)\s*;"
    match = re.search(pattern, sql_statement, re.IGNORECASE | re.DOTALL)

    if match:
        table_name = match.group('table_name')
        columns_str = match.group('columns')

        # 解析列定义
        column_pattern = r"(?P<column_name>\w+)\s+(?P<data_type>\w+(\s*\(\d+(,\s*\d+)?\))?)(?:\s+(?P<constraints>.*?))?(?=,|\))"
        columns = re.finditer(column_pattern, columns_str)

        table_structure = {
            'table_name': table_name,
            'columns': []
        }

        for column in columns:
            column_info = {
                'name': column.group('column_name'),
                'type': column.group('data_type'),
                'constraints': column.group('constraints')
            }
            table_structure['columns'].append(column_info)

        return table_structure
    else:
        return None


# 示例SQL语句
sql_statement = """
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE
);
"""

# 解析SQL语句
table_structure = parse_create_table(sql_statement)
print(table_structure)

