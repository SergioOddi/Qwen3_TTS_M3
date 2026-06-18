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
// Ogni voce clone espone anche le sue varianti emotive come opzioni separate
// (value "id|emozione"). Le voci design non hanno campioni → solo base.
const voiceOptions = () => voicesCache.flatMap((v) => [
  `<option value="${esc(v.id)}">${esc(v.id)} (${esc(v.type)})</option>`,
  ...(v.emotions || []).map((e) =>
    `<option value="${esc(v.id)}|${esc(e)}">${esc(v.id)} · ${esc(e)}</option>`),
]).join("");
const parseVoice = (val) => {
  const i = val.indexOf("|");
  return i < 0 ? { voice_id: val, emotion: null }
               : { voice_id: val.slice(0, i), emotion: val.slice(i + 1) };
};
async function loadVoices() {
  const r = await fetch("/api/voices");
  voicesCache = await r.json();
  voicesCache.sort((a, b) => a.id.localeCompare(b.id, "it", { sensitivity: "base" }));
  for (const sel of ["#g-voice", "#b-voice"]) $(sel).innerHTML = voiceOptions();
  $("#e-voice").innerHTML = voicesCache.filter((v) => v.type === "clone")
    .map((v) => `<option value="${esc(v.id)}">${esc(v.id)}${v.emotions.length ? " ["+v.emotions.join(",")+"]" : ""}</option>`).join("");
  $$("#t-blocks .t-voice").forEach((sel) => {
    const cur = sel.value; sel.innerHTML = voiceOptions(); sel.value = cur;
  });
  renderVoiceCards();
  updateGenPreview();
  if (!$("#t-blocks").children.length) addBlock();
}

function renderVoiceCards() {
  $("#v-list").innerHTML = voicesCache.map((v) => `
    <div class="card" data-id="${esc(v.id)}">
      <h3>${esc(v.id)}</h3>
      <div>${v.tags.map((t) => `<span class="badge">${esc(t)}</span>`).join("")}
           <span class="badge">${esc(v.type)}</span>
           ${(v.emotions || []).length ? `<span class="badge">😊 ${esc(v.emotions.join(", "))}</span>` : ""}</div>
      <div class="desc">${esc(v.description || "")}</div>
      ${v.type === "clone"
        ? `<audio controls src="/api/voices/${encodeURIComponent(v.id)}/sample"></audio>` : ""}
      <div class="card-actions">
        <button class="v-edit">✎ Modifica</button>
        <a class="v-export" href="/api/voices/${encodeURIComponent(v.id)}/export"
           download="${esc(v.id)}.voice.json">⬇ Esporta</a>
        <button class="v-del danger">🗑 Elimina</button>
      </div>
      <div class="v-editor hidden"></div>
    </div>`).join("");
  $$("#v-list .card").forEach(bindVoiceCard);
}

function bindVoiceCard(card) {
  const id = card.dataset.id;
  card.querySelector(".v-del").onclick = async () => {
    if (!confirm(`Eliminare la voce "${id}"? L'operazione è irreversibile.`)) return;
    const r = await fetch(`/api/voices/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!r.ok) { alert("Errore: " + (await r.text())); return; }
    await loadVoices();
  };
  card.querySelector(".v-edit").onclick = () => toggleEditor(card, id);
}

const LANGS = ["Italian", "English", "Spanish", "French", "German"];
async function toggleEditor(card, id) {
  const box = card.querySelector(".v-editor");
  if (!box.classList.contains("hidden")) { box.classList.add("hidden"); box.innerHTML = ""; return; }
  const cfg = await (await fetch(`/api/voices/${encodeURIComponent(id)}/config`)).json();
  box.innerHTML = `
    <label>Nome</label><input class="v-e-name" type="text" value="${esc(cfg.id)}">
    <label>Lingua</label>
    <select class="v-e-lang">${LANGS.map((l) =>
      `<option ${l === cfg.language ? "selected" : ""}>${l}</option>`).join("")}</select>
    <label>Tag (separati da virgola)</label>
    <input class="v-e-tags" type="text" value="${esc((cfg.tags || []).join(", "))}">
    <label>Descrizione</label>
    <textarea class="v-e-desc" rows="2">${esc(cfg.description || "")}</textarea>
    ${cfg.type === "clone"
      ? `<label>Trascrizione (ref_text)</label><textarea class="v-e-ref" rows="2">${esc(cfg.ref_text || "")}</textarea>` : ""}
    <label>Stile (instruct)</label><input class="v-e-instruct" type="text" value="${esc(cfg.instruct || "")}">
    <div class="row" style="margin-top:.5rem">
      <button class="v-e-save primary">Salva</button>
      <button class="v-e-cancel">Annulla</button>
    </div>
    <div class="status v-e-status"></div>`;
  box.classList.remove("hidden");
  box.querySelector(".v-e-cancel").onclick = () => { box.classList.add("hidden"); box.innerHTML = ""; };
  box.querySelector(".v-e-save").onclick = async () => {
    const body = {
      new_id: box.querySelector(".v-e-name").value.trim(),
      language: box.querySelector(".v-e-lang").value,
      tags: box.querySelector(".v-e-tags").value.split(",").map((t) => t.trim()).filter(Boolean),
      description: box.querySelector(".v-e-desc").value,
      instruct: box.querySelector(".v-e-instruct").value,
    };
    const ref = box.querySelector(".v-e-ref");
    if (ref) body.ref_text = ref.value;
    const r = await fetch(`/api/voices/${encodeURIComponent(id)}`, {
      method: "PATCH", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body) });
    if (!r.ok) { setStatus(box.querySelector(".v-e-status"), "Errore: " + (await r.text()), "err"); return; }
    await loadVoices();
  };
}

// Importa voce (bundle JSON da Esporta)
$("#v-import-btn").onclick = () => $("#v-import").click();
$("#v-import").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file, file.name);
  const r = await fetch("/api/voices/import", { method: "POST", body: fd });
  if (!r.ok) alert("Errore import: " + (await r.text()));
  else await loadVoices();
  e.target.value = "";
};

// Preview della voce selezionata nella scheda Genera (solo voci clone hanno campione)
function updateGenPreview() {
  const v = voicesCache.find((x) => x.id === parseVoice($("#g-voice").value).voice_id);
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
async function pollJob(jid) {
  while (true) {
    const job = await (await fetch(`/api/jobs/${jid}`)).json();
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
      ...parseVoice($("#g-voice").value),
      text, format: $("#g-format").value, biochem: $("#g-biochem").checked,
      speed: parseFloat($("#g-speed").value) }),
  });
  if (!r.ok) { setStatus("#g-status", "Errore: " + (await r.text()), "err"); return; }
  const { job_id } = await r.json();
  setStatus("#g-status", "Generazione in corso…", "");
  const job = await pollJob(job_id);
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
      items, ...parseVoice($("#b-voice").value),
      format: $("#b-format").value, biochem: $("#b-biochem").checked }),
  });
  const { job_id } = await r.json();
  setStatus("#b-status", "Batch in corso…", "");
  const job = await pollJob(job_id);
  if (job.status === "error") { setStatus("#b-status", "Errore: " + job.error, "err"); return; }
  $("#b-results").innerHTML = job.result.map((p) => {
    const f = p.split("/").pop();
    return `<li>${f} — <a href="/api/outputs/${f}" download>scarica</a></li>`;
  }).join("");
  setStatus("#b-status", "Batch completato ✓", "ok");
};

// --- Teatro ---
function addBlock(data = {}) {
  const tpl = $("#t-block-tpl").content.firstElementChild.cloneNode(true);
  tpl.querySelector(".t-voice").innerHTML = voiceOptions();
  if (data.voice_id)
    tpl.querySelector(".t-voice").value =
      data.emotion ? `${data.voice_id}|${data.emotion}` : data.voice_id;
  if (data.character != null) tpl.querySelector(".t-char").value = data.character;
  if (data.speed != null) tpl.querySelector(".t-speed").value = String(data.speed);
  if (data.instruct != null) tpl.querySelector(".t-instruct").value = data.instruct;
  if (data.pause_after != null) tpl.querySelector(".t-pause").value = data.pause_after;
  if (data.text != null) tpl.querySelector(".t-text").value = data.text;
  tpl.querySelector(".t-del").onclick = () => tpl.remove();
  tpl.querySelector(".t-dup").onclick = () => tpl.after(addBlock(readBlock(tpl)));
  tpl.querySelector(".t-up").onclick = () => tpl.previousElementSibling?.before(tpl);
  tpl.querySelector(".t-down").onclick = () => tpl.nextElementSibling?.after(tpl);
  tpl.querySelector(".t-regen").onclick = () => regenBlock(tpl);
  $("#t-blocks").appendChild(tpl);
  return tpl;
}

function readBlock(div) {
  const { voice_id, emotion } = parseVoice(div.querySelector(".t-voice").value);
  const clipEl = div.querySelector(".t-clip");
  const clip = clipEl && !clipEl.classList.contains("hidden") && clipEl.src
    ? clipEl.src.split("/").pop() : null;
  return {
    character: div.querySelector(".t-char").value.trim(),
    voice_id, emotion,
    speed: parseFloat(div.querySelector(".t-speed").value),
    instruct: div.querySelector(".t-instruct").value.trim(),
    pause_after: parseFloat(div.querySelector(".t-pause").value) || 0,
    text: div.querySelector(".t-text").value.trim(),
    clip,
  };
}

function blockToApi(b) {
  return { character: b.character, voice_id: b.voice_id, text: b.text, speed: b.speed,
           emotion: b.emotion, instruct: b.instruct || null, pause_after: b.pause_after,
           clip: b.clip || null };
}

$("#t-add").onclick = () => addBlock();

// Genera (o rigenera) il clip di un singolo blocco. Ritorna true se ok.
async function regenBlock(div) {
  const b = readBlock(div);
  if (!b.text) { setStatus("#t-status", "Battuta vuota", "err"); return false; }
  setStatus("#t-status", "Rigenero battuta…", "");
  const clip = div.querySelector(".t-clip");
  const prog = div.querySelector(".t-prog");
  clip.classList.add("hidden");
  prog.classList.remove("hidden");   // indeterminata: il TTS non espone un % reale
  const r = await fetch("/api/generate", {
    method: "POST", headers: { "Content-Type": "application/json" },
    // clip sempre wav: la scena lo riusa per lo stitch (sf.read non legge mp3)
    body: JSON.stringify({ text: b.text, voice_id: b.voice_id, format: "wav",
                           speed: b.speed, emotion: b.emotion,
                           instruct: b.instruct || null }),
  });
  if (!r.ok) { prog.classList.add("hidden"); setStatus("#t-status", "Errore: " + (await r.text()), "err"); return false; }
  const { job_id } = await r.json();
  const job = await pollJob(job_id);
  if (job.status === "error") { prog.classList.add("hidden"); setStatus("#t-status", "Errore: " + job.error, "err"); return false; }
  prog.classList.add("hidden");
  clip.src = "/api/outputs/" + job.result.split("/").pop();
  clip.classList.remove("hidden");
  setStatus("#t-status", "Battuta pronta ✓", "ok");
  return true;
}

// 🎬 All-in-one: genera ogni battuta da zero, poi unisce nella scena.
$("#t-genall").onclick = async () => {
  const divs = [...$$("#t-blocks .t-block")].filter((d) => readBlock(d).text);
  if (!divs.length) { setStatus("#t-status", "Nessuna battuta", "err"); return; }
  for (let i = 0; i < divs.length; i++) {
    setStatus("#t-status", `Genero battuta ${i + 1}/${divs.length}…`, "");
    if (!await regenBlock(divs[i])) return;   // stop al primo errore (status già impostato)
  }
  await stitchScene();
};

$("#t-run").onclick = stitchScene;

// Unisce nella scena SOLO i clip già generati per ogni battuta.
async function stitchScene() {
  const blocks = [...$$("#t-blocks .t-block")].map(readBlock).filter((b) => b.text);
  if (!blocks.length) { setStatus("#t-status", "Nessuna battuta", "err"); return; }
  const missing = blocks.filter((b) => !b.clip).length;
  if (missing) { setStatus("#t-status", `Genera prima le ${missing} battute mancanti (↻ Rigenera o 🎬 Genera scena completa)`, "err"); return; }
  setStatus("#t-status", "Unisco le battute…", "");
  $("#t-scene").classList.add("hidden"); $("#t-download").classList.add("hidden");
  const prog = $("#t-progress");
  prog.classList.remove("hidden");
  const r = await fetch("/api/teatro", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ blocks: blocks.map(blockToApi),
                           format: $("#t-format").value, title: $("#t-title").value || "scena" }),
  });
  if (!r.ok) { prog.classList.add("hidden"); setStatus("#t-status", "Errore: " + (await r.text()), "err"); return; }
  const { job_id } = await r.json();
  const job = await pollJob(job_id);
  if (job.status === "error") { prog.classList.add("hidden"); setStatus("#t-status", "Errore: " + job.error, "err"); return; }
  prog.classList.add("hidden");
  const name = job.result.scene.split("/").pop();   // scena.wav o scena.mp3
  const url = "/api/outputs/" + name;
  $("#t-scene-label").classList.remove("hidden");
  $("#t-scene").src = url; $("#t-scene").classList.remove("hidden");
  $("#t-download").href = url; $("#t-download").setAttribute("download", name);
  $("#t-download").classList.remove("hidden");
  // assegna i clip ai rispettivi blocchi (stesso ordine, esclusi i vuoti)
  const divs = [...$$("#t-blocks .t-block")].filter((d) => readBlock(d).text);
  job.result.clips.forEach((c, i) => {
    const clip = divs[i]?.querySelector(".t-clip");
    if (clip) { clip.src = "/api/outputs/" + c.path.split("/").pop(); clip.classList.remove("hidden"); }
  });
  setStatus("#t-status", "Scena pronta ✓", "ok");
};

// Export / import scena (impostazioni + testi, no audio)
$("#t-export").onclick = () => {
  const data = [...$$("#t-blocks .t-block")].map(readBlock);
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = ($("#t-title").value || "scena") + ".json";
  a.click();
};
$("#t-import-btn").onclick = () => $("#t-import").click();
$("#t-import").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const raw = await file.text();
  let data;
  try { data = JSON.parse(raw); }      // JSON esportato
  catch { data = parseScene(raw); }    // fallback: testo .txt/.md (campi o copione)
  if (!Array.isArray(data) || !data.length) {
    setStatus("#t-status", "File scena non valido", "err"); e.target.value = ""; return;
  }
  $("#t-blocks").innerHTML = "";
  data.forEach((b) => addBlock(b));
  const known = new Set(voicesCache.map((v) => v.id));
  const unknown = [...new Set(data.filter((b) => b.voice_id && !known.has(b.voice_id)).map((b) => b.voice_id))];
  const noChar = data.filter((b) => !b.character).length;
  const warn = [
    unknown.length && `voci sconosciute: ${unknown.join(", ")}`,
    noChar && `${noChar} battute senza Personaggio`,
  ].filter(Boolean).join(" — ");
  setStatus("#t-status", warn ? `Scena importata — ${warn}` : "Scena importata ✓", warn ? "err" : "ok");
  e.target.value = "";
};
// ponytail: persistenza via export/import file; niente DB/localStorage finché basta.

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

async function transcribeInto(blob, lang, filename, statusSel, reftextSel) {
  setStatus(statusSel, "Trascrizione in corso…", "");
  const fd = new FormData();
  fd.append("language", lang);
  fd.append("audio", blob, filename);
  const r = await fetch("/api/transcribe", { method: "POST", body: fd });
  if (!r.ok) { setStatus(statusSel, "Trascrizione non disponibile: " + (await r.text()), "err"); return; }
  $(reftextSel).value = (await r.json()).text;
  setStatus(statusSel, "Trascrizione pronta (correggi se serve) ✓", "ok");
}

$("#v-transcribe").onclick = () => {
  const blob = currentSampleBlob();
  if (!blob) { setStatus("#v-status", "Prima registra o carica un campione", "err"); return; }
  transcribeInto(blob, $("#v-language").value, "sample.webm", "#v-status", "#v-reftext");
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

// --- Variante emotiva (campione emotivo per voce esistente) ---
let eBlob = null;
$("#e-file").onchange = (e) => {
  eBlob = e.target.files[0] || null;
  if (eBlob) { $("#e-sample").src = URL.createObjectURL(eBlob); $("#e-sample").classList.remove("hidden"); }
};
$("#e-transcribe").onclick = () => {
  if (!eBlob) { setStatus("#e-status", "Carica prima un campione", "err"); return; }
  transcribeInto(eBlob, "Italian", eBlob.name || "sample.wav", "#e-status", "#e-reftext");
};
$("#e-save").onclick = async () => {
  if (!eBlob) { setStatus("#e-status", "Manca il campione audio", "err"); return; }
  if (!$("#e-reftext").value.trim()) { setStatus("#e-status", "Manca la trascrizione", "err"); return; }
  const fd = new FormData();
  fd.append("emotion", $("#e-emotion").value);
  fd.append("ref_text", $("#e-reftext").value);
  fd.append("audio", eBlob, eBlob.name || "sample.wav");
  const r = await fetch(`/api/voices/${encodeURIComponent($("#e-voice").value)}/emotion`,
    { method: "POST", body: fd });
  if (!r.ok) { setStatus("#e-status", "Errore: " + (await r.text()), "err"); return; }
  setStatus("#e-status", "Variante emotiva salvata ✓", "ok");
  await loadVoices();
};

function setStatus(sel, msg, kind) {
  const el = typeof sel === "string" ? $(sel) : sel;
  el.textContent = msg;
  el.className = "status" + (kind ? " " + kind : "");
}

loadVoices();
