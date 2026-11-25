import {inspectionParseSearch,inspectionParseReport} from '../web/source.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
const raw=JSON.parse(input),captures=raw.captures.map(c=>({query:c.query,...inspectionParseSearch(c.html),reports:Object.fromEntries(Object.entries(c.reports).map(([id,html])=>[id,inspectionParseReport(html,id)]))}));
console.log(JSON.stringify({schema:1,checked_at:raw.checked_at,record_count:captures.reduce((sum,c)=>sum+Object.keys(c.reports).length,0),captures}));
