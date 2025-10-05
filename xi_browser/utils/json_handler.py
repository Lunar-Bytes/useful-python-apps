# utils/json_handler.py
import json
import os

def load_json(path: str):
    """
    Robust JSON loader: returns {} if file is missing, empty, or invalid.
    """
    try:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        # corrupted or invalid JSON
        return {}

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)