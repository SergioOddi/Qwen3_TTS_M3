"""Caricamento lazy dei modelli Qwen3-TTS e funzioni di generazione.

I modelli restano residenti in RAM dopo il primo caricamento. L'import di
torch/qwen_tts avviene dentro i metodi così i test possono mockare l'istanza.
"""

DESIGN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
BASE_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"


class ModelManager:
    def __init__(self):
        self._design = None
        self._base = None

    def _load(self, repo):
        import torch
        from qwen_tts import Qwen3TTSModel
        try:
            return Qwen3TTSModel.from_pretrained(
                repo, device_map="mps", dtype=torch.bfloat16,
                attn_implementation="flash_attention_2",
            )
        except Exception:
            return Qwen3TTSModel.from_pretrained(
                repo, device_map="mps", dtype=torch.bfloat16,
            )

    def design(self):
        if self._design is None:
            self._design = self._load(DESIGN_MODEL)
        return self._design

    def base(self):
        if self._base is None:
            self._base = self._load(BASE_MODEL)
        return self._base

    def generate_design(self, text, language, voice_description):
        wavs, sr = self.design().generate_voice_design(
            text=text, language=language, instruct=voice_description,
        )
        return wavs[0], sr

    def generate_clone(self, text, language, ref_audio, ref_text,
                       instruct=None, speed_factor=1.0):
        kwargs = dict(text=text, language=language,
                      ref_audio=ref_audio, ref_text=ref_text)
        if instruct:
            kwargs["instruct"] = instruct
        try:
            wavs, sr = self.base().generate_voice_clone(**kwargs)
        except TypeError:
            kwargs.pop("instruct", None)
            wavs, sr = self.base().generate_voice_clone(**kwargs)
        audio = wavs[0]
        if speed_factor and speed_factor != 1.0:
            import librosa
            audio = librosa.effects.time_stretch(
                audio.astype("float32"), rate=speed_factor)
        return audio, sr

    def status(self):
        return {"design_loaded": self._design is not None,
                "base_loaded": self._base is not None}
