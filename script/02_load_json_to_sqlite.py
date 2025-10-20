# 02_load_json_to_sqlite.py

import sqlite3
import json
import os

DB_PATH = "surin_health.db"
JSON_FOLDER = "output_json"

# Connect DB
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create Table
cur.execute("""
CREATE TABLE IF NOT EXISTS person (
    person_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    gender TEXT,
    birth_date TEXT,
    district TEXT,
    province TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS health (
    check_id INTEGER PRIMARY KEY,
    person_id INTEGER,
    height_cm REAL,
    weight_kg REAL,
    bmi REAL,
    systolic INTEGER,
    diastolic INTEGER,
    blood_type TEXT,
    cholesterol INTEGER,
    blood_sugar INTEGER,
    exercise_freq INTEGER,
    smoking INTEGER,
    alcohol INTEGER,
    check_date TEXT,
    FOREIGN KEY(person_id) REFERENCES person(person_id)
)
""")

conn.commit()

# Load JSON FILE
person_files = sorted([f for f in os.listdir(JSON_FOLDER) if f.startswith("person")])
health_files = sorted([f for f in os.listdir(JSON_FOLDER) if f.startswith("health")])

# Insert Data
for f in person_files:
    with open(os.path.join(JSON_FOLDER, f), encoding="utf-8") as file:
        data = json.load(file)
        records = [(d['person_id'], d['first_name'], d['last_name'], d['gender'],
                    d['birth_date'], d['district'], d['province']) for d in data]
        cur.executemany("INSERT OR IGNORE INTO person VALUES (?,?,?,?,?,?,?)", records)
        conn.commit()
        print(f"Inserted {len(records)} records from {f} into person")

for f in health_files:
    with open(os.path.join(JSON_FOLDER, f), encoding="utf-8") as file:
        data = json.load(file)
        records = [(d['check_id'], d['person_id'], d['height_cm'], d['weight_kg'], d['bmi'],
                    d['systolic'], d['diastolic'], d['blood_type'], d['cholesterol'],
                    d['blood_sugar'], d['exercise_freq'], d['smoking'], d['alcohol'], d['check_date'])
                   for d in data]
        cur.executemany("INSERT OR IGNORE INTO health VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", records)
        conn.commit()
        print(f"Inserted {len(records)} records from {f} into health")

conn.close()
print("Done! All JSON data loaded into SQLite database.")