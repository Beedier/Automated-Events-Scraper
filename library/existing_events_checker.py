import os
import csv
from dbcore import get_config

def get_existing_event_urls():
    config = get_config()

    csv_path = config.get('OLD_DATASET')
    if not csv_path or not os.path.isfile(csv_path):
        print(f"❌ CSV file not found at: {csv_path}")
        return []

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row["Event URL"].strip() for row in reader if row.get("Event URL")]
