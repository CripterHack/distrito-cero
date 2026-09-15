#!/usr/bin/env python3
"""Package audited v0.16 source and standalone delivery files (no network action)."""
from pathlib import Path
import argparse, hashlib, json, shutil, zipfile
R=Path(__file__).resolve().parents[1]
O=R/'qa/v016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('/mnt/data'))
    out=parser.parse_args().out;out.mkdir(parents=True,exist_ok=True)
    report=json.loads((O/'release-report.json').read_text())
    assert sha(R/'index.html')==report['html']['sha256']
    assert sha(R/'assets/dc016-human-traits.glb')==report['glb']['sha256']
    for p,h in report['sourceHashes'].items():assert sha(R/p)==h,p
    assert all(x['exit_code']==0 for x in json.loads((O/'browser-execution.json').read_text()))
    selected=[]
    for p in sorted(R.rglob('*')):
        rel=p.relative_to(R)
        if not p.is_file() or any(s in {'.git','__pycache__','.pytest_cache','clip-frames','initial'} for s in rel.parts):continue
        if rel.parts[0]=='qa' and (len(rel.parts)<2 or rel.parts[1]!='v016'):continue
        if p.name in {'SOURCE-MANIFEST.json','.DS_Store'} or p.suffix in {'.pyc','.pyo','.pid'}:continue
        if p.suffix.lower() in {'.ttf','.otf','.woff','.woff2'}:raise ValueError('Font files must not be distributed')
        selected.append(p)
    manifest={'version':'0.16','htmlSha256':report['html']['sha256'],'files':{str(p.relative_to(R)):sha(p) for p in selected}}
    (R/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    archive=out/'distrito-cero-v0.16-codigo.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in [*selected,R/'SOURCE-MANIFEST.json']:
            info=zipfile.ZipInfo('distrito-cero/'+str(p.relative_to(R)),date_time=(2026,9,15,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for n,h in manifest['files'].items():assert hashlib.sha256(z.read('distrito-cero/'+n)).hexdigest()==h,n
        assert z.read('distrito-cero/index.html')==(R/'index.html').read_bytes()
    publish={
        'index.html':'distrito-cero-v0.16-rasgos.html',
        'assets/dc016-human-traits.glb':'distrito-cero-v0.16-personaje.glb',
        'docs/v016/VERIFICACION.md':'distrito-cero-v0.16-verificacion.md',
        'docs/v016/GUIA.md':'distrito-cero-v0.16-guia.md',
        'qa/v016/comparacion-rasgos.jpg':'distrito-cero-v0.16-comparacion.jpg',
        'qa/v016/review-neck.png':'distrito-cero-v0.16-cuello.png',
        'qa/v016/galeria-peinados.jpg':'distrito-cero-v0.16-peinados.jpg',
        'qa/v016/editor-rasgos.png':'distrito-cero-v0.16-editor.png',
        'qa/v016/review-cast.png':'distrito-cero-v0.16-reparto.png',
        'qa/v016/movilidad-rasgos.mp4':'distrito-cero-v0.16-movilidad.mp4'}
    for p,n in publish.items():shutil.copyfile(R/p,out/n)
    result={'version':'0.16','source_files_verified':len(manifest['files']),'zip_integrity':'passed','artifacts':{n:{'bytes':(out/n).stat().st_size,'sha256':sha(out/n)} for n in [archive.name,*publish.values()]}}
    (out/'distrito-cero-v0.16-entrega.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
