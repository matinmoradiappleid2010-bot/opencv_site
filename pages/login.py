import streamlit as st
import sqlite3
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"]=False
st.title("Login Page")
username=st.text_input('username')
password=st.text_input('password',type='password')
if st.button('Login',type='primary'):
    if not username or not password:
        st.error('filling username or password')
    else:
        conn=sqlite3.connect("users.db")
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        row=cursor.fetchone()
        conn.close()
        if row:
            st.success('Logged in')
            st.session_state["logged_in"]=True
            st.session_state["current_user"]=username
            st.switch_page('main.py')
        else:
            st.error('wrong info')