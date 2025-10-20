import base64
import io
import soundfile as sf
import numpy as np
from pydub import AudioSegment

def b64_wav_to_float32(audio_b64: str):
    data = base64.b64decode(audio_b64)
    buf = io.BytesIO(data)
    audio, sr = sf.read(buf, dtype="float32", always_2d=True)
    # mono
    if audio.shape[1] > 1:
        audio = np.mean(audio, axis=1, keepdims=True)
    return audio.flatten(), sr

def concat_with_overlap(buffer: np.ndarray, new_chunk: np.ndarray, overlap_samples: int):
    if buffer is None or buffer.size == 0:
        return new_chunk
    # keep last overlap_samples from buffer and append new chunk
    head = buffer[-overlap_samples:] if buffer.size > overlap_samples else buffer
    return np.concatenate([head, new_chunk])