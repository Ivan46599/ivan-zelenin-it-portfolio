from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import requests


def load_json(source: str) -> list[dict[str, Any]]:
    if source.startswith(('http://', 'https://')):
        response = requests.get(source, timeout=15)
        response.raise_for_status()
        data = response.json()
    else:
        data = json.loads(Path(source).read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError('Expected a list of objects')
    return data


def normalize_jobs(raw_jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    jobs = []
    for item in raw_jobs:
        skills = item.get('skills', [])
        if isinstance(skills, list):
            skills_text = ', '.join(map(str, skills))
        else:
            skills_text = str(skills)
        jobs.append({
            'company': item.get('company', ''),
            'title': item.get('title', ''),
            'salary_from': int(item.get('salary_from') or 0),
            'remote': bool(item.get('remote')),
            'skills': skills_text,
        })
    return jobs


def filter_jobs(jobs: list[dict[str, Any]], min_salary: int = 0, remote_only: bool = False) -> list[dict[str, Any]]:
    result = []
    for job in jobs:
        if job['salary_from'] < min_salary:
            continue
        if remote_only and not job['remote']:
            continue
        result.append(job)
    return result


def save_csv(jobs: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company', 'title', 'salary_from', 'remote', 'skills'])
        writer.writeheader()
        writer.writerows(jobs)


def main() -> None:
    parser = argparse.ArgumentParser(description='Load JSON job data and export filtered CSV')
    parser.add_argument('--source', default='data/sample_jobs.json', help='Path or URL with JSON list')
    parser.add_argument('--output', type=Path, default=Path('outputs/jobs.csv'))
    parser.add_argument('--min-salary', type=int, default=0)
    parser.add_argument('--remote-only', action='store_true')
    args = parser.parse_args()

    raw = load_json(args.source)
    jobs = normalize_jobs(raw)
    jobs = filter_jobs(jobs, min_salary=args.min_salary, remote_only=args.remote_only)
    save_csv(jobs, args.output)
    print(f'Saved {len(jobs)} jobs to {args.output}')


if __name__ == '__main__':
    main()
