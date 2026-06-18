from typing import Any
import json

def safe_json_dumps(obj: Any, indent: int = 2) -> str:
    try:
        return json.dumps(obj, indent=indent, default=str)
    except Exception:
        return str(obj)