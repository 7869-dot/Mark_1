import json
import os
from typing import Dict, Any, Optional

STORE_FILE = os.path.join(os.path.dirname(__file__), "personas.json")

def load_all_personas() -> Dict[str, Any]:
    if not os.path.exists(STORE_FILE):
        return {}
    with open(STORE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_all_personas(data: Dict[str, Any]):
    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_persona(user_id: str, job_context: str, writing_samples: list, style_summary: str):
    personas = load_all_personas()
    personas[user_id] = {
        "job_context": job_context,
        "writing_samples": writing_samples,
        "style_summary": style_summary
    }
    save_all_personas(personas)

def load_persona(user_id: str) -> Optional[Dict[str, Any]]:
    personas = load_all_personas()
    return personas.get(user_id)
