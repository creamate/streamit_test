import streamlit as st
import requests
from time import sleep

st.set_page_config(
    page_icon="🐶",
    page_title="streamlit test",
    layout="wide",
)
# 로딩바 구현하기
with st.spinner(text="페이지 로딩중..."):
    sleep(1.1)
    st.header("streamlit test page👋")
    st.subheader("testing")
