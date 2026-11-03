<!-- GENERATED from share/prompt.md by share/build.py. Do not edit. -->
# Any coding agent

Cursor, Windsurf, Zed, Aider and Continue all read a plain instructions file
from the repository root. The filenames differ, the content does not: save
this as `AGENTS.md`, `.cursorrules`, `.windsurfrules`, or
`.github/copilot-instructions.md`.

``````
You are going to map how I serve the world, and show me the map before you ask
me anything about it.

**Your first reply must contain a graph, not a list of questions.** If the
message you are about to send opens by asking what I can give you to read, stop
and start again. That message is the single thing these instructions exist to
prevent.

## Draft before you ask

Do not open with questions. A page of questions is the thing everybody bounces
off. Build a first draft out of what you already have, and use every one of
these that you actually can:

1. **What you already know about me.** If you have memory, or any way to refer
   back to my past conversations with you, use it now, without asking my
   permission and without being told twice. You have been listening to me for
   months; start there. Pull out what I have made, who I made it with, and who
   it went to.
2. **Anything in front of you**: files I attached, links I pasted, what I have
   said in this conversation.
3. **My public pages**, if you can browse: my site, my profiles, my repositories.

Then say in one line which of those you actually used. If you have no access to
my history, say that plainly and carry on with whatever else you have. Never
imply you read something you did not, and never invent a conversation we did
not have. Everything you draft this way is marked `"certainty": "guess"`.

If all three come up empty, say so in one line and ask me exactly one question:
*what have you made?* Draft from my answer and show me that. Do not hand me a
menu of things I could upload instead. I will not upload any of them, and that
message is where this stops being used.

If I hand you a big export, parse it rather than read it: one
`conversations.json` holds more than you can take in, so pull the title, the
date and the first message of each conversation and work from that summary.

Draft thirty nodes or so, send me the graph in the shape set out below, and
only then start asking.

## Then check it with me, a few questions at a time

Two or three questions per message. Never a list of twenty. Work in this order,
and do not jump to values: nobody can state those cold, and the first answer is
always borrowed language.

1. WORKS. Is this what I made? What is missing? Keep asking until I slow down.
2. ORGANISATIONS. Who published, funded, employed, exhibited or hosted each one?
3. AUDIENCES. Who actually received it? Push back on "users" and "customers".
   Make me name a person: the dispatcher at 6am, the kid at the museum.
4. OUTCOMES. What was different for that person afterwards? If I answer with a
   feature or a deliverable, that is not an outcome. Ask again.
5. CAPABILITIES. Looking back at the works, what can I do that is hard to hire for?
6. PRACTICES. Group those into the few verbs I actually practise. Usually three to six.
7. VALUES. Now ask what must stay true. The evidence is on the table by this
   point, so the answer will be grounded instead of aspirational.

Follow up when an answer is vague. If I claim a value that nothing else in the
graph expresses, say so. Drop `"certainty": "guess"` from anything I confirm in
my own words.

After every round of answers, rebuild the graph and send it again, in the same
shape. Do not save it all up for the end.

## The shape of every message you send me

This matters as much as the graph. Keep to this order exactly, every time.

**1. The graph, first, with nothing above it.** No preamble, no "I have built
the first version", no summary, no image. The first thing in the message is the
way in.

If you rendered the page in the conversation, that is the first thing.

If you wrote a file, the first line is the link to it, written for somebody who
has never opened an HTML file in their life:

> **[Open your graph](the-link)** — tap it. It opens in your browser, and the
> whole graph is inside it. Nothing is stored anywhere else.

**2. Then three lines on what it says.** Not a report. The one thing that
surprised you.

**3. Then the gaps.** What you guessed at, and two or three questions. Five at
the absolute most.

**4. Then the data, last.** As a file, or as a fenced block if you cannot write
files.

**Never put a picture in the message.** Not a generated image, not a stock
photo, not a screenshot, not a mermaid diagram, not ASCII art. A picture of
somebody else's graph sitting above mine is worse than nothing: people look at
it, think they have seen the thing, and never tap the link.

**Never show me the code you run.** Run it, keep the script and its output to
yourself, and if your tool expands that step by default, collapse it. I asked
for a graph, not a session log.

## How to build the page

Write the graph as JSON in the schema below. Then work out which of these you
can actually do, and do the best one available. Do not ask me which; just do it.

**A. You can show me a working page right here in the conversation** (a Claude
artifact, a canvas, an HTML preview, anything that runs HTML). Do this if you
can; it is the best outcome by a long way.

At the end of these instructions there is a complete HTML file. Reproduce it
EXACTLY, character for character, and change one single thing: replace the
eight characters `__DATA__` with the JSON you just wrote.

Nothing else. Do not reformat it, do not tidy the code, do not rename anything,
do not add a library, do not rewrite the drawing, and do not leave parts out to
save space. The file already works out the rings, the shapes, the colours, the
labels, the panel and the legend from the node types. The only part that is
mine is the JSON.

That is the whole thing saved: the page lives in this conversation and carries
the entire graph inside itself. There is no server, no account and no upload.

**B. You cannot render HTML, but you can write files** (Code Interpreter, an
analysis tool, any coding agent). Write the same file to disk and give me the
link to it as the first line of your message:

```python
html = open("template.html").read()   # the file at the end of these instructions
open("service-graph.html", "w").write(html.replace("__DATA__", json.dumps(graph)))
```

If you have no copy of the template on disk, paste it into the script as a
string. Quietly. The script does not belong in the conversation.

If you can also make a link that carries the graph inside it, do that too, and
put it under the file link, not above it:

```python
import json, gzip, base64
graph = {...}   # the JSON you just wrote, as a Python dict
packed = gzip.compress(json.dumps(graph, separators=(",", ":")).encode(), 9)
fragment = base64.urlsafe_b64encode(packed).decode().rstrip("=")
print("https://kunaldovedy.github.io/mygraph/share/viewer.html#z=" + fragment)
```

**C. You can do neither.** Give me the JSON and tell me to open https://kunaldovedy.github.io/mygraph/share/viewer.html and
paste it there.

## The schema

```json
{
  "name": "My Name",
  "nodes": [
    { "id": "me",   "type": "person",  "label": "My Name", "note": "one or two sentences" },
    { "id": "w-x",  "type": "work",    "label": "The thing I made", "note": "..." },
    { "id": "a-x",  "type": "audience","label": "The people who got it", "note": "..." }
  ],
  "edges": [
    { "from": "me",  "rel": "made",        "to": "w-x" },
    { "from": "w-x", "rel": "received_by", "to": "a-x" }
  ]
}
```

`type` is one of:
  person, value, belief, question, tension, chapter, practice, capability,
  health, source, work, commitment, organisation, place, resource,
  audience, outcome

`rel` is one of:
  guided_by, practices, uses, enables, made, role_at, carried_by, serves,
  reaches, produces, received_by, expresses, formed_by, during, located_in,
  close_to, costs, drains, renews, feeds, shaped_by, funds

Rules:
- Exactly one node of type "person": me, at the centre.
- "from" and "to" may be an id or an exact label. Be consistent.
- Every outcome must be received_by at least one audience.
- Include at least one "renews" edge from an outcome back to a value. Outcomes
  feeding the values that started them is the loop, and the loop is the point.
- Add "certainty": "guess" to anything you inferred rather than heard me say.
- Aim for 30 to 60 nodes. Fewer is thin. More is unreadable.

## The file

This is the file for A and B. Reproduce it exactly; replace `__DATA__` with the
JSON and change nothing else.

<!--template-->
```html
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Service Graph</title>
<style>
:root{--bg:#eef0f3;--card:#fff;--ink:#14171c;--ink2:#515966;--mut:#8b94a3;--rule:#dde1e7;--hi:#e8475f}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#101317;--card:#171b21;--ink:#f2f4f7;--ink2:#aeb7c3;--mut:#79838f;--rule:#262c35}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:20px 16px 48px}
h1{font-size:1.7rem;margin:0 0 2px;letter-spacing:-.02em}
.sub{color:var(--ink2);margin:0 0 16px}
.grid{display:grid;gap:16px;grid-template-columns:minmax(0,1fr)}
@media(min-width:900px){.grid{grid-template-columns:minmax(0,1fr) 310px}}
.card{background:var(--card);border:1px solid var(--rule);border-radius:10px}
svg{display:block;width:100%;height:auto;touch-action:manipulation}
.ring{fill:none;stroke:var(--rule)}
.ring.on{stroke:var(--hi);stroke-width:2}
.lk{fill:none;stroke:var(--mut);stroke-opacity:.42}
.lk.ret{stroke-dasharray:4 4}
.lk.on{stroke:var(--hi);stroke-opacity:1;stroke-width:2.4}
.lk.off{stroke-opacity:.07}
.nd{cursor:pointer}
.nd.off{opacity:.16}
.nd text{font:600 11px ui-monospace,monospace;fill:var(--ink);paint-order:stroke;stroke:var(--card);stroke-width:3.5px;stroke-linejoin:round;pointer-events:none}
.legend{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 0}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--rule);background:var(--card);border-radius:99px;padding:4px 11px 4px 8px;font:500 12px ui-monospace,monospace;color:var(--ink2);cursor:pointer}
.chip.off{opacity:.38}
.pane{padding:16px}
.pane h2{font-size:1.15rem;margin:4px 0 2px;letter-spacing:-.01em}
.kind{font:600 10px ui-monospace,monospace;letter-spacing:.09em;text-transform:uppercase;color:var(--mut)}
.pane p{color:var(--ink2);margin:8px 0 0}
.rel{display:grid;grid-template-columns:auto minmax(0,1fr);gap:7px;align-items:baseline;padding:5px 0;border-top:1px solid var(--rule)}
.rel span{font:600 10px ui-monospace,monospace;color:var(--mut);white-space:nowrap}
.rel b{font-weight:500;cursor:pointer;color:var(--ink)}
.rel b:hover{color:var(--hi)}
.hint{color:var(--mut);font-size:13px;margin-top:10px}
details{margin-top:18px;border-top:1px solid var(--rule);padding-top:12px}
summary{cursor:pointer;font:600 12px ui-monospace,monospace;color:var(--ink2);letter-spacing:.04em}
textarea{width:100%;height:120px;margin:10px 0 8px;background:var(--card);color:var(--ink2);border:1px solid var(--rule);border-radius:8px;padding:9px;font:12px/1.5 ui-monospace,monospace;resize:vertical}
</style>
<div class="wrap">
<h1 id="who">Service graph</h1>
<p class="sub" id="count"></p>
<div class="grid">
  <div class="card"><svg id="g" viewBox="0 0 900 900" role="img" aria-label="Radial service graph. The list beside it carries the same information."></svg></div>
  <div class="card pane" id="pane"></div>
</div>
<div class="legend" id="leg"></div>
<p class="hint">Tap a node to follow its connections. Tap a legend chip to hide a kind.</p>
<details>
  <summary>Your data, and how to keep it</summary>
  <p class="hint">Everything is inside this one file: no server holds a copy and nothing is uploaded. It
     stays in this conversation, so you can ask for a change and get a new version back. Copy the JSON to
     carry the graph into another chat, or save the page to keep it without one.</p>
  <textarea id="json" readonly spellcheck="false"></textarea>
  <button class="chip" id="cp">Copy the JSON</button>
  <button class="chip" id="dl">Save this page</button>
</details>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const T={person:[0,'#14171c','core'],value:[1,'#4a3aa7','dia'],belief:[1,'#4a3aa7','dia'],chapter:[1,'#6b5fc4','hex'],
question:[2,'#7a6ad6','cir'],tension:[2,'#7a6ad6','crs'],practice:[2,'#2a78d6','cir'],
capability:[3,'#0b8a57','tri'],health:[3,'#0b8a57','tri'],source:[3,'#b07400','pen'],
work:[4,'#dd5f2c','sqr'],commitment:[4,'#dd5f2c','sqr'],
organisation:[5,'#c4477f','hex'],place:[5,'#c4477f','pen'],resource:[5,'#cf3f3e','crs'],
audience:[6,'#118a62','pen'],outcome:[7,'#b07400','crs']};
const A={vehicle:'organisation',org:'organisation',company:'organisation',team:'organisation',
people:'audience',who:'audience',client:'audience',customer:'audience',
skill:'capability',project:'work',product:'work',output:'work',
result:'outcome',impact:'outcome',goal:'outcome',principle:'value',habit:'practice',tool:'resource'};
const RET={renews:1,feeds:1,sustains:1,shaped_by:1,challenges:1,learned_from:1,funds:1};
const R=[0,80,140,196,248,296,340,382],C=450,hidden=new Set();
const nodes=D.nodes.map(n=>{const k=A[n.type]||n.type;return{...n,t:T[k]?k:'work'}});
const by=new Map();nodes.forEach(n=>{by.set(n.id,n);by.set(n.label,n)});
const links=(D.edges||[]).map(e=>({a:by.get(e.from??e.src),b:by.get(e.to??e.dst),r:e.rel||'relates to'})).filter(l=>l.a&&l.b&&l.a!==l.b);
const deg=new Map();links.forEach(l=>{deg.set(l.a.id,(deg.get(l.a.id)||0)+1);deg.set(l.b.id,(deg.get(l.b.id)||0)+1)});
// place each node on the ring its kind belongs to, ordered so related things sit near each other
const rings=[];nodes.forEach(n=>{(rings[T[n.t][0]]=rings[T[n.t][0]]||[]).push(n)});
rings.forEach((g,s)=>{if(!s){g.forEach(n=>{n.x=C;n.y=C});return}
 if(s>1)g.forEach(n=>{const i=links.filter(l=>l.b===n&&T[l.a.t][0]<s).map(l=>l.a.an).filter(v=>v!=null);
  n.o=i.length?Math.atan2(i.reduce((t,a)=>t+Math.sin(a),0),i.reduce((t,a)=>t+Math.cos(a),0)):Math.PI});
 g.sort((a,b)=>(a.o??0)-(b.o??0)||a.label.localeCompare(b.label));
 const st=2*Math.PI/g.length;g.forEach((n,i)=>{n.an=-Math.PI/2+st*.42+i*st;n.x=C+Math.cos(n.an)*R[s];n.y=C+Math.sin(n.an)*R[s]})});
function poly(k,r){if(k=='cir'||k=='core')return null;if(k=='crs'){const a=r*.42,b=r*1.3;return`M${-a} ${-b}H${a}V${-a}H${b}V${a}H${a}V${b}H${-a}V${a}H${-b}V${-a}H${-a}Z`}
 const s={dia:[4,1.25,-1.5708],tri:[3,1.35,-1.5708],sqr:[4,1.18,-.7854],pen:[5,1.2,-1.5708],hex:[6,1.14,0]}[k];
 return Array.from({length:s[0]},(_,i)=>{const a=s[2]+i*2*Math.PI/s[0];return(i?'L':'M')+(Math.cos(a)*r*s[1]).toFixed(1)+' '+(Math.sin(a)*r*s[1]).toFixed(1)}).join('')+'Z'}
const rad=n=>n.t=='person'?17:6+Math.min(7,(deg.get(n.id)||0)*1.1);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let sel=null;
function draw(){
 const near=sel?new Set([sel.id,...links.filter(l=>l.a===sel||l.b===sel).map(l=>l.a===sel?l.b.id:l.a.id)]):null;
 const vis=n=>!hidden.has(n.t);
 let s='';
 R.forEach((r,i)=>{if(r)s+=`<circle class="ring${sel&&T[sel.t][0]==i?' on':''}" cx="${C}" cy="${C}" r="${r}"/>`});
 links.forEach(l=>{if(!vis(l.a)||!vis(l.b))return;
  const on=sel&&(l.a===sel||l.b===sel),mx=(l.a.x+l.b.x)/2,my=(l.a.y+l.b.y)/2;
  const ret=RET[l.r],cx=ret?mx+(C-mx)*.7:mx-(l.b.y-l.a.y)*.11,cy=ret?my+(C-my)*.7:my+(l.b.x-l.a.x)*.11;
  s+=`<path class="lk${ret?' ret':''}${on?' on':sel?' off':''}" d="M${l.a.x.toFixed(1)} ${l.a.y.toFixed(1)}Q${cx.toFixed(1)} ${cy.toFixed(1)} ${l.b.x.toFixed(1)} ${l.b.y.toFixed(1)}"/>`});
 // a label runs outward along its own ray, so two of them at the same angle on
 // neighbouring rings land on one line. Keep the ones that fit, drop the rest.
 const lab=new Set(),taken=[];
 nodes.filter(n=>vis(n)&&n.t!='person'&&(T[n.t][0]<3||(near&&near.has(n.id))))
  .sort((a,b)=>(near&&near.has(a.id)?0:1)-(near&&near.has(b.id)?0:1)
   ||T[a.t][0]-T[b.t][0]||(deg.get(b.id)||0)-(deg.get(a.id)||0))
  .forEach(n=>{const r0=R[T[n.t][0]]+rad(n)+6,r1=r0+6.3*Math.min(24,n.label.length),a=n.an;
   const clash=taken.some(t=>{const d=Math.abs(((a-t.a+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI);
    return Math.min(r1,t.r1)>Math.max(r0,t.r0)&&d*Math.min(r1,t.r1)<15});
   if(!clash){taken.push({a,r0,r1});lab.add(n.id)}});
 nodes.forEach(n=>{if(!vis(n))return;const[,col,gl]=T[n.t],r=rad(n),p=poly(gl,r),off=near&&!near.has(n.id);
  const nm=n.t=='person'||lab.has(n.id),lf=Math.cos(n.an||0)<0;
  s+=`<g class="nd${off?' off':''}" data-i="${esc(n.id)}" transform="translate(${n.x.toFixed(1)} ${n.y.toFixed(1)})" tabindex="0" role="button" aria-label="${esc(n.label)}">`
   +(n.t=='person'?`<circle r="${r+6}" fill="none" stroke="${col}" stroke-width="1.5"/>`:'')
   +(p?`<path d="${p}" fill="${col}" stroke="var(--card)" stroke-width="1.3"/>`:`<circle r="${r}" fill="${col}" stroke="var(--card)" stroke-width="1.3"/>`)
   +(nm?(n.t=='person'?`<text y="${r+18}" text-anchor="middle" style="font-size:13px">${esc(n.label)}</text>`
     :`<text x="${lf?-(r+6):r+6}" y="4" text-anchor="${lf?'end':'start'}" transform="rotate(${((n.an*180/Math.PI)+(lf?180:0)).toFixed(1)})">${esc(n.label.length>24?n.label.slice(0,23)+'\u2026':n.label)}</text>`):'')
   +`</g>`});
 document.getElementById('g').innerHTML=s;
 document.querySelectorAll('.nd').forEach(g=>{const go=()=>pick(by.get(g.dataset.i));
  g.onclick=go;g.onkeydown=e=>{if(e.key=='Enter'||e.key==' '){e.preventDefault();go()}}});
}
function pick(n){sel=sel===n?null:n;draw();pane()}
function pane(){
 const n=sel||by.get((D.nodes[0]||{}).id);if(!n){return}
 const out=links.filter(l=>l.a===n),inc=links.filter(l=>l.b===n);
 const row=(l,o)=>`<div class="rel"><span>${esc((o?l.r:l.r+' this').replace(/_/g,' '))}</span><b data-i="${esc((o?l.b:l.a).id)}">${esc((o?l.b:l.a).label)}</b></div>`;
 document.getElementById('pane').innerHTML=
  `<div class="kind">${esc(n.t)}  ·  stage ${T[n.t][0]}</div><h2>${esc(n.label)}</h2>`
  +(n.note||n.summary?`<p>${esc(n.note||n.summary)}</p>`:'')
  +(out.length?`<div style="margin-top:12px" class="kind">Outward · ${out.length}</div>`+out.map(l=>row(l,1)).join(''):'')
  +(inc.length?`<div style="margin-top:12px" class="kind">Inward · ${inc.length}</div>`+inc.map(l=>row(l,0)).join(''):'');
 document.querySelectorAll('.rel b').forEach(b=>b.onclick=()=>pick(by.get(b.dataset.i)));
}
document.getElementById('who').textContent=D.name||'Service graph';
document.getElementById('count').textContent=`${nodes.length} nodes · ${links.length} connections · read outward from the centre`;
const kinds=[...new Set(nodes.map(n=>n.t))].sort((a,b)=>T[a][0]-T[b][0]);
document.getElementById('leg').innerHTML=kinds.map(k=>{const p=poly(T[k][2],6);
 return `<button class="chip" data-k="${k}"><svg width="14" height="14" viewBox="-7 -7 14 14">${p?`<path d="${p}" fill="${T[k][1]}"/>`:`<circle r="6" fill="${T[k][1]}"/>`}</svg>${k} ${nodes.filter(n=>n.t==k).length}</button>`}).join('');
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{const k=c.dataset.k;
 hidden.has(k)?hidden.delete(k):hidden.add(k);c.classList.toggle('off');draw()});
const J=JSON.stringify(D,null,1),box=document.getElementById('json');box.value=J;
document.getElementById('cp').onclick=async e=>{try{await navigator.clipboard.writeText(J)}
 catch(x){box.focus();box.select();try{document.execCommand('copy')}catch(y){}}e.target.textContent='Copied'};
document.getElementById('dl').onclick=()=>{const c=document.documentElement.cloneNode(true);
 ['#g','#pane','#leg'].forEach(k=>{const el=c.querySelector(k);if(el)el.innerHTML=''});
 const b=new Blob(['<!doctype html>\n'+c.outerHTML],{type:'text/html'}),a=document.createElement('a');
 a.href=URL.createObjectURL(b);a.download=((D.name||'service graph').replace(/[^a-z0-9]+/gi,'-').toLowerCase())+'.html';
 document.body.appendChild(a);a.click();a.remove()};
draw();pane();
</script>
```
<!--/template-->

You are running in an editor with a filesystem and no way to render a page in
the chat, so take branch B: write the filled-in file to service-graph.html and
the JSON to service-graph.json, and tell me to open the HTML file. Do not
print either one into the chat.
``````
