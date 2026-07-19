import streamlit as st
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
if st.button('SIGNUP',type='primary'):
    st.switch_page('pages/signup.py')
if st.button('LOGIN',type='primary'):
    st.switch_page('pages/login.py')