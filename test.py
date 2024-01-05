#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/7 S{TIME} 
# @Name test. Py
# @Author：jialtang
import server.utils


def get_start():
    server.utils.test_get_current_module_name()
    print("Finish started.")


if __name__ == "__main__":
    get_start()

