"""Reports query layer.

Pure functions that filter, sort, and paginate the in-memory dataset. Kept separate
from the HTTP layer (`main.py`) so it can be reused by any future export feature.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.data import all_reports
from app.models import OwnerAmount, Report, ReportStatus, ReportSummary


_SORTABLE_FIELDS = {"id", "title", "status", "owner", "amount", "created_at"}


def query(
    *,
    status: ReportStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort: str = "created_at",
    descending: bool = True,
) -> list[Report]:
    """Filter and sort reports. Pagination is applied by the caller."""

    if sort not in _SORTABLE_FIELDS:
        raise ValueError(f"Unsupported sort field: {sort!r}")

    rows: Iterable[Report] = all_reports()

    if status is not None:
        rows = (r for r in rows if r.status == status)
    if date_from is not None:
        rows = (r for r in rows if r.created_at >= date_from)
    if date_to is not None:
        rows = (r for r in rows if r.created_at <= date_to)

    return sorted(rows, key=lambda r: getattr(r, sort), reverse=descending)


def summarize(
    *,
    status: ReportStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> ReportSummary:
    """Return aggregate statistics for the filtered report set."""

    rows = query(status=status, date_from=date_from, date_to=date_to)

    total_reports = len(rows)
    total_amount = round(sum(r.amount for r in rows), 2)
    average_amount = round(total_amount / total_reports, 2) if total_reports else 0.0

    counts_by_status: dict[str, int] = {}
    owner_amounts: dict[str, float] = {}
    for r in rows:
        counts_by_status[r.status] = counts_by_status.get(r.status, 0) + 1
        owner_amounts[r.owner] = owner_amounts.get(r.owner, 0.0) + r.amount

    top_3 = sorted(owner_amounts.items(), key=lambda x: x[1], reverse=True)[:3]

    return ReportSummary(
        total_reports=total_reports,
        total_amount=total_amount,
        average_amount=average_amount,
        counts_by_status=counts_by_status,
        top_3_owners_by_amount=[
            OwnerAmount(owner=owner, total_amount=round(amount, 2))
            for owner, amount in top_3
        ],
    )
