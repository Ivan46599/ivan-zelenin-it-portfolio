from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from parse_jobs import filter_jobs, normalize_jobs


def test_filter_remote_jobs():
    jobs = normalize_jobs([
        {'company': 'A', 'title': 'Python Intern', 'salary_from': 50000, 'remote': True, 'skills': ['Python']},
        {'company': 'B', 'title': 'QA', 'salary_from': 30000, 'remote': False, 'skills': ['Testing']},
    ])
    result = filter_jobs(jobs, min_salary=40000, remote_only=True)
    assert len(result) == 1
    assert result[0]['company'] == 'A'
