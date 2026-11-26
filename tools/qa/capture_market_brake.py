"""Measure fixed heel and toe vertices during natural Mercado arrivals in the game's renderer."""
import argparse
import base64
import json
from hashlib import sha256
from itertools import groupby
from math import hypot
from pathlib import Path

from playwright.sync_api import sync_playwright

from capture_market_pedestrian import SETUP, load_page, launch_options
from capture_market_turn import SIDES, STAGE, grounded_drift, measure

HZ = 60
START, END = -72, 144
MARKERS = ('heel', 'toe')


def span(points):
    return max((hypot(a[0]-b[0], a[2]-b[2]) for a in points for b in points), default=0.)


def marker_spans(rows, side, name, height=None):
    if height is None:
        return span([r['feet'][side][name] for r in rows])
    groups = groupby(rows, lambda r: r['feet'][side][name][1] <= height)
    return max((span([r['feet'][side][name] for r in group]) for touch, group in groups if touch), default=0.)


def measure_window(rows):
    result = {'solesWithin10mm': grounded_drift(rows), 'markers': {}}
    for side in SIDES:
        samples = [r['feet'][side] for r in rows]
        markers = {name: {'spanM':marker_spans(rows, side, name),
                          'within10mmM':marker_spans(rows, side, name, .010),
                          'minHeightM':min(f[name][1] for f in samples),
                          'maxHeightM':max(f[name][1] for f in samples)} for name in MARKERS}
        # Lowest deformed shoe point, independent from the production route/animation label.
        result['markers'][side] = dict(**markers,
            meanAbsoluteClearanceM=sum(abs(f['clearance']) for f in samples)/len(samples),
            peakClearanceM=max(f['clearance'] for f in samples),
            minClearanceM=min(f['clearance'] for f in samples))
    return result


def arrival_times(page):
    # A deterministic dry run locates both actual arrival ticks. A fresh simulation then
    # follows the same route, sampling every tick before and after those landmarks.
    return page.evaluate("""() => {
      const {sim,ped}=marketQA, result=[];
      for(let i=0;i<3300 && result.length<2;i++){
        const outgoing=ped.sidewalkRoute.towardEnd;
        sim.step(1/60,{});
        if(ped.sidewalkRoute.towardEnd!==outgoing){
          if(Math.abs(ped.sidewalkRoute.wait-2.4)>.001)throw Error('No calm arrival');
          result.push(sim.time);
        }
      }
      if(result.length!==2)throw Error('Missing route end');
      return result;
    }""")


def marker_steps(a, b):
    return {s: {m: hypot(a['feet'][s][m][0]-b['feet'][s][m][0],
                        a['feet'][s][m][2]-b['feet'][s][m][2])
                for m in MARKERS} for s in SIDES}


def brake_event(rows):
    active = [i for i, r in enumerate(rows) if r['brake'] is not None]
    if not active:
        return None
    first, last = active[0], active[-1]
    if active != list(range(first, last+1)):
        raise ValueError('Braking clip stopped or restarted')
    if any(b['brake']<=a['brake'] for a,b in zip(rows[first:last],rows[first+1:last+1])):
        raise ValueError('Braking clip phase did not advance')
    clips = {rows[i]['clip'] for i in active}
    if len(clips)!=1:
        raise ValueError('Braking anchor changed side')
    return {
        'clip':clips.pop(), 'firstTick':rows[first]['tick'], 'lastTick':rows[last]['tick'],
        'startPhase':rows[first]['brake'], 'endPhase':rows[last]['brake'],
        'entryTravelM':marker_steps(rows[first-1], rows[first]),
        'exitTravelM':marker_steps(rows[last], rows[last+1]),
        'rootTravelM':abs(rows[first-1]['root'][1]-rows[last+1]['root'][1]),
        'firstSpeedMps':rows[first]['speed'], 'lastSpeedMps':rows[last]['speed'],
        'maxSpeedIncreaseMps':max(b['speed']-a['speed'] for a,b in zip(rows[first:last],rows[first+1:last+1])),
    }


def capture(html, output, far, media):
    raw=html.read_bytes()
    output.mkdir(parents=True, exist_ok=True)
    report=dict(htmlSha256=sha256(raw).hexdigest(), hz=HZ, startTick=START, endTick=END, endpoints={})
    errors=[]
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        page=load_page(browser, raw.decode(), errors)
        page.set_viewport_size({'width':640, 'height':480})
        page.evaluate(SETUP)
        arrivals=arrival_times(page)
        report['environment']=page.evaluate(SETUP)
        report['chromium']=browser.version
        report['landmarks']=page.evaluate(STAGE, {'far':far, 'braking':True})
        for label,arrival in zip(('south','north'), arrivals):
            endpoint=page.evaluate('args => marketTurnQA.arrive(args)',
                {'begin':arrival+START/HZ,'arrival':arrival})
            if endpoint['towardEnd']!=(label=='south'):
                raise ValueError('Unexpected approach direction')
            rows=[]
            for tick in range(START, END+1, 3):
                draw=media and (tick==6 if far else -36<=tick<=30)
                frame=page.evaluate('a=>marketTurnQA.frame(a)', {'ticks':3 if tick>START else 0, 'draw':draw})
                rows.extend(frame['rows'])
                if draw:(output/f'{label}-{tick:03}.png').write_bytes(base64.b64decode(frame['png']))
            if len(rows)!=END-START+1: raise ValueError('Incomplete trajectory')
            for tick,r in enumerate(rows,START):
                r['tick']=tick
                if abs(r['time']-arrival-tick/HZ)>1e-6: raise ValueError('Arrival tick mismatch')
            arrived=rows[-START]
            if abs(arrived['root'][1]-endpoint['dest'])>.001 or abs(arrived['wait']-2.4)>.001:
                raise ValueError('Arrival differs from independent route clock')
            def window(a,b):return [r for r in rows if a<=r['tick']<=b]
            turn=measure(window(0,144),.5)
            windows={name:measure_window(window(lo,hi)) for name,lo,hi in (
                ('lead',-72,-30),('finalStep',-29,0),('settle',0,30),('entireApproach',-72,0))}
            final=windows['finalStep']['markers']
            support=min(SIDES,key=lambda side:final[side]['meanAbsoluteClearanceM'])
            report['endpoints'][label]=dict(**endpoint,windows=windows,turn=turn,
                observedFinalSupport=support, brake=brake_event(rows), samples=len(rows))
            (output/f'{label}.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
            print(label,'support',support,'settle center',windows['settle']['solesWithin10mm'],
                  'final markers',json.dumps(final),flush=True)
        page.evaluate('marketTurnQA.finish()')
        if errors: raise RuntimeError(errors)
    (output/'measurements.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report


def require_braking(report, reference=None):
    if reference and (reference['landmarks']!=report['landmarks']
                      or reference['environment']['actor']!=report['environment']['actor']
                      or reference['environment']['seed']!=report['environment']['seed']):
        raise ValueError('Reference uses different tread points, actor or seed')
    for end,ep in report['endpoints'].items():
        windows=ep['windows']
        settle=windows['settle']
        for side in SIDES:
            if settle['markers'][side]['peakClearanceM']>.005:
                raise ValueError(f'{end}/{side} is not resting on the street before the turn')
            for marker in MARKERS:
                if settle['markers'][side][marker]['within10mmM']>.005:
                    raise ValueError(f'{end}/{side}/{marker} slides over 5 mm after arrival')
        support=ep['observedFinalSupport']
        planted=windows['finalStep']['markers'][support]
        if max(planted[m]['spanM'] for m in MARKERS)>.005 or planted['peakClearanceM']>.005:
            raise ValueError(f'{end}/{support} loses its planted support before arrival')
        event=ep['brake']
        if not event or event['clip']!='Frenada'+support:
            raise ValueError(f'{end} disagrees with the observed weight-bearing foot')
        if event['firstTick'] not in (-30,-29) or event['lastTick']!=-1:
            raise ValueError(f'{end} braking is out of phase with its arrival')
        if not .145<event['rootTravelM']<.19 or event['lastSpeedMps']>.02 or event['maxSpeedIncreaseMps']>.001:
            raise ValueError(f'{end} does not decelerate continuously through the final step')
        if max(event['entryTravelM'][support].values())>.005:
            raise ValueError(f'{end} jumps the planted heel/toe when entering the stop')
        if max(d for foot in event['exitTravelM'].values() for d in foot.values())>.005:
            raise ValueError(f'{end} jumps either shoe when entering rest')
        if reference:
            earlier=reference['endpoints'][end]
            if any(ep[k]!=earlier[k] for k in ('eye','target','batch','fov','quality','dest','towardEnd')):
                raise ValueError('Camera, direction or distance selection differs from reference')
            for name in ('lead','entireApproach'):
                def worst(w):
                    return max(foot[m]['within10mmM'] for foot in w['markers'].values() for m in MARKERS)
                if worst(windows[name])>worst(earlier['windows'][name])+.005:
                    raise ValueError(f'{end} moves the contact drift into the approach: {name}')
        turn=ep['turn']
        if turn['turnRuns']!=1 or not turn['progressMonotonic'] or not turn['headingReversed']:
            raise ValueError(f'{end} no longer completes one half-turn')
        if (turn['rootDriftM']>.001 or turn['minClearanceM']<-.005
                or abs(turn['turnStartS']-.5)>.017 or abs(turn['turnEndS']-1.9)>.017
                or any(p['supportDriftM']>.005 or p['supportMaxClearanceM']>.005 or p['swingClearanceM']<.025
                       for p in turn['phases'])):
            raise ValueError(f'{end} no longer preserves the turning feet')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--html',type=Path,default=Path('index.html'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--far',action='store_true')
    p.add_argument('--metrics-only',action='store_true')
    p.add_argument('--require-braking',action='store_true')
    p.add_argument('--reference',type=Path,help='Preceding release measurements.json at the same distance')
    args=p.parse_args()
    result=capture(args.html,args.output,args.far,not args.metrics_only)
    if args.require_braking:
        require_braking(result, json.loads(args.reference.read_text()) if args.reference else None)
