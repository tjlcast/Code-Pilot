#!/usr/bin/env python
import io
import os
import streamlit as st
import time


import streamlit as st
from streamlit_chatbox import *

from webui.web_utils.api_client import ApiRequest
from markitdown import MarkItDown


def page_file_2_md(api: ApiRequest = None):
    # 文件上传
    uploaded_file = st.file_uploader(
        "上传文件", type=["txt", "csv", "pdf", "xlsx", "doc"])

    if uploaded_file is not None:
        # 显示上传的文件内容
        file_details = {"文件名": uploaded_file.name,
                        "文件类型": uploaded_file.type, "文件大小": uploaded_file.size}
        st.write(file_details)

        # 异步处理文件
        with st.spinner("正在处理文件..."):
            st.toast("上传成功")
            md = MarkItDown()
            result = md.convert_stream(io.BytesIO(
                uploaded_file.getvalue())).text_content
            st.toast(f"转换完成 {len(result)}")

        st.success("文件处理完成！")

        # 修改文件扩展名为 .md
        file_name, _ = os.path.splitext(uploaded_file.name)
        new_file_name = f"{file_name}.md"

        st.download_button(
            label="下载处理后的文件",
            data=result,
            file_name=f"processed_{new_file_name}",  # 使用新的文件名
            mime="text/markdown",  # 指定 MIME 类型为 Markdown
        )

# 模拟文件处理函数


def process_file(file):
    # 模拟处理过程（这里简单地将文件内容转换为大写）
    time.sleep(5)  # 模拟耗时操作
    processed_content = file.getvalue().upper()
    return processed_content


if __name__ == "__main__":
    page_file_2_md()
