"""Audit logging for interview sessions.

Stores structured audit events in Redis (rpush to list) with
JSON-lines file fallback. Follows the redis_store.py pattern.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
AUDIT_LOG_DIR = os.getenv(
    "AUDIT_LOG_DIR",
    str(Path(__file__).parent.parent.parent / "audit_logs"),
)

_audit_logger = None


def get_audit_logger() -> "AuditLogger":
    """Get or create the singleton AuditLogger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


class AuditLogger:
    """Append-only audit log with Redis primary and file fallback."""

    def __init__(self):
        self._redis = None
        try:
            import redis
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
            )
            client.ping()
            self._redis = client
        except Exception:
            pass
        self._log_dir = Path(AUDIT_LOG_DIR)

    @property
    def is_redis_available(self) -> bool:
        return self._redis is not None

    def log_event(
        self,
        session_id: str,
        event_type: str,
        data: Optional[dict] = None,
    ) -> None:
        """Append an audit event for a session.

        Args:
            session_id: The session identifier.
            event_type: Event name (e.g., "answer", "retry", "contradiction").
            data: Optional event payload.
        """
        entry = {
            "timestamp": time.time(),
            "session_id": session_id,
            "event_type": event_type,
            "data": data or {},
        }
        serialized = json.dumps(entry)

        if self._redis:
            try:
                self._redis.rpush(f"audit:{session_id}", serialized)
                return
            except Exception:
                pass

        # File fallback
        self._write_to_file(session_id, serialized)

    def log_answer(
        self,
        session_id: str,
        question_id: int,
        answer: str,
        score: float,
        category: str = "",
    ) -> None:
        """Log an answer event."""
        self.log_event(session_id, "answer", {
            "question_id": question_id,
            "answer": answer,
            "score": score,
            "category": category,
        })

    def log_retry(
        self,
        session_id: str,
        question_id: int,
        attempt: int,
    ) -> None:
        """Log a retry event."""
        self.log_event(session_id, "retry", {
            "question_id": question_id,
            "attempt": attempt,
        })

    def log_contradiction(
        self,
        session_id: str,
        question_id: int,
        reason: str,
    ) -> None:
        """Log a contradiction detection event."""
        self.log_event(session_id, "contradiction", {
            "question_id": question_id,
            "reason": reason,
        })

    def log_language_switch(
        self,
        session_id: str,
        direction: str,
        question_id: int = 0,
    ) -> None:
        """Log a language switch event."""
        self.log_event(session_id, "language_switch", {
            "direction": direction,
            "question_id": question_id,
        })

    def get_session_log(self, session_id: str) -> list[dict]:
        """Retrieve all audit events for a session.

        Returns:
            List of event dicts, ordered chronologically.
        """
        if self._redis:
            try:
                entries = self._redis.lrange(f"audit:{session_id}", 0, -1)
                return [json.loads(e) for e in entries]
            except Exception:
                pass

        # File fallback
        return self._read_from_file(session_id)

    def _write_to_file(self, session_id: str, serialized: str) -> None:
        """Append a JSON line to the session's audit log file."""
        self._log_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._log_dir / f"{session_id}.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(serialized + "\n")

    def _read_from_file(self, session_id: str) -> list[dict]:
        """Read all events from a session's audit log file."""
        file_path = self._log_dir / f"{session_id}.jsonl"
        if not file_path.exists():
            return []
        events = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events
