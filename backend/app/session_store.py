"""
In-memory session store. Intentionally simple for a portfolio-scale demo: no
database, no auth, no persistence across restarts — a session just holds the
cleaned DataFrame and its profile in memory until it goes stale or the
in-memory cap is hit. This is a deliberate scoping decision (documented in the
README), not an oversight: swapping this for Redis/Postgres later wouldn't
touch the analysis/query logic that sits on top of it.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

import pandas as pd

from .profiling import ColumnProfile

MAX_SESSIONS = 50
SESSION_TTL_SECONDS = 60 * 60 * 2  # 2 hours


@dataclass
class Session:
    session_id: str
    df: pd.DataFrame
    profiles: list[ColumnProfile]
    filename: str
    created_at: float = field(default_factory=time.time)


_STORE: dict[str, Session] = {}


def _evict_stale() -> None:
    now = time.time()
    stale_ids = [sid for sid, s in _STORE.items() if now - s.created_at > SESSION_TTL_SECONDS]
    for sid in stale_ids:
        _STORE.pop(sid, None)
    while len(_STORE) > MAX_SESSIONS:
        oldest = min(_STORE.values(), key=lambda s: s.created_at)
        _STORE.pop(oldest.session_id, None)


def create_session(df: pd.DataFrame, profiles: list[ColumnProfile], filename: str) -> Session:
    _evict_stale()
    session_id = uuid.uuid4().hex
    session = Session(session_id=session_id, df=df, profiles=profiles, filename=filename)
    _STORE[session_id] = session
    return session


def get_session(session_id: str) -> Session | None:
    return _STORE.get(session_id)
