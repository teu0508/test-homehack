"""Data loading and cleaning utilities for the housing dashboard."""

from __future__ import annotations

import os
from typing import Dict, Iterable, List

import pandas as pd
from dotenv import load_dotenv

# Load environment variables early so DATA_PATH is available when imported
load_dotenv()

DEFAULT_DATA_PATH = os.getenv(
    "DATA_PATH", "data/Copy of Housing_Pipeline_Long_List_External_Hackathon(Longlist).csv"
)


def _normalize_columns(columns: Iterable[str]) -> List[str]:
    """Normalize column names by stripping whitespace and replacing breaks.

    The dataset contains line breaks within headers (e.g., "Number\n Of Units ").
    This helper collapses whitespace to make downstream selection easier.
    """

    normalized: List[str] = []
    for column in columns:
        cleaned = " ".join(str(column).replace("\n", " ").split())
        normalized.append(cleaned)
    return normalized


def load_raw_data(path: str | None = None) -> pd.DataFrame:
    """Load the raw CSV file.

    Parameters
    ----------
    path: str | None
        Optional custom path; falls back to ``DATA_PATH`` env var.
    """

    csv_path = path or DEFAULT_DATA_PATH
    # The source file occasionally includes Windows-1252 characters (e.g., £),
    # which pandas cannot decode with the default UTF-8 setting. Explicitly
    # setting the encoding keeps the loader resilient across environments.
    return pd.read_csv(csv_path, encoding="latin1")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Perform light-weight cleaning and normalization.

    Steps include:
    * Normalize column headers
    * Convert numeric fields
    * Standardize common categorical values
    * Derive helper fields for analytics
    """

    df = df.copy()
    df.columns = _normalize_columns(df.columns)

    # Friendly aliases used across the dashboard
    column_aliases: Dict[str, str] = {
        "LA": "Area",
        "Developer": "Developer",
        "Planning Status": "Planning Status",
        "Developer Status": "Developer Status",
        "Number Of Units": "Units",
        "Site Size (hectares)": "Site Size (hectares)",
        "Revenue / Development Ask": "Cost (£)",
        "Project Completion Date": "Expected Completion",
        "Pipeline First Cut": "Timeline",
        "Mix": "Mix",
        "Greenfield/Brownfield": "Land Type",
        "Sponsor": "Sponsor",
        "Postcode": "Postcode",
        "Project Name": "Project Name",
    }

    for src, dst in column_aliases.items():
        if src in df.columns:
            df[dst] = df[src]

    # Convert numeric fields
    for numeric_col in ["Units", "Site Size (hectares)"]:
        if numeric_col in df.columns:
            df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")

    # Cost can contain text; extract numeric component when possible
    if "Cost (£)" in df.columns:
        df["Cost (£)"] = (
            df["Cost (£)"]
            .astype(str)
            .str.replace(r"[^0-9.]+", "", regex=True)
            .replace("", float("nan"))
        )
        df["Cost (£)"] = pd.to_numeric(df["Cost (£)"], errors="coerce")

    # Normalize text fields
    for text_col in ["Planning Status", "Developer Status", "Timeline", "Land Type"]:
        if text_col in df.columns:
            df[text_col] = (
                df[text_col]
                .astype(str)
                .str.strip()
                .str.replace("  ", " ")
                .str.title()
            )

    # Derived helper columns
    if "Units" in df.columns:
        df["Estimated Capacity (people)"] = (df["Units"] * 1.8).round().astype("Int64")
    if "Expected Completion" in df.columns:
        df["Expected Completion"] = pd.to_datetime(df["Expected Completion"], errors="coerce").dt.date

    return df


__all__ = ["load_raw_data", "clean_data", "DEFAULT_DATA_PATH"]
