// Parser scene Teatro da testo umano (.txt/.md).
// Battute separate da una riga "---". Dentro ogni blocco: righe "Campo: valore".
// La Battuta va a capo liberamente: le righe senza un Campo noto si attaccano
// al campo corrente (in pratica la Battuta).
const SCENE_FIELDS = {
  personaggio: "character",
  voce: "voce",
  "velocità": "speed", velocita: "speed",
  "pausa dopo (sec)": "pause_after", "pausa dopo": "pause_after", pausa: "pause_after",
  "istruzione libera": "instruct", istruzione: "instruct",
  battuta: "text", testo: "text",
};

function parseSceneText(text) {
  return text.split(/^[ \t]*-{3,}[ \t]*$/m).map((block) => {
    const acc = {};
    let cur = null;
    for (const line of block.split("\n")) {
      const m = line.match(/^[ \t]*([^:]+?)[ \t]*:[ \t]?(.*)$/);
      const key = m && SCENE_FIELDS[m[1].toLowerCase()];
      if (key) { acc[key] = m[2]; cur = key; }
      else if (cur && line.trim()) acc[cur] += "\n" + line;
    }
    const voce = (acc.voce || "").trim();
    const sep = voce.indexOf("|");
    // accetta virgola (locale IT) o punto come separatore decimale
    const num = (v) => parseFloat(String(v ?? "").replace(",", "."));
    const sp = num(acc.speed), pa = num(acc.pause_after);
    return {
      character: (acc.character || "").trim(),
      voice_id: sep < 0 ? voce : voce.slice(0, sep),
      emotion: sep < 0 ? null : voce.slice(sep + 1).trim() || null,
      speed: isNaN(sp) ? undefined : sp.toFixed(1),
      instruct: (acc.instruct || "").trim(),
      pause_after: isNaN(pa) ? undefined : pa,
      text: (acc.text || "").trim(),
    };
  }).filter((b) => b.text);   // serve solo la Battuta; voce/velocità/pausa opzionali
}

if (typeof module !== "undefined") module.exports = { parseSceneText };
