"""Exercise the real built app at its GitHub project subpath."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, shutil, tempfile, threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def main():
 screenshots=ROOT/'browser-checks';screenshots.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shutil.copytree(ROOT/'dist',Path(temp)/ROOT.name)
  server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=temp));threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH'),args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/assets/tool-metrics.js',lambda route:route.fulfill(status=200,body=''))
    page.route('https://tile.openstreetmap.org/**',lambda route:route.abort())
    page.goto(f'http://127.0.0.1:{server.server_port}/{ROOT.name}/');page.locator('.card').first.wait_for()
    page.locator('.card').first.get_by_role('button',name='Read inspection history',exact=True).click()
    page.locator('.report').first.wait_for();assert 'Inspected' in page.locator('.report').first.inner_text()
    page.locator('.card').first.get_by_role('button',name='Watch establishment',exact=True).click()
    page.reload();page.locator('.card').first.wait_for();page.locator('#show-saved').click()
    assert page.locator('.card').count()==1
    payload={'fetched_at':'2026-11-25T12:00:00Z','data':{'source_updated':'24 Nov, 2026 3:12 AM','total':1,'truncated':False,'establishments':[{'id':'999','name':'<img src=x onerror=alert(1)> New Cafe','address':'123 New Town'}]}}
    page.route('**/api/inspectiontrail/search?**',lambda route:route.fulfill(status=200,json=payload))
    page.locator('#query').fill('Any New Cafe');page.locator('#town').fill('');page.locator('#submit').click()
    page.get_by_role('heading',name='<img src=x onerror=alert(1)> New Cafe').wait_for()
    assert page.locator('#results img').count()==0
    page.route('**/api/inspectiontrail/search?**',lambda route:route.fulfill(status=502,json={'error':{'message':'The provincial source is unavailable.'}}))
    page.locator('#query').fill('Another Cafe');page.locator('#submit').click()
    page.wait_for_function("document.querySelector('#status').textContent.includes('previous results')")
    assert 'New Cafe' in page.locator('#results').inner_text()
    page.screenshot(path=str(screenshots/'desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.screenshot(path=str(screenshots/'mobile.png'),full_page=True)
    assert not errors,errors;browser.close()
   print('Browser task, persistence, safe text, source failures and mobile layout passed')
  finally:server.shutdown()
if __name__=='__main__':main()
