# AI Treasure Hunt — Neon Cyberpunk Redesign Spec
**Date:** 2026-03-25
**Scope:** Complete visual overhaul of `web/index.html` — CSS, HTML structure, animated backgrounds. All JavaScript game logic is preserved unchanged.

---

## Overview

Replace the current plain dark theme with a full Neon Cyberpunk aesthetic featuring animated backgrounds (live maze solver + neural network overlay), glitch effects, scanlines, and chromatic aberration throughout.

---

## Typography

| Role | Font | Weight | Characteristics |
|---|---|---|---|
| Title / labels / buttons | Orbitron | 700, 900 | Geometric, futuristic, all-caps |
| Stats / body | Rajdhani | 400, 600 | Clean, slightly military, readable |

**Google Fonts CDN change required:** Replace the existing `<link>` tag (which loads `Cinzel` + `Rajdhani`) with one that loads `Orbitron` + `Rajdhani`. Also update `--font-display` CSS variable from `'Cinzel', 'Palatino Linotype', serif` to `'Orbitron', 'Courier New', monospace`.

---

## Color Palette

These values replace the existing `--border` and `--border-bright` variables (intentional changes, not errors):

| Variable | Value | Usage |
|---|---|---|
| `--bg` | `#020209` | Page background (near-void black) |
| `--cyan` | `#00ffff` | Primary neon accent |
| `--magenta` | `#ff00ff` | Secondary glitch/aberration accent |
| `--gold` | `#C9A227` | Winner highlights only |
| `--border` | `#0d0d28` | Subtle borders (replaces `#18182e`) |
| `--border-bright` | `#1a1a3a` | Active borders (replaces `#262644`) |
| `--panel-bg` | `#04040f` | Stats panel background |
| `--card-bg` | `#06060f` | Agent card background |
| `--text-primary` | `#e0e0ff` | Body text |
| `--text-secondary` | `#4a4a7a` | Label text |
| Agent colors | unchanged | `#4A9EFF` `#FFB830` `#50E3A4` `#FF6B6B` |

---

## Animated Background Canvas

### Placement
`<canvas id="bg-canvas">` is placed as a **direct child of `<body>`**, NOT inside `#app`. This ensures `position:fixed` anchors to the viewport correctly.

```html
<body>
<canvas id="bg-canvas" style="position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;"></canvas>
<div id="app">...</div>
```

### Lifecycle
- The canvas `requestAnimationFrame` loop **pauses** when the game screen (`#game-area`) becomes visible
- It **resumes** when returning to title, select, or results screens
- Pause/resume is controlled by a boolean `bgPaused` toggled inside `showScreen()`
- During the game, CPU is not wasted on background animation

### Fullscreen Panel Backgrounds
All three fullscreen panels (`#title-screen`, `#select-screen`, `#results-screen`) get:
- `background: rgba(2,2,9,0.72)` — semi-transparent so canvas shows through
- Remove (do not reuse) any existing `::after` pseudo-element radial-gradient overlays on these screens — they are replaced by this approach

The `#game-area` and `#stats-panel` keep solid backgrounds.

### Layer 1 — Live Maze Solver (bottom layer)
- Renders a miniature `25×15` grid filling the canvas at ~12% opacity overall
- Uses **BFS only** for the decorative algorithm (simpler, reliable visual flood fill)
- Agent color cycles on each reset: BFS blue → DFS amber → A* mint → Greedy coral
- Wall blocks: `rgba(13,13,26,0.6)`, explored cells: agent color at 12% opacity, found path: agent color at 35% opacity
- On path found: 1s pause, then full reset with next agent color
- Dense scanline texture drawn last: every 2px row, `rgba(0,0,0,0.22)` fill

### Layer 2 — Neural Network Web (top layer)
- 28 floating nodes, slowly drifting (vx/vy ±0.4px/frame), bounce off edges
- Edges drawn between any two nodes within 75px — stroke opacity = `(1 - dist/75) * 0.3`
- Nodes pulse via a `phase` value (per-node, random start): opacity oscillates 0.3→0.9
- Signal dots: every frame, random edge has a 0.4% chance of spawning a signal dot that travels from node A to node B over 60 frames at full cyan brightness
- Node colors: `['#4A9EFF','#FFB830','#50E3A4','#FF6B6B','#00ffff','#ff00ff']` assigned at init
- Both layers composited in a single `requestAnimationFrame` loop (no separate setInterval)

---

## Title Screen

```
┌─ HUD brackets (corners) ────────────────────────────────┐
│                                                           │
│  [ 21CSC206T · ARTIFICIAL INTELLIGENCE ]  ← eyebrow tag │
│                                                           │
│     AI TREASURE                                           │
│          HUNT          ← Orbitron 900, glitch loop       │
│                                                           │
│  ══════════════════════  ← 4-color agent bar + glow      │
│                                                           │
│  COMPARATIVE ANALYSIS OF SEARCH ALGORITHMS               │
│  BFS  ·  DFS  ·  A*  ·  GREEDY BEST-FIRST               │
│                                                           │
│       [ PRESS ENTER TO BEGIN ]  ← pulsing CTA            │
│                                                           │
│    > pacman_minigame.exe  ← console-style mini link      │
│                                                           │
│  [Enter] PLAY   [G] MINIGAME   [Esc] QUIT ← bottom left  │
└────────────────────────────────────────────────────────── ┘
```

### Title Glitch Animation
- Loops every 3.5s with CSS `@keyframes glitchTitle`
- Keyframe structure (percentages of 3.5s):
  - `0%–82%`: stable — `text-shadow: 0 0 20px #00ffff, 0 0 40px rgba(0,200,255,0.4); transform: translate(0)`
  - `84%`: `transform: translate(-3px,0); text-shadow: -3px 0 #ff00ff, 3px 0 #00ffff`
  - `86%`: `transform: translate(3px,-1px); clip-path: inset(20% 0 40% 0)`
  - `88%`: `transform: translate(0); clip-path: none; filter: hue-rotate(90deg)`
  - `90%`: `transform: translate(2px,0); text-shadow: 2px 0 #ff00ff; filter: none`
  - `92%–100%`: back to stable

### Moving Scanline Sweep
- Implemented as a `::after` pseudo-element on `#title-screen` only (not all screens)
- `position: absolute; left:0; right:0; height:3px`
- `background: linear-gradient(90deg, transparent, rgba(0,255,255,0.5), transparent)`
- `animation: scanSweep 4s linear infinite`
- `@keyframes scanSweep { 0% { top: -1% } 100% { top: 101% } }`
- This keeps it scoped to only the title screen; select and results screens do NOT get the sweep

### HUD Corner Brackets
- 4 `<div class="corner tl/tr/bl/br">` elements inside `#title-screen`
- Each is `36×36px`, `position:absolute`, `border: 1px solid rgba(0,255,255,0.4)`
- Only 2 sides visible: `.tl { border-width: 1px 0 0 1px; top:18px; left:18px }`
- Same for select screen and results screen corners

---

## Stats Panel

```
[ LIVE INTEL ]_           ← Orbitron label with blinking cursor
──────────────────────────  ← cyan-glowing separator
```

- Panel top: `box-shadow: inset 0 1px 0 rgba(0,255,255,0.25)` (top inner glow line)
- `.panel-title` gets `::after { content: '_'; animation: cursorBlink 0.8s step-end infinite; }`
- `@keyframes cursorBlink { 0%,100%{opacity:1} 50%{opacity:0} }`
- Agent cards: full-height left bar (3px), directional inner glow `inset 20px 0 30px -10px <agent-color-rgba-0.15>`
- Winner card: `border-color: var(--gold)` + `box-shadow: 0 0 16px rgba(201,162,39,0.3)` + animated sweep:
  - `background-image: repeating-linear-gradient(90deg, transparent 0px, transparent 18px, rgba(201,162,39,0.08) 18px, rgba(201,162,39,0.08) 20px)`
  - `background-size: 200% 100%`
  - `animation: winnerSweep 1.5s linear infinite`
  - `@keyframes winnerSweep { 0%{background-position:200% 0} 100%{background-position:-200% 0} }`

---

## Controls & Buttons

All `.btn` elements:
- Default: `background: transparent; border: 1px solid rgba(0,255,255,0.2); color: rgba(0,255,255,0.6)`
- `::before`: `content:''; position:absolute; inset:0; background:rgba(0,255,255,0.08); transform:scaleX(0); transform-origin:left; transition:transform 0.2s`
- Hover: `border-color: #00ffff; color:#fff` and `::before { transform:scaleX(1) }` + `box-shadow: 0 0 12px rgba(0,255,255,0.2)`

---

## Bottom Bar

- Height: `36px`, background `#03030c`, `border-top: 1px solid rgba(0,255,255,0.15)`
- `kbd` keys: `background:#0a0a1e; border:1px solid rgba(0,255,255,0.2); border-bottom:2px solid rgba(0,255,255,0.3); border-radius:3px; font-family:'Courier New',monospace`

---

## Select Screen

- Map cards: remove `border-radius`, add corner bracket pseudo-elements (same as HUD brackets, scaled down to 20×20px)
- Selected: `border-color:#00ffff; box-shadow:0 0 20px rgba(0,255,255,0.2)`
- Selected card interior sweep:
  - `background-image: linear-gradient(90deg, transparent 0%, rgba(0,255,255,0.04) 50%, transparent 100%)`
  - `background-size: 200% 100%; animation: cardSweep 2s linear infinite`
  - `@keyframes cardSweep { 0%{background-position:-100% 0} 100%{background-position:200% 0} }`
- Agent toggle buttons: outlined pill (border-radius:20px), active = `background:rgba(0,255,255,0.12); border-color:currentColor; box-shadow:0 0 10px currentColor * 0.3`
- "START RACE" button: full-width, same hover sweep, on hover also applies `@keyframes btnGlitch` (1 glitch frame: translate(2px,0) + text-shadow shift)

---

## Results Screen

- `.results-title`: same `glitchTitle` keyframes, but `animation-duration:5s` (less frequent)
- Winner row: `<tr>` for winning agent gets a class `winner-row` dynamically via `buildResultsScreen()` — styled with `background: rgba(201,162,39,0.06); border-left:3px solid #C9A227`
  - Note: `buildResultsScreen()` in the JS already sets `style="color:${a.color}"` on agent name `<td>` but does NOT add a row class for the winner — the winner is identified by `a.firstFound === true`. Add class assignment: if `a.firstFound` then `tr.classList.add('winner-row')`
- Table headers: `font-family: Orbitron; font-size:10px; letter-spacing:0.2em; color:rgba(0,255,255,0.5); border-bottom: 1px solid rgba(0,255,255,0.2)`

---

## Animations Reference

| Name | Element | CSS property animated | Duration |
|---|---|---|---|
| `glitchTitle` | `.title-main` | transform, text-shadow, clip-path, filter | 3.5s loop |
| `scanSweep` | `#title-screen::after` | top (translateY via position) | 4s loop |
| `cardSweep` | `.map-card.selected` | background-position | 2s loop |
| `ctaPulse` | `.title-cta` | box-shadow, opacity | 2.5s loop |
| `cursorBlink` | `.panel-title::after` | opacity | 0.8s step-end |
| `winnerSweep` | `.agent-card.winner` | background-position | 1.5s loop |
| `btnGlitch` | `.select-start-btn:hover` | transform + text-shadow | 0.3s once |
| Button hover fill | All `.btn` | ::before scaleX 0→1 | 0.2s transition |
| Screen fade | All screens | opacity | 0.15s transition |
| BG maze loop | `#bg-canvas` JS | canvas draw per rAF frame | continuous |
| BG neural web | `#bg-canvas` JS | canvas draw per rAF frame | continuous |

---

## Implementation Notes

1. **Font CDN**: Replace existing `<link>` for Google Fonts with `Orbitron:wght@700,900` + `Rajdhani:wght@400,600`. Update `--font-display` variable to `'Orbitron', 'Courier New', monospace`.

2. **Canvas placement**: `<canvas id="bg-canvas">` goes as a direct child of `<body>`, before `<div id="app">`.

3. **Canvas lifecycle**: Add `bgPaused` boolean. In `showScreen()`, set `bgPaused = (name === 'game')`. The rAF loop checks `bgPaused` and skips drawing (but keeps the rAF scheduled so it unpauses cleanly).

4. **Existing `::after` overlays**: Remove the old radial-gradient overlay `::after` rules from `#title-screen`, `#select-screen`, and `#results-screen`. These are replaced by `background: rgba(2,2,9,0.72)` on the panels themselves. Note: the new `#title-screen::after` rule for `scanSweep` (see Moving Scanline Sweep section) is a fresh addition — it is not removed.

5. **Maze solver algorithm**: BFS only (queue-based). Color cycles per reset. No need to implement DFS/A*/Greedy variants for the decorative background.

6. **Winner row class**: In `buildResultsScreen()` JS function (line ~667), add `if(a.firstFound) tr.classList.add('winner-row')` so the CSS gold highlight applies.

7. **Canvas bleed-through on fade**: The `opacity: 0.15s` screen transition is intentional — the canvas will be visible during fade in/out, which adds to the neon atmosphere.

8. **All JS IDs and class names used by game logic are preserved exactly.**

---

## Out of Scope

- Pacman mini-game screen (styling kept as-is)
- Game logic, algorithms, rendering — untouched
- Any new files beyond `index.html`
