import mysql.connector 
import csv
from dotenv import load_dotenv
import os

load_dotenv()

# establishing a connection 

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

#creating a cursor

cursor = conn.cursor()

with open ("users.csv", newline='',encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        cursor.execute("""
                       INSERT INTO Users (Email, Username, Gender, Age, Birthdate, Country)
                       VALUES (%s, %s,%s,%s,%s,%s)
                       """, (
                           row["email"],
                           row["username"],
                           row["gender"],
                           row["age"],
                           row["birthdate"],
                           row["country"],
                       ))
conn.commit()

print("connected successfully")