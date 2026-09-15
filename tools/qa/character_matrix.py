"""Versioned visual coverage. Numerical success must never imply artistic acceptance."""
import copy
import html
import itertools
import json
import math
import re
from pathlib import Path

AXES={'profile':{'neutral','light','robust','extreme'},'camera':{'front','profile','three-quarter','back'},'light':{'neutral','side','night'},'pose':{'idle','walk','run','brake','turn','crouch','air','seated','aim','reload','entry','neck'}}
SHAPES={'build','face','neck','neckLength','hairVolume'}
ACTOR={'moveSpeed','walk','sprintBlend','crouch','y','vy','turnRate','lookYaw','lookPitch','lookRoll'}
def numeric(value,low,high):
    return type(value) in (int,float) and math.isfinite(value) and low<=value<=high

def validate_matrix(m):
    if not isinstance(m,dict) or m.get('version')!=1 or m.get('id')!='dc-character-benchmark-v1':
        raise ValueError('Unknown character benchmark contract.')
    if not numeric(m.get('seed'),0,2**31-1) or not numeric(m.get('time'),0,100):
        raise ValueError('Invalid deterministic scene inputs.')
    for axis,ids in AXES.items():
        if not isinstance(m.get(axis+'s'),dict) or set(m[axis+'s'])!=ids:
            raise ValueError('Unknown or missing '+axis)
    for p in m['profiles'].values():
        if set(p)!=SHAPES or not all(numeric(v,-1,1) for v in p.values()):
            raise ValueError('Invalid or misspelled appearance field.')
    if not all(numeric(v,-math.pi,math.pi) for v in m['cameras'].values()):
        raise ValueError('Invalid camera yaw.')
    if not all(numeric(v,0,1) for v in m['lights'].values()):
        raise ValueError('Invalid daylight.')
    for p in m['poses'].values():
        if set(p)-{'label','scene','actor','weapon','aim','reload','acceleration'} or p.get('scene') not in ('studio','game'):
            raise ValueError('Invalid pose or scene.')
        if not isinstance(p.get('label'),str) or not p['label'] or len(p['label'])>100:
            raise ValueError('Invalid pose label.')
        if not isinstance(p.get('actor'),dict) or set(p['actor'])-ACTOR or not all(numeric(v,-10,10) for v in p['actor'].values()):
            raise ValueError('Invalid actor field.')
        if p.get('weapon','rifle')!='rifle' or not numeric(p.get('aim',0),0,1) or not numeric(p.get('reload',0),0,1) or not numeric(p.get('acceleration',0),-7,7):
            raise ValueError('Invalid equipment or acceleration fixture.')
    if m.get('hairStyles')!=list(range(11)):
        raise ValueError('All eleven stable styles are required.')
    return m

def load_matrix(path):
    return validate_matrix(json.loads(Path(path).read_text(encoding='utf-8')))

def make_cases(matrix,mode='smoke'):
    m=validate_matrix(matrix)
    if mode not in ('smoke','full'):raise ValueError('Choose smoke or full.')
    keys=list(itertools.product(m['profiles'],m['poses'],m['lights'],m['cameras'])) if mode=='full' else (
        [('neutral',p,'neutral','front') for p in m['poses']]+
        [('neutral','idle','neutral',c) for c in m['cameras'] if c!='front']+
        [('neutral','idle',l,'front') for l in m['lights'] if l!='neutral']+
        [(p,'idle','neutral','front') for p in m['profiles'] if p!='neutral'])
    out=[]
    for profile,pose,light,camera in keys:
        out.append({'id':'--'.join((profile,pose,light,camera)),'profile':profile,'pose':pose,'light':light,'camera':camera,
            'look':{**copy.deepcopy(m['profiles'][profile]),'hairStyle':0},'yaw':m['cameras'][camera],
            'daylight':m['lights'][light],'sample':copy.deepcopy(m['poses'][pose]),'seed':m['seed'],'time':m['time']})
    reference=next(c for c in out if c['profile']=='neutral' and c['pose']=='idle' and c['light']=='neutral' and c['camera']=='three-quarter')
    for style in range(1,11):
        c=copy.deepcopy(reference);c['id']='hair-'+str(style).zfill(2);c['look']['hairStyle']=style;out.append(c)
    return out

def accept_review(review,sha):
    if (not isinstance(review,dict) or review.get('status')!='accepted' or review.get('htmlSha256')!=sha or
        any(not isinstance(review.get(k),str) or not review[k].strip() for k in ('reviewer','evidence','decision'))):
        raise ValueError('Acceptance requires reviewer, decision and evidence for this exact HTML.')
    return True

def render_gallery(manifest,cases):
    esc=lambda s:html.escape(str(s),quote=True)
    cards=[]
    for c in cases:
        image=c['image']
        if not re.fullmatch(r'images/[A-Za-z0-9_-]+\.png',image):raise ValueError('Unsafe evidence path.')
        cards.append('<article><h2>'+esc(c['id'])+'</h2><img loading="lazy" src="'+esc(image)+'" alt="'+esc(c.get('label',c['pose']))+'">'+
            '<p>'+esc(' · '.join(c[k] for k in ('profile','pose','light','camera')))+'</p><details><summary>Mediciones y configuración</summary><pre>'+esc(json.dumps(c.get('metrics',{}),ensure_ascii=False,indent=2))+'</pre></details></article>')
    return '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Distrito Cero · Benchmark de personajes</title><style>body{font:16px system-ui;background:#101b22;color:#edf2f0;margin:0;padding:24px}h1{font-size:28px}header{max-width:1100px;margin:auto}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:24px}article{border:1px solid #42505c;border-radius:8px;overflow:hidden;padding:14px;background:#16232c}h2{font-size:15px;overflow-wrap:anywhere}img{width:100%;height:auto}p{line-height:1.5}pre{white-space:pre-wrap;font-size:12px;overflow-wrap:anywhere}summary{cursor:pointer;min-height:44px}code{overflow-wrap:anywhere}</style><header><h1>Distrito Cero · Referencia reproducible</h1><p><strong>Revisión artística pendiente.</strong> Las capturas son del renderer del juego. Los checks numéricos no certifican hiperrealismo.</p><p>Matriz: '+esc(manifest['matrix'])+' · HTML: <code>'+esc(manifest['htmlSha256'])+'</code></p><p>Tiempo y estados preparados. No es un benchmark de FPS, un recorrido completo ni una prueba de guardado nativo. Comparar siempre la misma ficha antes/después.</p></header><main>'+''.join(cards)+'</main></html>'
