const baseUrlEl = document.getElementById("baseUrl");
const userIdEl = document.getElementById("userId");
const sceneEl = document.getElementById("scene");
const sizeEl = document.getElementById("size");
const apiKeyEl = document.getElementById("apiKey");
const adminKeyEl = document.getElementById("adminKey");
const statusTextEl = document.getElementById("statusText");
const statusDot = document.querySelector(".status .dot");
const recoListEl = document.getElementById("recoList");
const metaEl = document.getElementById("meta");
const feedbackItemEl = document.getElementById("feedbackItem");
const feedbackResultEl = document.getElementById("feedbackResult");
const seedPreviewEl = document.getElementById("seedPreview");

const seedPayload = {
  items: [
    { userId: "u123", scene: "home", itemId: "p001", score: 0.98 },
    { userId: "u123", scene: "home", itemId: "p002", score: 0.95 },
    { userId: "u123", scene: "home", itemId: "p003", score: 0.93 },
  ],
};
seedPreviewEl.textContent = JSON.stringify(seedPayload, null, 2);

function buildHeaders(isAdmin = false) {
  const headers = { "Content-Type": "application/json" };
  const apiKey = apiKeyEl.value.trim();
  const adminKey = adminKeyEl.value.trim();

  if (apiKey) {
    headers["x-api-key"] = apiKey;
  }
  if (isAdmin && adminKey) {
    headers["x-admin-key"] = adminKey;
  }
  return headers;
}

async function request(path, options = {}) {
  const base = baseUrlEl.value.replace(/\/$/, "");
  const url = `${base}${path}`;
  const response = await fetch(url, options);
  const requestId = response.headers.get("x-request-id") || "n/a";
  let body = null;
  if (response.status !== 204) {
    try {
      body = await response.json();
    } catch (err) {
      body = await response.text();
    }
  }
  return { response, body, requestId };
}

async function checkHealth() {
  statusDot.style.background = "#f97316";
  statusTextEl.textContent = "Checking...";
  try {
    const api = await request("/api/health");
    const model = await request("/model/health");
    if (api.response.ok && model.response.ok) {
      statusDot.style.background = "#22c55e";
      statusTextEl.textContent = "API + Model OK";
    } else {
      statusDot.style.background = "#f97316";
      statusTextEl.textContent = `API ${api.response.status} / Model ${model.response.status}`;
    }
  } catch (err) {
    statusDot.style.background = "#ef4444";
    statusTextEl.textContent = "Unavailable";
  }
}

async function fetchRecommendations() {
  const userId = userIdEl.value.trim();
  const scene = sceneEl.value;
  const size = sizeEl.value || 5;
  if (!userId) return;

  recoListEl.innerHTML = "";
  metaEl.textContent = "Loading...";

  const { response, body, requestId } = await request(
    `/api/recommendations?userId=${encodeURIComponent(userId)}&scene=${encodeURIComponent(scene)}&size=${size}`,
    { headers: buildHeaders(false) }
  );

  if (!response.ok) {
    metaEl.textContent = `Error ${response.status} | requestId ${requestId}`;
    return;
  }

  const items = body.items || [];
  metaEl.textContent = `requestId ${body.requestId || requestId} | model ${body.modelVersion}`;
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "item";
    row.innerHTML = `
      <div>
        <div><strong>${item.itemId}</strong> <span class="badge">score ${item.score.toFixed(2)}</span></div>
        <div class="meta">rank ${item.rank}</div>
      </div>
      <button class="ghost" data-item="${item.itemId}">Click</button>
    `;
    row.querySelector("button").addEventListener("click", () => sendFeedback(item.itemId, "click"));
    recoListEl.appendChild(row);
  });
}

async function sendFeedback(itemIdOverride, eventOverride) {
  const userId = userIdEl.value.trim();
  const scene = sceneEl.value;
  const itemId = itemIdOverride || feedbackItemEl.value.trim();
  const eventType = eventOverride || document.getElementById("eventType").value;
  if (!userId || !itemId) return;

  const payload = {
    requestId: `req_${Date.now()}`,
    userId,
    itemId,
    eventType,
    scene,
    modelVersion: "v2026.01",
    ts: Date.now(),
  };

  const { response, requestId } = await request("/api/feedback", {
    method: "POST",
    headers: buildHeaders(false),
    body: JSON.stringify(payload),
  });

  feedbackResultEl.textContent = response.ok
    ? `Feedback accepted | requestId ${requestId}`
    : `Feedback failed ${response.status} | requestId ${requestId}`;
}

async function seedCandidates() {
  const { response, requestId, body } = await request("/api/admin/candidates", {
    method: "POST",
    headers: buildHeaders(true),
    body: JSON.stringify(seedPayload),
  });

  feedbackResultEl.textContent = response.ok
    ? `Seeded candidates | requestId ${requestId}`
    : `Seed failed ${response.status} | requestId ${requestId} | ${JSON.stringify(body)}`;
}


document.getElementById("checkHealth").addEventListener("click", checkHealth);
document.getElementById("fetchRecs").addEventListener("click", fetchRecommendations);
document.getElementById("sendFeedback").addEventListener("click", () => sendFeedback());
document.getElementById("seedCandidates").addEventListener("click", seedCandidates);

checkHealth();
