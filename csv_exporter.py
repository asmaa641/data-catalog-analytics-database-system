import mysql.connector
import pandas as pd
import os

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

tables = [
    "Dataset_Tag", "Dataset", "DatasetUsage", "File_Resource",
    "Publishing_Organization", "Tag", "User"
]

for table in tables:
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    df.to_csv(f"{table}.csv", index=False)

conn.close()

print(" All CSVs exported")