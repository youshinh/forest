// Forest-gram Frontend Main Logic: Boids Engine & Pixelation Pipeline

// --- 1. 32-Color Forest-gram Classic Woodworking Palette ---
const FOREST_PALETTE = [
  "#1a0f05", "#3a2211", "#5c3a21", "#785032", "#966c4c", "#b48a68", "#d2aa8a", "#ebd0b0", // Browns (Trunk/Oak)
  "#14381b", "#1e5227", "#286c35", "#378a47", "#4baa5d", "#6cc87e", "#92e2a2", "#bcf2c8", // Greens (Leaves/Forest)
  "#d97706", "#f59e0b", "#fbbf24", "#fcd34d", "#fde68a", "#fef3c7", // Golds (Autumn/Maple)
  "#ef4444", "#f87171", "#fca5a5", "#fee2e2", // Reds (Infestation/Dieback)
  "#06b6d4", "#22d3ee", "#67e8f9", "#cffafe", // Cybers (Tailscale/Glow)
];

// --- 2. State & Data Structures ---
const state = {
  agents: [
    { id: "willow_v1", name: "willow", clade: "SOFTWOOD", level: 4, smile: 450, trust: 98, x: 200, y: 150, vx: 1, vy: 1, precision: 80, velocity: 70, efficiency: 90, harmony: 60, resilience: 80, tags: ["Python", "Calculator"], color: "#6cc87e", avatar: "🌲" },
    { id: "maple_v3", name: "maple", clade: "HARDWOOD", level: 5, smile: 680, trust: 95, x: 400, y: 300, vx: -1, vy: 1.2, precision: 85, velocity: 75, efficiency: 82, harmony: 88, resilience: 90, tags: ["Wood-flooring", "Maple-properties", "DXF-generation"], color: "#f59e0b", avatar: "🍁" },
    { id: "walnut_v1", name: "walnut", clade: "HARDWOOD", level: 3, smile: 320, trust: 92, x: 100, y: 400, vx: 1.5, vy: -0.5, precision: 90, velocity: 65, efficiency: 85, harmony: 75, resilience: 70, tags: ["3D-CAD-Geometry", "CNC-GCode"], color: "#b48a68", avatar: "🌰" },
    { id: "cherry_v2", name: "cherry", clade: "HARDWOOD", level: 2, smile: 180, trust: 88, x: 500, y: 100, vx: -0.5, vy: -1.5, precision: 70, velocity: 85, efficiency: 65, harmony: 90, resilience: 80, tags: ["UI-UX", "Next.js"], color: "#fca5a5", avatar: "🌸" },
    { id: "pine_v1", name: "pine", clade: "SOFTWOOD", level: 3, smile: 250, trust: 90, x: 300, y: 200, vx: 0.8, vy: 0.8, precision: 75, velocity: 75, efficiency: 80, harmony: 70, resilience: 85, tags: ["Device-Control", "SQLite"], color: "#378a47", avatar: "🌲" }
  ],
  tickets: [
    { id: "FG-01", title: "階段段鼻の湿度伸縮補正DXF作成", x: 350, y: 250, tags: ["Wood-flooring", "Maple-properties"], status: "OPEN", lockTimer: 0, lockedBy: null },
    { id: "FG-02", title: "CNC用G-Code座標オフセット最適化", x: 150, y: 150, tags: ["CNC-GCode"], status: "OPEN", lockTimer: 0, lockedBy: null }
  ],
  weather: "NORMAL", // NORMAL, RAINY
  camera: { x: 0, y: 0, zoom: 1 },
  isDragging: false,
  dragStart: { x: 0, y: 0 },
  selectedAgent: null,
  raindrops: []
};

// --- 3. Boids & Swarm Engine on HTML5 Canvas ---
const canvas = document.getElementById("boids-canvas");
const ctx = canvas.getContext("2d");
const container = document.getElementById("canvas-container");

function resizeCanvas() {
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

// Initialize raindrops for weather effect
for (let i = 0; i < 60; i++) {
  state.raindrops.push({
    x: Math.random() * 1000,
    y: Math.random() * 800,
    len: Math.random() * 15 + 5,
    speed: Math.random() * 10 + 10
  });
}

// Boids Math Helper Functions
function getDistance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function updateBoids() {
  const width = canvas.width;
  const height = canvas.height;
  
  // Update raindrops if rainy
  if (state.weather === "RAINY") {
    state.raindrops.forEach(drop => {
      drop.y += drop.speed;
      drop.x -= 2; // slightly wind-blown
      if (drop.y > height) {
        drop.y = -20;
        drop.x = Math.random() * width;
      }
    });
  }

  // Update tickets status (simulation of lock events)
  state.tickets.forEach(ticket => {
    if (ticket.status === "OPEN") {
      // Check if any agent is close enough to LOCK/CLAIM the ticket
      state.agents.forEach(agent => {
        const dist = getDistance(agent, ticket);
        if (dist < 30) {
          // CAS Lock Succeeded Simulation!
          ticket.status = "IN_PROGRESS";
          ticket.lockedBy = agent.id;
          ticket.lockTimer = 180; // 3 seconds simulation lock
          
          // "シュタッ！" jump arc trigger
          agent.x = ticket.x;
          agent.y = ticket.y;
          agent.vx = 0;
          agent.vy = 0;
          
          console.log(`[+] CAS Lock Succeeded: Agent ${agent.name} claimed ticket ${ticket.id}`);
        }
      });
    } else if (ticket.status === "IN_PROGRESS") {
      ticket.lockTimer--;
      if (ticket.lockTimer <= 0) {
        // Complete ticket simulation
        ticket.status = "OPEN";
        const winner = state.agents.find(a => a.id === ticket.lockedBy);
        if (winner) {
          winner.smile += ticket.id === "FG-01" ? 250 : 180;
          winner.experience += 40;
          
          // Trigger Level-up fanfare simulation if experience reaches 100
          if (winner.experience >= 100) {
            winner.experience = 0;
            winner.level++;
            triggerLevelUpFanfare(winner);
          }
        }
        
        // Randomly relocate the ticket to simulate new ticket ingestion
        ticket.x = Math.random() * (width - 200) + 100;
        ticket.y = Math.random() * (height - 150) + 100;
        ticket.status = "OPEN";
        ticket.lockedBy = null;
      }
    }
  });

  // Apply Boids Forces to Agents
  state.agents.forEach(agent => {
    // If agent is currently working on a ticket, hold its position
    const isWorking = state.tickets.some(t => t.status === "IN_PROGRESS" && t.lockedBy === agent.id);
    if (isWorking) return;

    let fx = 0, fy = 0;
    
    // 1. Separation force (avoid colliding with other agents)
    let sepX = 0, sepY = 0, sepCount = 0;
    // 2. Cohesion force (fly towards center of flock)
    let cohX = 0, cohY = 0, cohCount = 0;
    // 3. Alignment force (steer in the same direction as neighbors)
    let alignX = 0, alignY = 0, alignCount = 0;

    state.agents.forEach(other => {
      if (other.id === agent.id) return;
      const dist = getDistance(agent, other);
      
      if (dist < 40) { // Separation range
        sepX += agent.x - other.x;
        sepY += agent.y - other.y;
        sepCount++;
      }
      
      if (dist < 150) { // Cohesion & Alignment range
        cohX += other.x;
        cohY += other.y;
        cohCount++;
        
        alignX += other.vx;
        alignY += other.vy;
        alignCount++;
      }
    });

    if (sepCount > 0) {
      fx += (sepX / sepCount) * 1.5;
      fy += (sepY / sepCount) * 1.5;
    }
    
    if (cohCount > 0) {
      const targetCohX = (cohX / cohCount) - agent.x;
      const targetCohY = (cohY / cohCount) - agent.y;
      fx += targetCohX * 0.02;
      fy += targetCohY * 0.02;
    }
    
    if (alignCount > 0) {
      fx += (alignX / alignCount) * 0.05;
      fy += (alignY / alignCount) * 0.05;
    }

    // 4. Attraction force to OPEN tickets
    state.tickets.forEach(ticket => {
      if (ticket.status !== "OPEN") return;
      const dist = getDistance(agent, ticket);
      
      // Match tags check
      const matchesTag = ticket.tags.some(t => agent.tags.includes(t));
      
      // Weight is 3 times higher if tags match (specification 12.1.1)
      const w_attraction = matchesTag ? 0.35 : 0.1;
      
      fx += (ticket.x - agent.x) * w_attraction * 0.02;
      fy += (ticket.y - agent.y) * w_attraction * 0.02;
    });

    // Apply forces to velocity
    agent.vx += fx;
    agent.vy += fy;

    // Clamp speed limits
    const speed = Math.hypot(agent.vx, agent.vy);
    const maxSpeed = 3.5;
    if (speed > maxSpeed) {
      agent.vx = (agent.vx / speed) * maxSpeed;
      agent.vy = (agent.vy / speed) * maxSpeed;
    }

    // Update position
    agent.x += agent.vx;
    agent.y += agent.vy;

    // Wrap around boundaries
    if (agent.x < 0) agent.x = width;
    if (agent.x > width) agent.x = 0;
    if (agent.y < 0) agent.y = height;
    if (agent.y > height) agent.y = 0;
  });
}

function drawCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  ctx.save();
  // Apply Zoom & Pan Camera transforms
  ctx.translate(state.camera.x, state.camera.y);
  ctx.scale(state.camera.zoom, state.camera.zoom);

  // Draw Grid lines for mechanical/scientific blueprint feel
  ctx.strokeStyle = "rgba(16, 185, 129, 0.03)";
  ctx.lineWidth = 1;
  const gridSize = 40;
  for (let x = -2000; x < 2000; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, -2000);
    ctx.lineTo(x, 2000);
    ctx.stroke();
  }
  for (let y = -2000; y < 2000; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(-2000, y);
    ctx.lineTo(2000, y);
    ctx.stroke();
  }

  // Draw Rainy weather effect
  if (state.weather === "RAINY") {
    ctx.strokeStyle = "rgba(34, 211, 238, 0.2)";
    ctx.lineWidth = 1;
    state.raindrops.forEach(drop => {
      ctx.beginPath();
      ctx.moveTo(drop.x, drop.y);
      ctx.lineTo(drop.x - 2, drop.y + drop.len);
      ctx.stroke();
    });
  }

  // Draw Tickets
  state.tickets.forEach(ticket => {
    // Outer glow
    const radialGlow = ctx.createRadialGradient(ticket.x, ticket.y, 5, ticket.x, ticket.y, 35);
    radialGlow.addColorStop(0, "rgba(6, 182, 212, 0.3)");
    radialGlow.addColorStop(1, "rgba(6, 182, 212, 0)");
    ctx.fillStyle = radialGlow;
    ctx.beginPath();
    ctx.arc(ticket.x, ticket.y, 35, 0, Math.PI * 2);
    ctx.fill();

    // Ticket center ring
    ctx.strokeStyle = ticket.status === "OPEN" ? "var(--accent-glow)" : "var(--primary-glow)";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.arc(ticket.x, ticket.y, 16, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Ticket solid center dot
    ctx.fillStyle = ticket.status === "OPEN" ? "var(--accent-glow)" : "var(--primary-glow)";
    ctx.beginPath();
    ctx.arc(ticket.x, ticket.y, 5, 0, Math.PI * 2);
    ctx.fill();

    // Text details
    ctx.fillStyle = "var(--text-main)";
    ctx.font = "bold 11px Outfit";
    ctx.textAlign = "center";
    ctx.fillText(ticket.id, ticket.x, ticket.y - 25);
    
    ctx.fillStyle = "var(--text-muted)";
    ctx.font = "9px Inter";
    ctx.fillText(ticket.tags.join("/"), ticket.x, ticket.y + 28);
  });

  // Draw Boids Agents
  state.agents.forEach(agent => {
    // Selection outline circle
    if (state.selectedAgent && state.selectedAgent.id === agent.id) {
      ctx.strokeStyle = "var(--primary-glow)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(agent.x, agent.y, 22, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Outer palette circle glow
    ctx.fillStyle = `${agent.color}22`; // transparency
    ctx.beginPath();
    ctx.arc(agent.x, agent.y, 16, 0, Math.PI * 2);
    ctx.fill();

    // Agent core avatar (render tree emojis as placeholders for pixelated graphics)
    ctx.font = "16px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(agent.avatar, agent.x, agent.y);

    // Agent name and Level tag
    ctx.fillStyle = "var(--text-main)";
    ctx.font = "bold 10px Outfit";
    ctx.textAlign = "center";
    ctx.fillText(agent.name, agent.x, agent.y - 18);
  });

  ctx.restore();
}

// Interactive zoom & pan listeners
let dragStartPoint = { x: 0, y: 0 };
canvas.addEventListener("mousedown", (e) => {
  // Check if clicked an agent
  const rect = canvas.getBoundingClientRect();
  const clickX = (e.clientX - rect.left - state.camera.x) / state.camera.zoom;
  const clickY = (e.clientY - rect.top - state.camera.y) / state.camera.zoom;

  let clickedAgent = null;
  state.agents.forEach(agent => {
    if (Math.hypot(agent.x - clickX, agent.y - clickY) < 22) {
      clickedAgent = agent;
    }
  });

  if (clickedAgent) {
    state.selectedAgent = clickedAgent;
    openBottomSheet(clickedAgent);
  } else {
    state.isDragging = true;
    dragStartPoint = { x: e.clientX - state.camera.x, y: e.clientY - state.camera.y };
  }
});

canvas.addEventListener("mousemove", (e) => {
  if (state.isDragging) {
    state.camera.x = e.clientX - dragStartPoint.x;
    state.camera.y = e.clientY - dragStartPoint.y;
  }
});

window.addEventListener("mouseup", () => {
  state.isDragging = false;
});

canvas.addEventListener("wheel", (e) => {
  e.preventDefault();
  const zoomFactor = 1.1;
  if (e.deltaY < 0) {
    state.camera.zoom *= zoomFactor;
  } else {
    state.camera.zoom /= zoomFactor;
  }
  // Clamp zoom range
  state.camera.zoom = Math.min(3, Math.max(0.5, state.camera.zoom));
}, { passive: false });

// --- 4. Interactive Bottom Sheet UI ---
const bottomSheet = document.getElementById("bottom-sheet");
function openBottomSheet(agent) {
  document.getElementById("sheet-agent-name").textContent = agent.name;
  document.getElementById("sheet-agent-level").textContent = `Level ${agent.level} (${agent.clade})`;
  document.getElementById("sheet-avatar-slot").textContent = agent.avatar;
  
  // Set parameters value
  document.getElementById("val-precision").textContent = agent.precision;
  document.getElementById("bar-precision").style.width = `${agent.precision}%`;
  
  document.getElementById("val-velocity").textContent = agent.velocity;
  document.getElementById("bar-velocity").style.width = `${agent.velocity}%`;
  
  document.getElementById("val-efficiency").textContent = agent.efficiency;
  document.getElementById("bar-efficiency").style.width = `${agent.efficiency}%`;
  
  document.getElementById("val-harmony").textContent = agent.harmony;
  document.getElementById("bar-harmony").style.width = `${agent.harmony}%`;
  
  document.getElementById("val-resilience").textContent = agent.resilience;
  document.getElementById("bar-resilience").style.width = `${agent.resilience}%`;

  // Wallet and Trust
  document.getElementById("sheet-agent-wallet").textContent = `${agent.smile} ☺`;
  document.getElementById("sheet-agent-trust").textContent = `${agent.trust}%`;

  bottomSheet.classList.add("open");
}

document.getElementById("sheet-close-btn").addEventListener("click", () => {
  bottomSheet.classList.remove("open");
  state.selectedAgent = null;
});

// --- 5. Climate / 天候操作 Controls ---
document.getElementById("btn-rain").addEventListener("click", () => {
  state.weather = "RAINY";
  const badge = document.getElementById("weather-status");
  badge.textContent = "慈雨のバフ発令中";
  badge.classList.add("rainy");
  
  // Update wallet display mock deduction
  console.log("[-] Gardener spent 100☺ for Rain Buff.");
});

document.getElementById("btn-pesticide").addEventListener("click", () => {
  alert("🧪 散布完了！すべての樹木エージェントの虫食い（Infestation）バグが駆除されました。");
});

// Quest Ticket Injection
document.getElementById("btn-add-ticket").addEventListener("click", () => {
  const title = document.getElementById("ticket-title").value.trim ? document.getElementById("ticket-title").value.trim() : document.getElementById("ticket-title").value;
  const tagsStr = document.getElementById("ticket-tags").value;
  if (!title) return;

  const tags = tagsStr.split(",").map(t => t.trim());
  const newTicket = {
    id: `FG-${(state.tickets.length + 1).toString().padStart(2, '0')}`,
    title: title,
    x: Math.random() * (canvas.width - 200) + 100,
    y: Math.random() * (canvas.height - 150) + 100,
    tags: tags,
    status: "OPEN",
    lockTimer: 0,
    lockedBy: null
  };
  state.tickets.push(newTicket);
  console.log(`[+] Ingested custom ticket: ${title}`);
});

// --- 6. Level Up Fanfare Overlay ---
const fanfareOverlay = document.getElementById("fanfare-overlay");
function triggerLevelUpFanfare(agent) {
  document.getElementById("fanfare-agent-name").textContent = agent.name;
  document.getElementById("fanfare-level-change").textContent = `Level ${agent.level - 1} ➡️ Level ${agent.level}`;
  fanfareOverlay.classList.add("open");
}
document.getElementById("fanfare-close-btn").addEventListener("click", () => {
  fanfareOverlay.classList.remove("open");
});

// --- 7. Pixelation Pipeline (4-Step Image Convert Sandbox) ---
const canvasOriginal = document.getElementById("canvas-original");
const canvasPixelated = document.getElementById("canvas-pixelated");
const ctxOrig = canvasOriginal.getContext("2d");
const ctxPixel = canvasPixelated.getContext("2d");

const uploadZone = document.getElementById("upload-zone");
const fileInput = document.getElementById("avatar-uploader");
const rangePixelSize = document.getElementById("pixel-size");
const rangeChroma = document.getElementById("chroma-threshold");

uploadZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", handleFileSelect);

// Handle drag and drop image
uploadZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.style.borderColor = "var(--primary-glow)";
});
uploadZone.addEventListener("dragleave", () => {
  uploadZone.style.borderColor = "rgba(255, 255, 255, 0.15)";
});
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.style.borderColor = "rgba(255, 255, 255, 0.15)";
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    handleFileSelect();
  }
});

function handleFileSelect() {
  const file = fileInput.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(event) {
    const img = new Image();
    img.onload = function() {
      processSandboxImage(img);
    };
    img.src = event.target.result;
  };
  reader.readAsDataURL(file);
}

// Range input monitors
rangePixelSize.addEventListener("input", (e) => {
  document.getElementById("val-pixel-size").textContent = e.target.value;
  reRunPixelation();
});
rangeChroma.addEventListener("input", (e) => {
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

  // Step 1: Draw and apply white background transparent keying
  ctxOrig.clearRect(0, 0, w, h);
  ctxOrig.drawImage(currentImageSource, 0, 0, w, h);
  const imgData = ctxOrig.getImageData(0, 0, w, h);
  const data = imgData.data;

  const threshold = parseInt(rangeChroma.value);

  // Apply Chroma Keying (make white background transparent)
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i+1];
    const b = data[i+2];
    
    // Check Euclidean distance to pure white (#FFFFFF)
    const dist = Math.hypot(255 - r, 255 - g, 255 - b);
    if (dist < threshold * 2.5) {
      data[i+3] = 0; // Alpha = 0
    }
  }
  ctxOrig.putImageData(imgData, 0, 0);

  // Step 2 & 4: Downsample and Palette Quantization
  const pixelSize = parseInt(rangePixelSize.value);
  ctxPixel.clearRect(0, 0, w, h);
  
  for (let y = 0; y < h; y += pixelSize) {
    for (let x = 0; x < w; x += pixelSize) {
      // Find pixel colour at grid point
      const idx = (y * w + x) * 4;
      const r = data[idx];
      const g = data[idx+1];
      const b = data[idx+2];
      const a = data[idx+3];

      if (a < 50) continue; // skip transparent pixels

      // Map to 32-color woodworking palette (Euclidean distance minimization)
      let nearestColor = FOREST_PALETTE[0];
      let minDist = Infinity;
      
      FOREST_PALETTE.forEach(color => {
        // Hex to RGB
        const cr = parseInt(color.slice(1, 3), 16);
        const cg = parseInt(color.slice(3, 5), 16);
        const cb = parseInt(color.slice(5, 7), 16);
        
        const d = Math.hypot(cr - r, cg - g, cb - b);
        if (d < minDist) {
          minDist = d;
          nearestColor = color;
        }
      });

      // Step 3: Draw outline borders checks (deep warm brown #1a0f05)
      // Check if neighboring pixels are transparent
      let isEdge = false;
      if (x === 0 || x >= w - pixelSize || y === 0 || y >= h - pixelSize) {
        isEdge = true;
      } else {
        const idxRight = (y * w + (x + pixelSize)) * 4;
        const idxBottom = ((y + pixelSize) * w + x) * 4;
        if (data[idxRight + 3] < 50 || data[idxBottom + 3] < 50) {
          isEdge = true;
        }
      }

      ctxPixel.fillStyle = isEdge ? "#1a0f05" : nearestColor;
      ctxPixel.fillRect(x, y, pixelSize, pixelSize);
    }
  }
}

// Presets click handlers
document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", (e) => {
    document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
    e.target.classList.add("active");
    
    // Draw preset shapes as base image triggers
    const preset = e.target.getAttribute("data-preset");
    drawPresetShape(preset);
  });
});

function drawPresetShape(preset) {
  // Programmatically draw a leaf/tree/trunk on original canvas, then process it
  ctxOrig.fillStyle = "#ffffff";
  ctxOrig.fillRect(0, 0, canvasOriginal.width, canvasOriginal.height);
  
  if (preset === "willow") {
    // Draw green willow tree shape
    ctxOrig.fillStyle = "#3a2211";
    ctxOrig.fillRect(54, 70, 20, 50); // Trunk
    
    ctxOrig.fillStyle = "#1e5227";
    ctxOrig.beginPath();
    ctxOrig.arc(64, 50, 40, 0, Math.PI * 2); // Foliage
    ctxOrig.fill();
  } else if (preset === "maple") {
    // Draw red/orange maple leaf shape
    ctxOrig.fillStyle = "#f59e0b";
    ctxOrig.beginPath();
    ctxOrig.moveTo(64, 10);
    ctxOrig.lineTo(94, 60);
    ctxOrig.lineTo(64, 45);
    ctxOrig.lineTo(34, 60);
    ctxOrig.closePath();
    ctxOrig.fill();
    
    ctxOrig.fillStyle = "#3a2211";
    ctxOrig.fillRect(62, 45, 4, 30); // Stem
  } else if (preset === "oak") {
    // Draw thick oak trunk shape
    ctxOrig.fillStyle = "#5c3a21";
    ctxOrig.fillRect(40, 30, 48, 80);
    
    ctxOrig.fillStyle = "#785032";
    ctxOrig.fillRect(36, 100, 56, 15);
  }

  // Treat current original canvas as image source
  const img = new Image();
  img.onload = function() {
    processSandboxImage(img);
  };
  img.src = canvasOriginal.toDataURL();
}

// Trigger initial preset
document.querySelector('[data-preset="willow"]').click();

// --- 8. Ecosystem Main Render Loop ---
function renderLoop() {
  updateBoids();
  drawCanvas();
  requestAnimationFrame(renderLoop);
}
requestAnimationFrame(renderLoop);
