import streamlit as st
import sqlite3
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
st.title("signup Page")
def add_user(username, password):
    conn=sqlite3.connect("users.db")
    cursor=conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",(username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()
username=st.text_input('username')
password=st.text_input('password',type='password')
if st.button('signup',type='primary'):
    if not username or not password:
        st.error('filling username or password')
    else:
        if add_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = username
            st.success("Account created")
            st.switch_page("main.py")
        else:
            st.error("User already exists")
