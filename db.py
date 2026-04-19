import os
import streamlit as st
import mysql.connector

def get_secret(name):
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name)

def get_connection():
    host = get_secret("AVN_HOST")
    port = get_secret("AVN_PORT")
    user = get_secret("AVN_USER")
    password = get_secret("AVN_PASSWORD")
    database = get_secret("AVN_DATABASE")

    if not all([host, port, user, password, database]):
        raise ValueError(
            "Missing DB config. Required: AVN_HOST, AVN_PORT, AVN_USER, AVN_PASSWORD, AVN_DATABASE"
        )

    return mysql.connector.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
    )