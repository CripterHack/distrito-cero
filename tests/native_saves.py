"""Native HTTP + persistent Chromium profile, real DOM, two real pages.
The renderer is parked after boot to isolate storage from software-GPU cost.
World values are prepared explicitly. Storage is never replaced or intercepted.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from datetime import datetime, timezone
import hashlib,json,os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
from native_support import game_origin

R=Path(__file__).resolve().parents[1];O=R/'qa/v019';O.mkdir(parents=True,exist_ok=True)
checks=[];errors=[];requests=[];boots=[];context=None
SETTINGS="""if(!localStorage.getItem('distrito-cero:settings:v1')) localStorage.setItem('distrito-cero:settings:v1', JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false}));"""
NATIVE="Object.getPrototypeOf(localStorage)===Storage.prototype&&String(Storage.prototype.setItem).includes('[native code]')"

def ck(name,value):
    checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True)
    assert value,name

def boot(context,origin):
    p=context.new_page();p.set_default_timeout(30000)
    p.on('pageerror',lambda e:errors.append(str(e)))
    p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) and urlsplit(r.url).netloc!=urlsplit(origin).netloc else None)
    response=p.goto(origin,wait_until='load',timeout=90000)
    assert response.status==200
    p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
    # Preserve native storage and the production UI/save path. No GPU benchmark here.
    p.evaluate('window.drawNativeFrame=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.setMode("menu")')
    boots.append({'url':p.url,'nativeStorage':p.evaluate(NATIVE),'browser':p.evaluate('navigator.userAgent')})
    assert boots[-1]['nativeStorage']
    return p

def card(id):return '[data-slot="'+id+'"]'
def pause(p):
    if p.locator('#tutorial').is_visible():p.click('#dismissTutorial')
    p.evaluate('DC_APP.setMode("pause")')
def create(p,name,slot,style,cash,story,weapon,reserve):
    p.fill('#characterName',name);p.fill('#newSaveName',slot)
    p.select_option('#characterHairStyle',str(style));p.click('#commitCreator')
    p.wait_for_function('DC_APP.mode==="play"');pause(p)
    p.evaluate('''([cash,story,weapon,reserve])=>{const s=DC_APP.sim;s.cash=cash;s.story=story;s.equipWeapon(weapon);s.equipment.ammo[weapon].reserve=reserve;}''',[cash,story,weapon,reserve])
    assert p.evaluate('DC_APP.save(true)')
    return p.evaluate('DC_APP.activeSlot.id')

def sample(p,id):return p.evaluate('id=>DC_APP.getStore().get(id)',id)
def import_json(p,obj):
    p.locator('#saveFile').set_input_files({'name':'qa-import.json','mimeType':'application/json','buffer':json.dumps(obj).encode()})
    p.wait_for_function('document.getElementById("saveFile").value===""')

try:
    assert os.environ.get('DC_QA_ORIGIN')=='http','Run through the harness with --origin http.'
    with game_origin(R) as origin, TemporaryDirectory(prefix='dc-native-profile-') as profile, sync_playwright() as pw:
        def reopen():
            c=pw.chromium.launch_persistent_context(profile,viewport={'width':900,'height':640},accept_downloads=True,**launch_options())
            c.add_init_script(SETTINGS)
            for page in list(c.pages):page.close()
            return c
        context=reopen();p=boot(context,origin)
        ck('Browser uses native Web Storage at a real HTTP origin',p.evaluate(NATIVE) and p.url.startswith(origin))
        ck('Isolated test profile starts without personal saves',p.evaluate('DC_APP.getStore().list().length===0'))
        p.click('#start');a=create(p,'Noa','Ruta nativa A',4,1299,2,'gauss',11)
        ck('Creator stores named identity and hairstyle A',sample(p,a)['data']['identity']['name']=='Noa' and sample(p,a)['data']['identity']['look']['hairStyle']==4)
        p.click('#pauseSaves');p.click('#libraryNew');b=create(p,'Luz','Ruta nativa B',8,2345,3,'emp',5)
        ck('Second character has a separate stable save ID',a!=b and p.evaluate('DC_APP.getStore().list().length===2'))
        ck('A retains its mission and inventory after creating B',sample(p,a)['data']['cash']==1299 and sample(p,a)['data']['equipment']['ammo']['gauss']['reserve']==11)
        ck('B retains its own equipment and hairstyle',sample(p,b)['data']['equipment']['selected']=='emp' and sample(p,b)['data']['identity']['look']['hairStyle']==8)
        saved={id:sample(p,id) for id in (a,b)}
        raw=p.evaluate('DC_APP.getStore().raw()')
        context.close();context=reopen();p=boot(context,origin)
        ck('A new browser context still uses native storage',p.evaluate(NATIVE))
        ck('Catalogue bytes survive closing and reopening Chromium',p.evaluate('DC_APP.getStore().raw()')==raw)
        ck('Both saved snapshots and IDs survive browser restart',all(sample(p,id)==saved[id] for id in (a,b)))
        p.click('#landingSaves');p.click(card(a)+' .slot-load');pause(p)
        ck('Loading A restores its character, mission and cash',p.evaluate('DC_APP.sim.characterName==="Noa"&&DC_APP.sim.story===2&&DC_APP.sim.cash===1299'))
        ck('Loading A restores selected weapon and cell reserve',p.evaluate('DC_APP.sim.equipment.selected==="gauss"&&DC_APP.sim.equipment.ammo.gauss.reserve===11'))
        p.click('#pauseSaves');p.locator(card(a)+' .slot-name').fill('Ruta nativa · renombrada');p.click(card(a)+' .slot-name-row button')
        ck('Rename changes metadata without replacing identity',sample(p,a)['name']=='Ruta nativa · renombrada' and sample(p,a)['data']['identity']['name']=='Noa')
        before_b=sample(p,b)
        with p.expect_download() as dl:p.click(card(a)+' .slot-export')
        exported=json.loads(Path(dl.value.path()).read_text())
        ck('Individual export is a real browser download',exported['format']=='distrito-cero-slot' and exported['data']['cash']==1299)
        with p.expect_download() as dl:p.click('#libraryExportAll')
        bundle=json.loads(Path(dl.value.path()).read_text())
        ck('Collection download includes both native slots',bundle['format']=='distrito-cero-collection' and len(bundle['slots'])==2)
        old=p.evaluate('DC_APP.getStore().raw()');import_json(p,{'version':999})
        ck('Invalid import leaves native catalogue bytes unchanged',p.evaluate('DC_APP.getStore().raw()')==old)
        import_json(p,exported)
        copies=p.evaluate('DC_APP.getStore().list()');copy_id=next(s['id'] for s in copies if s['id'] not in (a,b))
        ck('Import with same name adds a new ID without overwriting',len(copies)==3 and sample(p,copy_id)['name']==sample(p,a)['name'])
        p.once('dialog',lambda d:d.dismiss());p.click(card(copy_id)+' .slot-delete')
        ck('Deletion cancellation preserves native imported slot',sample(p,copy_id) is not None)
        p.once('dialog',lambda d:d.accept());p.click(card(copy_id)+' .slot-delete')
        ck('Confirmed deletion removes only the imported copy',sample(p,copy_id) is None and sample(p,b)==before_b)
        context.close();context=reopen();p=boot(context,origin)
        ck('Deleted copy does not reappear after another restart',sample(p,copy_id) is None and p.evaluate('DC_APP.getStore().list().length===2'))
        ck('Renamed title survives restart and preserves its ID',sample(p,a)['name']=='Ruta nativa · renombrada')
        p.click('#landingSaves');p.click(card(a)+' .slot-load');pause(p)
        q=boot(context,origin);q.click('#landingSaves');q.click(card(a)+' .slot-load');pause(q)
        ck('Two real tabs hold the same slot revision',p.evaluate('DC_APP.activeSlot.revision')==q.evaluate('DC_APP.activeSlot.revision'))
        p.evaluate('DC_APP.sim.cash=3101');ck('First tab can save a new native revision',p.evaluate('DC_APP.save(true)'))
        q.wait_for_function('DC_APP.getStore().get(DC_APP.activeSlot.id).data.cash===3101')
        ck('Second tab observes the native write from the first',sample(q,a)['data']['cash']==3101)
        q.evaluate('DC_APP.sim.cash=4102');newraw=q.evaluate('DC_APP.getStore().raw()')
        ck('Stale tab write is rejected instead of replacing newer data',q.evaluate('DC_APP.save(true)===false'))
        ck('Rejected write preserves newer bytes and unsaved local progress',q.evaluate('DC_APP.getStore().raw()')==newraw and q.evaluate('DC_APP.sim.cash===4102'))
        ck('Conflict is communicated to the player',q.evaluate('DC_APP.saveNotice.includes("conflicto")'))
        q.click('#pauseSaves');q.fill('#copySaveName','Rama recuperada');q.click('#librarySaveCopy');branch=q.evaluate('DC_APP.activeSlot.id')
        ck('Unsaved conflicting state can be saved to its own ID',branch!=a and sample(q,branch)['data']['cash']==4102)
        ck('Creating a conflict copy preserves newer original state',sample(q,a)['data']['cash']==3101)
        # One more conflict exercises the existing Recargar confirmation, not just copy.
        p.evaluate('DC_APP.sim.cash=5103');assert p.evaluate('DC_APP.save(true)')
        q.click(card(a)+' .slot-load');pause(q)
        p.evaluate('DC_APP.sim.cash=6104');assert p.evaluate('DC_APP.save(true)')
        q.evaluate('DC_APP.sim.cash=7105');q.click('#pauseSaves')
        q.once('dialog',lambda d:d.dismiss());q.click(card(a)+' .slot-load')
        ck('Declining reload preserves the unsaved tab',q.evaluate('DC_APP.mode==="saves"&&DC_APP.sim.cash===7105'))
        q.once('dialog',lambda d:d.accept());q.click(card(a)+' .slot-load');pause(q)
        ck('Confirmed reload restores the current native revision',q.evaluate('DC_APP.sim.cash===6104&&DC_APP.activeSlot.revision===DC_APP.getStore().get(DC_APP.activeSlot.id).revision'))
        ck('Other character remains independent throughout conflicts',sample(q,b)==before_b)
        q.click('#pauseSaves');q.screenshot(path=str(O/'native-library.png'))
        ck('Final library remains usable and native',q.locator('#saveCards').is_visible() and q.evaluate(NATIVE))
        context.close();context=reopen();p=boot(context,origin)
        ck('Conflict copy and latest original survive final restart',sample(p,branch)['data']['cash']==4102 and sample(p,a)['data']['cash']==6104)
        ck('Unrelated slot still has its own named identity after restart',sample(p,b)['data']['identity']['name']=='Luz' and sample(p,b)['data']['equipment']['selected']=='emp')
        ck('No unexpected runtime errors or external resources',not errors and not requests)
        context.close();context=None
except Exception as error:
    errors.append(str(error));raise
finally:
    if context:
        try:context.close()
        except Exception:pass
    report={'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'runId':os.environ.get('DC_QA_RUN_ID'),'nativeStorage':True,'physicalGpu':False,'renderMode':'parked after actual WebGL boot','originMode':'HTTP loopback','profileMode':'temporary persistent Chromium profile; no personal data','boots':boots,'checks':checks,'errors':errors,'requests':requests,'finishedUtc':datetime.now(timezone.utc).isoformat()}
    (O/'native-saves.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
