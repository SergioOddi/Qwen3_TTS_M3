# Tema base frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sostituire il tema scuro tecnico con palette chiara "studio editoriale", tipografia leggibile, nav a sidebar — solo CSS + riorganizzazione markup statico, nessuna logica JS toccata.

**Architecture:** Tutto lo styling passa già da custom properties in `:root` (`app/static/style.css`) e da un solo file `app/static/index.html`. Il piano tocca solo questi due file: swap variabili colore, import font, spostamento `<nav>` da top-bar a sidebar con breakpoint responsive esistente come modello (`#t-picker`, già a 1180px).

**Tech Stack:** CSS puro (custom properties, flexbox, media query), HTML statico. Nessuna dipendenza nuova, nessun JS.

**Nota su TDD:** compito è styling/markup statico, nessuna logica testabile con assert. Niente step "scrivi test" — verifica è manuale (avvio app, controllo visivo) come da spec.

---

### Task 1: Palette colori

**Files:**
- Modify: `app/static/style.css:1-4`

- [ ] **Step 1: Sostituire il blocco `:root`**

Trova:
```css
:root {
  --bg: #0f1115; --panel: #1a1d24; --accent: #6c8cff; --text: #e8eaf0;
  --muted: #9aa3b2; --border: #2a2e38; --ok: #3ecf8e; --err: #ff6b6b;
}
```

Sostituisci con:
```css
:root {
  --bg: #F6F0E7; --panel: #FFFDF8; --accent: #B7C9A8; --text: #2E2A22;
  --muted: #8a8272; --border: #E3D9C6; --ok: #7FA66B; --err: #C97B5A;
  --info: #9B85B8;
}
```

- [ ] **Step 2: Verifica visiva rapida**

Apri `app/static/index.html` in browser (senza server, `file://` va bene per questo check) e conferma che sfondo/testo/bottoni cambiano colore, nessuno stile rotto (bordi visibili, testo leggibile).

- [ ] **Step 3: Commit**

```bash
git add app/static/style.css
git commit -m "style: palette chiara studio editoriale (era tema scuro)"
```

---

### Task 2: Tipografia

**Files:**
- Modify: `app/static/style.css:1` (aggiungere import in cima) e riga `body`/`h1`

- [ ] **Step 1: Aggiungere import font in cima al file** (prima del blocco `:root`)

```css
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Source+Serif+4:wght@600;700&display=swap');
```

- [ ] **Step 2: Applicare i font**

Trova:
```css
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: -apple-system, system-ui, sans-serif; line-height: 1.5;
}
```

Sostituisci con:
```css
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: 'Atkinson Hyperlegible', -apple-system, system-ui, sans-serif; line-height: 1.5;
}
h1, h2, h3, .t-block::before, .te-block::before {
  font-family: 'Source Serif 4', Georgia, serif;
}
```

(`.t-block::before`/`.te-block::before` sono le etichette "Battuta 001" in Teatro — già stilizzate, cambia solo il font)

- [ ] **Step 3: Verifica visiva**

Ricarica `index.html`, conferma che il font UI è cambiato (sans-serif più leggibile) e i titoli usano il serif.

- [ ] **Step 4: Commit**

```bash
git add app/static/style.css
git commit -m "style: applica Atkinson Hyperlegible (UI) e Source Serif 4 (titoli)"
```

---

### Task 3: Nav sidebar

**Files:**
- Modify: `app/static/index.html:9-19` (header → aside)
- Modify: `app/static/style.css` (nuove regole layout, righe 6-18 esistenti da adattare)

- [ ] **Step 1: Riscrivere l'header come aside in index.html**

Trova (righe 9-19):
```html
  <header>
    <h1>🎙️ GASSMANN — Studio Voce</h1>
    <nav>
      <button class="tab active" data-tab="genera">Genera</button>
      <button class="tab" data-tab="batch">Batch</button>
      <button class="tab" data-tab="teatro">Teatro</button>
      <button class="tab" data-tab="teatro-emo">Teatro-Emozioni</button>
      <button class="tab" data-tab="voci">Voci</button>
    </nav>
  </header>

  <main>
```

Sostituisci con:
```html
  <aside>
    <h1>🎙️ GASSMANN</h1>
    <nav>
      <button class="tab active" data-tab="genera">Genera</button>
      <button class="tab" data-tab="batch">Batch</button>
      <button class="tab" data-tab="teatro">Teatro</button>
      <button class="tab" data-tab="teatro-emo">Teatro-Emozioni</button>
      <button class="tab" data-tab="voci">Voci</button>
    </nav>
  </aside>

  <main>
```

Nessun cambio a `id`/`data-tab`/classi: `app.js` seleziona i tab tramite `data-tab` e non tocca `header`/`aside`, lo switch continua a funzionare invariato.

- [ ] **Step 2: Aggiornare CSS layout — sostituire regole header/nav/main**

Trova (righe 6-18 circa):
```css
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: 'Atkinson Hyperlegible', -apple-system, system-ui, sans-serif; line-height: 1.5;
}
h1, h2, h3, .t-block::before, .te-block::before {
  font-family: 'Source Serif 4', Georgia, serif;
}
header { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); }
h1 { margin: 0 0 .75rem; font-size: 1.3rem; }
nav { display: flex; gap: .5rem; }
```

Sostituisci con:
```css
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: 'Atkinson Hyperlegible', -apple-system, system-ui, sans-serif; line-height: 1.5;
  display: flex; min-height: 100vh;
}
h1, h2, h3, .t-block::before, .te-block::before {
  font-family: 'Source Serif 4', Georgia, serif;
}
aside {
  width: 180px; flex-shrink: 0; border-right: 1px solid var(--border);
  padding: 1rem .75rem;
}
h1 { margin: 0 0 .75rem; font-size: 1.1rem; }
aside nav { display: flex; flex-direction: column; gap: .3rem; }
```

- [ ] **Step 3: Aggiornare `main` per stare a fianco della sidebar**

Trova:
```css
main { max-width: 820px; margin: 0 auto; padding: 1.5rem; }
```

Sostituisci con:
```css
main { flex: 1; max-width: 820px; margin: 0 auto; padding: 1.5rem; min-width: 0; }
```

- [ ] **Step 4: Aggiungere breakpoint responsive** (in fondo al file, dopo il breakpoint esistente `@media (max-width: 1180px)` di `#t-picker` — riga ~173-179)

Trova:
```css
@media (max-width: 1180px) {
  #t-picker { left: .75rem; right: .75rem; bottom: .75rem; top: auto; width: auto;
              display: flex; gap: .6rem; align-items: flex-end; }
  #t-picker-body { margin-top: 0; flex: 1; max-height: 32vh; }
  #t-picker-names { flex-direction: row; flex-wrap: wrap; }
  #teatro { padding-bottom: 6rem; }   /* la striscia non copre l'ultima battuta */
}
```

Aggiungi subito dopo (stesso blocco media query, nuove righe):
```css
@media (max-width: 1180px) {
  body { flex-direction: column; }
  aside { width: auto; border-right: none; border-bottom: 1px solid var(--border); }
  aside nav { flex-direction: row; flex-wrap: wrap; }
}
```

- [ ] **Step 5: Verifica visiva a due larghezze**

Apri l'app (`./launch.sh` o `uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`), controlla:
1. Finestra larga (>1180px): sidebar a sinistra, 5 tab in colonna, click su ogni tab cambia pannello.
2. Finestra stretta (<1180px, es. DevTools responsive mode): sidebar diventa barra orizzontale in alto, tab ancora cliccabili.
3. Tab Teatro: la palette voci `#t-picker` (fixed) non si sovrappone in modo rotto alla nuova sidebar.

- [ ] **Step 6: Commit**

```bash
git add app/static/index.html app/static/style.css
git commit -m "feat(ui): nav da top-bar a sidebar con fallback responsive"
```

---

## Self-review (copertura spec)

- Palette → Task 1. ✅
- Tipografia → Task 2. ✅
- Nav sidebar + breakpoint 1180px → Task 3. ✅
- Fuori scope (Genera/Teatro card/wizard Voci/feedback/a11y) → non toccati, come da spec. ✅
