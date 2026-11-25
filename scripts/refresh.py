#!/usr/bin/env python3
"""Refresh a small, explicitly labelled starter capture from the official NS search."""
import json, urllib.request, urllib.parse, http.cookiejar, re, html, subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
URL='https://novascotia.ca/nse/food-protection/reports/Request.aspx'
def search(query):
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def read(url,body=None):
        req=urllib.request.Request(url,data=body,headers={'User-Agent':'CoolCode InspectionTrail/1.0 (+https://coolcode.ca/inspectiontrail/)'})
        with opener.open(req,timeout=40) as r:raw=r.read(2_000_001)
        if len(raw)>2_000_000:raise ValueError('Inspection response too large')
        return raw.decode('utf-8')
    initial=read(URL);fields={}
    for tag in re.findall('<input[^>]+>',initial):
        attrs=dict(re.findall(r'(\w+)="([^"]*)"',tag))
        if attrs.get('type')=='hidden':fields[attrs['name']]=html.unescape(attrs.get('value',''))
    fields.update(TxtEstablishmentName=query.get('q',''),TxtCity=query.get('town',''),TxtEstablishmentStreet=query.get('address',''),TxtEstablishmentStreetNo='')
    for a in ['From','To']:
        for b in ['Month','Day','Year']:fields['Drop'+a+b]=''
    buttons={'search':('BttnSubmit','Submit'),'current-closures':('BttnClosuresCurrent','Current Closures'),'closures-year':('BttnClosuresPastYear','Closures in Past 12 Months'),'current-warnings':('BttnWarningsCurrent','Current Warnings'),'warnings-year':('BttnWarningsPastYear','Warnings in Past 12 Months')}
    k,v=buttons[query.get('mode','search')];fields[k]=v
    result=read(URL,urllib.parse.urlencode(fields).encode())
    ids=list(dict.fromkeys(re.findall(r'Details\.aspx\?Id1=(\d+)',result)))
    reports={i:read(urllib.parse.urljoin(URL,'Details.aspx?Id1='+i)) for i in ids[:query.get('capture_reports',3)]}
    return {'query':query,'html':result,'reports':reports}
if __name__=='__main__':
    config=json.loads((ROOT/'web/config.json').read_text());payload={'checked_at':datetime.now(timezone.utc).isoformat(),'captures':[search(q) for q in config['starter_queries']]}
    result=subprocess.run(['node',str(ROOT/'scripts/normalize.mjs')],input=json.dumps(payload),text=True,capture_output=True)
    if result.returncode:raise ValueError(result.stderr)
    normalized=json.loads(result.stdout)
    target=ROOT/'web/data/latest.json';target.parent.mkdir(exist_ok=True)
    tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(normalized,ensure_ascii=False,indent=2)+'\n');tmp.replace(target)
    (ROOT/'web/data/status.json').write_text(json.dumps({k:normalized[k] for k in ['schema','checked_at','record_count']},indent=2)+'\n')
    print('Collected',normalized['record_count'],'starter reports;',sum(c['total'] for c in normalized['captures']),'search matches')
