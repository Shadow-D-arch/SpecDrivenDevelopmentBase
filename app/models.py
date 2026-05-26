"""Pydantic models for the Reports app.
The CSV export feature added during the workshop must also honor this distinction.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ReportStatus = Literal["pending", "approved", "rejected", "archived"]


class Report(BaseModel):
    """Internal report model. Holds every field, including internal-only ones."""

    model_config = ConfigDict(frozen=True)

    id: int
    internal_id: str  # INTERNAL ONLY — must never be exposed
    title: str
    status: ReportStatus
    owner: str
    owner_email: str  # INTERNAL ONLY — must never be exposed
    amount: float
    created_at: datetime


class ReportPublic(BaseModel):
    """Public response shape. Omits internal-only fields by construction."""

    id: int
    title: str
    status: ReportStatus
    owner: str
    amount: float
    created_at: datetime

    @classmethod
    def from_internal(cls, r: Report) -> "ReportPublic":
        return cls(
            id=r.id,
            title=r.title,
            status=r.status,
            owner=r.owner,
            amount=r.amount,
            created_at=r.created_at,
        )


class ReportListResponse(BaseModel):
    """Paginated list response."""

    items: list[ReportPublic]
    total: int = Field(description="Total number of rows matching the filter")
    offset: int
    limit: int


class OwnerAmount(BaseModel):
    owner: str
    total_amount: float


class ReportSummary(BaseModel):
    """Aggregated summary of reports matching the applied filters."""

    total_reports: int
    total_amount: float
    average_amount: float
    counts_by_status: dict[str, int]
    top_3_owners_by_amount: list[OwnerAmount]
