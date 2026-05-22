import json
import os
from datetime import datetime
from threading import Lock

FILE_PATH = "data/history.json"

# 🔥 thread-safe lock (important for production)
lock = Lock()


# ---------------- ENSURE FILE ----------------
def ensure_file():
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump([], f)


# ---------------- SAVE ----------------
def save_to_json(data):
    data["timestamp"] = datetime.utcnow().isoformat()
    try:
        ensure_file()

        with lock:  # 🔥 prevent race condition
            with open(FILE_PATH, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []

            existing.append(data)

            with open(FILE_PATH, "w") as f:
                json.dump(existing, f, indent=4)

    except Exception as e:
        print("ERROR (save_to_json):", e)


# ---------------- READ ----------------
def read_json():
    try:
        ensure_file()

        with open(FILE_PATH, "r") as f:
            return json.load(f)

    except Exception as e:
        print("ERROR (read_json):", e)
        return []


# ---------------- CLEAR ----------------
def clear_json():
    try:
        with lock:
            with open(FILE_PATH, "w") as f:
                json.dump([], f)

    except Exception as e:
        print("ERROR (clear_json):", e)