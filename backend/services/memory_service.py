import json
import os
from datetime import datetime

STORAGE_DIR = "storage"
MEDICAL_PATH = os.path.join(STORAGE_DIR, "medical_memory.json")
CHAT_PATH = os.path.join(STORAGE_DIR, "chat_memory.json")
MAX_CHAT = 50


def get_medical_memory() -> dict:
    with open(MEDICAL_PATH, "r") as f:
        return json.load(f)


def save_medical_memory(memory: dict):
    with open(MEDICAL_PATH, "w") as f:
        json.dump(memory, f, indent=2)


def add_to_medical_memory(new_data: dict):
    current = get_medical_memory()

    # Deduplicate medications (case-insensitive)
    existing = [
        (m.get("name", "") if isinstance(m, dict) else m).lower()
        for m in current["medications"]
    ]
    for med in new_data.get("medications", []):
        name = med.get("name", "") if isinstance(med, dict) else med
        if name.lower() not in existing:
            current["medications"].append(med)
            existing.append(name.lower())

    # Deduplicate conditions
    existing_c = [c.lower() for c in current["conditions"]]
    for cond in new_data.get("conditions", []):
        if cond.lower() not in existing_c:
            current["conditions"].append(cond)
            existing_c.append(cond.lower())

    # Deduplicate allergies
    existing_a = [a.lower() for a in current["allergies"]]
    for allergy in new_data.get("allergies", []):
        if allergy.lower() not in existing_a:
            current["allergies"].append(allergy)
            existing_a.append(allergy.lower())

    save_medical_memory(current)


def get_medication_names_only() -> list:
    meds = get_medical_memory().get("medications", [])
    return [m.get("name", m) if isinstance(m, dict) else m for m in meds]


def get_chat_history() -> list:
    with open(CHAT_PATH, "r") as f:
        return json.load(f)


def add_chat_message(role: str, message: str):
    history = get_chat_history()
    history.append({
        "role": role,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    if len(history) > MAX_CHAT:
        history = history[-MAX_CHAT:]
    with open(CHAT_PATH, "w") as f:
        json.dump(history, f, indent=2)


def clear_medical_memory():
    save_medical_memory({"medications": [], "conditions": [], "allergies": []})


def clear_chat_history():
    with open(CHAT_PATH, "w") as f:
        json.dump([], f)
