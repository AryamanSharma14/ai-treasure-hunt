# Neon Cyberpunk Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely restyle `web/index.html` with a Neon Cyberpunk theme featuring Orbitron font, cyan/magenta glows, glitch animations, and an animated background canvas (live BFS maze solver + neural network web).

**Architecture:** All changes are confined to `web/index.html`. The `<style>` block is replaced wholesale, the HTML structure gains a background `<canvas>` element and minor markup additions (corner brackets, class updates), and a small JS block is appended before `</script>` to drive the canvas. No game logic is modified.

**Tech Stack:** Vanilla HTML/CSS/JS, Google Fonts CDN (Orbitron + Rajdhani), HTML5 Canvas 2D API

---

## File Map

| File | Action | What changes |
|---|---|---|
| `web/index.html` | Modify | Fonts CDN, CSS variables, all CSS rules, HTML structure additions, canvas JS, `showScreen()` bgPaused, `buildResultsScreen()` winner-row class |

---

### Task 1: Font CDN + CSS Variables Foundation

**Files:**
- Modify: `web/index.html` lines 7–41 (head / :root block)

- [ ] **Step 1.1: Replace Google Fonts link**

Find and replace the existing fonts link tag:
```html
<!-- REMOVE THIS: -->
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- REPLACE WITH: -->
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">
```

- [ ] **Step 1.2: Replace CSS `:root` variables block**

Find the existing `:root { ... }` block and replace entirely with:
```css
:root {
  --bg: #020209;
  --wall: #0d0d1a;
  --open: #0a0a14;
  --panel-bg: #04040f;
  --bfs: #4A9EFF;
  --dfs: #FFB830;
  --astar: #50E3A4;
  --greedy: #FF6B6B;
  --cyan: #00ffff;
  --magenta: #ff00ff;
  --gold: #C9A227;
  --start-color: #50E3A4;
  --treasure-color: #FF4757;
  --text-primary: #e0e0ff;
  --text-secondary: #4a4a7a;
  --text-dim: #252545;
  --border: #0d0d28;
  --border-bright: #1a1a3a;
  --card-bg: #06060f;
  --success: #50E3A4;
  --failure: #FF6B6B;
  --font-display: 'Orbitron', 'Courier New', monospace;
  --font: 'Rajdhani', 'Segoe UI', Arial, sans-serif;
  --panel-w: 300px;
}
```

- [ ] **Step 1.3: Replace `html, body` rule**

```css
html, body {
  width: 100%; height: 100%;
  background: var(--bg);
  color: var(--text-primary);
  font-family: var(--font);
  overflow: hidden;
  user-select: none;
}
```

- [ ] **Step 1.4: Open browser and verify**

Open `web/index.html` in browser. Title screen should show Orbitron font with near-black background. If fonts haven't loaded yet, refresh after a moment.

- [ ] **Step 1.5: Commit**
```bash
git add web/index.html
git commit -m "style: switch fonts to Orbitron/Rajdhani, update CSS variables to neon cyberpunk palette"
```

---

### Task 2: Animated Background Canvas — HTML + JS

**Files:**
- Modify: `web/index.html` — add `<canvas>` before `<div id="app">`, add JS block before closing `</script>`

- [ ] **Step 2.1: Add canvas element to body**

Find `<div id="app">` (currently first element inside `<body>`) and insert the canvas before it:
```html
<canvas id="bg-canvas" style="position:fixed;inset:0;width:100vw;height:100vh;z-index:0;pointer-events:none;display:block;"></canvas>
<div id="app">
```

- [ ] **Step 2.2: Add background canvas JS**

Find the closing `</script>` tag (very last line of the script block, after `showScreen('title');`) and insert the following block BEFORE it:

```javascript
// ============================================================
// BACKGROUND CANVAS — Maze Solver (Layer 1) + Neural Net (Layer 2)
// ============================================================
(function() {
  const bgCanvas = document.getElementById('bg-canvas');
  const bgCtx = bgCanvas.getContext('2d');
  let bgPaused = false;
  let bgRafId = null;

  // Expose bgPaused setter for showScreen()
  window.setBgPaused = function(val) { bgPaused = val; };

  function resizeBg() {
    bgCanvas.width = window.innerWidth;
    bgCanvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resizeBg);
  resizeBg();

  // ── LAYER 1: BFS Maze Solver ──────────────────────────────
  const MR = 15, MC = 25;
  const AGENT_COLORS = ['#4A9EFF','#FFB830','#50E3A4','#FF6B6B'];
  const MAZE_WALLS = new Set();
  // Simple static walls for decorative maze
  const mw = (r,c) => MAZE_WALLS.add(r+','+c);
  for(let c=3;c<=8;c++){mw(3,c);mw(4,c);}
  for(let r=2;r<=7;r++) mw(r,10);
  for(let c=14;c<=19;c++){mw(7,c);mw(8,c);}
  for(let r=9;r<=13;r++) mw(r,6);
  for(let c=18;c<=22;c++) mw(3,c);
  for(let r=4;r<=9;r++) mw(r,19);
  for(let c=2;c<=6;c++) mw(12,c);
  for(let r=10;r<=13;r++) mw(r,22);

  const MAZE_START = [13,1], MAZE_GOAL = [1,23];
  let mazeColorIdx = 0;
  let mazeExplored = [], mazePath = [], mazePhase = 'searching';
  let mazeQueue = [[...MAZE_START]];
  let mazeVisited = new Set([MAZE_START[0]+','+MAZE_START[1]]);
  let mazeCameFrom = new Map();
  let mazePauseFrames = 0;

  function mazeNeighbors(r,c) {
    const n = [];
    for(const[dr,dc] of [[-1,0],[1,0],[0,-1],[0,1]]) {
      const nr=r+dr, nc=c+dc;
      if(nr>=0&&nr<MR&&nc>=0&&nc<MC&&!MAZE_WALLS.has(nr+','+nc)) n.push([nr,nc]);
    }
    return n;
  }

  function mazeReconstruct() {
    const path=[];let n=[...MAZE_GOAL];
    while(n){path.push(n);const k=n[0]+','+n[1];n=mazeCameFrom.get(k)||null;}
    return path;
  }

  function mazeReset() {
    mazeColorIdx = (mazeColorIdx+1) % AGENT_COLORS.length;
    mazeExplored=[]; mazePath=[]; mazePhase='searching';
    mazeQueue=[[...MAZE_START]];
    mazeVisited=new Set([MAZE_START[0]+','+MAZE_START[1]]);
    mazeCameFrom=new Map();
    mazePauseFrames=0;
  }

  function mazeStep() {
    if(mazePhase==='searching') {
      for(let i=0;i<4&&mazeQueue.length;i++) {
        const cur=mazeQueue.shift();
        const ck=cur[0]+','+cur[1];
        mazeExplored.push([...cur]);
        if(cur[0]===MAZE_GOAL[0]&&cur[1]===MAZE_GOAL[1]){
          mazePath=mazeReconstruct(); mazePhase='found'; return;
        }
        for(const nb of mazeNeighbors(cur[0],cur[1])) {
          const nk=nb[0]+','+nb[1];
          if(!mazeVisited.has(nk)){mazeVisited.add(nk);mazeCameFrom.set(nk,cur);mazeQueue.push([...nb]);}
        }
      }
      if(!mazeQueue.length) mazePhase='found';
    } else {
      mazePauseFrames++;
      if(mazePauseFrames>90) mazeReset();
    }
  }

  function drawMazeLayer(W, H) {
    const cw = W/MC, ch = H/MR;
    const col = AGENT_COLORS[mazeColorIdx];
    const rgb = col.match(/\w\w/g).map(x=>parseInt(x,16));
    // explored cells
    bgCtx.fillStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.12)`;
    for(const[r,c] of mazeExplored)
      bgCtx.fillRect(c*cw+0.5, r*ch+0.5, cw-1, ch-1);
    // path
    if(mazePath.length) {
      bgCtx.fillStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.35)`;
      for(const[r,c] of mazePath)
        bgCtx.fillRect(c*cw+1, r*ch+1, cw-2, ch-2);
    }
    // walls
    bgCtx.fillStyle = 'rgba(13,13,26,0.5)';
    for(let r=0;r<MR;r++) for(let c=0;c<MC;c++)
      if(MAZE_WALLS.has(r+','+c))
        bgCtx.fillRect(c*cw+0.5, r*ch+0.5, cw-1, ch-1);
  }

  // ── LAYER 2: Neural Network Web ───────────────────────────
  const NODE_COLORS = ['#4A9EFF','#FFB830','#50E3A4','#FF6B6B','#00ffff','#ff00ff'];
  const nodes = Array.from({length:28}, () => ({
    x: 40 + Math.random() * (window.innerWidth - 80),
    y: 20 + Math.random() * (window.innerHeight - 40),
    vx: (Math.random()-0.5)*0.35,
    vy: (Math.random()-0.5)*0.35,
    r: 1.5 + Math.random()*2,
    color: NODE_COLORS[Math.floor(Math.random()*NODE_COLORS.length)],
    phase: Math.random()*Math.PI*2
  }));

  // Active signals: {x1,y1,x2,y2,t,maxT,color}
  const signals = [];

  function updateNodes(W, H) {
    for(const n of nodes) {
      n.x+=n.vx; n.y+=n.vy;
      if(n.x<10||n.x>W-10) n.vx*=-1;
      if(n.y<10||n.y>H-10) n.vy*=-1;
      n.phase+=0.018;
    }
  }

  function drawNeuralLayer() {
    // Edges
    for(let i=0;i<nodes.length;i++) {
      for(let j=i+1;j<nodes.length;j++) {
        const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
        const d=Math.sqrt(dx*dx+dy*dy);
        if(d<75) {
          const a=(1-d/75)*0.28;
          bgCtx.strokeStyle=`rgba(0,200,255,${a})`;
          bgCtx.lineWidth=0.5;
          bgCtx.beginPath();
          bgCtx.moveTo(nodes[i].x,nodes[i].y);
          bgCtx.lineTo(nodes[j].x,nodes[j].y);
          bgCtx.stroke();
          // Spawn signal
          if(Math.random()<0.004) {
            signals.push({
              x1:nodes[i].x,y1:nodes[i].y,
              x2:nodes[j].x,y2:nodes[j].y,
              t:0,maxT:55,
              color:nodes[i].color
            });
          }
        }
      }
    }
    // Signals
    for(let i=signals.length-1;i>=0;i--) {
      const s=signals[i];
      s.t++;
      const p=s.t/s.maxT;
      const sx=s.x1+(s.x2-s.x1)*p, sy=s.y1+(s.y2-s.y1)*p;
      const rgb=s.color.match(/\w\w/g).map(x=>parseInt(x,16));
      bgCtx.shadowBlur=6; bgCtx.shadowColor=s.color;
      bgCtx.fillStyle=`rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.9)`;
      bgCtx.beginPath(); bgCtx.arc(sx,sy,2,0,Math.PI*2); bgCtx.fill();
      bgCtx.shadowBlur=0;
      if(s.t>=s.maxT) signals.splice(i,1);
    }
    // Nodes
    for(const n of nodes) {
      const pulse=0.35+0.65*Math.abs(Math.sin(n.phase));
      const rgb=n.color.match(/\w\w/g).map(x=>parseInt(x,16));
      bgCtx.shadowBlur=8*pulse; bgCtx.shadowColor=n.color;
      bgCtx.fillStyle=`rgba(${rgb[0]},${rgb[1]},${rgb[2]},${pulse*0.7})`;
      bgCtx.beginPath(); bgCtx.arc(n.x,n.y,n.r,0,Math.PI*2); bgCtx.fill();
      bgCtx.shadowBlur=0;
    }
  }

  // ── MAIN LOOP ─────────────────────────────────────────────
  function bgLoop() {
    bgRafId = requestAnimationFrame(bgLoop);
    if(bgPaused) return;

    const W=bgCanvas.width, H=bgCanvas.height;
    bgCtx.clearRect(0,0,W,H);

    // Layer 1: maze
    mazeStep();
    drawMazeLayer(W,H);

    // Layer 2: neural net
    updateNodes(W,H);
    drawNeuralLayer();

    // Scanline overlay
    bgCtx.fillStyle='rgba(0,0,0,0.18)';
    for(let y=0;y<H;y+=3) bgCtx.fillRect(0,y,W,1);
  }

  bgLoop();
})();
```

- [ ] **Step 2.3: Wire `bgPaused` into `showScreen()`**

Find the `showScreen` function (search for `function showScreen(name)`). Add one line at the very start of the function body:
```javascript
function showScreen(name){
  if(window.setBgPaused) window.setBgPaused(name === 'game');
  // Stop ATH if leaving game
  ...
```

- [ ] **Step 2.4: Verify canvas works**

Open `web/index.html`. The title screen background should show a dim animated grid with glowing cells and floating connected dots. If it's blank, check browser console for errors.

- [ ] **Step 2.5: Commit**
```bash
git add web/index.html
git commit -m "feat: add animated background canvas (BFS maze solver + neural network web)"
```

---

### Task 3: Global Layout + Screen Transparency

**Files:**
- Modify: `web/index.html` CSS block

- [ ] **Step 3.1: Update `#app` and screen base styles**

Replace existing `#app`, `#title-screen / #select-screen / #results-screen`, `#game-area`, `#maze-wrap`, `#maze` CSS rules with:

```css
#app { display: flex; flex-direction: column; width: 100vw; height: 100vh; position: relative; z-index: 1; }

#title-screen, #select-screen, #results-screen {
  position: absolute; inset: 0; z-index: 10;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(2,2,9,0.72);
}

/* Remove old ::after overlays — delete the rules for:
   #title-screen::after, #select-screen::after, #results-screen::after
   (they are no longer needed — canvas shows through the transparent panel bg) */

#game-area { display: flex; flex: 1; overflow: hidden; }
#maze-wrap {
  flex: 1; display: flex; align-items: center; justify-content: center; padding: 8px;
  background: rgba(2,2,9,0.95);
}
#maze { background: #020209; border-radius: 4px; box-shadow: 0 0 30px rgba(0,0,0,0.8), 0 0 1px rgba(0,255,255,0.1); }
```

- [ ] **Step 3.2: Verify transparency**

Open browser. Title screen background should now show the animated maze + nodes through the dark overlay. Text should be fully readable over the `rgba(2,2,9,0.72)` overlay.

- [ ] **Step 3.3: Commit**
```bash
git add web/index.html
git commit -m "style: make fullscreen panels transparent to show animated background"
```

---

### Task 4: Title Screen CSS + HTML

**Files:**
- Modify: `web/index.html` — title screen CSS rules + HTML structure

- [ ] **Step 4.1: Replace title screen CSS**

Remove all old `.title-*` CSS rules and add:

```css
/* ── TITLE SCREEN ────────────────────────── */
@keyframes glitchTitle {
  0%,82%,100% {
    text-shadow: 0 0 20px #00ffff, 0 0 40px rgba(0,200,255,0.4);
    transform: translate(0); clip-path: none; filter: none;
  }
  84% { transform: translate(-3px,0); text-shadow: -3px 0 #ff00ff, 3px 0 #00ffff; }
  86% { transform: translate(3px,-1px); clip-path: inset(20% 0 40% 0); }
  88% { transform: translate(0); clip-path: none; filter: hue-rotate(90deg); }
  90% { transform: translate(2px,0); text-shadow: 2px 0 #ff00ff; filter: none; }
  92% { transform: translate(0); }
}
@keyframes scanSweep {
  0% { top: -1%; }
  100% { top: 101%; }
}
@keyframes ctaPulse {
  0%,100% { opacity: 0.75; box-shadow: 0 0 0 0 rgba(0,255,255,0); }
  50% { opacity: 1; box-shadow: 0 0 20px 4px rgba(0,255,255,0.15); }
}
@keyframes barGlow {
  0%,100% { filter: brightness(1); opacity: 0.85; }
  50% { filter: brightness(1.4); opacity: 1; }
}

/* Scanline sweep — title screen only */
#title-screen::after {
  content: '';
  position: absolute; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, rgba(0,255,255,0.5), transparent);
  animation: scanSweep 4s linear infinite;
  pointer-events: none; z-index: 1;
}

/* HUD corner brackets (reused on select + results too) */
.corner {
  position: absolute; width: 32px; height: 32px;
  border-color: rgba(0,255,255,0.35); border-style: solid;
  pointer-events: none;
}
.corner.tl { top: 16px; left: 16px; border-width: 1px 0 0 1px; }
.corner.tr { top: 16px; right: 16px; border-width: 1px 1px 0 0; }
.corner.bl { bottom: 16px; left: 16px; border-width: 0 0 1px 1px; }
.corner.br { bottom: 16px; right: 16px; border-width: 0 1px 1px 0; }

.title-eyebrow {
  font-family: var(--font-display);
  font-size: 9px; font-weight: 700;
  letter-spacing: 0.45em; text-transform: uppercase;
  color: var(--cyan); opacity: 0.55;
  margin-bottom: 20px;
}
.title-main {
  font-family: var(--font-display);
  font-size: 52px; font-weight: 900;
  letter-spacing: 0.06em; line-height: 1.1;
  color: #fff;
  margin-bottom: 14px;
  animation: glitchTitle 3.5s steps(1) infinite;
  position: relative; z-index: 2;
  text-align: center;
}
.title-bar {
  display: flex; height: 2px; width: 320px;
  margin-bottom: 24px;
  overflow: hidden; gap: 3px;
  animation: barGlow 3s ease-in-out infinite;
}
.title-bar div { flex: 1; }
.title-sub {
  font-family: var(--font-display);
  font-size: 9px; font-weight: 700;
  color: rgba(0,255,255,0.5);
  letter-spacing: 0.22em; text-transform: uppercase;
  margin-bottom: 6px;
}
.title-course {
  font-size: 11px; color: var(--text-dim);
  margin-bottom: 48px;
  letter-spacing: 0.2em; font-family: var(--font-display);
}
.title-cta {
  font-family: var(--font-display);
  font-size: 12px; font-weight: 700;
  letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--cyan);
  cursor: pointer;
  padding: 14px 38px;
  border: 1px solid rgba(0,255,255,0.3);
  background: rgba(0,255,255,0.04);
  animation: ctaPulse 2.5s ease-in-out infinite;
  transition: all 0.15s;
  position: relative; z-index: 2;
}
.title-cta:hover {
  color: #fff; border-color: var(--cyan);
  background: rgba(0,255,255,0.1);
  animation: none;
  box-shadow: 0 0 24px rgba(0,255,255,0.25);
}
.title-minigame {
  margin-top: 20px;
  font-family: 'Courier New', monospace;
  font-size: 12px; color: rgba(0,255,100,0.4);
  cursor: pointer; letter-spacing: 0.06em;
  transition: color 0.15s, opacity 0.15s;
  position: relative; z-index: 2;
}
.title-minigame:hover { color: rgba(0,255,100,0.85); }
.title-hints {
  position: absolute; bottom: 24px; left: 24px;
  font-family: var(--font-display);
  font-size: 10px; color: var(--text-dim); line-height: 2.2;
  letter-spacing: 0.1em; text-transform: uppercase;
}
```

- [ ] **Step 4.2: Replace title screen HTML**

Find the `<!-- ===== AI TREASURE HUNT TITLE ===== -->` block and replace with:
```html
<!-- ===== AI TREASURE HUNT TITLE ===== -->
<div id="title-screen">
  <div class="corner tl"></div>
  <div class="corner tr"></div>
  <div class="corner bl"></div>
  <div class="corner br"></div>
  <div class="title-eyebrow">21CSC206T &mdash; Artificial Intelligence</div>
  <div class="title-main">AI TREASURE<br>HUNT</div>
  <div class="title-bar">
    <div style="background:var(--bfs)"></div>
    <div style="background:var(--dfs)"></div>
    <div style="background:var(--astar)"></div>
    <div style="background:var(--greedy)"></div>
  </div>
  <div class="title-sub">Comparative Analysis of Search Algorithms</div>
  <div class="title-course">BFS &nbsp;&bull;&nbsp; DFS &nbsp;&bull;&nbsp; A* &nbsp;&bull;&nbsp; GREEDY</div>
  <div class="title-cta" onclick="showScreen('select')">[ PRESS ENTER TO BEGIN ]</div>
  <div class="title-minigame" onclick="showScreen('pacman')">&gt; pacman_minigame.exe</div>
  <div class="title-hints">
    [Enter]&nbsp; Play &nbsp;&nbsp; [G]&nbsp; Mini Game &nbsp;&nbsp; [Esc]&nbsp; Quit
  </div>
</div>
```

- [ ] **Step 4.3: Verify title screen**

Open browser. Should see: stacked "AI TREASURE / HUNT" in Orbitron 900, 4-color agent bar, cyan CTA button pulsing, scanline sweeping, glitch firing every ~3s, corner brackets visible, animated background showing through.

- [ ] **Step 4.4: Commit**
```bash
git add web/index.html
git commit -m "style: neon cyberpunk title screen with glitch animation, scanline sweep, HUD brackets"
```

---

### Task 5: Stats Panel CSS

**Files:**
- Modify: `web/index.html` CSS — stats panel section

- [ ] **Step 5.1: Replace stats panel CSS**

Remove existing `#stats-panel`, `.panel-title`, `.agent-card`, `.agent-card::before`, agent color rules, `.stat-row`, `.stat-label`, `.stat-value` rules and replace with:

```css
/* ── STATS PANEL ────────────────────────── */
@keyframes cursorBlink {
  0%,100% { opacity: 1; }
  50% { opacity: 0; }
}
@keyframes winnerSweep {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
@keyframes barGlowPulse {
  0%,100% { filter: brightness(1); }
  50% { filter: brightness(1.6); }
}

#stats-panel {
  width: var(--panel-w);
  background: linear-gradient(180deg, #050510 0%, #020209 100%);
  border-left: 1px solid var(--border-bright);
  box-shadow: inset 0 1px 0 rgba(0,255,255,0.2);
  overflow-y: auto; padding: 16px 12px; flex-shrink: 0;
}
#stats-panel::-webkit-scrollbar { width: 3px; }
#stats-panel::-webkit-scrollbar-thumb { background: var(--border-bright); }

.panel-title {
  font-family: var(--font-display);
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--cyan); opacity: 0.8;
  margin-bottom: 12px; padding-bottom: 10px;
  border-bottom: 1px solid var(--border-bright);
}
.panel-title::after {
  content: '_';
  animation: cursorBlink 0.8s step-end infinite;
  margin-left: 2px;
}

.agent-card {
  background: var(--card-bg);
  border: 1px solid var(--border-bright);
  border-radius: 4px;
  margin-bottom: 7px; padding: 10px 10px 10px 16px;
  position: relative; overflow: hidden;
  transition: border-color 0.2s;
}
.agent-card::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
}
.agent-card[data-agent="bfs"]::before    { background: var(--bfs); }
.agent-card[data-agent="dfs"]::before    { background: var(--dfs); }
.agent-card[data-agent="astar"]::before  { background: var(--astar); }
.agent-card[data-agent="greedy"]::before { background: var(--greedy); }

/* Directional inner glow per agent */
.agent-card[data-agent="bfs"]    { box-shadow: inset 20px 0 30px -12px rgba(74,158,255,0.18); }
.agent-card[data-agent="dfs"]    { box-shadow: inset 20px 0 30px -12px rgba(255,184,48,0.18); }
.agent-card[data-agent="astar"]  { box-shadow: inset 20px 0 30px -12px rgba(80,227,164,0.18); }
.agent-card[data-agent="greedy"] { box-shadow: inset 20px 0 30px -12px rgba(255,107,107,0.18); }

.agent-card.inactive { opacity: 0.25; }
.agent-card.winner {
  border-color: var(--gold) !important;
  box-shadow: 0 0 14px rgba(201,162,39,0.25) !important;
  background-image: repeating-linear-gradient(
    90deg,
    transparent 0px, transparent 18px,
    rgba(201,162,39,0.07) 18px, rgba(201,162,39,0.07) 20px
  );
  background-size: 200% 100%;
  animation: winnerSweep 1.5s linear infinite;
}

.agent-name {
  font-family: var(--font-display);
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  margin-bottom: 6px;
}
.agent-card[data-agent="bfs"] .agent-name    { color: var(--bfs); }
.agent-card[data-agent="dfs"] .agent-name    { color: var(--dfs); }
.agent-card[data-agent="astar"] .agent-name  { color: var(--astar); }
.agent-card[data-agent="greedy"] .agent-name { color: var(--greedy); }

.stat-row { display:flex; justify-content:space-between; font-size:12px; line-height:1.75; }
.stat-label { color: var(--text-secondary); letter-spacing: 0.04em; }
.stat-value { color: var(--text-primary); font-weight: 600; }
```

- [ ] **Step 5.2: Verify stats panel**

Start a race and check the panel. Cards should have colored left bars, directional inner glows, blinking cursor after "LIVE INTEL", winner card should show gold sweep animation.

- [ ] **Step 5.3: Commit**
```bash
git add web/index.html
git commit -m "style: neon stats panel with glowing agent cards, blinking cursor, winner sweep"
```

---

### Task 6: Controls + Bottom Bar CSS

**Files:**
- Modify: `web/index.html` CSS — controls and bottom bar sections

- [ ] **Step 6.1: Replace controls + bottom bar CSS**

Remove existing `.controls-section`, `.speed-row`, `.speed-label`, `.btn`, `.btn-row`, `.btn-sm`, `#bottom-bar`, `.key-hint`, `.key-hint kbd` rules and add:

```css
/* ── CONTROLS ────────────────────────────── */
.controls-section {
  margin-top: 14px; padding-top: 12px;
  border-top: 1px solid var(--border-bright);
}
.speed-row {
  display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;
}
.speed-label {
  font-family: var(--font-display);
  font-size: 10px; color: var(--cyan);
  letter-spacing: 0.15em; opacity: 0.8;
}
.btn {
  padding: 7px 14px;
  background: transparent;
  border: 1px solid rgba(0,255,255,0.2);
  border-radius: 3px;
  color: rgba(0,255,255,0.6);
  font-size: 11px; cursor: pointer;
  font-family: var(--font-display);
  font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase;
  position: relative; overflow: hidden;
  transition: border-color 0.15s, color 0.15s, box-shadow 0.15s;
}
.btn::before {
  content:''; position:absolute; inset:0;
  background: rgba(0,255,255,0.08);
  transform: scaleX(0); transform-origin: left;
  transition: transform 0.2s;
}
.btn:hover {
  border-color: var(--cyan); color: #fff;
  box-shadow: 0 0 12px rgba(0,255,255,0.2);
}
.btn:hover::before { transform: scaleX(1); }
.btn-row { display:flex; gap:7px; flex-wrap:wrap; margin-top:8px; }
.btn-sm { padding: 5px 11px; font-size: 10px; }

/* ── BOTTOM BAR ──────────────────────────── */
#bottom-bar {
  height: 34px;
  background: #03030c;
  border-top: 1px solid rgba(0,255,255,0.12);
  display: flex; align-items: center; padding: 0 20px;
  font-size: 11px; color: var(--text-dim); gap: 18px; flex-shrink: 0;
}
.key-hint { color: var(--text-secondary); display:flex; align-items:center; gap:4px; }
.key-hint kbd {
  background: #0a0a1e;
  border: 1px solid rgba(0,255,255,0.18);
  border-bottom: 2px solid rgba(0,255,255,0.28);
  border-radius: 3px;
  padding: 1px 6px;
  font-family: 'Courier New', monospace;
  font-size: 10px; font-weight: 700;
  color: rgba(0,255,255,0.55);
}
```

- [ ] **Step 6.2: Update the panel title text in HTML**

Find `<div class="panel-title">Live Intelligence</div>` (or whatever it currently reads) and change to:
```html
<div class="panel-title">Live Intel</div>
```
(Shorter — looks cleaner with the blinking cursor appended by CSS.)

- [ ] **Step 6.3: Verify buttons**

Hover over Pause/Restart/New Map buttons. Should see left-to-right cyan fill sweep and box-shadow glow. Speed +/- buttons should also glow.

- [ ] **Step 6.4: Commit**
```bash
git add web/index.html
git commit -m "style: neon buttons with sweep-fill hover, cyberpunk bottom bar kbd keys"
```

---

### Task 7: Select Screen CSS + HTML

**Files:**
- Modify: `web/index.html` CSS + HTML select screen block

- [ ] **Step 7.1: Replace select screen CSS**

Remove existing `.select-title`, `.select-sub`, `.map-grid`, `.map-card`, `.map-card-name`, `.toggle-row`, `.toggle-btn`, `.select-start-btn` rules and add:

```css
/* ── SELECT SCREEN ───────────────────────── */
@keyframes cardSweep {
  0% { background-position: -100% 0; }
  100% { background-position: 200% 0; }
}
@keyframes btnGlitch {
  0%,100% { transform:translate(0); text-shadow:none; }
  30% { transform:translate(-2px,0); text-shadow:-2px 0 var(--magenta); }
  60% { transform:translate(2px,0); text-shadow:2px 0 var(--cyan); }
  90% { transform:translate(0); }
}

.select-title {
  font-family: var(--font-display);
  font-size: 18px; font-weight: 900;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: #fff; margin-bottom: 6px;
  text-shadow: 0 0 20px rgba(0,255,255,0.3);
}
.select-sub {
  font-family: var(--font-display);
  font-size: 9px; color: rgba(0,255,255,0.4);
  margin-bottom: 26px; letter-spacing: 0.2em; text-transform: uppercase;
}
.map-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:22px; }
.map-card {
  width: 280px;
  background: var(--card-bg);
  border: 1px solid var(--border-bright);
  border-radius: 0;
  padding: 12px; cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  position: relative;
}
/* Corner bracket decoration on map cards */
.map-card::before, .map-card::after {
  content: ''; position: absolute;
  width: 16px; height: 16px;
  border-color: rgba(0,255,255,0.2); border-style: solid;
  transition: border-color 0.15s;
}
.map-card::before { top: -1px; left: -1px; border-width: 1px 0 0 1px; }
.map-card::after  { bottom: -1px; right: -1px; border-width: 0 1px 1px 0; }
.map-card:hover { transform: translateY(-2px); border-color: rgba(0,255,255,0.4); }
.map-card:hover::before,
.map-card:hover::after { border-color: rgba(0,255,255,0.5); }
.map-card.selected {
  border-color: var(--cyan);
  box-shadow: 0 0 18px rgba(0,255,255,0.2);
  background-image: linear-gradient(90deg, transparent 0%, rgba(0,255,255,0.03) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: cardSweep 2s linear infinite;
}
.map-card.selected::before,
.map-card.selected::after { border-color: var(--cyan); }
.map-card-name {
  font-family: var(--font-display);
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.15em; text-transform: uppercase;
  margin-bottom: 10px; color: var(--cyan); opacity: 0.8;
}
.map-card canvas { width:100%; height:100px; border-radius:0; }

.toggle-row { display:flex; gap:10px; margin-bottom:22px; }
.toggle-btn {
  padding: 8px 20px;
  border-radius: 20px;
  border: 1px solid var(--border-bright);
  background: transparent;
  cursor: pointer;
  font-family: var(--font-display);
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  transition: all 0.15s; opacity: 0.4;
}
.toggle-btn.active {
  border-color: currentColor; opacity: 1;
  background: rgba(255,255,255,0.05);
  box-shadow: 0 0 10px currentColor;
  filter: brightness(1.2);
}

.select-start-btn {
  padding: 13px 44px;
  background: transparent;
  border: 1px solid rgba(0,255,255,0.4);
  color: var(--cyan);
  font-family: var(--font-display);
  font-size: 12px; font-weight: 700;
  letter-spacing: 0.25em; text-transform: uppercase;
  cursor: pointer;
  position: relative; overflow: hidden;
  transition: color 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.select-start-btn::before {
  content: '';
  position: absolute; inset: 0;
  background: rgba(0,255,255,0.1);
  transform: scaleX(0); transform-origin: left;
  transition: transform 0.2s;
}
.select-start-btn:hover {
  color: #fff; border-color: var(--cyan);
  box-shadow: 0 0 20px rgba(0,255,255,0.25);
  animation: btnGlitch 0.3s steps(1) 1;
}
.select-start-btn:hover::before { transform: scaleX(1); }
.select-start-btn span { position: relative; z-index: 1; }
```

- [ ] **Step 7.2: Update select screen HTML**

Find the `<!-- ===== SELECT SCREEN ===== -->` block and replace with:
```html
<!-- ===== SELECT SCREEN ===== -->
<div id="select-screen" style="display:none">
  <div class="corner tl"></div>
  <div class="corner tr"></div>
  <div class="corner bl"></div>
  <div class="corner br"></div>
  <div class="select-title">Select Map</div>
  <div class="select-sub">Choose terrain &mdash; deploy agents</div>
  <div class="map-grid" id="map-grid"></div>
  <div class="toggle-row" id="toggle-row"></div>
  <button class="select-start-btn" onclick="startGame()"><span>Start Race</span></button>
</div>
```

- [ ] **Step 7.3: Verify select screen**

Navigate to select screen (press Enter from title). Map cards should have corner brackets, selected card sweeps cyan, agent toggle buttons should have colored glow rings when active.

- [ ] **Step 7.4: Commit**
```bash
git add web/index.html
git commit -m "style: neon select screen with bracket-corner cards, glowing toggles, glitch start button"
```

---

### Task 8: Results Screen CSS + HTML + JS winner-row

**Files:**
- Modify: `web/index.html` CSS, HTML results block, `buildResultsScreen()` JS function

- [ ] **Step 8.1: Replace results CSS**

Remove existing `.results-title`, `.results-winner`, `.results-table`, `.results-btns`, `.results-btn` rules and add:

```css
/* ── RESULTS SCREEN ──────────────────────── */
.results-title {
  font-family: var(--font-display);
  font-size: 22px; font-weight: 900;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: #fff; margin-bottom: 14px;
  animation: glitchTitle 5s steps(1) infinite;
  text-shadow: 0 0 20px rgba(0,255,255,0.3);
}
.results-winner {
  font-family: var(--font-display);
  font-size: 12px; font-weight: 700;
  margin-bottom: 24px; color: var(--gold);
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 11px 28px;
  border: 1px solid rgba(201,162,39,0.3);
  background: rgba(201,162,39,0.05);
  text-align: center;
}
.results-table { border-collapse:collapse; margin-bottom:24px; font-size:13px; }
.results-table th {
  padding: 10px 16px; text-align:left;
  font-family: var(--font-display);
  color: rgba(0,255,255,0.5); font-weight: 700;
  border-bottom: 1px solid rgba(0,255,255,0.15);
  font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
}
.results-table td { padding: 10px 16px; border-bottom: 1px solid var(--border); }
.results-table tr.winner-row td {
  background: rgba(201,162,39,0.06);
  border-left: 3px solid var(--gold);
}
.results-table tr.winner-row td:not(:first-child) { border-left: none; }

.results-btns { display:flex; gap:12px; margin-top:20px; }
.results-btn {
  padding: 11px 26px;
  background: transparent;
  border: 1px solid var(--border-bright);
  color: var(--text-primary);
  font-family: var(--font-display);
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.15em; text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  position: relative; overflow: hidden;
}
.results-btn::before {
  content:''; position:absolute; inset:0;
  background: rgba(0,255,255,0.06);
  transform:scaleX(0); transform-origin:left; transition:transform 0.2s;
}
.results-btn:hover { border-color: rgba(0,255,255,0.4); color:#fff; }
.results-btn:hover::before { transform:scaleX(1); }
```

- [ ] **Step 8.2: Update results screen HTML**

Find `<!-- ===== RESULTS SCREEN ===== -->` block and replace:
```html
<!-- ===== RESULTS SCREEN ===== -->
<div id="results-screen" style="display:none">
  <div class="corner tl"></div>
  <div class="corner tr"></div>
  <div class="corner bl"></div>
  <div class="corner br"></div>
  <div class="results-title">Race Results</div>
  <div class="results-winner" id="results-winner"></div>
  <table class="results-table" id="results-table">
    <thead><tr><th>Agent</th><th>Explored</th><th>Path</th><th>Time</th><th>Status</th><th>Optimal?</th></tr></thead>
    <tbody id="results-body"></tbody>
  </table>
  <div class="results-btns">
    <button class="results-btn" onclick="restartRace()">Race Again</button>
    <button class="results-btn" onclick="showScreen('select')">New Map</button>
    <button class="results-btn" onclick="showScreen('title')">Menu</button>
  </div>
</div>
```

- [ ] **Step 8.3: Add winner-row class in `buildResultsScreen()`**

Find `buildResultsScreen()` function. Locate this line inside the `for(const a of agents)` loop:
```javascript
const tr=document.createElement('tr');
```
Add the following line immediately after:
```javascript
if(a.firstFound) tr.classList.add('winner-row');
```

- [ ] **Step 8.4: Verify results screen**

Complete a race and wait for auto-navigation or press Tab. Results should show glitching title, gold winner banner, gold-highlighted winner row, cyan table headers, neon buttons.

- [ ] **Step 8.5: Commit**
```bash
git add web/index.html
git commit -m "style: neon results screen with glitch title, gold winner row, cyberpunk table"
```

---

### Task 9: Final Polish Pass

**Files:**
- Modify: `web/index.html` CSS — any leftover plain styles

- [ ] **Step 9.1: Scan for any remaining old/plain styles**

Open browser and check all screens. Look for anything still plain:
- Check `#bottom-bar` key hints are styled (cyan kbd keys)
- Check the game area has solid background (maze should not bleed the canvas)
- Check Pacman screen is unchanged

- [ ] **Step 9.2: Verify canvas pauses during game**

Start a race. Open DevTools console and run `window.setBgPaused(false)` — the canvas should become visible behind the transparent maze area. Then `window.setBgPaused(true)` to re-pause. This confirms the mechanism works.

Actually, the game area has solid background so canvas doesn't matter — but verify no CPU waste: in DevTools Performance, start recording, run the game, stop. The bg canvas rAF callback should not appear in the call stack while `bgPaused=true`.

- [ ] **Step 9.3: Check keyboard navigation**

Verify:
- Title → Enter starts select screen ✓
- Select → Enter / Start Race begins game ✓
- Game → Esc returns to title ✓
- Game → Tab (when done) → Results ✓
- Results → Enter restarts ✓
- G key → Pacman screen ✓

- [ ] **Step 9.4: Final commit**
```bash
git add web/index.html
git commit -m "style: complete neon cyberpunk redesign — polish pass and verification"
```

---

## Summary

| Task | What it builds | Key files |
|---|---|---|
| 1 | Font + CSS variables foundation | `web/index.html` `:root` |
| 2 | Animated background canvas (maze + neural net) | `web/index.html` JS |
| 3 | Screen transparency + layout | `web/index.html` CSS |
| 4 | Title screen (glitch, scanline, HUD brackets) | `web/index.html` CSS + HTML |
| 5 | Stats panel (glow cards, cursor, winner sweep) | `web/index.html` CSS |
| 6 | Controls + bottom bar (neon buttons, kbd keys) | `web/index.html` CSS |
| 7 | Select screen (brackets, sweeps, toggles) | `web/index.html` CSS + HTML |
| 8 | Results screen + winner-row JS fix | `web/index.html` CSS + HTML + JS |
| 9 | Final polish + verification | verification only |
