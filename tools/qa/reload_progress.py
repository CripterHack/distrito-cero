"""Retain partial native reload observations without creating a passing report."""
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
from .run import write_json


def write_progress(path: Path, payload: Mapping[str, Any]) -> None:
    """The runner never reads this journal as its canonical reload.json result."""
    path = Path(path)
    if not path.name.endswith('.progress.json'):
        raise ValueError('Partial observations require a separate .progress.json journal')
    report = deepcopy(dict(payload))
    report['status'] = 'in_progress'
    report['completedChecks'] = len(report.get('checks', []))
    report.pop('finishedUtc', None)
    write_json(path, report)
