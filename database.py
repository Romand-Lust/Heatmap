# database.py
import json
from datetime import datetime

def save_session(date, heatmap_path):
    db_file = "data/sessions.json"
    try:
        with open(db_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data[date] = heatmap_path
    with open(db_file, "w") as f:
        json.dump(data, f)
