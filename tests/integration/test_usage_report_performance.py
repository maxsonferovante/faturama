from __future__ import annotations

import time

from faturama.application.use_cases.generate_usage_report import generate_usage_report


def test_usage_report_completes_under_ten_seconds(usage_report_repo):
    start = time.perf_counter()
    generate_usage_report(repository_root=str(usage_report_repo))
    elapsed = time.perf_counter() - start

    assert elapsed < 10
