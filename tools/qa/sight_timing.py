"""Diagnostic host wall times. Nested browser times are not additive or FPS."""
from contextlib import contextmanager
from copy import deepcopy
import json
from time import perf_counter_ns


class SightTiming:
    """Time synchronous calls once, preserving their values and exceptions."""
    def __init__(self, clock=perf_counter_ns, emit=None):
        self._clock = clock
        self._emit = emit or (lambda text: print(text, flush=True))
        self._start = clock()
        self._sections = []
        self._active = None
        self._environment = {}

    def describe(self, **values):
        self._environment.update(deepcopy(values))

    @contextmanager
    def section(self, name):
        if self._active is not None:
            raise ValueError('Timing sections must not overlap.')
        row = {'name': name, 'status': 'running', 'operations': {}}
        self._sections.append(row)
        self._active = row
        start = self._clock()
        self._emit('SIGHT_TIMING ' + json.dumps({'event': 'start', 'name': name}))
        try:
            yield
            row['status'] = 'completed'
        except BaseException:
            row['status'] = 'failed'
            raise
        finally:
            row['durationSeconds'] = (self._clock() - start) / 1e9
            self._active = None
            self._emit('SIGHT_TIMING ' + json.dumps(row, ensure_ascii=False))

    def call(self, operation, callback, *args, **kwargs):
        if self._active is None:
            raise ValueError('Timing calls require an active section.')
        entry = self._active['operations'].setdefault(
            operation, dict(calls=0, failures=0, seconds=0, maximumSeconds=0))
        start = self._clock()
        entry['calls'] += 1
        try:
            return callback(*args, **kwargs)
        except BaseException:
            entry['failures'] += 1
            raise
        finally:
            elapsed = (self._clock() - start) / 1e9
            entry['seconds'] += elapsed
            entry['maximumSeconds'] = max(entry['maximumSeconds'], elapsed)

    def browser(self, data):
        if self._active is None:
            raise ValueError('Browser measurements require an active section.')
        self._active['browser'] = deepcopy(data)

    def snapshot(self):
        return {'schema': 1, 'diagnosticOnly': True, 'physicalGpu': False,
                'clock': 'perf_counter_ns', 'environment': deepcopy(self._environment),
                'elapsedSeconds': (self._clock() - self._start) / 1e9,
                'note': 'Host wall time includes browser work. Browser milliseconds '
                        'are nested, not additive; render includes gl.finish, not a GPU timer.',
                'sections': deepcopy(self._sections)}
