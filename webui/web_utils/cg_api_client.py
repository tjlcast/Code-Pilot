#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/27 S{TIME} 
# @Name cg_api_client. Py
# @Author：jialtang

import json

from server.response import BaseResponse
from webui.web_utils.api_client import ApiRequest


def create_cg_api_client(ip: str = "127.0.0.1", port: int = 9866, is_mock: bool = False):
    url = f"http://{ip}:{port}"

    if is_mock:
        return MockCgApiClient()
    else:
        return CgApiClient(url)


class CgApiClient(ApiRequest):
    def __init__(
            self,
            base_url: str = "http://127.0.0.1:9866",
            # httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
            timeout: float = 300.0,
    ):
        super(CgApiClient, self).__init__(base_url, timeout)

    def list_cg_projects(self):
        url = "/genspace/"
        response = self.get(url)
        return BaseResponse.from_json_str(response.text).data

    def show_cg_project(self, project_name):
        url = f"/genspace/{project_name}"
        response = self.get(url)
        return BaseResponse.from_json_str(response.text).data

    def delete_cg_project(self, project_name):
        url = f"/genspace/{project_name}"
        response = self.delete(url)
        assert response.status_code == 200

    def list_db_tables(self):
        url = "/db/tables"
        response = self.get(url)
        return BaseResponse.from_json_str(response.text).data

    def list_entities(self, table_name):
        url = f"/tables/{table_name}/entities"
        response = self.get(url)
        return BaseResponse.from_json_str(response.text).data

    def generate_cg_project(self, table_name, entity_name, project_name, bussi_package, entity_package_name,
                            project_desc):
        url = f"/gen/project"
        data = {
            "tableName": table_name,
            "entityName": entity_name,
            "projectName": project_name,
            "bussiPackage": bussi_package,
            "entityPackageName": entity_package_name,
            "projectDesc": project_desc,
        }
        response = self.get(url, data=data)
        assert response.status_code == 200

    def download_proj_zip(self, project_name):
        url = f"/genspace/{project_name}/download"
        response = self.get(url)
        return response

    def search_table(self, search_key, field=""):
        url = f"/search"
        response = self.post(url, {"query": search_key, "field": field})
        return BaseResponse.from_json_str(response.text).data

    def show_table(self, tableName):
        url = f"/db/table"
        response = self.get(url, {"tableName": tableName})
        return BaseResponse.from_json_str(response.text).data


class MockCgApiClient(CgApiClient):

    def __init__(
            self,
            base_url: str = "http://127.0.0.1:9866",
            # httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
            timeout: float = 300.0,
    ):
        self.MOCK_PROJ_LIST = {}
        self.MOCK_PROJ_LIST['DemoProj'] = {
            "tableName": "demo",
            "entityName": "Demo",
            "projectName": 'DemoProj',
            "bussiPackage": 'com.jialtang',
            "entityPackageName": 'demo',
            "projectDesc": "This is proj for demo",
        }
        self.MOCK_PROJ_LIST['autogen'] = {
            "tableName": "ceshi_note",
            "entityName": "CeShiNote",
            "projectName": 'autogen',
            "bussiPackage": 'com.jialtang',
            "entityPackageName": 'ceshi',
            "projectDesc": "This is proj for ceshi",
        }
        self.MOCK_PROJ_LIST['autogen1'] = {
        }

    def list_cg_projects(self):
        return dict(self.MOCK_PROJ_LIST)

    def list_db_tables(self):
        return list(["ceshi_note", "demo"])

    def show_cg_project(self, project_name):
        return ['DemoProj/DemoProj.iml', 'DemoProj/src/main/java/com/jialtang/demo/vo/Result.java',
                'DemoProj/src/main/java/com/jialtang/demo/Application.java',
                'DemoProj/src/main/java/com/jialtang/demo/example_pom.xml',
                'DemoProj/src/main/java/com/jialtang/demo/config/Swagger2Config.java',
                'DemoProj/src/main/java/com/jialtang/demo/config/MybatisPlusConfig.java',
                'DemoProj/src/main/java/com/jialtang/demo/entity/Demo.java',
                'DemoProj/src/main/java/com/jialtang/demo/mapper/DemoMapper.java',
                'DemoProj/src/main/java/com/jialtang/demo/mapper/xml/DemoMapper.xml',
                'DemoProj/src/main/java/com/jialtang/demo/controller/DemoController.java',
                'DemoProj/src/main/java/com/jialtang/demo/common/SpringContextUtils.java',
                'DemoProj/src/main/java/com/jialtang/demo/common/utils/oConvertUtils.java',
                'DemoProj/src/main/java/com/jialtang/demo/common/IpUtils.java',
                'DemoProj/src/main/java/com/jialtang/demo/common/CommonConstant.java',
                'DemoProj/src/main/java/com/jialtang/demo/aspect/AutoLogAspect.java',
                'DemoProj/src/main/java/com/jialtang/demo/aspect/annotations/AutoLog.java',
                'DemoProj/src/main/java/com/jialtang/demo/service/impl/DemoServiceImpl.java',
                'DemoProj/src/main/java/com/jialtang/demo/service/IDemoService.java',
                'DemoProj/src/main/java/com/jialtang/demo/example_application.yml']

    def delete_cg_project(self, project_name):
        self.MOCK_PROJ_LIST.pop(project_name)

    def generate_cg_project(self, table_name, entity_name, project_name, bussi_package, entity_package_name,
                            project_desc):
        data = {
            "tableName": table_name,
            "entityName": entity_name,
            "projectName": project_name,
            "bussiPackage": bussi_package,
            "entityPackageName": entity_package_name,
            "projectDesc": project_desc,
        }
        self.MOCK_PROJ_LIST[project_name] = data

    def download_proj_zip(self, project_name):
        raise Exception("To do")

    def search_table(self, search_key):
        return json.loads(
            """[{'createSQL': "CREATE TABLE `ceshi_note` (\n  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,\n  `create_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人',\n  `create_time` datetime DEFAULT NULL COMMENT '创建日期',\n  `update_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人',\n  `update_time` datetime DEFAULT NULL COMMENT '更新日期',\n  `sys_org_code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属部门',\n  `name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '请假人',\n  `sex` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '性别',\n  `days` int DEFAULT NULL COMMENT '请假天数',\n  `dep_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '部门',\n  `dep_leader` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '上级领导',\n  `ccc` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '请假原因',\n  `pic` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '头像',\n  PRIMARY KEY (`id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC", 'tableName': 'ceshi_note'}, {'createSQL': "CREATE TABLE `demo` (\n  `id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '主键ID',\n  `name` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '姓名',\n  `key_word` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '关键词',\n  `punch_time` datetime DEFAULT NULL COMMENT '打卡时间',\n  `salary_money` decimal(10,3) DEFAULT NULL COMMENT '工资',\n  `bonus_money` double(10,2) DEFAULT NULL COMMENT '奖金',\n  `sex` varchar(2) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '性别 {男:1,女:2}',\n  `age` int DEFAULT NULL COMMENT '年龄',\n  `birthday` date DEFAULT NULL COMMENT '生日',\n  `email` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '邮箱',\n  `content` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '个人简介',\n  `create_by` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '创建人',\n  `create_time` datetime DEFAULT NULL COMMENT '创建时间',\n  `update_by` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '修改人',\n  `update_time` datetime DEFAULT NULL COMMENT '修改时间',\n  `sys_org_code` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '所属部门编码',\n  `tenant_id` int DEFAULT '0',\n  `update_count` int DEFAULT NULL COMMENT '乐观锁测试',\n  PRIMARY KEY (`id`) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC", 'tableName': 'demo'}]""")


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 8080
    url = f"http://{ip}:{port}"

    client = CgApiClient(base_url=url)
    table = client.show_table("ceshi_note")
    print(table)
