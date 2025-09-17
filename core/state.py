import json
from pathlib import Path

state_path = 'pdf_state.json'


def read_state() -> dict:
    state_file = Path(state_path)
    if state_file.exists():
        return json.loads(state_file.read_text(encoding = "utf-8"))
    else:
        return {}  # 默认空字典


def write_state(state: dict):
    state_file = Path(state_path)
    state_file.write_text(json.dumps(state, ensure_ascii = False, indent = 2), encoding = "utf-8")


def update_state(key: str, value):
    state = read_state()
    state[key] = value
    write_state(state)
