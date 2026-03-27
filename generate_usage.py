import mysql.connector
import random
from faker import Faker
import os
from dotenv import load_dotenv

# load env
load_dotenv()

fake = Faker()

# DB connection
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conn.cursor()

# get users
cursor.execute("SELECT Email FROM Users")
users = [u[0] for u in cursor.fetchall()]

# get datasets
cursor.execute("SELECT Dataset_ID FROM Dataset")
datasets = [d[0] for d in cursor.fetchall()]

categories = ['analytics', 'machine learning', 'field research']

# generate 500 records
for _ in range(500):
    user = random.choice(users)
    dataset = random.choice(datasets)

    cursor.execute("""
        INSERT INTO DatasetUsage
        (Project_Name, Project_Category, Dataset_ID, User_Email)
        VALUES (%s, %s, %s, %s)
    """, (
        fake.catch_phrase(),
        random.choice(categories),
        dataset,
        user
    ))

conn.commit()

print("DatasetUsage populated!")

cursor.close()
conn.close()