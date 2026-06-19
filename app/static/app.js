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
// Teatro: solo voci clone, neutre (niente varianti emotive nel menu)
const cloneVoiceOptions = () => voicesCache.filter((v) => v.type === "clone")
  .map((v) => `<option value="${esc(v.id)}">${esc(v.id)}</option>`).join("");
// Teatro-Emozioni: voci design filtrate per sesso
const designVoicesByGender = (g) =>
  voicesCache.filter((v) => v.type === "design" && v.gender === g);
// ponytail: lista emozioni hardcoded (come la select "Variante emotiva" in index.html);
// l'unica fonte canonica è SELECTABLE_EMOTIONS in voices.py.
const EMOTIONS = ["felice", "triste", "arrabbiato", "impaurito",
                  "sorpreso", "ironico", "calmo"];
async function loadVoices() {
  const r = await fetch("/api/voices");
  voicesCache = await r.json();
  voicesCache.sort((a, b) => a.id.localeCompare(b.id, "it", { sensitivity: "base" }));
  for (const sel of ["#g-voice", "#b-voice"]) $(sel).innerHTML = voiceOptions();
  $("#e-voice").innerHTML = voicesCache.filter((v) => v.type === "clone")
    .map((v) => `<option value="${esc(v.id)}">${esc(v.id)}${v.emotions.length ? " ["+v.emotions.join(",")+"]" : ""}</option>`).join("");
  teatro.repopulateVoices();
  teatroEmo.repopulateVoices();
  renderVoiceCards();
  updateGenPreview();
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
async function pollJob(jid, shouldStop) {
  while (true) {
    const job = await (await fetch(`/api/jobs/${jid}`)).json();
    if (job.status === "done" || job.status === "error") return job;
    if (shouldStop && shouldStop()) return { status: "aborted" };  // smette di pollare
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

// --- Teatro (factory condivisa tra Teatro e Teatro-Emozioni) ---
// I due tab differiscono solo per i controlli voce (fillVoiceUI/readVoice);
// generazione, stitch, export/import e azioni blocco sono identici.
function makeTeatro({ prefix, fillVoiceUI, readVoice }) {
  const P = (s) => $(`#${prefix}-${s}`);
  const cls = (el, s) => el.querySelector(`.${prefix}-${s}`);
  const tpl = $(`#${prefix}-block-tpl`);
  let stopScene = false;  // per-istanza: niente collisione tra i due tab

  function addBlock(data = {}) {
    const el = tpl.content.firstElementChild.cloneNode(true);
    fillVoiceUI(el, data);
    if (data.character != null) cls(el, "char").value = data.character;
    if (data.speed != null) cls(el, "speed").value = String(data.speed);
    if (data.instruct != null) cls(el, "instruct").value = data.instruct;
    if (data.pause_after != null) cls(el, "pause").value = data.pause_after;
    if (data.text != null) cls(el, "text").value = data.text;
    cls(el, "del").onclick = () => el.remove();
    cls(el, "dup").onclick = () => el.after(addBlock(readBlock(el)));
    cls(el, "up").onclick = () => el.previousElementSibling?.before(el);
    cls(el, "down").onclick = () => el.nextElementSibling?.after(el);
    cls(el, "regen").onclick = () => regenBlock(el);
    P("blocks").appendChild(el);
    return el;
  }

  function readBlock(div) {
    const { voice_id, emotion } = readVoice(div);
    const clipEl = cls(div, "clip");
    const clip = clipEl && !clipEl.classList.contains("hidden") && clipEl.src
      ? clipEl.src.split("/").pop() : null;
    return {
      character: cls(div, "char").value.trim(),
      voice_id, emotion,
      speed: parseFloat(cls(div, "speed").value),
      instruct: cls(div, "instruct").value.trim(),
      pause_after: parseFloat(cls(div, "pause").value) || 0,
      text: cls(div, "text").value.trim(),
      clip,
    };
  }

  function blockToApi(b) {
    return { character: b.character, voice_id: b.voice_id, text: b.text, speed: b.speed,
             emotion: b.emotion, instruct: b.instruct || null, pause_after: b.pause_after,
             clip: b.clip || null };
  }

  // Genera (o rigenera) il clip di un singolo blocco. true se ok.
  async function regenBlock(div, shouldStop) {
    const b = readBlock(div);
    if (!b.text) { setStatus(P("status"), "Battuta vuota", "err"); return false; }
    setStatus(P("status"), "Rigenero battuta…", "");
    const clip = cls(div, "clip");
    const prog = cls(div, "prog");
    clip.classList.add("hidden");
    prog.classList.remove("hidden");
    const r = await fetch("/api/generate", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: b.text, voice_id: b.voice_id, format: "wav",
                             speed: b.speed, emotion: b.emotion,
                             instruct: b.instruct || null }),
    });
    if (!r.ok) { prog.classList.add("hidden"); setStatus(P("status"), "Errore: " + (await r.text()), "err"); return false; }
    const { job_id } = await r.json();
    const job = await pollJob(job_id, shouldStop);
    if (job.status !== "done") {
      prog.classList.add("hidden");
      setStatus(P("status"), job.status === "aborted" ? "Interrotto ⏹" : "Errore: " + job.error,
        job.status === "aborted" ? "" : "err");
      return false;
    }
    prog.classList.add("hidden");
    clip.src = "/api/outputs/" + job.result.split("/").pop();
    clip.classList.remove("hidden");
    setStatus(P("status"), "Battuta pronta ✓", "ok");
    return true;
  }

  async function genAll() {
    const divs = [...P("blocks").querySelectorAll(`.${prefix}-block`)].filter((d) => readBlock(d).text);
    if (!divs.length) { setStatus(P("status"), "Nessuna battuta", "err"); return; }
    stopScene = false;
    const prog = P("progress");
    P("scene").classList.add("hidden"); P("download").classList.add("hidden");
    prog.classList.remove("hidden");
    P("stop").classList.remove("hidden"); P("genall").disabled = true;
    try {
      for (let i = 0; i < divs.length; i++) {
        if (stopScene) { setStatus(P("status"), "Interrotto ⏹", ""); return; }
        setStatus(P("status"), `Genero battuta ${i + 1}/${divs.length}…`, "");
        if (!await regenBlock(divs[i], () => stopScene)) return;
      }
      await stitchScene();
    } finally {
      prog.classList.add("hidden");
      P("stop").classList.add("hidden"); P("genall").disabled = false;
    }
  }

  async function stitchScene() {
    const blocks = [...P("blocks").querySelectorAll(`.${prefix}-block`)].map(readBlock).filter((b) => b.text);
    if (!blocks.length) { setStatus(P("status"), "Nessuna battuta", "err"); return; }
    const missing = blocks.filter((b) => !b.clip).length;
    if (missing) { setStatus(P("status"), `Genera prima le ${missing} battute mancanti (↻ Rigenera o 🎬 Genera scena completa)`, "err"); return; }
    setStatus(P("status"), "Unisco le battute…", "");
    P("scene").classList.add("hidden"); P("download").classList.add("hidden");
    const prog = P("progress");
    prog.classList.remove("hidden");
    const r = await fetch("/api/teatro", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ blocks: blocks.map(blockToApi),
                             format: P("format").value, title: P("title").value || "scena" }),
    });
    if (!r.ok) { prog.classList.add("hidden"); setStatus(P("status"), "Errore: " + (await r.text()), "err"); return; }
    const { job_id } = await r.json();
    const job = await pollJob(job_id);
    if (job.status === "error") { prog.classList.add("hidden"); setStatus(P("status"), "Errore: " + job.error, "err"); return; }
    prog.classList.add("hidden");
    const name = job.result.scene.split("/").pop();
    const url = "/api/outputs/" + name;
    P("scene-label").classList.remove("hidden");
    P("scene").src = url; P("scene").classList.remove("hidden");
    P("download").href = url; P("download").setAttribute("download", name);
    P("download").classList.remove("hidden");
    const divs = [...P("blocks").querySelectorAll(`.${prefix}-block`)].filter((d) => readBlock(d).text);
    job.result.clips.forEach((c, i) => {
      const clip = divs[i] && cls(divs[i], "clip");
      if (clip) { clip.src = "/api/outputs/" + c.path.split("/").pop(); clip.classList.remove("hidden"); }
    });
    setStatus(P("status"), "Scena pronta ✓", "ok");
  }

  function repopulateVoices() {
    P("blocks").querySelectorAll(`.${prefix}-block`).forEach((el) => fillVoiceUI(el, readBlock(el)));
    if (!P("blocks").children.length) addBlock();
  }

  // wiring controlli del pannello
  P("add").onclick = () => addBlock();
  P("stop").onclick = () => { stopScene = true; setStatus(P("status"), "Interruzione…", ""); };
  P("genall").onclick = genAll;
  P("run").onclick = stitchScene;
  P("export").onclick = () => {
    const data = [...P("blocks").querySelectorAll(`.${prefix}-block`)].map(readBlock);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = (P("title").value || "scena") + ".json";
    a.click();
  };
  P("import-btn").onclick = () => P("import").click();
  P("import").onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const raw = await file.text();
    let data;
    try { data = JSON.parse(raw); }
    catch { data = parseScene(raw); }
    if (!Array.isArray(data) || !data.length) {
      setStatus(P("status"), "File scena non valido", "err"); e.target.value = ""; return;
    }
    P("blocks").innerHTML = "";
    data.forEach((b) => addBlock(b));
    const known = new Set(voicesCache.map((v) => v.id));
    const unknown = [...new Set(data.filter((b) => b.voice_id && !known.has(b.voice_id)).map((b) => b.voice_id))];
    const noChar = data.filter((b) => !b.character).length;
    const warn = [
      unknown.length && `voci sconosciute: ${unknown.join(", ")}`,
      noChar && `${noChar} battute senza Personaggio`,
    ].filter(Boolean).join(" — ");
    setStatus(P("status"), warn ? `Scena importata — ${warn}` : "Scena importata ✓", warn ? "err" : "ok");
    e.target.value = "";
  };

  return { addBlock, repopulateVoices };
}

// Istanza Teatro: solo voci clone, neutre
const teatro = makeTeatro({
  prefix: "t",
  fillVoiceUI(el, data) {
    const s = el.querySelector(".t-voice");
    s.innerHTML = cloneVoiceOptions();
    if (data.voice_id) s.value = data.voice_id;
  },
  readVoice(el) {
    return { voice_id: el.querySelector(".t-voice").value, emotion: null };
  },
});

// Istanza Teatro-Emozioni: voci design + sesso + emozione
const teatroEmo = makeTeatro({
  prefix: "te",
  fillVoiceUI(el, data) {
    const btnM = el.querySelector(".te-sex-male");
    const btnF = el.querySelector(".te-sex-female");
    const voiceSel = el.querySelector(".te-voice");
    const emoSel = el.querySelector(".te-emotion");
    let gender = "male";
    if (data.voice_id) {
      const v = voicesCache.find((x) => x.id === data.voice_id);
      if (v && v.gender) gender = v.gender;
    }
    const setGender = (g) => {
      gender = g;
      btnM.classList.toggle("active", g === "male");
      btnF.classList.toggle("active", g === "female");
      voiceSel.innerHTML = designVoicesByGender(g)
        .map((v) => `<option value="${esc(v.id)}">${esc(v.id)}</option>`).join("");
    };
    btnM.onclick = () => setGender("male");
    btnF.onclick = () => setGender("female");
    setGender(gender);
    if (data.voice_id) voiceSel.value = data.voice_id;
    emoSel.innerHTML = ["neutro", ...EMOTIONS]
      .map((e) => `<option value="${esc(e)}">${esc(e)}</option>`).join("");
    if (data.emotion) emoSel.value = data.emotion;
  },
  readVoice(el) {
    const emo = el.querySelector(".te-emotion").value;
    return { voice_id: el.querySelector(".te-voice").value,
             emotion: emo === "neutro" ? null : emo };
  },
});

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
