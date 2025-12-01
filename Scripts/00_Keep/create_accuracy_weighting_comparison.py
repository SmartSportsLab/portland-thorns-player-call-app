#!/usr/bin/env python3
"""
Create a comparison workbook showing how player scores/grades move
when accuracy metrics carry different weights (80/20, 70/30, 60/40).
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


BASE_DIR = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search")
REPORT_TEMPLATE = "Mike_Norris_Scouting_Report_ACC_IntraConference_{suffix}_PAdj.xlsx"
OUTPUT_PATH = BASE_DIR / "Accuracy_Weighting_Comparison.xlsx"

POSITION_SHEETS = [
    "Hybrid CB",
    "DM Box-To-Box",
    "AM Advanced Playmaker",
    "Right Touchline Winger",
]

WEIGHTING_MAP = {
    "80_20": "80% Attempts / 20% Accuracy",
    "70_30": "70% Attempts / 30% Accuracy",
    "60_40": "60% Attempts / 40% Accuracy",
}


def load_report(suffix: str) -> pd.DataFrame:
    """Load all player rows from a weighting-specific report."""
    path = BASE_DIR / REPORT_TEMPLATE.format(suffix=suffix)
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")

    frames = []
    for sheet in POSITION_SHEETS:
        try:
            df = pd.read_excel(path, sheet_name=sheet)
        except ValueError:
            continue
        if df.empty:
            continue
        df["Position_Profile"] = sheet
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined["Weighting"] = WEIGHTING_MAP[suffix]
    return combined


def build_comparison() -> pd.DataFrame:
    """Combine reports and pivot scores/grades by weighting."""
    data_frames = []
    for suffix in WEIGHTING_MAP:
        df = load_report(suffix)
        if df.empty:
            continue
        subset = df[
            [
                "Player",
                "Team",
                "Position",
                "Position_Profile",
                "2025 Total Score",
                "Conference Grade",
                "Power Five Grade",
                "Weighting",
            ]
        ].copy()
        data_frames.append(subset)

    if not data_frames:
        raise RuntimeError("No report data was loaded for the comparison.")

    combined = pd.concat(data_frames, ignore_index=True)

    pivot_score = combined.pivot_table(
        index=["Player", "Team", "Position", "Position_Profile"],
        columns="Weighting",
        values="2025 Total Score",
        aggfunc="first",
    )
    pivot_conf_grade = combined.pivot_table(
        index=["Player", "Team", "Position", "Position_Profile"],
        columns="Weighting",
        values="Conference Grade",
        aggfunc="first",
    )
    pivot_pf_grade = combined.pivot_table(
        index=["Player", "Team", "Position", "Position_Profile"],
        columns="Weighting",
        values="Power Five Grade",
        aggfunc="first",
    )

    pivot_score = pivot_score.rename(columns=lambda col: f"Score ({col})")
    pivot_conf_grade = pivot_conf_grade.rename(columns=lambda col: f"Conference Grade ({col})")
    pivot_pf_grade = pivot_pf_grade.rename(columns=lambda col: f"Power Five Grade ({col})")

    wide = pd.concat([pivot_score, pivot_conf_grade, pivot_pf_grade], axis=1).reset_index()

    # Ensure score columns are numeric before diffing
    for col in wide.columns:
        if col.startswith("Score ("):
            wide[col] = pd.to_numeric(wide[col], errors="coerce")

    # Calculate score deltas relative to 80/20
    base_col = "Score (80% Attempts / 20% Accuracy)"
    for suffix, label in WEIGHTING_MAP.items():
        score_col = f"Score ({label})"
        if score_col == base_col or score_col not in wide.columns:
            continue
        wide[f"Δ Score ({label} - 80/20)"] = wide[score_col] - wide[base_col]

    wide = wide.sort_values(["Position_Profile", base_col], ascending=[True, False])
    return wide


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize average score changes by position profile."""
    base_col = "Score (80% Attempts / 20% Accuracy)"
    summary_rows = []
    for profile, group in df.groupby("Position_Profile"):
        row = {"Position_Profile": profile, "Players": len(group)}
        for suffix, label in WEIGHTING_MAP.items():
            score_col = f"Score ({label})"
            if score_col in group.columns:
                row[f"Avg Score ({label})"] = group[score_col].mean()
        for suffix, label in WEIGHTING_MAP.items():
            delta_col = f"Δ Score ({label} - 80/20)"
            if delta_col in group.columns:
                row[f"Avg {delta_col}"] = group[delta_col].mean()
        summary_rows.append(row)

    summary = pd.DataFrame(summary_rows)
    if base_col in df.columns:
        overall = {"Position_Profile": "All", "Players": len(df)}
        for suffix, label in WEIGHTING_MAP.items():
            score_col = f"Score ({label})"
            if score_col in df.columns:
                overall[f"Avg Score ({label})"] = df[score_col].mean()
        for suffix, label in WEIGHTING_MAP.items():
            delta_col = f"Δ Score ({label} - 80/20)"
            if delta_col in df.columns:
                overall[f"Avg {delta_col}"] = df[delta_col].mean()
        summary = pd.concat([summary, pd.DataFrame([overall])], ignore_index=True)

    return summary


def main():
    comparison_df = build_comparison()
    summary_df = build_summary(comparison_df)

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        comparison_df.to_excel(writer, sheet_name="Player Comparison", index=False)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    print(f"✅ Comparison workbook saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()


