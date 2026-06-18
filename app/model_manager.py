"""Caricamento lazy dei modelli Qwen3-TTS e funzioni di generazione.

I modelli restano residenti in RAM dopo il primo caricamento. L'import di
torch/qwen_tts avviene dentro i metodi così i test possono mockare l'istanza.
"""

import threading

DESIGN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
BASE_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"


class ModelManager:
    def __init__(self):
        self._design = None
        self._base = None
        self._lock = threading.Lock()  # il pre-warm in background non deve duplicare il load

    def _load(self, repo):
        import torch
        from qwen_tts import Qwen3TTSModel
        # float16, non bfloat16: su MPS lo speech-tokenizer encoder (STFT/conv del
        # voice-clone) non supporta bf16 → "BFloat16 is not supported on MPS". fp16 ok.
        try:
            return Qwen3TTSModel.from_pretrained(
                repo, device_map="mps", dtype=torch.float16,
                attn_implementation="flash_attention_2",
            )
        except (RuntimeError, ImportError, ValueError):
            # flash_attention_2 non disponibile: fallback a implementazione standard
            return Qwen3TTSModel.from_pretrained(
                repo, device_map="mps", dtype=torch.float16,
            )

    def design(self):
        if self._design is None:
            with self._lock:
                if self._design is None:
                    self._design = self._load(DESIGN_MODEL)
        return self._design

    def base(self):
        if self._base is None:
            with self._lock:
                if self._base is None:
                    self._base = self._load(BASE_MODEL)
        return self._base

    @staticmethod
    def _sampling_kwargs(temperature):
        # do_sample + temperature inoltrati a generate() di HF (validi per tutti i metodi)
        if temperature is None:
            return {}
        return {"do_sample": True, "temperature": float(temperature)}

    def generate_design(self, text, language, voice_description, temperature=None):
        wavs, sr = self.design().generate_voice_design(
            text=text, language=language, instruct=voice_description,
            **self._sampling_kwargs(temperature),
        )
        return wavs[0], sr

    def generate_clone(self, text, language, ref_audio, ref_text,
                       speed_factor=1.0, temperature=None):
        # NB: il modello Base (clone) NON supporta `instruct`: l'emozione si ottiene
        # dal campione di riferimento o in post-processing (vedi pipeline).
        # ponytail: niente cache del voice_clone_prompt — il prompt item riusato si
        # corrompe dopo la prima generate (la voce cambia tra un rigenera e l'altro).
        # Ri-encoding del ref per battuta è trascurabile vs il generate del talker.
        wavs, sr = self.base().generate_voice_clone(
            text=text, language=language, ref_audio=ref_audio, ref_text=ref_text,
            **self._sampling_kwargs(temperature),
        )
        audio = wavs[0]
        if speed_factor and speed_factor != 1.0:
            import librosa
            audio = librosa.effects.time_stretch(
                audio.astype("float32"), rate=speed_factor)
        return audio, sr
