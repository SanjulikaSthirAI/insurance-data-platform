import psycopg2
import os

print("Connecting to postgres database...")
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="1234",
    port=5432
)
conn.autocommit = True
cursor = conn.cursor()

sql_file_path = r"C:\Users\User\Downloads\insurance_claim_report_script.sql"
print(f"Reading SQL file from {sql_file_path}...")
with open(sql_file_path, "r", encoding="utf-8") as f:
    sql = f.read()

print("Executing SQL script...")
cursor.execute(sql)
print("Successfully seeded the database with raw tables and data!")

cursor.close()
conn.close()
