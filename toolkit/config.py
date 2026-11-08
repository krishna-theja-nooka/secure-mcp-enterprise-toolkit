import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database: Path
    keys: dict
    requests_per_minute: int = 60

    @classmethod
    def load(cls):
        home = Path(os.getenv("TOOLKIT_HOME", "data")).resolve()
        path = Path(os.getenv("TOOLKIT_KEYS_FILE", str(home / "keys.json")))
        keys = json.loads(path.read_text()) if path.exists() else {}
        return cls(home / "toolkit.db", keys, int(os.getenv("TOOLKIT_RATE_LIMIT", "60")))
