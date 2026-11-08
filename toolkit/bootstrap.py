"""Create private local demo credentials; never overwrite existing credentials."""

import hashlib
import json
import os
import secrets
from pathlib import Path

from toolkit.store import Store


def main():
    home = Path(os.getenv("TOOLKIT_HOME", "data")).resolve()
    home.mkdir(parents=True, exist_ok=True)
    path = Path(os.getenv("TOOLKIT_KEYS_FILE", str(home / "keys.json")))
    if path.exists():
        print(f"Credentials already exist at {path}. No files changed.")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tokens = {role: secrets.token_urlsafe(32) for role in ("analyst", "operator", "approver")}
    hashes = {
        hashlib.sha256(key.encode()).hexdigest(): {"id": f"demo-{role}", "role": role}
        for role, key in tokens.items()
    }
    with path.open("x", encoding="utf-8") as out:
        json.dump(hashes, out, indent=2)
    path.chmod(0o600)
    credentials = home / "demo-credentials.json"
    with credentials.open("x", encoding="utf-8") as out:
        json.dump(tokens, out, indent=2)
    credentials.chmod(0o600)
    Store(home / "toolkit.db").initialize()
    print(f"Synthetic database initialized. Private demo keys saved to {credentials}")
    print("Use separate operator and approver keys. Never upload the data folder to GitHub.")


if __name__ == "__main__":
    main()
