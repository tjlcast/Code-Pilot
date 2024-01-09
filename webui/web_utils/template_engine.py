#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2024/1/7 S{TIME} 
# @Name template_engine. Py
# @Author：jialtang


import json
import re
from string import Template


class TemplateEngine:
    def __init__(self, template, type=0):
        self.type = type
        if self.type == 0:
            self.template = template
        elif self.type == 1:
            self.template = Template(template)

    def render(self, data_dict):
        if self.type == 0:
            return self.template.format(**data_dict)
        elif self.type == 1:
            return self.template.substitute(data_dict)

    def extract_params(self):
        if self.type == 0:
            # 使用正则表达式匹配模板中的所有参数占位符
            params = re.findall(r'\{(\w+)\}', self.template)
            # 将参数列表转换为字典
            param_dict = {param: param for param in params}
            # 将字典转换为JSON字符串
            return json.dumps(param_dict)
        elif self.type == 1:
            params = re.findall(r'\$(\w+)', self.template.template)
            # 将参数列表转换为字典
            param_dict = {param: param for param in params}
            # 将字典转换为JSON字符串
            return json.dumps(param_dict)


def test1():
    template = "Hello, {name} {}! The answer is {answer}."
    engine = TemplateEngine(template)
    context = {"name": "Alice", "answer": 42}

    result = engine.render(context)
    print(result)


def test11():
    template = "Hello, $name! The answer is $answer."
    engine = TemplateEngine(template, 1)
    context = {"name": "Alice", "answer": 42}

    result = engine.render(context)
    print(result)


def test2():
    # 示例使用
    template = "Hello, {name}! The answer is {answer}"
    engine = TemplateEngine(template)
    print(engine.extract_params())  # 输出： {"name": "name", "answer": "answer"}


def test22():
    # 示例使用
    template = "Hello, $name! The answer is $answer, "
    engine = TemplateEngine(template, 1)
    print(engine.extract_params())  # 输出： {"name": "name", "answer": "answer"}


if __name__ == '__main__':
    test2()
