'use strict';
let apiKey = '';
const $ = id => document.getElementById(id);
function node(tag, text, cls) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (cls) el.className = cls; return el; }
async function api(path, body) {
  const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST', headers: {'X-API-Key': apiKey, 'Content-Type': 'application/json'}, body: body === undefined ? undefined : JSON.stringify(body)});
  const result = await response.json();
  if (!response.ok || result.status === 'error') throw new Error(`${result.error || 'Request failed'}${result.trace_id ? ' · Trace: ' + result.trace_id : ''}`);
  return result;
}
function table(rows) {
  if (!rows.length) return node('p', 'No records found.', 'empty');
  const wrap=node('div',undefined,'table-wrap'), t=node('table'), head=node('tr');
  const keys=Object.keys(rows[0]); keys.forEach(k=>head.append(node('th',k.replaceAll('_',' ')))); const thead=node('thead'); thead.append(head);t.append(thead);
  const tbody=node('tbody');rows.forEach(row=>{const tr=node('tr');keys.forEach(k=>tr.append(node('td',typeof row[k]==='object'?JSON.stringify(row[k]):String(row[k]??'—'))));tbody.append(tr);});t.append(tbody);wrap.append(t);return wrap;
}
function render(result) {
  $('trace').textContent='TRACE / '+result.trace_id;$('result').replaceChildren();
  const data=result.data;
  if(data.rows) $('result').append(table(data.rows));
  else if(data.documents){
    $('result').append(node('p',data.notice));
    if(!data.documents.length)$('result').append(node('p','No matching documents. Try “maintenance” or “replacement”.'));
    data.documents.forEach(d=>{const card=node('div',undefined,'doc');card.append(node('h3',d.id+' · '+d.title),node('p',d.body));$('result').append(card);});
  } else $('result').append(node('pre',JSON.stringify(data,null,2)));
}
async function refresh() {
  const m=(await api('/api/metrics')).data;
  $('requests').textContent=m.requests;$('pending').textContent=m.pending_approvals;$('tickets-count').textContent=m.tickets;$('latency').textContent=m.mean_latency_ms.toFixed(1)+' ms';
  const rows=(await api('/api/approvals')).data.approvals;$('queue').replaceChildren();
  if(!rows.length)$('queue').append(node('p','No proposals visible for this identity.','empty'));
  rows.forEach(row=>{
    const card=node('article',undefined,'approval');card.append(node('h3',row.payload.title),node('span',row.status.toUpperCase(),'badge'),node('p',`Vehicle ${row.payload.vehicle_id} · ${row.payload.priority} · Requested by ${row.requester}`),node('p',row.payload.description),node('p',`Approval ${row.id} · Expires ${new Date(row.expires_at*1000).toLocaleString()}`));
    if(row.status==='pending' && row.expires_at*1000>Date.now())['approve','reject'].forEach(decision=>{const b=node('button',decision==='approve'?'Approve & create ticket':'Reject');b.onclick=()=>guard(async()=>{if(!confirm(`${decision==='approve'?'Create this ticket exactly as displayed':'Reject this proposal'}?`))return;b.disabled=true;try{render(await api(`/api/approvals/${row.id}/decision`,{decision}));await refresh();}finally{b.disabled=false;}});card.append(b);});
    $('queue').append(card);
  });
}
async function guard(fn){$('notice').textContent='';try{await fn();}catch(error){$('notice').textContent=error.message;}}
$('connect').onclick=()=>guard(async()=>{apiKey=$('key').value.trim();$('key').value='';$('connection').textContent='Connecting…';try{await refresh();$('connection').textContent='Authenticated';}catch(e){$('connection').textContent='Connection failed';throw e;}});
for(const [form,tool] of [['analytics','analytics'],['documents','documents'],['proposal','propose_ticket']]){
  $(form).onsubmit=event=>{event.preventDefault();guard(async()=>{const button=$(form).querySelector('button');button.disabled=true;try{render(await api('/api/tools/'+tool,Object.fromEntries(new FormData($(form)))));await refresh();}finally{button.disabled=false;}});};
}
$('refresh').onclick=()=>guard(refresh);
for(const view of ['audit','tickets'])$(view).onclick=()=>guard(async()=>{$('activity-data').replaceChildren(table((await api('/api/'+view)).data[view==='audit'?'events':'tickets']));});
