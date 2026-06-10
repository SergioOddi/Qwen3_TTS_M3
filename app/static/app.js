const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// --- Tabs ---
$$(".tab").forEach((t) => t.onclick = () => {
  $$(".tab").forEach((x) => x.classList.remove("active"));
  $$(".panel").forEach((x) => x.classList.remove("active"));
  t.classList.add("active");
  $("#" + t.dataset.tab).classList.add("active");
});

// --- Caricamento voci ---
let voicesCache = [];
async function loadVoices() {
  const r = await fetch("/api/voices");
  voicesCache = await r.json();
  for (const sel of ["#g-voice", "#b-voice"]) {
    $(sel).innerHTML = voicesCache
      .map((v) => `<option value="${esc(v.id)}">${esc(v.id)} (${esc(v.type)})</option>`).join("");
  }
  renderVoiceCards();
  updateGenPreview();
}

function renderVoiceCards() {
  $("#v-list").innerHTML = voicesCache.map((v) => `
    <div class="card">
      <h3>${esc(v.id)}</h3>
      <div>${v.tags.map((t) => `<span class="badge">${esc(t)}</span>`).join("")}
           <span class="badge">${esc(v.type)}</span></div>
      <div class="desc">${esc(v.description || "")}</div>
      ${v.type === "clone"
        ? `<audio controls src="/api/voices/${encodeURIComponent(v.id)}/sample"></audio>` : ""}
    </div>`).join("");
}

// Preview della voce selezionata nella scheda Genera (solo voci clone hanno campione)
function updateGenPreview() {
  const v = voicesCache.find((x) => x.id === $("#g-voice").value);
  const prev = $("#g-preview");
  if (v && v.type === "clone") {
    prev.src = `/api/voices/${encodeURIComponent(v.id)}/sample`;
    prev.classList.remove("hidden");
  } else {
    prev.removeAttribute("src");
    prev.classList.add("hidden");
  }
}
$("#g-voice").onchange = updateGenPreview;

// --- Polling job ---
async function pollJob(jid, onProgress) {
  while (true) {
    const job = await (await fetch(`/api/jobs/${jid}`)).json();
    onProgress(job);
    if (job.status === "done" || job.status === "error") return job;
    await new Promise((r) => setTimeout(r, 400));
  }
}

// --- Genera ---
$("#g-run").onclick = async () => {
  const text = $("#g-text").value.trim();
  if (!text) { setStatus("#g-status", "Inserisci del testo", "err"); return; }
  setStatus("#g-status", "Invio…", "");
  $("#g-player").classList.add("hidden");
  $("#g-download").classList.add("hidden");
  const r = await fetch("/api/generate", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text, voice_id: $("#g-voice").value,
      format: $("#g-format").value, biochem: $("#g-biochem").checked,
      speed: parseFloat($("#g-speed").value) }),
  });
  if (!r.ok) { setStatus("#g-status", "Errore: " + (await r.text()), "err"); return; }
  const { job_id } = await r.json();
  const job = await pollJob(job_id, (j) =>
    setStatus("#g-status", `Generazione… ${Math.round(j.progress * 100)}%`, ""));
  if (job.status === "error") { setStatus("#g-status", "Errore: " + job.error, "err"); return; }
  const file = job.result.split("/").pop();
  const url = `/api/outputs/${file}`;
  $("#g-player").src = url; $("#g-player").classList.remove("hidden");
  $("#g-download").href = url; $("#g-download").classList.remove("hidden");
  setStatus("#g-status", "Completato ✓", "ok");
};

// --- Batch ---
function addBatchItem(name = "", text = "") {
  const div = document.createElement("div");
  div.className = "b-item";
  div.innerHTML = `<input placeholder="nome" value="${esc(name)}">
                   <textarea rows="2" placeholder="testo">${esc(text)}</textarea>`;
  $("#b-items").appendChild(div);
}
$("#b-add").onclick = () => addBatchItem();
addBatchItem();

$("#b-run").onclick = async () => {
  const items = [...$$("#b-items .b-item")].map((d, i) => ({
    name: d.querySelector("input").value.trim() || `item_${i + 1}`,
    text: d.querySelector("textarea").value.trim(),
  })).filter((it) => it.text);
  if (!items.length) { setStatus("#b-status", "Nessun testo", "err"); return; }
  const r = await fetch("/api/batch", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      items, voice_id: $("#b-voice").value,
      format: $("#b-format").value, biochem: $("#b-biochem").checked }),
  });
  const { job_id } = await r.json();
  const job = await pollJob(job_id, (j) =>
    setStatus("#b-status", `Batch… ${Math.round(j.progress * 100)}%`, ""));
  if (job.status === "error") { setStatus("#b-status", "Errore: " + job.error, "err"); return; }
  $("#b-results").innerHTML = job.result.map((p) => {
    const f = p.split("/").pop();
    return `<li>${f} — <a href="/api/outputs/${f}" download>scarica</a></li>`;
  }).join("");
  setStatus("#b-status", "Batch completato ✓", "ok");
};

// --- Registrazione microfono ---
let mediaRecorder, chunks = [], recBlob = null, recTimer, recSeconds = 0;
$("#v-rec").onclick = async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    $("#v-rec").textContent = "● Registra";
    clearInterval(recTimer);
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = () => {
    recBlob = new Blob(chunks, { type: "audio/webm" });
    $("#v-sample").src = URL.createObjectURL(recBlob);
    $("#v-sample").classList.remove("hidden");
    stream.getTracks().forEach((t) => t.stop());
  };
  mediaRecorder.start();
  $("#v-rec").textContent = "■ Stop";
  recSeconds = 0;
  recTimer = setInterval(() => {
    recSeconds++;
    const m = String(Math.floor(recSeconds / 60)).padStart(2, "0");
    const s = String(recSeconds % 60).padStart(2, "0");
    $("#v-rec-time").textContent = `${m}:${s}`;
  }, 1000);
};

$("#v-file").onchange = (e) => {
  if (e.target.files[0]) {
    recBlob = e.target.files[0];
    $("#v-sample").src = URL.createObjectURL(recBlob);
    $("#v-sample").classList.remove("hidden");
  }
};

function currentSampleBlob() {
  return recBlob;  // registrazione o file caricato
}

$("#v-transcribe").onclick = async () => {
  const blob = currentSampleBlob();
  if (!blob) { setStatus("#v-status", "Prima registra o carica un campione", "err"); return; }
  setStatus("#v-status", "Trascrizione in corso…", "");
  const fd = new FormData();
  fd.append("language", $("#v-language").value);
  fd.append("audio", blob, "sample.webm");
  const r = await fetch("/api/transcribe", { method: "POST", body: fd });
  if (!r.ok) { setStatus("#v-status", "Trascrizione non disponibile: " + (await r.text()), "err"); return; }
  $("#v-reftext").value = (await r.json()).text;
  setStatus("#v-status", "Trascrizione pronta (correggi se serve) ✓", "ok");
};

$("#v-save").onclick = async () => {
  const blob = currentSampleBlob();
  if (!blob) { setStatus("#v-status", "Manca il campione audio", "err"); return; }
  if (!$("#v-reftext").value.trim()) { setStatus("#v-status", "Manca la trascrizione", "err"); return; }
  if (!$("#v-name").value.trim()) { setStatus("#v-status", "Manca il nome", "err"); return; }
  const fd = new FormData();
  fd.append("name", $("#v-name").value);
  fd.append("language", $("#v-language").value);
  fd.append("ref_text", $("#v-reftext").value);
  fd.append("instruct", $("#v-instruct").value);
  fd.append("tags", $("#v-tags").value);
  fd.append("audio", blob, "sample.webm");
  const r = await fetch("/api/voices", { method: "POST", body: fd });
  if (!r.ok) { setStatus("#v-status", "Errore: " + (await r.text()), "err"); return; }
  setStatus("#v-status", "Voce salvata ✓", "ok");
  await loadVoices();
};

function setStatus(sel, msg, kind) {
  const el = $(sel);
  el.textContent = msg;
  el.className = "status" + (kind ? " " + kind : "");
}

loadVoices();
