import json
import uuid
from pathlib import Path

_history = []
current_session_id = None
MAX_HISTORY_MESSAGES = 8

def start_new_session():
    global current_session_id, _history
    current_session_id = str(uuid.uuid4())
    _history = []
    return current_session_id

def add_message(role, content):
    _history.append({"role": role, "content": content})

def get_messages_for_request(system_prompt, new_question):
    recent_history = _history[-MAX_HISTORY_MESSAGES:] if len(_history) > 0 else []
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": new_question})
    return messages

def reset_history():
    global _history
    _history.clear()

def save_session():
    if not current_session_id:
        return
    Path("sessions").mkdir(exist_ok=True)
    filepath = Path("sessions") / f"{current_session_id}.json"
    data = {"session_id": current_session_id, "messages": _history}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_session(session_id):
    global current_session_id, _history
    filepath = Path("sessions") / f"{session_id}.json"
    if not filepath.exists():
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            _history = data.get("messages", [])
            current_session_id = session_id
            return True
    except Exception:
        return False