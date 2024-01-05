#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/30 S{TIME} 
# @Name CgCommands. Py
# @Author：jialtang
from typing import Union

import httpx
from tabulate import tabulate

# 此处导入的配置为发起请求（如WEBUI）机器上的配置，主要用于为前端设置默认值。分布式部署时可以与服务器上的不同
from configs.log_config import (
    logger, log_verbose,
)


# params = {
#                 "prompt": prompt,
#                 "history": history,
#                 "api": api_client,
#             }


def show_table_info_action(params: dict):
    try:
        client = params["api"]
        prompt = params["prompt"]
        inputs = prompt.split(" ")
        if len(inputs) < 2:
            return "请指定具体表名. 例如： /d table_name"
        table_name = inputs[1]
        table_info = client.show_table(table_name)
        markdown = render_table_markdown(table_info)
        return markdown
    except httpx.ConnectError as e:
        msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except httpx.ReadTimeout as e:
        msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except Exception as e:
        msg = f"API通信遇到错误：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return {"code": 500, "msg": msg}


def snake_to_camel_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def generate_project_action(params: dict):
    try:
        client = params["api"]
        prompt = params["prompt"]
        inputs = prompt.split(" ")
        if len(inputs) < 3:
            return "请指定具体工程名和表名. 例如： /g project_name table_name"
        project_name = inputs[1]
        table_name = inputs[2]
        project = client.generate_cg_project(table_name=table_name, entity_name=snake_to_camel_case(table_name),
                                             project_name=project_name,
                                             bussi_package="com.hzbank", entity_package_name=project_name,
                                             project_desc="Auto generated")
        return {"code": 200,
                "msg": "我已经生成了一个包，点击如下地址进行下载: <br> " + f"<a href='http://127.0.0.1:8080/genspace/{project_name}/download'>下载</a>"}
    except httpx.ConnectError as e:
        msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except httpx.ReadTimeout as e:
        msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except Exception as e:
        msg = f"API通信遇到错误：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return {"code": 500, "msg": msg}


def show_all_table_action(params: dict):
    try:
        client = params["api"]
        tables = client.list_db_tables()

        if len(tables) > 100:
            def generate_long_string_chunks():
                chunk_size = 10
                long_string = tables
                for i in range(0, len(long_string), chunk_size):
                    yield long_string[i:i + chunk_size]

            return generate_long_string_chunks()
        else:
            return tables
    except httpx.ConnectError as e:
        msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except httpx.ReadTimeout as e:
        msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except Exception as e:
        msg = f"API通信遇到错误：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return {"code": 500, "msg": msg}


def get_usage_desc_action(params: dict):
    try:
        desc = "```"
        commands = Commands.values()
        for command in commands:
            desc += "\r\n" + command.get("Description", "desc") + ". Example: " + str(command.get("Simple", "simple"))
        desc += "\r\n```"
        return desc
    except httpx.ConnectError as e:
        msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except httpx.ReadTimeout as e:
        msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except Exception as e:
        msg = f"API通信遇到错误：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return {"code": 500, "msg": msg}


def search_table_action(params: dict):
    try:
        client = params["api"]
        search_key = params["prompt"]

        search_key = search_key.strip()[2:]
        tables = client.search_table(search_key, "tableJSON")

        msg = ""
        if tables != None:
            for table_info in tables[0:5]:
                # sql = table_info.get("createSQL", "None")
                # sql = "\r\n```\r\b" + sql + "\r\n```\r\b"
                render_show = render_table_markdown(table_info)
                msg += render_show
            if len(msg) == 0:
                return "No search result."
            else:
                def generate_long_string_chunks():
                    chunk_size = 100
                    long_string = msg
                    for i in range(0, len(long_string), chunk_size):
                        yield long_string[i:i + chunk_size]

                return generate_long_string_chunks()
        else:
            return "Fail to search"
    except httpx.ConnectError as e:
        msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except httpx.ReadTimeout as e:
        msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
        logger.error(msg)
        return {"code": 500, "msg": msg}
    except Exception as e:
        msg = f"API通信遇到错误：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return {"code": 500, "msg": msg}


def render_table_markdown(table_info: dict):
    fields = table_info.get("fields", None)
    if not fields:
        fields = table_info.get("fieldInfos", None)
    table_name = table_info["tableName"]
    field_array = [["name", "desc", "type"]]
    for field in fields:
        name = field["fieldName"]
        desc = field.get("fieldDesc", None)
        if not desc:
            desc = field.get("filedComment", None)
        type = field.get("fieldType", None)
        field_array.append([name, desc, type])

    # 生成Markdown表格
    markdown_table = tabulate(field_array, headers="firstrow", tablefmt="pipe")

    return "\r\n\r\n" + table_name + "\r\n" + markdown_table


Commands = {
    "All": {
        "Simple": "/A",
        "Description": "展示当前记录的数据表表名",
        "Call": show_all_table_action,
    },
    "Search": {
        "Simple": ["/S", "/s"],
        "Description": "搜索表信息",
        "Call": search_table_action,
    },
    "Generate": {
        "Simple": ["/G", "/g"],
        "Description": "使用表生成: /g prject_name table_name",
        "Call": generate_project_action,
    },
    "Help": {
        "Simple": ["/H", "/h", "/HELP", "/help"],
        "Description": "展示支持的操作",
        "Call": get_usage_desc_action,
    },
    "Detail": {
        "Simple": ["/d", "/D", "/detail"],
        "Description": "根据表名查询表的详情",
        "Call": show_table_info_action,
    },
}


def hit_command(prompt: str):
    for command in Commands.values():
        if type(command["Simple"]) is list:
            for command_s in command["Simple"]:
                if prompt.startswith(command_s):
                    return command.get("Call", None)
        elif type(command["Simple"]) is str:
            if prompt.startswith(command["Simple"]):
                return command.get("Call", None)
        else:
            return None
    return None


def check_error_msg(data: Union[str, dict, list], key: str = "errorMsg") -> str:
    '''
    return error message if error occured when requests API
    '''
    if isinstance(data, dict):
        if key in data:
            return data[key]
        if "code" in data and data["code"] != 200:
            return data["msg"]
    return ""


def get_start():
    pass
    print("Finish started.")


if __name__ == "__main__":
    get_start()
