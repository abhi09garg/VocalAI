import time
import asyncio
import numpy as np
from typing import Optional, Tuple
from backend.settings import settings
from backend.metrics import observe_asr
from backend.utils_audio import b64_wav_to_float32, concat_with_overlap

# Faster-Whisper
fwh_model = None

# OpenAI
openai_client = None
if settings.ASR_PROVIDER == "openai":
    from openai import OpenAI
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def init_asr():
    global fwh_model
    if settings.ASR_PROVIDER == "faster_whisper":
        from faster_whisper import WhisperModel
        # CPU-friendly settings
        fwh_model = WhisperModel(settings.FWHISPER_MODEL, device="cpu", compute_type="int8")
    # no init needed for OpenAI

async def transcribe_chunk(audio_b64: str, sample_rate: int) -> str:
    t0 = time.perf_counter()
    text = ""
    if settings.ASR_PROVIDER == "faster_whisper":
        # decode wav -> float32
        audio, sr = b64_wav_to_float32(audio_b64)
        # resample if needed – faster-whisper accepts numpy audio + sr
        segments, _ = fwh_model.transcribe(audio, language="en", beam_size=1)
        text = " ".join([seg.text.strip() for seg in segments]).strip()
    else:
        # OpenAI Whisper API
        # The OpenAI Python SDK expects file uploads; for simplicity you can skip OpenAI ASR in MVP
        # or implement streaming via temporary file:
        import base64, io
        from openai import BadRequestError
        try:
            raw = base64.b64decode(audio_b64)
            f = io.BytesIO(raw)
            f.name = "chunk.wav"
            resp = openai_client.audio.transcriptions.create(
                model=settings.OPENAI_WHISPER_MODEL,
                file=f,
                response_format="text"
            )
            text = resp or ""
        except Exception:
            text = ""
    observe_asr(time.perf_counter() - t0)
    return text

class OverlapBuffer:
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.overlap_samples = int(settings.ASR_OVERLAP_SECONDS * sample_rate)
        self.buffer: Optional[np.ndarray] = np.array([], dtype=np.float32)

    def add_wav_b64(self, audio_b64: str) -> np.ndarray:
        audio, sr = b64_wav_to_float32(audio_b64)
        if sr != self.sample_rate:
            # simple rate check; in MVP assume matching SR
            pass
        merged = concat_with_overlap(self.buffer, audio, self.overlap_samples)
        self.buffer = merged
        return merged