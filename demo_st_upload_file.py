import streamlit as st
import time
import pandas as pd
from io import StringIO

# 模拟文件处理函数
def process_file(file):
    # 模拟处理过程（这里简单地将文件内容转换为大写）
    time.sleep(5)  # 模拟耗时操作
    processed_content = file.getvalue().upper()
    return processed_content

# Streamlit 应用
def main():
    st.title("文件处理与下载示例")

    # 文件上传
    uploaded_file = st.file_uploader("上传文件", type=["txt", "csv"])

    if uploaded_file is not None:
        # 显示上传的文件内容
        file_details = {"文件名": uploaded_file.name, "文件类型": uploaded_file.type, "文件大小": uploaded_file.size}
        st.write(file_details)

        # 异步处理文件
        with st.spinner("正在处理文件..."):
            processed_content = process_file(uploaded_file)

        st.success("文件处理完成！")

        # 提供下载按钮
        st.download_button(
            label="下载处理后的文件",
            data=processed_content,
            file_name=f"processed_{uploaded_file.name}",
            mime=uploaded_file.type,
        )

if __name__ == "__main__":
    main()