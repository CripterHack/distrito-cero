"""Actual render-loop smoke test. Playwright is a test tool, not a game dependency.
The test environment uses Xvfb and SwiftShader. No renderer or storage replacement.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
errors = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/usr/bin/chromium', headless=True,
        args=['--no-sandbox', '--use-angle=swiftshader',
              '--enable-unsafe-swiftshader', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width': 640, 'height': 400})
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.set_content((ROOT / 'index.html').read_text(), wait_until='load')
    page.wait_for_function('!!window.DC_APP', timeout=30000)
    page.evaluate("DC_APP.renderer.quality='eco';DC_APP.renderer.rain=0;DC_APP.renderer.bloom=0;DC_APP.renderer.resize();")
    page.click('#start')
    page.click('#dismissTutorial')
    page.keyboard.press('f')
    page.wait_for_function('DC_APP.sim.player.car===0')
    before = page.evaluate('({frame:DC_APP.renderer.frame,z:DC_APP.sim.player.z})')
    page.keyboard.down('w')
    page.wait_for_timeout(3500)
    page.keyboard.up('w')
    after = page.evaluate('({frame:DC_APP.renderer.frame,z:DC_APP.sim.player.z,speed:DC_APP.sim.actor().speed,glError:DC_APP.renderer.gl.getError()})')
    assert after['frame'] > before['frame'] + 2, 'Real renderer must keep drawing'
    assert after['z'] > before['z'] + 1, 'Keyboard input must move the car while rendering'
    assert after['speed'] > 1, 'Car must accelerate'
    assert after['glError'] == 0 and not errors, errors
    browser.close()
report = {'passed':True,'before':before,'after':after,'errors':errors,
          'environment':'640x400 eco / Chromium / SwiftShader software GPU / set_content',
          'renderer_replaced':False,'storage_replaced':False,
          'hardware_performance_benchmark':False}
(ROOT/'qa/continuous-render-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report, indent=2))
