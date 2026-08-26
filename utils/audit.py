import os
import json
from datetime import datetime

LOG_PATH = "logs/user_actions.log"


def _ensure_dir():
    d = os.path.dirname(LOG_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def log_action(action: str, username: str, performed_by: str = None, details: dict = None):
    _ensure_dir()
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "username": username,
        "performed_by": performed_by,
        "details": details or {},
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_logs(limit: int = None):
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    entries = [json.loads(l) for l in lines]
    if limit:
        return entries[-limit:]
    return entries
