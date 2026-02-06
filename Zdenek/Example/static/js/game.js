const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const GRID = 10;
const CELL = canvas.width / GRID;

// pevná cesta (souřadnice v gridu)
const path = [
  {x:0,y:5},{x:1,y:5},{x:2,y:5},{x:3,y:5},{x:4,y:5},
  {x:5,y:5},{x:6,y:5},{x:7,y:5},{x:8,y:5},{x:9,y:5}
];

// stav hry
let baseLives = 3;
let kills = 0;
let wavesReached = 0;
const TOTAL_WAVES = 5;

let enemies = [];
let towers = [];

let waveEnemiesToSpawn = 0;
let waveSpawnTimer = 0;
let gameOver = false;

function gridToPixel(gx, gy) {
  return { px: gx * CELL + CELL/2, py: gy * CELL + CELL/2 };
}

// ----------------- ENEMY -----------------
function spawnEnemy() {
  const start = gridToPixel(path[0].x, path[0].y);
  enemies.push({
    hp: 30,
    speed: 0.6,      // "rychlost" posunu po cestě
    pathIndex: 0,
    progress: 0.0,
    x: start.px,
    y: start.py
  });
}

function updateEnemies() {
  for (let i = enemies.length - 1; i >= 0; i--) {
    const e = enemies[i];

    // cíl = další bod na cestě
    const current = path[e.pathIndex];
    const next = path[e.pathIndex + 1];

    if (!next) {
      // došel do cíle => základna ztrácí život
      enemies.splice(i, 1);
      baseLives -= 1;
      continue;
    }

    e.progress += e.speed * 0.02; // krok (0.02 je jen “vyvážení”)

    if (e.progress >= 1) {
      e.pathIndex++;
      e.progress = 0;
    }

    // interpolace mezi current a next
    const a = gridToPixel(current.x, current.y);
    const b = gridToPixel(next.x, next.y);

    e.x = a.px + (b.px - a.px) * e.progress;
    e.y = a.py + (b.py - a.py) * e.progress;
  }
}

// ----------------- TOWER -----------------
function addTower(gx, gy) {
  // nesmí být na cestě
  if (path.some(p => p.x === gx && p.y === gy)) return;

  // nesmí být na jiné věži
  if (towers.some(t => t.gx === gx && t.gy === gy)) return;

  towers.push({
    gx, gy,
    range: 120,
    dmg: 10,
    cooldown: 0
  });
}

function updateTowers() {
  for (const t of towers) {
    if (t.cooldown > 0) t.cooldown--;

    const tp = gridToPixel(t.gx, t.gy);

    // najdi první enemy v dosahu
    let target = null;
    for (const e of enemies) {
      const dx = e.x - tp.px;
      const dy = e.y - tp.py;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist <= t.range) {
        target = e;
        break;
      }
    }

    if (target && t.cooldown === 0) {
      target.hp -= t.dmg;
      t.cooldown = 30; // cca půl sekundy dle fps

      if (target.hp <= 0) {
        // kill
        const idx = enemies.indexOf(target);
        if (idx !== -1) enemies.splice(idx, 1);
        kills++;
      }
    }
  }
}

// ----------------- WAVES -----------------
function startNextWave() {
  wavesReached++;
  waveEnemiesToSpawn = 5 + wavesReached; // jednoduché zvyšování
  waveSpawnTimer = 0;
}

function updateWaves() {
  if (gameOver) return;

  // start první vlny
  if (wavesReached === 0) {
    startNextWave();
  }

  // spawn vlny postupně
  if (waveEnemiesToSpawn > 0) {
    waveSpawnTimer++;
    if (waveSpawnTimer >= 40) {
      spawnEnemy();
      waveEnemiesToSpawn--;
      waveSpawnTimer = 0;
    }
  } else {
    // vlna skončila (už nic nespawnujeme)
    // čekáme, až se dočistí enemies
    if (enemies.length === 0) {
      if (wavesReached >= TOTAL_WAVES) {
        endGame("WIN");
      } else {
        startNextWave();
      }
    }
  }

  if (baseLives <= 0) {
    endGame("LOSE");
  }
}

// ----------------- RENDER -----------------
function drawGrid() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // grid čáry
  ctx.strokeStyle = "#ccc";
  for (let i = 0; i <= GRID; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL, 0);
    ctx.lineTo(i * CELL, canvas.height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i * CELL);
    ctx.lineTo(canvas.width, i * CELL);
    ctx.stroke();
  }

  // cesta
  ctx.fillStyle = "#ffe08a";
  for (const p of path) {
    ctx.fillRect(p.x * CELL, p.y * CELL, CELL, CELL);
  }

  // věže
  for (const t of towers) {
    ctx.fillStyle = "#4a90e2";
    ctx.fillRect(t.gx * CELL + 8, t.gy * CELL + 8, CELL - 16, CELL - 16);
  }

  // enemies
  for (const e of enemies) {
    ctx.fillStyle = "#e24a4a";
    ctx.beginPath();
    ctx.arc(e.x, e.y, 10, 0, Math.PI * 2);
    ctx.fill();

    // HP bar (jednoduché)
    ctx.fillStyle = "#000";
    ctx.fillRect(e.x - 12, e.y - 18, 24, 4);
    ctx.fillStyle = "#00aa00";
    const hpWidth = Math.max(0, (e.hp / 30) * 24);
    ctx.fillRect(e.x - 12, e.y - 18, hpWidth, 4);
  }

  // HUD
  ctx.fillStyle = "#000";
  ctx.font = "16px Arial";
  ctx.fillText(`Lives: ${baseLives}`, 10, 20);
  ctx.fillText(`Wave: ${wavesReached}/${TOTAL_WAVES}`, 10, 40);
  ctx.fillText(`Kills: ${kills}`, 10, 60);

  if (gameOver) {
    ctx.fillText("GAME OVER", 180, 250);
  }
}

// ----------------- END + API -----------------
async function sendMatchEnd(result) {
  const payload = {
    result: result,
    waves_reached: wavesReached,
    kills: kills
  };

  const res = await fetch("/api/match_end", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  document.getElementById("info").innerText =
    `Výsledek uložen: ${JSON.stringify(data)}`;
}

function endGame(result) {
  if (gameOver) return;
  gameOver = true;
  sendMatchEnd(result);
}

// ----------------- LOOP -----------------
function loop() {
  if (!gameOver) {
    updateWaves();
    updateEnemies();
    updateTowers();
  }
  drawGrid();
  requestAnimationFrame(loop);
}

// klik na mapu = postavit věž
canvas.addEventListener("click", (ev) => {
  if (gameOver) return;

  const rect = canvas.getBoundingClientRect();
  const x = ev.clientX - rect.left;
  const y = ev.clientY - rect.top;
  const gx = Math.floor(x / CELL);
  const gy = Math.floor(y / CELL);

  addTower(gx, gy);
});

loop();