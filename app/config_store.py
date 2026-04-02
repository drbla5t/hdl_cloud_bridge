import json
from pathlib import Path
from typing import Any, Dict


class ConfigStore:
    def __init__(self, path: str = "/data/options.json"):
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path.resolve()}")
        return json.loads(self.path.read_text(encoding="utf-8"))