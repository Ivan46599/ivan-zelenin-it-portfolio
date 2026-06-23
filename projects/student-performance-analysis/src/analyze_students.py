from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SUBJECTS = ['math', 'programming', 'physics', 'english']


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {'student_id', 'group', 'attendance_percent', 'homework_done', *SUBJECTS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    return df


def build_report(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result['average_score'] = result[SUBJECTS].mean(axis=1).round(2)
    result['risk_group'] = (result['average_score'] < 65) | (result['attendance_percent'] < 75)
    return result


def group_summary(report: pd.DataFrame) -> pd.DataFrame:
    return (
        report.groupby('group')
        .agg(
            students=('student_id', 'count'),
            avg_score=('average_score', 'mean'),
            avg_attendance=('attendance_percent', 'mean'),
            risk_students=('risk_group', 'sum'),
        )
        .round(2)
        .reset_index()
    )


def save_charts(report: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    ax = report.sort_values('average_score').plot(
        x='student_id', y='average_score', kind='bar', legend=False, figsize=(10, 5)
    )
    ax.set_title('Average score by student')
    ax.set_xlabel('Student ID')
    ax.set_ylabel('Average score')
    plt.tight_layout()
    plt.savefig(output_dir / 'average_score_by_student.png')
    plt.close()

    ax = report[SUBJECTS].mean().sort_values().plot(kind='bar', figsize=(8, 5))
    ax.set_title('Average score by subject')
    ax.set_xlabel('Subject')
    ax.set_ylabel('Average score')
    plt.tight_layout()
    plt.savefig(output_dir / 'average_score_by_subject.png')
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze student performance CSV')
    parser.add_argument('--input', type=Path, default=Path('data/student_results.csv'))
    parser.add_argument('--output-dir', type=Path, default=Path('outputs'))
    args = parser.parse_args()

    df = load_data(args.input)
    report = build_report(df)
    summary = group_summary(report)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output_dir / 'student_report.csv', index=False)
    summary.to_csv(args.output_dir / 'group_summary.csv', index=False)
    save_charts(report, args.output_dir)
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
