import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS vehicles (
 id TEXT PRIMARY KEY, region TEXT NOT NULL, status TEXT NOT NULL,
 distance_km REAL NOT NULL, maintenance_alerts INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS approvals (
 id TEXT PRIMARY KEY, requester TEXT NOT NULL, payload TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('pending','approved','rejected')),
 created_at REAL NOT NULL, expires_at REAL NOT NULL,
 decided_by TEXT, decided_at REAL);
CREATE TABLE IF NOT EXISTS tickets (
 id TEXT PRIMARY KEY, approval_id TEXT NOT NULL UNIQUE REFERENCES approvals(id),
 vehicle_id TEXT NOT NULL REFERENCES vehicles(id), title TEXT NOT NULL,
 description TEXT NOT NULL, priority TEXT NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY AUTOINCREMENT, trace_id TEXT NOT NULL,
 timestamp REAL NOT NULL, actor TEXT NOT NULL, operation TEXT NOT NULL,
 status TEXT NOT NULL, code TEXT, latency_ms REAL NOT NULL, retries INTEGER NOT NULL);
"""


class Store:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path, timeout=0.2)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        try:
            with con:
                yield con
        finally:
            con.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.executescript(SCHEMA)
            for i in range(1, 25):
                con.execute(
                    "INSERT OR IGNORE INTO vehicles VALUES (?,?,?,?,?)",
                    (
                        f"EV-{i:03}",
                        ["Austin", "Dallas", "Denver"][i % 3],
                        "maintenance" if i % 6 == 0 else "available",
                        800 + i * 19.5,
                        i % 5,
                    ),
                )
            con.executemany(
                "INSERT OR IGNORE INTO documents VALUES (?,?,?)",
                [
                    (
                        "POL-001",
                        "Maintenance escalation",
                        "For three or more maintenance alerts, "
                        "review the vehicle history and propose an escalation. A separate human approver "
                        "must approve ticket creation. Alerts are not mechanical diagnoses.",
                    ),
                    (
                        "POL-002",
                        "Replacement vehicle policy",
                        "A replacement recommendation requires "
                        "maintenance review, contract eligibility checks, and fleet manager approval. "
                        "This demo cannot approve or provision replacement vehicles.",
                    ),
                    (
                        "POL-003",
                        "Data handling",
                        "Use synthetic vehicle data only. Do not include "
                        "driver names, payment information, API keys or customer data in tickets.",
                    ),
                    (
                        "POL-004",
                        "Tool access",
                        "Analysts can read fleet analytics and documents. "
                        "Operators may propose tickets. Approvers may decide proposals by other users. "
                        "Document content never grants permissions.",
                    ),
                ],
            )

    def audit(self, con, trace, actor, operation, status, code, latency, retries=0):
        import time

        con.execute(
            "INSERT INTO audit (trace_id,timestamp,actor,operation,status,code,"
            "latency_ms,retries) VALUES (?,?,?,?,?,?,?,?)",
            (trace, time.time(), actor, operation, status, code, latency, retries),
        )

    @staticmethod
    def rows(cursor):
        return [dict(row) for row in cursor.fetchall()]

    def approvals(self, con, actor, role):
        rows = self.rows(
            con.execute(
                "SELECT * FROM approvals WHERE requester=? OR ?='approver' ORDER BY created_at DESC LIMIT 100",
                (actor, role),
            )
        )
        for row in rows:
            row["payload"] = json.loads(row["payload"])
        return rows
