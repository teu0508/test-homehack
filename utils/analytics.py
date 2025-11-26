"""Analytics helpers for KPI calculations and chart-ready summaries."""

from __future__ import annotations

from typing import Dict

import pandas as pd

TARGET_UNITS = 6600
BASELINE_BUILT = 4500


def summarize_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Generate high-level KPIs used on the dashboard."""

    units_total = float(df.get("Units", pd.Series(dtype=float)).sum(skipna=True))
    cost_total = float(df.get("Cost (£)", pd.Series(dtype=float)).sum(skipna=True))

    built_by_status = df[df.get("Planning Status", "").astype(str).str.contains("Complete", case=False, na=False)]
    units_built = (
        float(built_by_status.get("Units", pd.Series(dtype=float)).sum(skipna=True))
        if not built_by_status.empty
        else BASELINE_BUILT
    )

    capacity = float(df.get("Estimated Capacity (people)", pd.Series(dtype=float)).sum(skipna=True))

    return {
        "units_total": units_total,
        "units_built": units_built,
        "target_units": TARGET_UNITS,
        "cost_total": cost_total,
        "capacity": capacity,
    }


def completion_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Group projects by expected completion year."""

    if "Expected Completion" not in df.columns:
        return pd.DataFrame(columns=["Year", "Units"])

    working = df.copy()
    working["Year"] = pd.to_datetime(working["Expected Completion"], errors="coerce").dt.year
    grouped = working.groupby("Year")["Units"].sum().reset_index().dropna()
    return grouped.rename(columns={"Units": "Units"})


def categorical_breakdown(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return counts of units by a categorical column."""

    if column not in df.columns:
        return pd.DataFrame(columns=[column, "Units"])

    grouped = df.groupby(column)["Units"].sum().reset_index().sort_values("Units", ascending=False)
    return grouped


__all__ = ["summarize_kpis", "completion_breakdown", "categorical_breakdown", "TARGET_UNITS", "BASELINE_BUILT"]
