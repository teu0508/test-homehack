"""CLI helper to load and clean the housing pipeline CSV.

Usage:
    python scripts/prepare_data.py [--input path] [--output path]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from utils.data_loader import clean_data, load_raw_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and normalize the housing pipeline dataset")
    parser.add_argument("--input", default=None, help="Path to the raw CSV file")
    parser.add_argument("--output", default="data/cleaned_housing_pipeline.csv", help="Destination for the cleaned CSV")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_raw_data(args.input)
    cleaned = clean_data(df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    print(f"Saved cleaned dataset to {output_path.resolve()}")


if __name__ == "__main__":
    main()
