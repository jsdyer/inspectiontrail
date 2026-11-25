// Source HTML is never inserted into the page. Only bounded text fields are exposed.
function inspectionText(value='') {
  return String(value).replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'').replace(/<[^>]*>/g,' ').replace(/&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi,(_,e)=>{const known={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '};if(known[e.toLowerCase()]!==undefined)return known[e.toLowerCase()];const n=e[1].toLowerCase()==='x'?parseInt(e.slice(2),16):parseInt(e.slice(1),10);return n>0&&n<=0x10ffff?String.fromCodePoint(n):'';}).replace(/\s+/g,' ').trim();
}
function inspectionSpan(html,id){return inspectionText(html.match(new RegExp('<span\\b[^>]*\\bid="'+id+'"[^>]*>([\\s\\S]*?)<\\/span>','i'))?.[1]||'');}
function inspectionParseSearch(html){
  const date=inspectionSpan(html,'lblLastUploadDateTime'),countText=inspectionSpan(html,'LblResultsCount');
  if(!date || !/^\d+$/.test(countText))throw new Error('Unrecognized inspection search response');
  const rows=[...html.matchAll(/<tr\b[^>]*class="ResultsTableRow[^"]*"[^>]*>([\s\S]*?)<\/tr>/gi)].map(m=>{const link=m[1].match(/href="Details\.aspx\?Id1=(\d+)"[^>]*>([\s\S]*?)<\/a>/i);const address=m[1].match(/<td\b[^>]*class="ResultsTableAddress"[^>]*>([\s\S]*?)<\/td>/i);if(!link||!address)throw new Error('Unrecognized establishment row');return {id:link[1],name:inspectionText(link[2]),address:inspectionText(address[1])};});
  if(rows.length!==Number(countText)||new Set(rows.map(x=>x.id)).size!==rows.length)throw new Error('Incomplete inspection results');
  return {source_updated:date,total:rows.length,truncated:rows.length>200,establishments:rows.slice(0,200)};
}
function inspectionParseReport(html,id){
  const name=inspectionSpan(html,'LblEstablishmentName'),address=inspectionSpan(html,'LblAddress');
  if(!name||!address||!html.includes('InspectionTable'))throw new Error('Unrecognized inspection report');
  const advisoryHTML=html.match(/<table\b[^>]*id="BoilWaterAdvisoryTable"[^>]*>([\s\S]*?)<\/table>/i)?.[1]||'';
  const advisories=[...advisoryHTML.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)].flatMap(m=>{const cells=[...m[1].matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/gi)].map(c=>inspectionText(c[1]));return cells.length===2?[{issued:cells[0]||null,removed:cells[1]||null}]:[];});
  const positions=[...html.matchAll(/<span\b[^>]*class="LabelInspectionDateStatus"[^>]*>Date Inspected:\s*([^<]*)<\/span>/gi)];
  const inspections=positions.map((m,i)=>{const block=html.slice(m.index,positions[i+1]?.index||html.indexOf('Disclaimer Footer'));const findings=[...block.matchAll(/<span\b[^>]*class="LabelInspectionText"[^>]*>([\s\S]*?)<\/span>\s*<\/td>\s*<td[^>]*>\s*<a\b[^>]*class="LinkInspectionText"[^>]*>([\s\S]*?)<\/a>[\s\S]*?<span\b[^>]*class="LabelInspectionHeader"[^>]*>Remedy<\/span>[\s\S]*?<span\b[^>]*class="LabelInspectionText"[^>]*>([\s\S]*?)<\/span>/gi)].map(f=>({finding:inspectionText(f[1]),status:inspectionText(f[2]),remedy:inspectionText(f[3])}));
    const summary=inspectionText(block.match(/class="DetailsCellOuter"[^>]*>\s*<span[^>]*>([\s\S]*?)<\/span>/i)?.[1]||'');
    // Preserve closure/warning annotations beside the inspection date as published.
    const annotation=inspectionText(block.match(/<\/span><\/td><td[^>]*>([\s\S]*?)<\/td>/i)?.[1]||'');
    if((block.match(/class="LinkInspectionText"/g)||[]).length!==findings.length)throw new Error('Unrecognized findings layout');
    return {date:inspectionText(m[1]),annotation,summary,findings};});
  if(!inspections.length)throw new Error('Report has no recognized inspection dates');
  return {id,name,address,advisories,inspections};
}
export {inspectionText,inspectionParseSearch,inspectionParseReport};
