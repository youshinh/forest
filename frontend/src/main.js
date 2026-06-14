// Forest-gram Frontend v2.0 — Boids Engine, Modal, Drawer, Touch Support

// ============================================================
// 1. 32-Color Forest-gram Woodworking Palette
// ============================================================
const FOREST_PALETTE = [
  "#1a0f05","#3a2211","#5c3a21","#785032","#966c4c","#b48a68","#d2aa8a","#ebd0b0",
  "#14381b","#1e5227","#286c35","#378a47","#4baa5d","#6cc87e","#92e2a2","#bcf2c8",
  "#d97706","#f59e0b","#fbbf24","#fcd34d","#fde68a","#fef3c7",
  "#ef4444","#f87171","#fca5a5","#fee2e2",
  "#06b6d4","#22d3ee","#67e8f9","#cffafe",
];

// ============================================================
// 2. Application State
// ============================================================
const state = {
  agents: [
    { id:"willow_v1", name:"willow", clade:"SOFTWOOD", level:4, smile:450, trust:98, x:200, y:150, vx:1, vy:1, precision:80, velocity:70, efficiency:90, harmony:60, resilience:80, tags:["Python","Calculator"], color:"#6cc87e", avatar:"🌲", experience:0 },
    { id:"maple_v3",  name:"maple",  clade:"HARDWOOD", level:5, smile:680, trust:95, x:400, y:300, vx:-1, vy:1.2, precision:85, velocity:75, efficiency:82, harmony:88, resilience:90, tags:["Wood-flooring","Maple-properties","DXF-generation"], color:"#f59e0b", avatar:"🍁", experience:0 },
    { id:"walnut_v1", name:"walnut", clade:"HARDWOOD", level:3, smile:320, trust:92, x:100, y:400, vx:1.5, vy:-0.5, precision:90, velocity:65, efficiency:85, harmony:75, resilience:70, tags:["3D-CAD-Geometry","CNC-GCode"], color:"#b48a68", avatar:"🌰", experience:0 },
    { id:"cherry_v2", name:"cherry", clade:"HARDWOOD", level:2, smile:180, trust:88, x:500, y:100, vx:-0.5, vy:-1.5, precision:70, velocity:85, efficiency:65, harmony:90, resilience:80, tags:["UI-UX","Next.js"], color:"#fca5a5", avatar:"🌸", experience:0 },
    { id:"pine_v1",   name:"pine",   clade:"SOFTWOOD", level:3, smile:250, trust:90, x:300, y:200, vx:0.8, vy:0.8, precision:75, velocity:75, efficiency:80, harmony:70, resilience:85, tags:["Device-Control","SQLite"], color:"#378a47", avatar:"🌲", experience:0 },
  ],
  tickets: [
    { id:"FG-01", title:"階段段鼻の湿度伸縮補正DXF作成", x:350, y:250, tags:["Wood-flooring","Maple-properties"], status:"OPEN", lockTimer:0, lockedBy:null },
    { id:"FG-02", title:"CNC用G-Code座標オフセット最適化", x:150, y:150, tags:["CNC-GCode"], status:"OPEN", lockTimer:0, lockedBy:null },
  ],
  weather: "NORMAL",
  camera: { x:0, y:0, zoom:1 },
  isDragging: false,
  dragStart: { x:0, y:0 },
  selectedAgent: null,
  raindrops: [],
};

// ============================================================
// 3. Boids Canvas Setup
// ============================================================
const canvas    = document.getElementById("boids-canvas");
const ctx       = canvas.getContext("2d");
const container = document.getElementById("canvas-container");

function resizeCanvas() {
  canvas.width  = container.clientWidth;
  canvas.height = container.clientHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

// Initialize raindrops
for (let i = 0; i < 60; i++) {
  state.raindrops.push({
    x: Math.random() * 1000,
    y: Math.random() * 800,
    len: Math.random() * 15 + 5,
    speed: Math.random() * 10 + 10,
  });
}

// ============================================================
// 4. Boids Logic
// ============================================================
function getDistance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function updateBoids() {
  const width  = canvas.width;
  const height = canvas.height;

  // Raindrops animation
  if (state.weather === "RAINY") {
    state.raindrops.forEach(drop => {
      drop.y += drop.speed;
      drop.x -= 2;
      if (drop.y > height) { drop.y = -20; drop.x = Math.random() * width; }
    });
  }

  // Ticket state machine
  state.tickets.forEach(ticket => {
    if (ticket.status === "OPEN") {
      state.agents.forEach(agent => {
        if (getDistance(agent, ticket) < 30) {
          ticket.status   = "IN_PROGRESS";
          ticket.lockedBy = agent.id;
          ticket.lockTimer = 180;
          agent.x = ticket.x;
          agent.y = ticket.y;
          agent.vx = 0;
          agent.vy = 0;
        }
      });
    } else if (ticket.status === "IN_PROGRESS") {
      ticket.lockTimer--;
      if (ticket.lockTimer <= 0) {
        ticket.status = "COMPLETED";
        const winner = state.agents.find(a => a.id === ticket.lockedBy);
        appendLog(ticket, winner);

        if (winner) {
          winner.smile += ticket.id === "FG-01" ? 250 : 180;
          winner.experience = (winner.experience || 0) + 40;
          if (winner.experience >= 100) {
            winner.experience = 0;
            winner.level++;
            triggerLevelUpFanfare(winner);
          }
        }
        state.tickets = state.tickets.filter(t => t.id !== ticket.id);
      }
    }
  });

  // Boids forces
  state.agents.forEach(agent => {
    const isWorking = state.tickets.some(t => t.status === "IN_PROGRESS" && t.lockedBy === agent.id);
    if (isWorking) return;

    let fx = 0, fy = 0;
    let sepX = 0, sepY = 0, sepCount = 0;
    let cohX = 0, cohY = 0, cohCount = 0;
    let alignX = 0, alignY = 0, alignCount = 0;

    state.agents.forEach(other => {
      if (other.id === agent.id) return;
      const dist = getDistance(agent, other);
      if (dist < 40) { sepX += agent.x - other.x; sepY += agent.y - other.y; sepCount++; }
      if (dist < 150) {
        cohX += other.x; cohY += other.y; cohCount++;
        alignX += other.vx; alignY += other.vy; alignCount++;
      }
    });

    if (sepCount > 0)   { fx += (sepX / sepCount) * 1.5;           fy += (sepY / sepCount) * 1.5; }
    if (cohCount > 0)   { fx += ((cohX / cohCount) - agent.x) * 0.02; fy += ((cohY / cohCount) - agent.y) * 0.02; }
    if (alignCount > 0) { fx += (alignX / alignCount) * 0.05;      fy += (alignY / alignCount) * 0.05; }

    // Ticket attraction
    state.tickets.forEach(ticket => {
      if (ticket.status !== "OPEN") return;
      const matchesTag = ticket.tags.some(t => agent.tags.includes(t));
      const w = matchesTag ? 0.35 : 0.1;
      fx += (ticket.x - agent.x) * w * 0.02;
      fy += (ticket.y - agent.y) * w * 0.02;
    });

    agent.vx += fx;
    agent.vy += fy;

    const speed = Math.hypot(agent.vx, agent.vy);
    if (speed > 3.5) { agent.vx = (agent.vx / speed) * 3.5; agent.vy = (agent.vy / speed) * 3.5; }

    agent.x += agent.vx;
    agent.y += agent.vy;

    if (agent.x < 0)      agent.x = width;
    if (agent.x > width)  agent.x = 0;
    if (agent.y < 0)      agent.y = height;
    if (agent.y > height) agent.y = 0;
  });
}

// ============================================================
// 5. Canvas Rendering
// ============================================================
function drawCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(state.camera.x, state.camera.y);
  ctx.scale(state.camera.zoom, state.camera.zoom);

  // Grid
  ctx.strokeStyle = "rgba(16,185,129,0.04)";
  ctx.lineWidth = 1;
  for (let x = -2000; x < 2000; x += 40) {
    ctx.beginPath(); ctx.moveTo(x, -2000); ctx.lineTo(x, 2000); ctx.stroke();
  }
  for (let y = -2000; y < 2000; y += 40) {
    ctx.beginPath(); ctx.moveTo(-2000, y); ctx.lineTo(2000, y); ctx.stroke();
  }

  // Rain
  if (state.weather === "RAINY") {
    ctx.strokeStyle = "rgba(34,211,238,0.2)";
    ctx.lineWidth = 1;
    state.raindrops.forEach(drop => {
      ctx.beginPath();
      ctx.moveTo(drop.x, drop.y);
      ctx.lineTo(drop.x - 2, drop.y + drop.len);
      ctx.stroke();
    });
  }

  // Tickets
  state.tickets.forEach(ticket => {
    const glow = ctx.createRadialGradient(ticket.x, ticket.y, 4, ticket.x, ticket.y, 36);
    glow.addColorStop(0, "rgba(6,182,212,0.28)");
    glow.addColorStop(1, "rgba(6,182,212,0)");
    ctx.fillStyle = glow;
    ctx.beginPath(); ctx.arc(ticket.x, ticket.y, 36, 0, Math.PI * 2); ctx.fill();

    ctx.strokeStyle = ticket.status === "OPEN" ? "#22d3ee" : "#4baa5d";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.arc(ticket.x, ticket.y, 16, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = ticket.status === "OPEN" ? "#22d3ee" : "#4baa5d";
    ctx.beginPath(); ctx.arc(ticket.x, ticket.y, 5, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = "rgba(235,208,176,0.9)";
    ctx.font = "bold 11px Outfit, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(ticket.id, ticket.x, ticket.y - 24);

    ctx.fillStyle = "rgba(155,185,165,0.7)";
    ctx.font = "9px Outfit, sans-serif";
    ctx.fillText(ticket.tags.join("/"), ticket.x, ticket.y + 28);
  });

  // Agents
  state.agents.forEach(agent => {
    if (state.selectedAgent && state.selectedAgent.id === agent.id) {
      ctx.strokeStyle = "#4baa5d";
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(agent.x, agent.y, 24, 0, Math.PI * 2); ctx.stroke();
    }

    ctx.fillStyle = `${agent.color}22`;
    ctx.beginPath(); ctx.arc(agent.x, agent.y, 16, 0, Math.PI * 2); ctx.fill();

    ctx.font = "16px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(agent.avatar, agent.x, agent.y);

    ctx.fillStyle = "rgba(235,208,176,0.85)";
    ctx.font = "bold 10px Outfit, sans-serif";
    ctx.textBaseline = "alphabetic";
    ctx.fillText(agent.name, agent.x, agent.y - 20);
  });

  ctx.restore();
}

// ============================================================
// 6. Camera: Mouse + Touch Pan/Zoom
// ============================================================
let dragStartPoint = { x:0, y:0 };
let lastTouchDist  = null;

// --- Mouse ---
canvas.addEventListener("mousedown", e => {
  const rect   = canvas.getBoundingClientRect();
  const clickX = (e.clientX - rect.left - state.camera.x) / state.camera.zoom;
  const clickY = (e.clientY - rect.top  - state.camera.y) / state.camera.zoom;

  let clicked = null;
  state.agents.forEach(a => { if (Math.hypot(a.x - clickX, a.y - clickY) < 22) clicked = a; });

  if (clicked) {
    state.selectedAgent = clicked;
    openBottomSheet(clicked);
  } else {
    state.isDragging = true;
    dragStartPoint = { x: e.clientX - state.camera.x, y: e.clientY - state.camera.y };
  }
});

canvas.addEventListener("mousemove", e => {
  if (!state.isDragging) return;
  state.camera.x = e.clientX - dragStartPoint.x;
  state.camera.y = e.clientY - dragStartPoint.y;
});

window.addEventListener("mouseup", () => { state.isDragging = false; });

canvas.addEventListener("wheel", e => {
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.1 : (1 / 1.1);
  state.camera.zoom = Math.min(3, Math.max(0.4, state.camera.zoom * factor));
}, { passive: false });

// --- Touch ---
canvas.addEventListener("touchstart", e => {
  e.preventDefault();
  if (e.touches.length === 1) {
    const t     = e.touches[0];
    const rect  = canvas.getBoundingClientRect();
    const tx    = (t.clientX - rect.left - state.camera.x) / state.camera.zoom;
    const ty    = (t.clientY - rect.top  - state.camera.y) / state.camera.zoom;

    let clicked = null;
    state.agents.forEach(a => { if (Math.hypot(a.x - tx, a.y - ty) < 26) clicked = a; });

    if (clicked) {
      state.selectedAgent = clicked;
      openBottomSheet(clicked);
    } else {
      state.isDragging = true;
      dragStartPoint = { x: t.clientX - state.camera.x, y: t.clientY - state.camera.y };
    }
  } else if (e.touches.length === 2) {
    state.isDragging = false;
    lastTouchDist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    );
  }
}, { passive: false });

canvas.addEventListener("touchmove", e => {
  e.preventDefault();
  if (e.touches.length === 1 && state.isDragging) {
    const t = e.touches[0];
    state.camera.x = t.clientX - dragStartPoint.x;
    state.camera.y = t.clientY - dragStartPoint.y;
  } else if (e.touches.length === 2 && lastTouchDist !== null) {
    const dist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    );
    const ratio = dist / lastTouchDist;
    state.camera.zoom = Math.min(3, Math.max(0.4, state.camera.zoom * ratio));
    lastTouchDist = dist;
  }
}, { passive: false });

canvas.addEventListener("touchend", () => {
  state.isDragging  = false;
  lastTouchDist     = null;
});

// ============================================================
// 7. Sidebar Drawer (Mobile)
// ============================================================
const sidebarPanel   = document.getElementById("sidebar-panel");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const btnMenuToggle  = document.getElementById("btn-menu-toggle");

function openSidebar() {
  sidebarPanel.classList.add("open");
  sidebarOverlay.style.display = "block";
  btnMenuToggle.setAttribute("aria-expanded", "true");
  document.body.style.overflow = "hidden";
}

function closeSidebar() {
  sidebarPanel.classList.remove("open");
  sidebarOverlay.style.display = "";
  btnMenuToggle.setAttribute("aria-expanded", "false");
  document.body.style.overflow = "";
}

btnMenuToggle.addEventListener("click", () => {
  sidebarPanel.classList.contains("open") ? closeSidebar() : openSidebar();
});

sidebarOverlay.addEventListener("click", closeSidebar);

// Close sidebar on escape
document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    closeSidebar();
    closeSandboxModal();
    closeBottomSheet();
  }
});

// ============================================================
// 8. Bottom Sheet — Agent Detail
// ============================================================
const bottomSheet = document.getElementById("bottom-sheet");

function openBottomSheet(agent) {
  document.getElementById("sheet-agent-name").textContent  = agent.name;
  document.getElementById("sheet-agent-level").textContent = `Level ${agent.level} · ${agent.clade}`;
  document.getElementById("sheet-avatar-slot").textContent = agent.avatar;

  const params = ["precision","velocity","efficiency","harmony","resilience"];
  params.forEach(p => {
    document.getElementById(`val-${p}`).textContent         = agent[p];
    document.getElementById(`bar-${p}`).style.width         = `${agent[p]}%`;
  });

  document.getElementById("sheet-agent-wallet").textContent = `${agent.smile} ☺`;
  document.getElementById("sheet-agent-trust").textContent  = `${agent.trust}%`;

  bottomSheet.classList.add("open");
}

function closeBottomSheet() {
  bottomSheet.classList.remove("open");
  state.selectedAgent = null;
}

document.getElementById("sheet-close-btn").addEventListener("click", closeBottomSheet);

// ============================================================
// 9. Climate Controls
// ============================================================
document.getElementById("btn-rain").addEventListener("click", () => {
  state.weather = "RAINY";
  const badge = document.getElementById("weather-status");
  const label = document.getElementById("weather-label");
  badge.classList.add("rainy");
  label.textContent = "慈雨バフ発令中";
});

document.getElementById("btn-pesticide").addEventListener("click", () => {
  // Subtle notification instead of alert
  const badge = document.getElementById("weather-status");
  const label = document.getElementById("weather-label");
  const orig  = label.textContent;
  badge.style.borderColor = "var(--accent-primary)";
  label.textContent = "虫食い駆除完了 ✓";
  setTimeout(() => {
    badge.style.borderColor = "";
    label.textContent = orig;
  }, 3000);
});

// ============================================================
// 10. Quest Ticket Injection
// ============================================================
document.getElementById("btn-add-ticket").addEventListener("click", () => {
  const title   = document.getElementById("ticket-title").value.trim();
  const tagsStr = document.getElementById("ticket-tags").value;
  if (!title) return;

  const tags = tagsStr.split(",").map(t => t.trim()).filter(Boolean);
  const newId = `FG-${String(state.tickets.length + 10).padStart(2,"0")}`;
  const ticket = {
    id: newId, title, tags, status:"OPEN", lockTimer:0, lockedBy:null,
    x: Math.random() * (canvas.width - 200) + 100,
    y: Math.random() * (canvas.height - 150) + 100,
  };
  state.tickets.push(ticket);

  // Close sidebar on mobile after submit
  if (window.innerWidth < 1024) closeSidebar();
});

// ============================================================
// 11. Live Logs Appender
// ============================================================
function appendLog(ticket, winner) {
  const container = document.getElementById("live-ticket-logs");

  // Remove placeholder
  const placeholder = container.querySelector(".log-placeholder");
  if (placeholder) placeholder.remove();

  const isFinancial = ticket.title.includes("資産を1000万");
  const codeContent = isFinancial
    ? `10年で1000万円増やす現実的戦略:\n1. 月利5.0%想定で「月6.5万円」積立投資。\n2. NISA(オール・カントリー80%, S&P500 20%)を軸に。\n3. 自己投資(年12万)で昇給・副業スキル獲得。\n4. 生活防衛資金(約150万)は現金で確保。`
    : `class ClearanceCalculator:\n    def __init__(self, delta_moisture=4.0):\n        self.expansion_factor = 0.0035\n        self.delta_moisture = delta_moisture\n    # ...`;

  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.innerHTML = `
    <span class="log-tag-success">[${ticket.id} DONE]</span>
    担当: <strong>${winner ? winner.name : "Unknown"}</strong><br>
    <span class="log-tag-info">要件:</span> ${ticket.title}<br>
    <span class="log-tag-warn">${isFinancial ? "[Financial Output]" : "[Code Output]"}:</span>
    <div class="log-code-block">${codeContent}</div>
  `;
  container.prepend(entry);
}

// ============================================================
// 12. Level Up Fanfare
// ============================================================
const fanfareOverlay = document.getElementById("fanfare-overlay");

function triggerLevelUpFanfare(agent) {
  document.getElementById("fanfare-agent-name").textContent   = agent.name;
  document.getElementById("fanfare-level-change").textContent = `Level ${agent.level - 1} ➡️ Level ${agent.level}`;
  document.getElementById("fanfare-avatar").textContent       = agent.avatar;
  fanfareOverlay.classList.add("open");
}

document.getElementById("fanfare-close-btn").addEventListener("click", () => {
  fanfareOverlay.classList.remove("open");
});

// ============================================================
// 13. Pixel Sandbox Modal
// ============================================================
const sandboxModal = document.getElementById("sandbox-modal");

function openSandboxModal() {
  sandboxModal.classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeSandboxModal() {
  sandboxModal.classList.remove("open");
  document.body.style.overflow = "";
}

document.getElementById("btn-open-sandbox").addEventListener("click", openSandboxModal);
document.getElementById("btn-close-sandbox").addEventListener("click", closeSandboxModal);
sandboxModal.addEventListener("click", e => {
  if (e.target === sandboxModal) closeSandboxModal();
});

// ============================================================
// 14. Pixelation Pipeline
// ============================================================
const canvasOriginal  = document.getElementById("canvas-original");
const canvasPixelated = document.getElementById("canvas-pixelated");
const ctxOrig         = canvasOriginal.getContext("2d");
const ctxPixel        = canvasPixelated.getContext("2d");

const uploadZone      = document.getElementById("upload-zone");
const fileInput       = document.getElementById("avatar-uploader");
const rangePixelSize  = document.getElementById("pixel-size");
const rangeChroma     = document.getElementById("chroma-threshold");

uploadZone.addEventListener("click", () => fileInput.click());
uploadZone.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") fileInput.click(); });
fileInput.addEventListener("change", handleFileSelect);

uploadZone.addEventListener("dragover", e => {
  e.preventDefault();
  uploadZone.style.borderColor = "var(--accent-primary)";
});
uploadZone.addEventListener("dragleave", () => {
  uploadZone.style.borderColor = "";
});
uploadZone.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.style.borderColor = "";
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    handleFileSelect();
  }
});

function handleFileSelect() {
  const file = fileInput.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    const img = new Image();
    img.onload = () => processSandboxImage(img);
    img.src = ev.target.result;
  };
  reader.readAsDataURL(file);
}

rangePixelSize.addEventListener("input", e => {
  document.getElementById("val-pixel-size").textContent = e.target.value;
  reRunPixelation();
});
rangeChroma.addEventListener("input", e => {
  document.getElementById("val-chroma-threshold").textContent = e.target.value;
  reRunPixelation();
});

let currentImageSource = null;

function processSandboxImage(img) {
  currentImageSource = img;
  reRunPixelation();
}

function reRunPixelation() {
  if (!currentImageSource) return;
  const w = canvasOriginal.width;
  const h = canvasOriginal.height;

  ctxOrig.clearRect(0, 0, w, h);
  ctxOrig.drawImage(currentImageSource, 0, 0, w, h);
  const imgData = ctxOrig.getImageData(0, 0, w, h);
  const data    = imgData.data;
  const threshold = parseInt(rangeChroma.value);

  for (let i = 0; i < data.length; i += 4) {
    const dist = Math.hypot(255 - data[i], 255 - data[i+1], 255 - data[i+2]);
    if (dist < threshold * 2.5) data[i+3] = 0;
  }
  ctxOrig.putImageData(imgData, 0, 0);

  const pixelSize = parseInt(rangePixelSize.value);
  ctxPixel.clearRect(0, 0, w, h);

  for (let y = 0; y < h; y += pixelSize) {
    for (let x = 0; x < w; x += pixelSize) {
      const idx = (y * w + x) * 4;
      if (data[idx+3] < 50) continue;

      let nearest = FOREST_PALETTE[0], minDist = Infinity;
      FOREST_PALETTE.forEach(color => {
        const cr = parseInt(color.slice(1,3), 16);
        const cg = parseInt(color.slice(3,5), 16);
        const cb = parseInt(color.slice(5,7), 16);
        const d  = Math.hypot(cr - data[idx], cg - data[idx+1], cb - data[idx+2]);
        if (d < minDist) { minDist = d; nearest = color; }
      });

      let isEdge = (x === 0 || x >= w - pixelSize || y === 0 || y >= h - pixelSize);
      if (!isEdge) {
        const ir = (y * w + (x + pixelSize)) * 4;
        const ib = ((y + pixelSize) * w + x)  * 4;
        if (data[ir+3] < 50 || data[ib+3] < 50) isEdge = true;
      }

      ctxPixel.fillStyle = isEdge ? "#1a0f05" : nearest;
      ctxPixel.fillRect(x, y, pixelSize, pixelSize);
    }
  }
}

// Preset shapes
document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", e => {
    document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
    e.currentTarget.classList.add("active");
    drawPresetShape(e.currentTarget.getAttribute("data-preset"));
  });
});

function drawPresetShape(preset) {
  const w = canvasOriginal.width;
  const h = canvasOriginal.height;
  ctxOrig.fillStyle = "#ffffff";
  ctxOrig.fillRect(0, 0, w, h);

  if (preset === "willow") {
    ctxOrig.fillStyle = "#3a2211";
    ctxOrig.fillRect(w*0.42, h*0.55, w*0.16, h*0.38);
    ctxOrig.fillStyle = "#1e5227";
    ctxOrig.beginPath();
    ctxOrig.arc(w*0.5, h*0.38, w*0.32, 0, Math.PI*2);
    ctxOrig.fill();
  } else if (preset === "maple") {
    ctxOrig.fillStyle = "#f59e0b";
    ctxOrig.beginPath();
    ctxOrig.moveTo(w*0.5, h*0.08);
    ctxOrig.lineTo(w*0.73, h*0.47);
    ctxOrig.lineTo(w*0.5, h*0.35);
    ctxOrig.lineTo(w*0.27, h*0.47);
    ctxOrig.closePath();
    ctxOrig.fill();
    ctxOrig.fillStyle = "#3a2211";
    ctxOrig.fillRect(w*0.48, h*0.35, w*0.04, h*0.25);
  } else if (preset === "oak") {
    ctxOrig.fillStyle = "#5c3a21";
    ctxOrig.fillRect(w*0.31, h*0.23, w*0.38, h*0.62);
    ctxOrig.fillStyle = "#785032";
    ctxOrig.fillRect(w*0.28, h*0.78, w*0.44, h*0.12);
  }

  const img = new Image();
  img.onload = () => processSandboxImage(img);
  img.src = canvasOriginal.toDataURL();
}

// Trigger default preset on open
document.querySelector('[data-preset="willow"]').click();

// ============================================================
// 15. Main Render Loop
// ============================================================
function renderLoop() {
  updateBoids();
  drawCanvas();
  requestAnimationFrame(renderLoop);
}
requestAnimationFrame(renderLoop);
