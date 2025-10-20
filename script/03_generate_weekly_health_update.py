# 03_generate_weekly_health_trend_batch_verbose.py
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

DB_PATH = "surin_health.db"
NUM_WEEKS = 12  # week simulate
BATCH_SIZE = 10000  # batch insert size

print("Connecting to SQLite DB...")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Fetching person table...")
person_df = pd.read_sql_query("SELECT person_id FROM person", conn)
person_ids = person_df['person_id'].tolist()
print(f"Number of people: {len(person_ids)}")

print("Fetching latest health records for all people...")
latest_health_df = pd.read_sql_query("""
    SELECT person_id, height_cm, blood_type, weight_kg
    FROM health
    WHERE check_date = (SELECT MAX(check_date) FROM health h2 WHERE h2.person_id = health.person_id)
""", conn)
latest_health_df.set_index("person_id", inplace=True)
print(f"Latest health records loaded: {len(latest_health_df)} rows")

today = datetime.today()
batch = []
total_inserted = 0

for week in range(NUM_WEEKS):
    check_date = today - timedelta(weeks=NUM_WEEKS - week - 1)
    print(f"\n Generating records for week {week+1} ({check_date.date()})")

    for idx, pid in enumerate(person_ids, 1):
        prev = latest_health_df.loc[pid]

        height = prev['height_cm']  # ส่วนสูงคงที่
        blood_type = prev['blood_type']  # คงที่
        weight = round(prev['weight_kg'] + random.uniform(-3, 3), 1)  # ±3kg
        bmi = round(weight / ((height / 100) ** 2), 1)
        systolic = random.randint(100, 140)
        diastolic = random.randint(60, 90)
        cholesterol = random.randint(150, 250)
        sugar = random.randint(70, 160)
        exercise = random.randint(0, 7)
        smoke = random.choices([0, 1], weights=[0.85, 0.15])[0]
        alcohol = random.choices([0, 1], weights=[0.7, 0.3])[0]

        batch.append((
            pid, height, weight, bmi, systolic, diastolic,
            blood_type, cholesterol, sugar, exercise, smoke, alcohol,
            check_date.date()
        ))

        latest_health_df.loc[pid, 'weight_kg'] = weight

        if len(batch) >= BATCH_SIZE:
            cur.executemany("""
                INSERT INTO health (
                    person_id, height_cm, weight_kg, bmi, systolic, diastolic,
                    blood_type, cholesterol, blood_sugar, exercise_freq, smoking, alcohol, check_date
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            conn.commit()
            total_inserted += len(batch)
            print(f"Inserted batch of {len(batch)} records (total so far: {total_inserted})")
            batch.clear()

# insert remaining
if batch:
    cur.executemany("""
        INSERT INTO health (
            person_id, height_cm, weight_kg, bmi, systolic, diastolic,
            blood_type, cholesterol, blood_sugar, exercise_freq, smoking, alcohol, check_date
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, batch)
    conn.commit()
    total_inserted += len(batch)
    print(f"Inserted remaining {len(batch)} records (total so far: {total_inserted})")

conn.close()
print(f"\nDone! Added {total_inserted} weekly health records for {len(person_ids)} people over {NUM_WEEKS} weeks.")
