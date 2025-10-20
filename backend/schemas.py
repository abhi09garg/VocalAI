from pydantic import BaseModel
from typing import Optional, List

class AudioChunk(BaseModel):
    type: str  # "audio_chunk"
    chunk_id: int
    # base64-encoded wav/pcm payload
    audio_b64: str
    # optional metadata
    sample_rate: Optional[int] = 16000
    channels: Optional[int] = 1
    format: Optional[str] = "wav"  # "wav" | "pcm"

class ClientControl(BaseModel):
    type: str  # "control"
    action: str  # "end" | "ping"
    session_id: Optional[str] = None

class ServerTranscript(BaseModel):
    type: str  # "partial_transcript"
    chunk_id: int
    text: str
    avg_latency_ms: Optional[float] = None

class ServerSummary(BaseModel):
    type: str  # "summary_update" | "final_summary"
    summary: str
    tokens_used: Optional[int] = None

class MetricsSnapshot(BaseModel):
    type: str  # "metrics"
    active_sessions: int
    avg_asr_latency_ms: float
    avg_summary_latency_ms: float