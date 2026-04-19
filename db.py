import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("AVN_HOST"),
        user=os.getenv("AVN_USER"),
        password=os.getenv("AVN_PASSWORD"),
        database=os.getenv("AVN_DB"),
        port=int(os.getenv("AVN_PORT"))
    )