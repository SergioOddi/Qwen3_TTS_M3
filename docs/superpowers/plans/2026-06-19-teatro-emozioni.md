# Tab Teatro-Emozioni Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere un tab "Teatro-Emozioni" che usa solo voci design scelte per Sesso → Voce → Emozione, e ridurre il tab Teatro alle sole voci clone neutre.

**Architettura:** Backend espone un campo `gender` sulle voci design (per filtrare M/F). Frontend: le funzioni del tab Teatro vengono fattorizzate in `makeTeatro({prefix, fillVoiceUI, readVoice})`, condivise tra Teatro (voci clone) e Teatro-Emozioni (voci design + sesso/emozione). Nessun nuovo endpoint: si riusa `/api/generate` (ramo design già supporta emozione+instruct) e `/api/teatro` (stitch).

**Tech Stack:** FastAPI (Python 3.12), pytest, vanilla JS (no framework), node assert per i test JS esistenti.

**Spec:** `docs/superpowers/specs/2026-06-19-teatro-emozioni-design.md`

---

## File map

- Modify `config/attore.json` — aggiunge `"gender": "male"`
- Modify `config/attrice.json` — aggiunge `"gender": "female"`
- Modify `app/voices.py` — `_voice_info` espone `gender`
- Modify `tests/test_voices.py` — assert su `gender`
- Modify `app/static/index.html` — tab nav + sezione `teatro-emo` + template `te-block-tpl`
- Modify `app/static/app.js` — factory `makeTeatro` + 2 istanze + wiring in `loadVoices`

---

## Task 1: Backend — campo `gender` sulle voci design

**Files:**
- Modify: `app/voices.py` (funzione `_voice_info`, ~riga 39-51)
- Modify: `tests/test_voices.py` (test `test_list_voices_separates_design_and_clone`)
- Modify: `config/attore.json`, `config/attrice.json`

- [ ] **Step 1: Aggiorna il test esistente (failing)**

In `tests/test_voices.py`, dentro `test_list_voices_separates_design_and_clone`, aggiungi `"gender"` alla fixture `narratore` e le asserzioni. La fixture diventa:

```python
    _write(tmp_dirs["config"], "narratore", {
        "language": "Italian",
        "voice_description": "Voce calda da narratore",
        "gender": "male",
    })
```

E in fondo allo stesso test aggiungi:

```python
    # design: gender esposto per il filtro M/F del tab Teatro-Emozioni
    assert by_id["narratore"]["gender"] == "male"
    # clone senza campo gender → None
    assert by_id["zaza_docente"]["gender"] is None
```

- [ ] **Step 2: Esegui il test, verifica che fallisce**

Run: `cd ~/repos/GASSMANN && python -m pytest tests/test_voices.py::test_list_voices_separates_design_and_clone -v`
Expected: FAIL con `KeyError: 'gender'`

- [ ] **Step 3: Aggiungi `gender` a `_voice_info`**

In `app/voices.py`, nel dict ritornato da `_voice_info`, aggiungi una riga subito dopo `"tags": _derive_tags(name, data),`:

```python
        "gender": data.get("gender"),  # "male" | "female" | None (cloni)
```

- [ ] **Step 4: Esegui il test, verifica che passa**

Run: `cd ~/repos/GASSMANN && python -m pytest tests/test_voices.py::test_list_voices_separates_design_and_clone -v`
Expected: PASS

- [ ] **Step 5: Aggiungi `gender` ai config attore/attrice**

In `config/attore.json` aggiungi la coppia (dopo `"language"`):
```json
  "gender": "male",
```
In `config/attrice.json`:
```json
  "gender": "female",
```

- [ ] **Step 6: Esegui l'intera suite**

Run: `cd ~/repos/GASSMANN && python -m pytest tests/ -q`
Expected: tutti i test passano (21+).

- [ ] **Step 7: Commit**

```bash
cd ~/repos/GASSMANN && git add app/voices.py tests/test_voices.py config/attore.json config/attrice.json && \
git commit -m "feat: campo gender sulle voci design (filtro M/F)"
```

---

## Task 2: index.html — tab, sezione e template Teatro-Emozioni

**Files:**
- Modify: `app/static/index.html` (nav riga ~15; nuova sezione dopo `</section>` di Teatro riga ~84; nuovo template dopo `t-block-tpl` riga ~113)

- [ ] **Step 1: Aggiungi il pulsante tab nella nav**

In `app/static/index.html`, dopo la riga `<button class="tab" data-tab="teatro">Teatro</button>` aggiungi:

```html
      <button class="tab" data-tab="teatro-emo">Teatro-Emozioni</button>
```

- [ ] **Step 2: Aggiungi la sezione `teatro-emo`**

Subito dopo la chiusura `</section>` del tab Teatro (prima del commento `<!-- template blocco teatro -->`), incolla:

```html
    <!-- TEATRO-EMOZIONI -->
    <section id="teatro-emo" class="panel">
      <p>Come Teatro, ma con voci sintetiche (design): per ogni battuta scegli <strong>Sesso → Voce → Emozione</strong>. L'emozione è nativa (instruct), non DSP.</p>
      <div class="row">
        <div><label>Nome scena</label><input id="te-title" type="text" value="scena"></div>
        <div><label>Formato</label><select id="te-format"><option>wav</option><option>mp3</option></select></div>
      </div>
      <div id="te-blocks"></div>
      <div class="row" style="margin-top:.75rem">
        <button id="te-add">+ Aggiungi battuta</button>
        <button id="te-export">⬇ Esporta scena</button>
        <button id="te-import-btn" title="JSON esportato, oppure .txt/.md con battute separate da una riga '---'">⬆ Importa scena</button>
        <input id="te-import" type="file" accept=".json,.txt,.md,application/json,text/plain,text/markdown" class="hidden">
      </div>
      <button id="te-genall" class="genall" title="Genera tutte le battute da zero e le unisce nella scena">🎬 Genera scena completa</button>
      <button id="te-stop" class="stop hidden" title="Ferma ora la generazione; le battute già pronte restano">⏹ Stop</button>
      <button id="te-run" class="primary" title="Unisce solo i clip già generati (↻ Rigenera), senza rigenerarli">Unisci battute in scena</button>
      <div id="te-status" class="status"></div>
      <progress id="te-progress" class="hidden"></progress>
      <label class="hidden" id="te-scene-label">Scena completa</label>
      <audio id="te-scene" controls class="hidden"></audio>
      <a id="te-download" class="hidden" download>⬇ Scarica scena</a>
    </section>
```

- [ ] **Step 3: Aggiungi il template `te-block-tpl`**

Subito dopo la chiusura `</template>` di `t-block-tpl`, incolla (uguale a `t-block-tpl` ma con classi `te-*` e la riga voce = sesso/voce/emozione):

```html
    <!-- template blocco teatro-emozioni (clonato da app.js) -->
    <template id="te-block-tpl">
      <div class="te-block">
        <div class="row">
          <div><label>Personaggio</label><input class="te-char" type="text" placeholder="es. AMLETO"></div>
          <div><label>Sesso</label><div class="te-sex">
            <button type="button" class="te-sex-male">♂ Uomo</button>
            <button type="button" class="te-sex-female">♀ Donna</button>
          </div></div>
          <div><label>Voce</label><select class="te-voice"></select></div>
          <div><label>Emozione</label><select class="te-emotion"></select></div>
        </div>
        <div class="row">
          <div><label>Velocità</label><select class="te-speed">
            <option value="0.8">0.8×</option><option value="0.9">0.9×</option>
            <option value="1.0" selected>1.0×</option>
            <option value="1.1">1.1×</option><option value="1.2">1.2×</option>
          </select></div>
          <div><label>Pausa dopo (sec)</label><input class="te-pause" type="number" min="0" step="0.1" value="0.5"></div>
        </div>
        <label>Istruzione libera <small>(combinata con l'emozione)</small></label>
        <input class="te-instruct" type="text" placeholder="es. sussurrando">
        <label>Battuta</label>
        <textarea class="te-text" rows="2" placeholder="testo della battuta…"></textarea>
        <div class="row te-block-actions">
          <button class="te-up" title="Su">↑</button>
          <button class="te-down" title="Giù">↓</button>
          <button class="te-dup" title="Duplica">⧉</button>
          <button class="te-regen" title="Rigenera solo questa battuta">↻ Rigenera</button>
          <button class="te-del" title="Elimina">✕</button>
        </div>
        <progress class="te-prog hidden"></progress>
        <audio class="te-clip hidden" controls></audio>
      </div>
    </template>
```

- [ ] **Step 4: Stile pulsanti sesso (attivo evidenziato)**

In `app/static/style.css`, in fondo al file, aggiungi:

```css
.te-sex { display: flex; gap: .25rem; }
.te-sex button { flex: 1; opacity: .55; }
.te-sex button.active { opacity: 1; outline: 2px solid currentColor; }
```

- [ ] **Step 5: Verifica visiva (la tab esiste ma è ancora vuota di logica)**

Run: avvia l'app `cd ~/repos/GASSMANN && python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000` e apri http://127.0.0.1:8000 .
Expected: compare il tab "Teatro-Emozioni"; cliccandolo si vede la sezione (i blocchi appariranno dopo Task 3). Ferma l'app con Ctrl-C.

- [ ] **Step 6: Commit**

```bash
cd ~/repos/GASSMANN && git add app/static/index.html app/static/style.css && \
git commit -m "feat: markup tab Teatro-Emozioni (sesso/voce/emozione)"
```

---

## Task 3: app.js — factory `makeTeatro` + due istanze

Questo task **sostituisce** il blocco Teatro attuale (da `// --- Teatro ---` riga ~214 fino alla fine del gestore `$("#t-import").onchange` ~riga 386) con una factory parametrica e due istanze. Sostituisce anche la riga di ripopolamento voci dentro `loadVoices`.

**Files:**
- Modify: `app/static/app.js`

- [ ] **Step 1: Aggiungi le costanti voci/emozioni per i due tab**

Subito dopo la definizione di `voiceOptions` / `parseVoice` (riga ~27, prima di `async function loadVoices`), aggiungi:

```js
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
```

- [ ] **Step 2: Sostituisci il ripopolamento voci dentro `loadVoices`**

In `loadVoices`, trova il blocco:

```js
  $$("#t-blocks .t-voice").forEach((sel) => {
    const cur = sel.value; sel.innerHTML = voiceOptions(); sel.value = cur;
  });
  renderVoiceCards();
  updateGenPreview();
  if (!$("#t-blocks").children.length) addBlock();
```

e sostituiscilo con:

```js
  teatro.repopulateVoices();
  teatroEmo.repopulateVoices();
  renderVoiceCards();
  updateGenPreview();
```

- [ ] **Step 3: Sostituisci tutto il vecchio blocco Teatro con la factory**

Cancella dal file il blocco che va da `// --- Teatro ---` (riga ~214) fino alla riga `// ponytail: persistenza via export/import file; niente DB/localStorage finché basta.` inclusa (~riga 386). Incolla al suo posto:

```js
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
```

- [ ] **Step 4: I test JS esistenti passano (parseScene riusato)**

Run: `cd ~/repos/GASSMANN && node app/static/scene_parse.test.mjs`
Expected: nessun errore (exit 0).

- [ ] **Step 5: Verifica manuale dell'app**

Run: `cd ~/repos/GASSMANN && python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`, apri http://127.0.0.1:8000 .
Verifica:
1. Tab **Teatro**: il menu Voce mostra SOLO voci clone, niente `· felice`/`· triste`.
2. Tab **Teatro-Emozioni**: c'è un blocco; pulsanti ♂/♀ (♂ attivo); Voce mostra `attore` con ♂ e `attrice` con ♀; Emozione mostra `neutro` + 7 emozioni.
3. In Teatro-Emozioni scrivi una battuta breve, premi ↻ Rigenera → genera un clip ascoltabile.
4. Esporta scena → reimporta: i blocchi tornano con sesso/voce/emozione corretti.
Ferma l'app con Ctrl-C.

- [ ] **Step 6: Commit**

```bash
cd ~/repos/GASSMANN && git add app/static/app.js && \
git commit -m "feat: tab Teatro-Emozioni via factory makeTeatro; Teatro = solo cloni"
```

---

## Task 4: Aggiorna la documentazione

**Files:**
- Modify: `CLAUDE.md` (sezione "Tab UI" e "Funzione TEATRO")

- [ ] **Step 1: Aggiorna la riga dei Tab UI**

In `CLAUDE.md`, nella sezione App Standalone, sostituisci la riga:

```
**Tab UI:** Genera (singolo) · Batch (più testi, stessa voce) · **Teatro** · Voci.
```

con:

```
**Tab UI:** Genera (singolo) · Batch (più testi, stessa voce) · **Teatro** (voci clone, neutre) · **Teatro-Emozioni** (voci design, Sesso→Voce→Emozione) · Voci.
```

- [ ] **Step 2: Commit**

```bash
cd ~/repos/GASSMANN && git add CLAUDE.md && \
git commit -m "docs: documenta tab Teatro-Emozioni in CLAUDE.md"
```

---

## Note di verifica finale

- Suite Python: `python -m pytest tests/ -q` → verde.
- Test JS: `node app/static/scene_parse.test.mjs` → exit 0.
- Nessun nuovo endpoint, nessuna nuova dipendenza.
- Il tab Teatro-Emozioni funziona solo se esiste almeno una voce design per sesso
  (`attore` = male, `attrice` = female). Se manca, il menu Voce di quel sesso è vuoto.
