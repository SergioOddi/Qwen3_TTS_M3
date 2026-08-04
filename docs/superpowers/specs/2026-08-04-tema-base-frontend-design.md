# Tema base frontend — design

Fonte: `Migliorie_frontend.md` (proposta restyling completo). Scope di questo giro:
solo palette, tipografia, navigazione. Le altre 5 aree della proposta (flusso Genera,
card Teatro, wizard Voci, feedback stati, accessibilità) restano fuori, da affrontare
in giri separati.

## Obiettivo

Sostituire il tema scuro tecnico attuale con uno stile "studio editoriale" chiaro,
caldo, leggibile — senza toccare markup funzionale o logica JS.

## Palette (`app/static/style.css`, blocco `:root`)

```css
--bg: #F6F0E7;      /* era #0f1115 */
--panel: #FFFDF8;   /* era #1a1d24 */
--border: #E3D9C6;  /* era #2a2e38 */
--text: #2E2A22;    /* era #e8eaf0 */
--muted: #8a8272;   /* era #9aa3b2 */
--accent: #B7C9A8;  /* salvia, era #6c8cff */
--ok: #7FA66B;       /* salvia scuro conferme, era #3ecf8e */
--err: #C97B5A;       /* terracotta azioni irreversibili, era #ff6b6b */
--info: #9B85B8;     /* lilla, var nuova, badge informativi */
```

Il resto del CSS referenzia solo queste custom properties (bottoni, card, progress,
`.t-block`, picker Teatro) → nessuna riscrittura di selettori, solo il blocco `:root`.
Confermato a video nel companion (swatch + testo su superficie chiara).

## Tipografia

`@import` Google Fonts in testa a `style.css`: Atkinson Hyperlegible (UI) + Source
Serif 4 (titoli/testo di scena).

```css
body { font-family: 'Atkinson Hyperlegible', -apple-system, system-ui, sans-serif; }
h1, h2, h3, .t-block::before, .te-block::before {
  font-family: 'Source Serif 4', Georgia, serif;
}
```

Dimensioni base restano quelle attuali (già ragionevoli), solo cambio font-family.

## Navigazione: header top-bar → sidebar

Confermato a video (opzione A tra sidebar/pillole).

**HTML** (`app/static/index.html`): `<header>` diventa `<aside>` con h1 (logo compatto)
+ `<nav>` verticale; `<body>` avvolge `aside` + `main` in un contenitore flex-row.
Nessun cambio agli `id`/`data-tab` dei bottoni — la logica di switch tab in `app.js`
resta identica.

**CSS**:
```css
body { display: flex; min-height: 100vh; margin: 0; }
aside { width: 180px; flex-shrink: 0; border-right: 1px solid var(--border);
        padding: 1rem .75rem; }
aside nav { display: flex; flex-direction: column; gap: .3rem; }
main { flex: 1; max-width: 820px; margin: 0 auto; padding: 1.5rem; }
```

Sotto i 1180px la sidebar torna barra orizzontale in cima (stesso breakpoint e stessa
logica già usata per `#t-picker` in questo file — pattern esistente, non nuovo):
```css
@media (max-width: 1180px) {
  body { flex-direction: column; }
  aside { width: auto; border-right: none; border-bottom: 1px solid var(--border); }
  aside nav { flex-direction: row; flex-wrap: wrap; }
}
```

## Fuori scope (questo giro)

Flusso "Genera" a blocchi, restyling card Teatro, wizard voce clonata, feedback
stati/progress descrittivi, target click/focus a11y — restano nella proposta
originale per un giro successivo, nessuna modifica ora.

## Test

Nessuna logica nuova (solo CSS + riorganizzazione markup statico) → nessun test
automatico aggiuntivo. Verifica manuale: avviare l'app (`./launch.sh`), controllare
le 5 tab, contrasto testo/sfondo, sidebar che collassa sotto i 1180px.
