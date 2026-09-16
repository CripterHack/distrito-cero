"""HTTP-native product identity and legacy import smoke, not a GPU benchmark."""
from pathlib import Path
from urllib.parse import urlsplit
from tempfile import TemporaryDirectory
import hashlib,json,os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
from native_support import game_origin

R=Path(__file__).resolve().parents[1];O=R/'qa/v020';O.mkdir(parents=True,exist_ok=True)
expected=json.loads((R/'build-info.json').read_text());checks=[];errors=[];requests=[];paths=[];info={}
SETTINGS="localStorage.setItem('distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false}))"
NATIVE="localStorage instanceof Storage && /native code/.test(Storage.prototype.setItem.toString())"
def ck(name,value):
    checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True);assert value,name
try:
    assert os.environ.get('DC_QA_ORIGIN')=='http'
    with game_origin(R) as origin,TemporaryDirectory(prefix='dc-release-profile-') as profile,sync_playwright() as pw:
        def boot():
            context=pw.chromium.launch_persistent_context(profile,viewport={'width':1100,'height':760},accept_downloads=True,**launch_options())
            context.add_init_script(SETTINGS);page=context.new_page();page.set_default_timeout(45000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url) if urlsplit(r.url).netloc!=urlsplit(origin).netloc and r.url.startswith(('http:','https:')) else None)
            page.on('request',lambda r:paths.append(urlsplit(r.url).path))
            response=page.goto(origin,wait_until='domcontentloaded',timeout=120000)
            page.wait_for_function('!!window.DC_APP',timeout=120000);page.evaluate('DC_APP.renderer.humanReady');return context,page,response
        context,p,response=boot()
        ck('Served HTML matches the active build hash',hashlib.sha256(response.body()).hexdigest()==expected['htmlSha256'])
        ck('Document title identifies the current product release',p.title()=='Distrito Cero '+expected['label']+' · '+expected['name'])
        ck('Landing label exposes the active version and is visible',p.locator('#buildLabel').is_visible() and p.locator('#buildLabel').get_attribute('data-build-version')==expected['version'])
        ck('Embedded immutable identity agrees with version manifest',p.evaluate('DC.BuildInfo.version')==expected['version'] and p.evaluate('Object.isFrozen(DC.BuildInfo)'))
        ck('Source fingerprint matches HTML meta and build sidecar',p.evaluate('DC.BuildInfo.sourceSha256')==expected['sourceSha256']==p.locator('meta[name="build-source"]').get_attribute('content'))
        ck('Release smoke uses native Web Storage',p.evaluate(NATIVE))
        p.screenshot(path=str(O/'release-menu.png'))
        p.click('#landingSaves');p.locator('#saveFile').set_input_files(str(R/'tests/fixtures/v019-slot.json'))
        p.wait_for_function('DC_APP.getStore().list().length===1')
        slot=p.evaluate('DC_APP.getStore().list()[0].id');p.click('[data-slot="'+slot+'"] .slot-load')
        if p.locator('#tutorial').is_visible():p.click('#dismissTutorial')
        p.wait_for_function('DC_APP.mode==="play"');p.keyboard.press('Escape');p.wait_for_function('DC_APP.mode==="pause"')
        ck('Legacy v0.19 JSON imports through the production UI',p.evaluate('DC_APP.sim.characterName')=='Noa v019' and p.evaluate('DC_APP.sim.cash')==2345)
        ck('Legacy equipment and hairstyle survive import',p.evaluate('DC_APP.sim.equipment.selected')=='emp' and p.evaluate('DC_APP.sim.equipment.ammo.emp.reserve')==5 and p.evaluate('DC_APP.sim.appearance.hairStyle')==8)
        ck('Pause displays the same active product and short build ID',p.locator('#releaseInfo').is_visible() and expected['sourceSha256'][:12] in p.locator('#releaseInfo').inner_text() and p.locator('#releaseInfo').get_attribute('data-build-version')==expected['version'])
        p.screenshot(path=str(O/'release-pause.png'))
        ck('Product bump keeps the existing catalogue key',p.evaluate('DC.SaveStore.KEY')=='distrito-cero:saves:v2')
        with p.expect_download() as dl:p.click('#exportSave')
        export=json.loads(Path(dl.value.path()).read_text())
        ck('Downloaded save retains schema one, not product version',export['version']==1 and export['format']=='distrito-cero-slot' and export['data']['equipment']['version']==1)
        raw=p.evaluate('DC_APP.getStore().raw()');context.close()
        context,p,response=boot();ck('Imported catalogue survives native browser restart',p.evaluate('DC_APP.getStore().raw()')==raw and p.evaluate(NATIVE))
        ck('Three visible version attributes never contain old labels',p.evaluate("[...document.querySelectorAll('[data-build-version]')].length===3 && [...document.querySelectorAll('[data-build-version]')].every(e=>e.dataset.buildVersion===DC.BuildInfo.version)"))
        ck('Versioning adds no runtime resource requests or exceptions',not errors and not requests and not any(x in ['/version.json','/build-info.json'] for x in paths))
        info={'browser':context.browser.version if context.browser else 'persistent Chromium','originMode':'HTTP loopback','preparedWorld':False,'legacyFixture':'ef905ec'};context.close()
except Exception as error:
    errors.append(str(error));raise
finally:
    (O/'release.json').write_text(json.dumps({'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'checks':checks,'errors':errors,'requests':requests,'nativeStorage':True,'physicalGpu':False,'build':expected,**info},ensure_ascii=False,indent=2))
