#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2024/1/7 S{TIME} 
# @Name template_engine. Py
# @Author：jialtang


import json
import re


class TemplateEngine:
    def __init__(self, template):
        self.template = template

    def render(self, data_dict):
        return self.template.format(**data_dict)

    def extract_params(self):
        # 使用正则表达式匹配模板中的所有参数占位符
        params = re.findall(r'\{(\w+)\}', self.template)
        # 将参数列表转换为字典
        param_dict = {param: param for param in params}
        # 将字典转换为JSON字符串
        return json.dumps(param_dict)


def test1():
    template = "Hello, {name}! The answer is {answer}."
    engine = TemplateEngine(template)
    context = {"name": "Alice", "answer": 42}

    result = engine.render(context)
    print(result)


def test2():
    # 示例使用
    template = "Hello, {name}! The answer is {answer}"
    engine = TemplateEngine(template)
    print(engine.extract_params())  # 输出： {"name": "name", "answer": "answer"}


if __name__ == '__main__':
    test2()
