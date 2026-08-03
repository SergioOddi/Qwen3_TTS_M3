// node app/static/scene_parse.test.mjs
import { createRequire } from "module";
const { parseScene, parseSceneText, parseScreenplay, sceneToMarkdown } =
  createRequire(import.meta.url)("./scene_parse.js");
import assert from "assert";

const txt = `Personaggio: Otello
voce: gazzolo|arrabbiato
velocità: 0,9
Pausa dopo (sec): 0,5
Istruzione libera: tono concitato
Battuta: Sangue, sangue!
Vendetta, vendetta.
---
Personaggio: Jago
voce:
velocità:
Pausa dopo (sec):
Battuta: Pazienza, mio signore.
---
Battuta: Una voce dal fondo.`;

const [a, b, c] = parseSceneText(txt);
assert.equal(parseSceneText(txt).length, 3);
assert.equal(a.character, "Otello");
assert.equal(a.voice_id, "gazzolo");
assert.equal(a.emotion, "arrabbiato");
assert.equal(a.speed, "0.9");                       // virgola decimale → punto, option del dropdown
assert.equal(a.pause_after, 0.5);                   // 0,5 → 0.5 (non 0!)
assert.equal(a.instruct, "tono concitato");
assert.equal(a.text, "Sangue, sangue!\nVendetta, vendetta.");  // Battuta multilinea
assert.equal(b.voice_id, "");                       // voce vuota tollerata
assert.equal(b.emotion, null);
assert.equal(b.speed, undefined);                   // velocità vuota → default UI
assert.equal(b.pause_after, undefined);             // pausa vuota → default UI
assert.equal(c.character, "");                      // Personaggio mancante: non scartato (warning a parte)
assert.equal(c.text, "Una voce dal fondo.");
assert.equal(parseSceneText("\n\n").length, 0);     // nessuna Battuta → niente blocchi
assert.equal(parseSceneText("Personaggio: Solo\nvoce: gazzolo").length, 0);  // senza Battuta → scartato

// --- formato COPIONE (screenplay) ---
const copione = `**ELLIDA** *(si toglie il cappuccio)* Ritornavo spesso *(entra Lida)*

*Lyngstrand monta il cavalletto. Indossa una giacca di velluto.*

**LIDA** *(si gira)* Oh, Lyngstrand! È dunque ritornato?

**LYNGSTRAND** Niente di serio, come un'oppressione quando respiro *... (si tocca il* *petto)*

*Entra Wangel.*`;

const sc = parseScene(copione);
assert.deepEqual(sc, parseScreenplay(copione));     // auto-rileva il copione
assert.equal(sc.length, 3);                         // 3 battute; 2 didascalie sole saltate
assert.equal(sc[0].character, "ELLIDA");
assert.equal(sc[0].text, "Ritornavo spesso");       // corsivo (didascalia) rimosso
assert.equal(sc[0].voice_id, "");                   // voce vuota → la assegni nell'app
assert.equal(sc[1].character, "LIDA");
assert.equal(sc[1].text, "Oh, Lyngstrand! È dunque ritornato?");
assert.equal(sc[2].text, "Niente di serio, come un'oppressione quando respiro");  // didascalia spezzata via
assert.equal(parseScene("Personaggio: X\nBattuta: ciao")[0].text, "ciao");  // senza ** → formato campi

// --- note di regia: corsivo, parentesi, didascalia isolata ---
assert.equal(sc[0].notes, "si toglie il cappuccio entra Lida");  // corsivo → note, non testo
assert.equal(sc[1].notes, "Lyngstrand monta il cavalletto. Indossa una giacca di velluto. si gira");
//        ^ didascalia isolata (paragrafo suo) attaccata alla battuta successiva

const tonde = `**WANGEL** (guarda il mare) Ti ho cercata tutto il giorno.

(Entra Lyngstrand.)`;
const tn = parseScreenplay(tonde);
assert.equal(tn.length, 1);
assert.equal(tn[0].text, "Ti ho cercata tutto il giorno.");
assert.equal(tn[0].notes, "guarda il mare Entra Lyngstrand.");  // coda finale → ultima battuta

// --- round-trip md: voce, emozione, velocità, pausa, note ---
const scena = [
  { character: "LINGSTRAND", voice_id: "Luca_confuso", emotion: null, speed: "1.1",
    pause_after: 0.5, notes: "guarda il mare, esitante", text: "Niente di serio." },
  { character: "ELLIDA", voice_id: "Ellida", emotion: "ironico", speed: "1.0",
    pause_after: 0, notes: "", text: "Davvero?" },
];
const md = sceneToMarkdown(scena, "La donna del mare");
const back = parseScene(md);
assert.equal(back.length, 2);
for (const k of ["character", "voice_id", "emotion", "speed", "pause_after", "notes", "text"])
  assert.deepEqual(back.map((b) => b[k]), scena.map((b) => b[k]), `round-trip ${k}`);
assert.ok(!md.includes("# La donna del mare\n**"), "titolo separato dalla prima battuta");
assert.equal(parseScene(md)[0].text.includes("gassmann"), false);  // metadata fuori dal parlato
console.log("ok");
