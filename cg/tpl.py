#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:46
# @Name. Py
# @Author: jialtang


# 示例JSON数据
entity = """
public class {{ class_name }} {
{% for field in fields %}
    private {{ field.type }} {{ field.name }};
{% endfor %}

{% for field in fields %}
    public {{ field.type }} get{{ field.name.title() }}() {
        return this.{{ field.name }};
    }

    public void set{{ field.name.title() }}({{ field.type }} {{ field.name }}) {
        this.{{ field.name }} = {{ field.name }};
    }
{% endfor %}
}
"""

tpls = {
    "entity": entity,
}
