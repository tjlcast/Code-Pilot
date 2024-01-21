#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2024/1/19 S{TIME} 
# @Name parse_creata_sql. Py
# @Author：jialtang
import json
import re
from typing import Dict, Union


def parser_create_sql(create_sql: str) -> Dict[str, Union[str, list]]:
    return parse_create_table(create_sql)


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
            "name": table_name,
            "columns": []
        }

        for column in columns:
            column_info = {
                "name": column.group("column_name"),
                "type": column.group("data_type"),
                "constraints": column.group("constraints")
            }
            table_structure["columns"].append(column_info)

        return table_structure
    else:
        return None


if __name__ == "__main__":
    # 示例SQL语句
    sql_statement = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        email VARCHAR(100) UNIQUE,
    );
    """

    sql_statement = """
    create table bs_user
    (
        id        INTEGER      not null,
        user_name VARCHAR(255) not null,
        email     VARCHAR(255) not null,
        passwd    TEXT not null,
    );
    """

    # 解析SQL语句
    table_structure = parse_create_table(sql_statement)
    dumps = json.dumps(table_structure, indent=4)
    print(dumps)
