import os
import yaml
from passlib.context import CryptContext
from utils.audit import log_action


CONFIG_PATH = "config.yaml"

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def load_config(path=CONFIG_PATH):
    if not os.path.exists(path):
        return {"credentials": {"usernames": {}}, "cookie": {}, "preauthorized": {"emails": []}}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(cfg, path=CONFIG_PATH):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


def list_users():
    cfg = load_config()
    return cfg.get("credentials", {}).get("usernames", {})


def get_user(username: str):
    users = list_users()
    return users.get(username)


def create_user(username: str, email: str, name: str, password: str, role: str = "teacher", centre: str = "CENTRE_PAR_DEFAUT", performed_by: str = None):
    cfg = load_config()
    users = cfg.setdefault("credentials", {}).setdefault("usernames", {})
    if username in users:
        raise ValueError("Utilisateur existe déjà")
    users[username] = {
        "email": email,
        "name": name,
        "password": hash_password(password),
        "role": role,
        "centre": centre,
    }
    save_config(cfg)
    try:
        log_action("create_user", username, performed_by=performed_by, details={"email": email, "role": role, "centre": centre})
    except Exception:
        pass


def update_password(username: str, password: str, performed_by: str = None):
    cfg = load_config()
    users = cfg.setdefault("credentials", {}).setdefault("usernames", {})
    if username not in users:
        raise ValueError("Utilisateur introuvable")
    users[username]["password"] = hash_password(password)
    save_config(cfg)
    try:
        log_action("update_password", username, performed_by=performed_by, details={})
    except Exception:
        pass


def update_user(username: str, email: str = None, name: str = None, role: str = None, centre: str = None, performed_by: str = None):
    cfg = load_config()
    users = cfg.setdefault("credentials", {}).setdefault("usernames", {})
    if username not in users:
        raise ValueError("Utilisateur introuvable")
    if email is not None:
        users[username]["email"] = email
    if name is not None:
        users[username]["name"] = name
    if role is not None:
        users[username]["role"] = role
    if centre is not None:
        users[username]["centre"] = centre
    save_config(cfg)
    try:
        log_action("update_user", username, performed_by=performed_by, details={"email": email, "name": name, "role": role, "centre": centre})
    except Exception:
        pass


def delete_user(username: str, performed_by: str = None):
    cfg = load_config()
    users = cfg.setdefault("credentials", {}).setdefault("usernames", {})
    if username in users:
        del users[username]
        save_config(cfg)
        try:
            log_action("delete_user", username, performed_by=performed_by, details={})
        except Exception:
            pass
    else:
        raise ValueError("Utilisateur introuvable")

