# 01_generate_mock_up_data.py

import os
import sys
import json
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta


''' จากข้อมูลจำนวนประชากรจังหวัดสุรินทร์ ณ วันที่ 31 ธันวาคม 2566 และจำนวนอำเภอทั้งหมด 17 อำเภอ สามารถคำนวณหาค่าเฉลี่ยจำนวนคนต่ออำเภอได้ดังนี้ 
ค่าเฉลี่ยจำนวนคนต่ออำเภอในจังหวัดสุรินทร์
ประชากรทั้งหมด: 1,392,229 คน (ข้อมูล ณ วันที่ 31 ธันวาคม 2566 โดยกรมการปกครอง)
จำนวนอำเภอ: 17 อำเภอ
การคำนวณ: 1,392,229 คน ÷ 17 อำเภอ
ค่าเฉลี่ย: ประมาณ 81,896 คนต่ออำเภอ 

min 35,496
max 217,140 '''

# districts = [
#     "อำเภอเมืองสุรินทร์", "อำเภอชุมพลบุรี", "อำเภอท่าตูม", "อำเภอจอมพระ", 
#     "อำเภอปราสาท", "อำเภอกาบเชิง", "อำเภอรัตนบุรี", "อำเภอสนม",
#     "อำเภอศีขรภูมิ", "อำเภอสังขะ", "อำเภอลำดวน", "อำเภอสำโรงทาบ", 
#     "อำเภอบัวเชด", "อำเภอพนมดงรัก", "อำเภอศรีณรงค์", 
#     "อำเภอเขวาสินรินทร์", "อำเภอโนนนารายณ์"
# ]

fake = Faker("th_TH")

# กำหนดอำเภอ 2 แห่งพร้อมสัดส่วนประชากร
districts = [
    ("อำเภอเมืองสุรินทร์", 0.65),
    ("อำเภอจอมพระ", 0.35)
]

# utility functions
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# เตรียม cache ชื่อไว้ก่อน เพื่อลดเวลาสุ่มซ้ำ
names_male = [fake.name_male() for _ in range(5000)]
names_female = [fake.name_female() for _ in range(5000)]

# Settings
NUM_PEOPLE = 100_000
BATCH_SIZE = 10_000   # Batch for reduce memory

person_records = []
health_records = []

os.makedirs("output_json", exist_ok=True)
print("...Generating mock data...")

for i in range(1, NUM_PEOPLE + 1):
    pid = 100000 + i
    gender = random.choice(["male", "female"])
    name = random.choice(names_male) if gender == "male" else random.choice(names_female)
    first, last = name.split(" ")[0], name.split(" ")[-1]
    birth = random_date(datetime(1960, 1, 1), datetime(2010, 12, 31))
    district = random.choices([d[0] for d in districts], weights=[d[1] for d in districts])[0]

    person_records.append({
        "person_id": pid,
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "birth_date": str(birth.date()),
        "district": district,
        "province": "สุรินทร์"
    })

    # generate health info
    height = round(random.uniform(150, 180), 1)
    weight = round(random.uniform(45, 90), 1)
    bmi = round(weight / ((height / 100) ** 2), 1)
    systolic = random.randint(100, 140)
    diastolic = random.randint(60, 90)
    blood_type = random.choice(["A", "B", "AB", "O"])
    cholesterol = random.randint(150, 250)
    sugar = random.randint(70, 160)
    exercise = random.randint(0, 7)
    smoke = random.choices([0, 1], weights=[0.85, 0.15])[0]
    alcohol = random.choices([0, 1], weights=[0.7, 0.3])[0]
    check_date = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))

    health_records.append({
        "check_id": 500000 + i,
        "person_id": pid,
        "height_cm": height,
        "weight_kg": weight,
        "bmi": bmi,
        "systolic": systolic,
        "diastolic": diastolic,
        "blood_type": blood_type,
        "cholesterol": cholesterol,
        "blood_sugar": sugar,
        "exercise_freq": exercise,
        "smoking": smoke,
        "alcohol": alcohol,
        "check_date": str(check_date.date())
    })

    # batch
    if i % BATCH_SIZE == 0 or i == NUM_PEOPLE:
        part = i // BATCH_SIZE
        person_path = f"output_json/person_part_{part}.json"
        health_path = f"output_json/health_part_{part}.json"

        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(person_records, f, ensure_ascii=False, indent=2)

        with open(health_path, "w", encoding="utf-8") as f:
            json.dump(health_records, f, ensure_ascii=False, indent=2)

        print(f"Saved batch {part} ({i:,} records)")

        person_records.clear()
        health_records.clear()
        fake = Faker("th_TH")  # reset Faker protect memory leak

print("Done! Generated 100,000 mock records in JSON format.")