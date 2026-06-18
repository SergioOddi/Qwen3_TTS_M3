// Parser scene Teatro da file di testo. Due formati, auto-rilevati:
//
// 1) CAMPI  — battute separate da una riga "---", righe "Campo: valore".
//    La Battuta va a capo liberamente (le righe senza Campo noto si attaccano
//    al campo corrente). Obbligatoria solo la Battuta.
//
// 2) COPIONE — classico screenplay markdown: "**NOME**" in grassetto a inizio
//    paragrafo = Personaggio; corsivo *...*/_..._ = didascalia registica, NON
//    letta dal TTS; paragrafo senza nome in grassetto (didascalia intera) saltato.
//    Voce/velocità/pausa restano vuote: le assegni nell'app.

const SCENE_FIELDS = {
  personaggio: "character",
  voce: "voce",
  "velocità": "speed", velocita: "speed",
  "pausa dopo (sec)": "pause_after", "pausa dopo": "pause_after", pausa: "pause_after",
  "istruzione libera": "instruct", istruzione: "instruct",
  battuta: "text", testo: "text",
};

const block = (o) => ({ character: "", voice_id: "", emotion: null, speed: undefined,
                        instruct: "", pause_after: undefined, text: "", ...o });

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
    const num = (v) => parseFloat(String(v ?? "").replace(",", "."));  // virgola IT o punto
    const sp = num(acc.speed), pa = num(acc.pause_after);
    return block({
      character: (acc.character || "").trim(),
      voice_id: sep < 0 ? voce : voce.slice(0, sep),
      emotion: sep < 0 ? null : voce.slice(sep + 1).trim() || null,
      speed: isNaN(sp) ? undefined : sp.toFixed(1),
      instruct: (acc.instruct || "").trim(),
      pause_after: isNaN(pa) ? undefined : pa,
      text: (acc.text || "").trim(),
    });
  }).filter((b) => b.text);   // serve solo la Battuta
}

function parseScreenplay(text) {
  return text.replace(/\r\n?/g, "\n").split(/\n[ \t]*\n/).map((blk) => {
    const m = blk.match(/^[ \t]*\*\*([^*]+)\*\*/);
    if (!m) return null;                       // niente nome in grassetto = didascalia, salta
    const spoken = blk.slice(m[0].length)
      .replace(/\*\*[^*]+\*\*/g, "")           // altro grassetto
      .replace(/_[^_]+_/g, "")                 // corsivo _..._
      .replace(/\*[^*]+\*/g, "")               // corsivo *...* = didascalia registica
      .replace(/\s+/g, " ").trim();
    return spoken ? block({ character: m[1].trim(), text: spoken }) : null;
  }).filter(Boolean);
}

// "**Nome**" da qualche parte a inizio riga → copione, altrimenti formato a campi
function parseScene(text) {
  return /^[ \t]*\*\*[^*\n]+\*\*/m.test(text) ? parseScreenplay(text) : parseSceneText(text);
}

if (typeof module !== "undefined") module.exports = { parseScene, parseSceneText, parseScreenplay };
