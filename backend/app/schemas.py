"""Pydantic request/response models shared by the API endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    session_id: str
    query: str = Field(..., min_length=1, max_length=500)
