// Parser scene Teatro da file di testo. Due formati, auto-rilevati:
//
// 1) CAMPI  — battute separate da una riga "---", righe "Campo: valore".
//    La Battuta va a capo liberamente (le righe senza Campo noto si attaccano
//    al campo corrente). Obbligatoria solo la Battuta.
//
// 2) COPIONE — classico screenplay markdown: "**NOME**" in grassetto a inizio
//    paragrafo = Personaggio, testo sulla stessa riga; corsivo *...*/_..._ e
//    parentesi (...) = didascalia registica → finisce in `notes`, NON letta dal
//    TTS. Un paragrafo di sola didascalia diventa nota della battuta successiva.
//    Voce/velocità/pausa arrivano dal commento <!--gassmann: voce;vel;pausa-->
//    scritto da sceneToMarkdown (invisibile in Obsidian) se presente.

const SCENE_FIELDS = {
  personaggio: "character",
  voce: "voce",
  "velocità": "speed", velocita: "speed",
  "pausa dopo (sec)": "pause_after", "pausa dopo": "pause_after", pausa: "pause_after",
  "istruzione libera": "instruct", istruzione: "instruct",
  battuta: "text", testo: "text",
};

const block = (o) => ({ character: "", voice_id: "", emotion: null, speed: undefined,
                        instruct: "", pause_after: undefined, text: "", notes: "", ...o });

const numOrUndef = (v) => {                     // virgola IT o punto
  const n = parseFloat(String(v ?? "").replace(",", "."));
  return isNaN(n) ? undefined : n;
};

function parseSceneText(text) {
  return text.replace(/\r\n?/g, "\n").split(/^[ \t]*-{3,}[ \t]*$/m).map((blk) => {
    const acc = {};
    let cur = null;
    for (const line of blk.split("\n")) {
      const m = line.match(/^[ \t]*([^:]+?)[ \t]*:[ \t]?(.*)$/);
      const key = m && SCENE_FIELDS[m[1].toLowerCase()];
      if (key) { acc[key] = m[2]; cur = key; }
      else if (cur && line.trim()) acc[cur] += "\n" + line;
    }
    const voce = (acc.voce || "").trim();
    const sep = voce.indexOf("|");
    const sp = numOrUndef(acc.speed);
    return block({
      character: (acc.character || "").trim(),
      voice_id: sep < 0 ? voce : voce.slice(0, sep),
      emotion: sep < 0 ? null : voce.slice(sep + 1).trim() || null,
      speed: sp === undefined ? undefined : sp.toFixed(1),
      instruct: (acc.instruct || "").trim(),
      pause_after: numOrUndef(acc.pause_after),
      text: (acc.text || "").trim(),
    });
  }).filter((b) => b.text);   // serve solo la Battuta
}

// grassetto interno, corsivo *..* / _.._, parentesi tonde = didascalia
const RE_NOTE = /\*\*[^*]+\*\*|_[^_]+_|\*[^*]+\*|\([^)]*\)/g;
const RE_META = /<!--\s*gassmann:([^>]*?)-->/;

// Separa il parlato dalle didascalie. Ritorna { text, notes }.
function splitNotes(s) {
  const notes = [];
  const text = s
    .replace(/^#{1,6} .*$/gm, "")                       // titoli markdown: ignorati
    .replace(RE_NOTE, (m) => {
      notes.push(m.replace(/[*_()]/g, "").trim());
      return " ";
    })
    .replace(/\s+/g, " ").trim();
  return { text, notes: notes.filter(Boolean).join(" ") };
}

// <!--gassmann: voce|emozione;velocità;pausa--> → campi del blocco
function metaFields(m) {
  if (!m) return {};
  const [v = "", sp = "", pa = ""] = m[1].split(";").map((x) => x.trim());
  const i = v.indexOf("|");
  const speed = numOrUndef(sp);
  return {
    voice_id: i < 0 ? v : v.slice(0, i),
    emotion: i < 0 ? null : v.slice(i + 1) || null,
    speed: speed === undefined ? undefined : speed.toFixed(1),
    pause_after: numOrUndef(pa),
  };
}

function parseScreenplay(text) {
  const out = [];
  let pending = "";   // didascalie viste finora, in attesa della prossima battuta
  const addPending = (n) => { if (n) pending = pending ? pending + " " + n : n; };
  for (const blk of text.replace(/\r\n?/g, "\n").split(/\n[ \t]*\n/)) {
    const m = blk.match(/^[ \t]*\*\*([^*]+)\*\*/);
    if (!m) {                                   // niente nome in grassetto = didascalia
      const d = splitNotes(blk);
      addPending([d.notes, d.text].filter(Boolean).join(" "));
      continue;
    }
    const rest = blk.slice(m[0].length);
    const meta = rest.match(RE_META);
    const { text: spoken, notes } = splitNotes(meta ? rest.replace(RE_META, " ") : rest);
    if (!spoken) { addPending(notes); continue; }   // battuta vuota: resta didascalia
    out.push(block({ character: m[1].trim(), text: spoken,
                     notes: [pending, notes].filter(Boolean).join(" "),
                     ...metaFields(meta) }));
    pending = "";
  }
  if (pending && out.length) {                  // coda finale → ultima battuta
    const last = out[out.length - 1];
    last.notes = [last.notes, pending].filter(Boolean).join(" ");
  }
  return out;
}

// "**Nome**" da qualche parte a inizio riga → copione, altrimenti formato a campi
function parseScene(text) {
  return /^[ \t]*\*\*[^*\n]+\*\*/m.test(text) ? parseScreenplay(text) : parseSceneText(text);
}

// Scena → copione markdown leggibile in Obsidian, ma con voce/velocità/pausa in un
// commento HTML (invisibile nel render) così il reimport è senza perdite.
function sceneToMarkdown(blocks, title = "scena") {
  const out = [`# ${title}`, ""];
  for (const b of blocks) {
    const voice = b.emotion ? `${b.voice_id}|${b.emotion}` : (b.voice_id || "");
    out.push(`**${b.character || "PERSONAGGIO"}** ` +
             `<!--gassmann: ${voice};${Number(b.speed ?? 1).toFixed(1)};${b.pause_after ?? 0}-->`);
    if (b.notes) out.push(`*(${b.notes})*`);
    out.push(b.text || "", "");
  }
  return out.join("\n");
}

if (typeof module !== "undefined") {
  module.exports = { parseScene, parseSceneText, parseScreenplay, sceneToMarkdown };
}
