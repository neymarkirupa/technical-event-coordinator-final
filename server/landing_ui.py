"""Landing page UI for Technical Event Coordinator.

Generates a self-contained HTML string served at GET /
with a premium, dynamic dashboard for the hackathon environment.
"""

UI_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Technical Event Coordinator — OpenEnv Environment</title>
<meta name="description" content="AI-powered room assignment simulator for technical fests. Solve constraint-satisfaction puzzles across easy, medium, and hard tiers." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0e17;--surface:#12162a;--card:#181d35;--border:#252b4a;
  --accent:#6c5ce7;--accent2:#a29bfe;--hot:#fd79a8;--success:#00cec9;
  --warn:#fdcb6e;--text:#e8e8f0;--muted:#7f8fa6;
  --radius:14px;--shadow:0 8px 32px rgba(0,0,0,.45);
}
html{scroll-behavior:smooth}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}
a{color:var(--accent2);text-decoration:none}

/* ── animated background ─────────────────────────────────────── */
.bg-glow{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.bg-glow span{position:absolute;border-radius:50%;filter:blur(120px);opacity:.18;animation:drift 18s ease-in-out infinite alternate}
.bg-glow span:nth-child(1){width:600px;height:600px;background:var(--accent);top:-10%;left:-5%;animation-delay:0s}
.bg-glow span:nth-child(2){width:500px;height:500px;background:var(--hot);bottom:-10%;right:-8%;animation-delay:-6s}
.bg-glow span:nth-child(3){width:400px;height:400px;background:var(--success);top:40%;left:50%;animation-delay:-12s}
@keyframes drift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(40px,-30px) scale(1.12)}100%{transform:translate(-20px,20px) scale(.95)}}

/* ── layout ──────────────────────────────────────────────────── */
.wrap{position:relative;z-index:1;max-width:1160px;margin:0 auto;padding:2rem 1.5rem 4rem}
header{text-align:center;padding:3rem 0 2rem}
header h1{font-size:2.6rem;font-weight:800;background:linear-gradient(135deg,var(--accent2),var(--hot));-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-.02em}
header p.tagline{color:var(--muted);font-size:1.05rem;margin-top:.5rem;max-width:640px;margin-inline:auto}
.badge-row{display:flex;gap:.6rem;justify-content:center;margin-top:1.2rem;flex-wrap:wrap}
.badge{display:inline-flex;align-items:center;gap:.35rem;padding:.3rem .8rem;font-size:.78rem;font-weight:600;border-radius:99px;background:rgba(108,92,231,.15);border:1px solid rgba(108,92,231,.3);color:var(--accent2)}
.badge.green{background:rgba(0,206,201,.12);border-color:rgba(0,206,201,.3);color:var(--success)}
.badge.pink{background:rgba(253,121,168,.12);border-color:rgba(253,121,168,.3);color:var(--hot)}

/* ── status bar ──────────────────────────────────────────────── */
.status-bar{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin:2rem 0}
.status-chip{display:flex;align-items:center;gap:.5rem;padding:.55rem 1.1rem;background:var(--card);border:1px solid var(--border);border-radius:99px;font-size:.82rem}
.dot{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 8px var(--success);animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

/* ── cards grid ──────────────────────────────────────────────── */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1.4rem;margin-top:2rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1.6rem;transition:transform .25s,box-shadow .25s;position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--accent),var(--hot));opacity:0;transition:opacity .3s}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
.card:hover::before{opacity:1}
.card h3{font-size:1.1rem;font-weight:700;margin-bottom:.6rem;display:flex;align-items:center;gap:.5rem}
.card p{color:var(--muted);font-size:.88rem}
.diff-badge{font-size:.7rem;padding:.2rem .55rem;border-radius:6px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.diff-easy{background:rgba(0,206,201,.15);color:var(--success)}
.diff-medium{background:rgba(253,203,110,.15);color:var(--warn)}
.diff-hard{background:rgba(253,121,168,.15);color:var(--hot)}

/* ── section titles ──────────────────────────────────────────── */
.section-title{font-size:1.3rem;font-weight:700;margin:2.5rem 0 .6rem;display:flex;align-items:center;gap:.5rem}
.section-title .icon{font-size:1.4rem}

/* ── API table ───────────────────────────────────────────────── */
.api-table{width:100%;border-collapse:collapse;margin-top:1rem;font-size:.88rem}
.api-table th{text-align:left;padding:.65rem .8rem;background:var(--surface);color:var(--muted);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em}
.api-table td{padding:.65rem .8rem;border-bottom:1px solid var(--border)}
.api-table tr:hover td{background:rgba(108,92,231,.06)}
.method{font-weight:700;font-family:'Courier New',monospace;font-size:.82rem;padding:.15rem .45rem;border-radius:4px}
.method.get{color:var(--success);background:rgba(0,206,201,.1)}
.method.post{color:var(--accent2);background:rgba(108,92,231,.1)}

/* ── interactive panel ───────────────────────────────────────── */
.panel{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1.6rem;margin-top:1.4rem}
.panel h3{font-size:1rem;font-weight:700;margin-bottom:1rem}
.btn-row{display:flex;gap:.7rem;flex-wrap:wrap;margin-bottom:1rem}
.btn{padding:.55rem 1.3rem;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);font-size:.85rem;font-weight:600;cursor:pointer;transition:all .2s}
.btn:hover{background:var(--accent);border-color:var(--accent);color:#fff;transform:translateY(-1px)}
.btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.pink{background:rgba(253,121,168,.15);border-color:var(--hot);color:var(--hot)}
.btn.pink:hover{background:var(--hot);color:#fff}
#output-box{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:1rem;min-height:160px;font-family:'Courier New',monospace;font-size:.82rem;color:var(--muted);white-space:pre-wrap;overflow-x:auto;transition:border-color .3s}
#output-box.active{border-color:var(--accent);color:var(--text)}

/* ── scoring section ─────────────────────────────────────────── */
.score-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem}
.score-card{text-align:center;padding:1.2rem;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius)}
.score-card .val{font-size:2rem;font-weight:800;background:linear-gradient(135deg,var(--accent2),var(--success));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.score-card .lbl{font-size:.78rem;color:var(--muted);margin-top:.3rem;text-transform:uppercase;letter-spacing:.04em}

/* ── approach section ────────────────────────────────────────── */
.approach-list{list-style:none;margin-top:1rem}
.approach-list li{position:relative;padding:.8rem 0 .8rem 2rem;border-bottom:1px solid var(--border);font-size:.9rem}
.approach-list li::before{content:'';position:absolute;left:0;top:50%;transform:translateY(-50%);width:10px;height:10px;border-radius:50%;background:var(--accent)}
.approach-list li:nth-child(2)::before{background:var(--success)}
.approach-list li:nth-child(3)::before{background:var(--hot)}

/* ── footer ──────────────────────────────────────────────────── */
footer{text-align:center;margin-top:3rem;padding:2rem 0;border-top:1px solid var(--border);color:var(--muted);font-size:.82rem}
footer strong{color:var(--text)}

/* ── responsive ──────────────────────────────────────────────── */
@media(max-width:640px){
  header h1{font-size:1.8rem}
  .grid{grid-template-columns:1fr}
  .score-grid{grid-template-columns:1fr}
  .wrap{padding:1rem}
}
</style>
</head>
<body>

<div class="bg-glow"><span></span><span></span><span></span></div>

<div class="wrap">

<!-- ── HEADER ────────────────────────────────────────────────── -->
<header>
  <h1>🎯 Technical Event Coordinator</h1>
  <p class="tagline">AI-powered room assignment simulator for large-scale technical fests.
  Solve constraint-satisfaction puzzles across easy, medium, and hard tiers.</p>
  <div class="badge-row">
    <span class="badge">OpenEnv</span>
    <span class="badge green">v1.1.0</span>
    <span class="badge pink">Meta × Scaler Hackathon</span>
    <span class="badge">Docker</span>
  </div>
</header>

<!-- ── STATUS BAR ────────────────────────────────────────────── -->
<div class="status-bar">
  <div class="status-chip"><span class="dot"></span> Environment Running</div>
  <div class="status-chip">📡 Port 7860</div>
  <div class="status-chip">🧩 3 Tasks Available</div>
  <div class="status-chip">🏆 Team NULL BYTE</div>
</div>

<!-- ── TASK CARDS ─────────────────────────────────────────────── -->
<h2 class="section-title"><span class="icon">📋</span> Scenario Board</h2>
<div class="grid">
  <div class="card" id="card-easy">
    <h3><span class="diff-badge diff-easy">Easy</span> Room Assignment</h3>
    <p>Assign <strong>50 teams</strong> to <strong>10 rooms</strong> subject to seating capacity and power-outlet limits. The agent must cover all teams while respecting room constraints.</p>
  </div>
  <div class="card" id="card-medium">
    <h3><span class="diff-badge diff-medium">Medium</span> Schedule Conflict Resolution</h3>
    <p>Resolve a double-booked VIP judge conflict. <strong>20 teams</strong> across <strong>5 rooms</strong> with uniform capacity — balance is key.</p>
  </div>
  <div class="card" id="card-hard">
    <h3><span class="diff-badge diff-hard">Hard</span> Sponsor Pullout Crisis</h3>
    <p>A major sponsor withdrew. <strong>50 teams</strong> must fit into <strong>7 rooms</strong> with tight capacity (5 each). Heavy contention, maximum pressure.</p>
  </div>
</div>

<!-- ── INTERACTIVE PANEL ─────────────────────────────────────── -->
<h2 class="section-title"><span class="icon">🚀</span> Launch Evaluation</h2>
<div class="panel">
  <h3>Quick Actions</h3>
  <div class="btn-row">
    <button class="btn active" onclick="callEndpoint('/health','GET')">🩺 Health Check</button>
    <button class="btn" onclick="callEndpoint('/tasks','GET')">📋 List Tasks</button>
    <button class="btn" onclick="callEndpoint('/reset','POST',{task_id:'easy'})">🔄 Reset Easy</button>
    <button class="btn" onclick="callEndpoint('/reset','POST',{task_id:'medium'})">🔄 Reset Medium</button>
    <button class="btn" onclick="callEndpoint('/reset','POST',{task_id:'hard'})">🔄 Reset Hard</button>
    <button class="btn pink" onclick="runBaseline()">⚡ Run Baseline</button>
  </div>
  <div id="output-box">← Click a button to interact with the environment</div>
</div>

<!-- ── BASELINE SCORES ───────────────────────────────────────── -->
<h2 class="section-title"><span class="icon">📊</span> Baseline Scores</h2>
<div class="score-grid">
  <div class="score-card">
    <div class="val" id="score-easy">~0.75</div>
    <div class="lbl">Easy</div>
  </div>
  <div class="score-card">
    <div class="val" id="score-medium">~0.65</div>
    <div class="lbl">Medium</div>
  </div>
  <div class="score-card">
    <div class="val" id="score-hard">~0.45</div>
    <div class="lbl">Hard</div>
  </div>
</div>

<!-- ── API SURFACE ───────────────────────────────────────────── -->
<h2 class="section-title"><span class="icon">🔌</span> API Surface</h2>
<div class="panel" style="padding:0;overflow:hidden">
  <table class="api-table">
    <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th></tr></thead>
    <tbody>
      <tr><td><span class="method post">POST</span></td><td>/reset</td><td>Reset environment for a task. Accepts <code>{"task_id": "easy"}</code></td></tr>
      <tr><td><span class="method post">POST</span></td><td>/step</td><td>Submit team→room assignments, receive reward</td></tr>
      <tr><td><span class="method post">POST</span></td><td>/grade</td><td>Stateless grading — same schema as /step</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/tasks</td><td>List all available tasks with metadata</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/tasks/{id}</td><td>Get details for a single task</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/state/{id}</td><td>Current observation without stepping</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/health</td><td>Liveness check — returns <code>{"status": "ok"}</code></td></tr>
    </tbody>
  </table>
</div>

<!-- ── APPROACH ───────────────────────────────────────────────── -->
<h2 class="section-title"><span class="icon">🧠</span> Agent Approach</h2>
<div class="panel">
  <ul class="approach-list">
    <li><strong>LLM Planner</strong> — sends room and team constraints to GPT-4o-mini, asks for an optimal JSON mapping that satisfies capacity, outlets, and balance.</li>
    <li><strong>Greedy Bin-Packing Fallback</strong> — if the LLM call fails, teams are sorted by laptop count (descending) and packed into the room with the most remaining headroom.</li>
    <li><strong>Hybrid Safety Net</strong> — always produces a valid assignment even when the LLM returns malformed output, ensuring non-zero scores on every task.</li>
  </ul>
</div>

<!-- ── SCORING FORMULA ───────────────────────────────────────── -->
<h2 class="section-title"><span class="icon">⚙️</span> Scoring Formula</h2>
<div class="panel">
  <p style="color:var(--muted);font-size:.88rem;margin-bottom:.8rem">Every task yields a score in the open interval <strong>(0, 1)</strong> computed as:</p>
  <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:1rem;font-family:'Courier New',monospace;font-size:.85rem;color:var(--accent2)">
    score = coverage×0.6 + balance_bonus×0.15 − capacity_penalty − outlet_penalty
  </div>
  <p style="color:var(--muted);font-size:.82rem;margin-top:.6rem">Coverage = assigned/total teams · Balance rewards even distribution · Penalties for exceeding room capacity or outlets</p>
</div>

<!-- ── FOOTER ─────────────────────────────────────────────────── -->
<footer>
  <strong>NULL BYTE</strong> · Meta Hackathon × Scaler — OpenEnv Track<br />
  Built with FastAPI · Deployed on Hugging Face Spaces
</footer>

</div>

<script>
const out = document.getElementById('output-box');

async function callEndpoint(path, method, body) {
  out.className = '';
  out.textContent = '⏳ Loading...';
  try {
    const opts = { method };
    if (body) {
      opts.headers = {'Content-Type': 'application/json'};
      opts.body = JSON.stringify(body);
    }
    const r = await fetch(path, opts);
    const d = await r.json();
    out.className = 'active';
    out.textContent = JSON.stringify(d, null, 2);
  } catch (e) {
    out.className = 'active';
    out.textContent = '❌ Error: ' + e.message;
  }
}

async function runBaseline() {
  out.className = '';
  out.textContent = '⚡ Running baseline across all tasks...';
  const results = {};
  for (const tid of ['easy','medium','hard']) {
    try {
      let r = await fetch('/reset', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task_id:tid})});
      const obs = await r.json();
      const inner = obs.observation || obs;
      const rooms = inner.rooms || [];
      const teams = inner.teams || [];
      // simple round-robin assignment
      const mapping = {};
      const rids = rooms.map(r => r.id);
      teams.forEach((t,i) => { mapping[t.id] = rids[i % rids.length]; });
      r = await fetch('/step', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task_id:tid,assignments:mapping})});
      const res = await r.json();
      const reward = res.reward;
      const score = typeof reward === 'object' ? reward.score : reward;
      results[tid] = score;
      const el = document.getElementById('score-'+tid);
      if(el) el.textContent = parseFloat(score).toFixed(4);
    } catch(e) {
      results[tid] = 'error: '+e.message;
    }
  }
  out.className = 'active';
  out.textContent = '✅ Baseline Results:\n\n' + JSON.stringify(results, null, 2);
}
</script>
</body>
</html>"""
