"""Importa le voci del Teatro (Wangel/Lida/Ellida) da NUOVE_VOCI/ nei config
dell'app, usando direttamente app.voices (stesse funzioni della UI Voci).

Uso: python -m scripts.import_teatro_voices
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config as appconfig  # noqa: E402
from app import voices  # noqa: E402

SRC = Path(__file__).resolve().parent.parent / "NUOVE_VOCI"
MD = SRC / "trascrizioni_voci.md"
LANGUAGE = "Italian"

# emozione (nel nome file/md) -> emozione canonica ALLOWED_EMOTIONS
EMOTION_ALIASES = {
    "arrabbiata": "arrabbiato", "impaurita": "impaurito",
    "disgustata": "disgustato", "malinconica": "malinconico",
    "confusa": "confuso", "sorpresa": "sorpreso", "calma": "calmo",
    "neutra": "neutro", "ironica": "ironico",
}

# decisioni utente per gli scarti audio/testo che non combaciavano 1:1
TEXT_OVERRIDES = {
    ("Wangel", "sorpreso"): (
        "Non pensavo che la sua anima fosse così vicina alla mia, "
        "e così lontana da ciò che credevo di sapere."
    ),
    ("Wangel", "disgustato"): (
        "Ma, Ellida, per amor del cielo! Come hai potuto legarti a un "
        "individuo simile! Con uno straniero, con uno che non conoscevi!"
    ),
}
# file audio -> (personaggio, emozione canonica) quando il nome file non
# combacia col testo md (stupita->sorpreso, sorniona->neutro/base)
FILENAME_EMOTION_OVERRIDES = {
    "Wangel_stupita": ("Wangel", "sorpreso"),
    "Ellida_sorniona": ("Ellida", "neutro"),
}


def canonical_emotion(raw: str) -> str:
    return EMOTION_ALIASES.get(raw, raw)


def parse_transcriptions() -> dict[tuple[str, str], str]:
    """{('Wangel','malinconico'): 'testo...', ...} da trascrizioni_voci.md.

    Chiave = (personaggio, emozione canonica), non lo stem grezzo: il md usa
    la forma maschile per Wangel (es. 'malinconico') mentre i file audio sono
    tutti in -a ('Wangel_malinconica.mp3') — l'alias le fa combaciare.

    Riga per riga (non a blocchi separati da riga vuota): alcune etichette nel
    md non hanno la riga vuota prima del testo, un parser a blocchi le perde."""
    label_re = re.compile(r"^[A-Za-z]+_[A-Za-z]+$")
    out: dict[tuple[str, str], str] = {}
    label = None
    buf: list[str] = []

    def flush():
        if label and buf:
            char, raw_emotion = label.split("_", 1)
            out[(char, canonical_emotion(raw_emotion))] = " ".join(buf).strip()

    for line in MD.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if label_re.fullmatch(line):
            flush()
            label, buf = line, []
        elif label:
            buf.append(line)
    flush()
    return out


def find_audio_files() -> dict[str, Path]:
    return {p.stem: p for p in SRC.iterdir() if p.suffix.lower() in (".mp3", ".wav")}


def existing_voice_id(char: str) -> str | None:
    """Stem (case originale) del config già presente per questo personaggio, se c'è."""
    for p in appconfig.CONFIG_DIR.glob("*.json"):
        if p.stem.lower() == char.lower():
            return p.stem
    return None


def main():
    texts = parse_transcriptions()
    audio = find_audio_files()
    characters = sorted({stem.split("_", 1)[0] for stem in audio})

    for char in characters:
        neutro_stems = {s for s in (f"{char}_neutro", f"{char}_neutra") if s in audio}
        voice_id = existing_voice_id(char)

        if voice_id:
            print(f"[OK] '{char}': uso base già esistente '{voice_id}.json' (non toccata)")
            if neutro_stems:
                print(f"     ignoro {sorted(neutro_stems)}: base esistente diversa, "
                      f"chiedere conferma prima di sostituirla")
        else:
            neutral_stem = next(iter(neutro_stems), None)
            if not neutral_stem:
                print(f"[SALTO] {char}: nessuna voce base esistente e nessun "
                      f"campione neutro in NUOVE_VOCI.")
                continue
            ref_text = texts.get((char, "neutro"))
            if not ref_text:
                print(f"[SALTO] {char}: manca trascrizione per {neutral_stem}.")
                continue
            voice_id = char
            voices.create_clone(
                name=char, language=LANGUAGE,
                audio_bytes=audio[neutral_stem].read_bytes(),
                ref_text=ref_text, tags=["teatro"],
            )
            print(f"[OK] voce base '{voice_id}' creata da {neutral_stem}")

        for stem, path in audio.items():
            if not stem.startswith(f"{char}_") or stem in neutro_stems:
                continue
            if stem in FILENAME_EMOTION_OVERRIDES:
                _, emotion = FILENAME_EMOTION_OVERRIDES[stem]
            else:
                raw_emotion = stem.split("_", 1)[1]
                emotion = canonical_emotion(raw_emotion)
            if emotion == "neutro":
                continue  # già usato come base sopra

            ref = TEXT_OVERRIDES.get((char, emotion)) or texts.get((char, emotion))
            if not ref:
                print(f"[SALTO] {stem}: nessuna trascrizione trovata.")
                continue
            voices.add_emotion_sample(
                voice_id=voice_id, emotion=emotion,
                audio_bytes=path.read_bytes(), ref_text=ref,
            )
            print(f"[OK] {voice_id} · {emotion} <- {stem}")


if __name__ == "__main__":
    main()
