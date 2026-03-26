import mysql.connector 
import csv

# establishing a connection 

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root123",
    database = "DataCatalog"
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