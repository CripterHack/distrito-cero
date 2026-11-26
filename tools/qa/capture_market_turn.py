"""Capture paired natural arrivals and measure the rendered soles on a seeded Mercado street."""
import argparse
import base64
from hashlib import sha256
import json
from itertools import groupby
from math import cos, hypot, isfinite
from pathlib import Path

from playwright.sync_api import sync_playwright
from capture_market_pedestrian import SETUP, load_page, launch_options

STAGE = Path(__file__).with_name('market_turn_stage.js').read_text()
SIDES = ('L', 'R')


def drift(rows, side):
    points = [r['feet'][side]['center'] for r in rows]
    return max(hypot(a[0] - b[0], a[2] - b[2]) for a in points for b in points)


def grounded_drift(rows):
    result = {}
    for side in SIDES:
        groups = groupby(rows, lambda r: r['feet'][side]['clearance'] <= .01)
        contacts = [list(group) for contact, group in groups if contact]
        result[side] = max((drift(group, side) for group in contacts), default=None)
    return result


def measure(rows, offset):
    total = 1.4
    phases = []
    start = rows[0]['time'] + offset
    for step, swing in enumerate('RLRLR'):
        support = 'R' if swing == 'L' else 'L'
        lo = start + total * step / 5
        hi = start + total * (step + 1) / 5
        phase = [r for r in rows if lo - 1e-8 <= r['time'] <= hi + 1e-8]
        phases.append(dict(swing=swing, support=support, supportDriftM=drift(phase, support),
                           swingClearanceM=max(r['feet'][swing]['clearance'] for r in phase),
                           supportMaxClearanceM=max(r['feet'][support]['clearance'] for r in phase)))
    # Independent of any clip definition. Track continuous physical contact separately per shoe.
    windows = {'arrival':(rows[0]['time'], start), 'turn':(start, start + total),
               'rest':(start + total, rows[-1]['time'])}
    by_window = {name:grounded_drift([r for r in rows if lo - 1e-8 <= r['time'] <= hi + 1e-8])
                 for name, (lo, hi) in windows.items()}
    turn_runs = [list(group) for present, group in groupby(rows, lambda r: r['turn'] is not None) if present]
    active = [r for run in turn_runs for r in run]
    if any(not isfinite(v) for row in rows for foot in row['feet'].values() for v in [*foot['center'], foot['clearance']]):
        raise RuntimeError('Non-finite skinned shoe position')
    return dict(phases=phases, groundedDriftM=grounded_drift(rows), groundedDriftByWindowM=by_window, turnSamples=len(active),
                turnRuns=len(turn_runs), headingReversed=cos(rows[-1]['heading'] - rows[0]['heading']) < -.999,
                progressMonotonic=all(b['turn'] > a['turn'] for a, b in zip(active, active[1:])),
                waitRemainingS=rows[-1]['wait'],
                turnStartS=active[0]['time'] - rows[0]['time'] if active else None,
                turnEndS=active[-1]['time'] - rows[0]['time'] if active else None,
                stopDriftM={s:drift(rows, s) for s in SIDES},
                minClearanceM=min(r['feet'][s]['clearance'] for r in rows for s in SIDES),
                maxClearanceM={s:max(r['feet'][s]['clearance'] for r in rows) for s in SIDES},
                rootDriftM=max(hypot(r['root'][0]-rows[0]['root'][0], r['root'][1]-rows[0]['root'][1]) for r in rows))


def capture(html, output, offset, images, far, snapshot_tick):
    raw = html.read_bytes()
    report = dict(htmlSha256=sha256(raw).hexdigest(), turnOffsetS=offset, endpoints={})
    errors = []
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        page = load_page(browser, raw.decode(), errors)
        page.set_viewport_size({'width':640, 'height':480})
        report['environment'] = page.evaluate(SETUP)
        report['chromium'] = browser.version
        report['landmarks'] = page.evaluate(STAGE, far)
        for label in ('south', 'north'):
            endpoint = page.evaluate('marketTurnQA.arrive()')
            if endpoint['towardEnd'] != (label == 'south'):
                raise RuntimeError('Expected +Z southbound first and −Z northbound on return')
            rows = []
            for tick in range(0, 145, 6):
                draw = images and (snapshot_tick is None or tick == snapshot_tick)
                frame = page.evaluate('a=>marketTurnQA.frame(a)', {'ticks':min(tick, 6), 'draw':draw})
                rows.extend(frame['rows'])
                if draw:
                    (output / f'{label}-{tick:03}.png').write_bytes(base64.b64decode(frame['png']))
            metrics = measure(rows, offset)
            report['endpoints'][label] = dict(**endpoint, **metrics)
            (output / f'{label}.json').write_text(json.dumps(rows, separators=(',', ':')) + '\n')
            print(label, json.dumps(metrics), flush=True)
        page.evaluate('marketTurnQA.finish()')
        if errors:
            raise RuntimeError(errors)
    (output / 'measurements.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, default=Path('index.html'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--turn-offset', type=float, default=.5)
    parser.add_argument('--metrics-only', action='store_true')
    parser.add_argument('--snapshot-tick', type=int, choices=range(0, 145, 6),
                        help='Save just one frame per endpoint while measuring the entire stop')
    parser.add_argument('--far', action='store_true', help='Sample the reduced mesh through the normal distance selection')
    parser.add_argument('--require-turn', action='store_true')
    args = parser.parse_args()
    if not 0 <= args.turn_offset <= 1:
        parser.error('The turn must fit inside the 2.4 s stop')
    args.output.mkdir(parents=True, exist_ok=True)
    report = capture(args.html, args.output, args.turn_offset, not args.metrics_only, args.far, args.snapshot_tick)
    if args.require_turn:
        for label, endpoint in report['endpoints'].items():
            if endpoint['turnRuns'] != 1 or not endpoint['progressMonotonic']:
                raise SystemExit(f'{label}: expected one continuous turn at arrival')
            if (abs(endpoint['turnStartS'] - args.turn_offset) > .017
                    or abs(endpoint['turnEndS'] - args.turn_offset - 1.4) > .017):
                raise SystemExit(f'{label}: incorrect start or duration of the authored turn')
            if (not endpoint['headingReversed'] or endpoint['waitRemainingS'] > .001
                    or endpoint['rootDriftM'] > .001 or endpoint['minClearanceM'] < -.005):
                raise SystemExit(f'{label}: changed endpoint, stop time, heading or shoe contact')
            for index, phase in enumerate(endpoint['phases'], 1):
                if phase['swingClearanceM'] < .025 or phase['supportDriftM'] > .005 or phase['supportMaxClearanceM'] > .005:
                    raise SystemExit(f'{label} step {index} requires ≥25 mm swing clearance and ≤5 mm support drift and clearance')


if __name__ == '__main__':
    main()
