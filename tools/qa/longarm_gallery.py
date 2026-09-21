"""Local inspectable evidence. Passing the harness does not approve CONTACT-03."""
import html
import json
import re


def render_gallery(report):
    esc=lambda value:html.escape(str(value),quote=True)
    cards=[]
    for case in report.get('cases',[]):
        image=case['image']
        if not re.fullmatch(r'images/[A-Za-z0-9_-]+\.png',image):
            raise ValueError('Unsafe evidence image path')
        m=case['measurement'];screen=case['screening']
        stock=''
        if case.get('stockClearance'):
            values=case['stockClearance']['minimum']
            stock=('<p><strong>'+esc(case.get('stockScreen',{}).get('status','sin evaluación'))+'</strong> · '
                   'Cara/cuello: '+esc(f"{values['face']['distance']*1000:.2f} mm")+
                   ' · Chaqueta: '+esc(f"{values['jacket']['distance']*1000:.2f} mm")+
                   '. Un valor negativo indica penetración. Este muestreo no acredita contacto ni anatomía.</p>')
        cards.append('<article><h2>'+esc(case['name'])+'</h2><img loading="lazy" src="'+esc(image)+'" alt="'+esc(case['name'])+'">'
                     '<p><strong>'+esc(screen['status'])+'</strong> · Ojo/eje: '+esc(f"{m['eyeError']*1000:.2f} mm")+
                     ' · Culata/referencia: '+esc(f"{m['stockError']*1000:.2f} mm")+'</p>'+stock+
                     '<details><summary>Parámetros y mediciones completas</summary><pre>'+esc(json.dumps(case,ensure_ascii=False,indent=2))+'</pre></details></article>')
    return ('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<title>Distrito Cero · Auditoría CONTACT-03</title><style>'
            'body{font:16px system-ui;margin:24px;background:#101b22;color:#edf2f0}header{max-width:1000px}p{line-height:1.5}'
            'main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:20px}'
            'article{border:1px solid #52606a;padding:14px;border-radius:8px}img{width:100%;height:auto}'
            'h2{font-size:18px;overflow-wrap:anywhere}pre,code{white-space:pre-wrap;overflow-wrap:anywhere}'
            'summary{cursor:pointer;min-height:44px}pre{font-size:12px}</style><header>'
            '<h1>Ojo, culata y alcance</h1><p><strong>CONTACT-03 pendiente de revisión cooperativa y artística.</strong> '
            'El éxito del auditor sólo confirma la integridad de las mediciones, no una corrección del juego.</p>'
            '<p>HTML: <code>'+esc(report['sha256'])+'</code></p><p>Metros en el JSON, milímetros en las fichas. '
            'Hombro: referencia articulada heredada, no colisión con la superficie completa. '
            'Escena, cámara y tiempo preparados. Storage fixture, no persistencia HTTP ni FPS de hardware. '
            'Los ciclos muestran muestras de movimiento, no todos sus fotogramas.</p></header><main>'+''.join(cards)+'</main></html>')
