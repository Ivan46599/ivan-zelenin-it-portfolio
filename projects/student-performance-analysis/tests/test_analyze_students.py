from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from analyze_students import build_report, group_summary, load_data


def test_build_report_adds_average_and_risk_columns():
    df = pd.DataFrame(
        [
            {
                "student_id": 1,
                "group": "A",
                "attendance_percent": 90,
                "homework_done": 10,
                "math": 80,
                "programming": 90,
                "physics": 70,
                "english": 60,
            }
        ]
    )

    report = build_report(df)

    assert report.loc[0, "average_score"] == 75.0
    assert bool(report.loc[0, "risk_group"]) is False


def test_build_report_marks_low_score_as_risk():
    df = pd.DataFrame(
        [
            {
                "student_id": 1,
                "group": "A",
                "attendance_percent": 90,
                "homework_done": 10,
                "math": 50,
                "programming": 50,
                "physics": 50,
                "english": 50,
            }
        ]
    )

    report = build_report(df)

    assert bool(report.loc[0, "risk_group"]) is True


def test_group_summary_counts_students_and_risk():
    report = pd.DataFrame(
        [
            {
                "student_id": 1,
                "group": "A",
                "average_score": 80.0,
                "attendance_percent": 90,
                "risk_group": False,
            },
            {
                "student_id": 2,
                "group": "A",
                "average_score": 60.0,
                "attendance_percent": 70,
                "risk_group": True,
            },
        ]
    )

    summary = group_summary(report)

    assert summary.loc[0, "students"] == 2
    assert summary.loc[0, "avg_score"] == 70.0
    assert summary.loc[0, "risk_students"] == 1


def test_load_data_rejects_missing_columns(tmp_path):
    csv_path = tmp_path / "invalid.csv"

    pd.DataFrame(
        [
            {
                "student_id": 1,
                "group": "A",
            }
        ]
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing columns"):
        load_data(csv_path)