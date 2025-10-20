import json
import time
import asyncio
import uvicorn
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from threading import Thread
from prometheus_client import start_http_server, generate_latest, CONTENT_TYPE_LATEST

from backend.settings import settings
from backend.schemas import AudioChunk, ClientControl, ServerTranscript, ServerSummary
from backend.metrics import inc_chunks, set_sessions
from backend.asr import init_asr, transcribe_chunk, OverlapBuffer
from backend.summarizer import summarize_incremental, summarize_final

app = FastAPI(title="Real-Time AI Audio Summarizer")

active_sessions: Dict[str, Dict] = {}

@app.on_event("startup")
async def on_startup():
    await init_asr()
    # start Prometheus exporter on separate port
    Thread(target=start_http_server, args=(settings.PROMETHEUS_PORT,), daemon=True).start()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    session_id = f"sess-{int(time.time()*1000)}"
    transcripts: List[str] = []
    last_summary_at = time.perf_counter()
    overlap = OverlapBuffer(sample_rate=16000)
    active_sessions[session_id] = {"started": time.time()}
    set_sessions(len(active_sessions))

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)

            if data.get("type") == "control":
                ctrl = ClientControl(**data)
                if ctrl.action == "end":
                    final = await summarize_final(transcripts)
                    msg = ServerSummary(type="final_summary", summary=final)
                    await ws.send_text(msg.model_dump_json())
                    break
                elif ctrl.action == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
                continue

            if data.get("type") == "audio_chunk":
                chunk = AudioChunk(**data)
                # Accumulate with overlap
                overlap.add_wav_b64(chunk.audio_b64)
                # ASR current chunk
                text = await transcribe_chunk(chunk.audio_b64, chunk.sample_rate)
                if text:
                    transcripts.append(text)
                inc_chunks()

                avg_latency_ms = None  # could compute rolling avg if desired
                tr_msg = ServerTranscript(
                    type="partial_transcript",
                    chunk_id=chunk.chunk_id,
                    text=text,
                    avg_latency_ms=avg_latency_ms
                )
                await ws.send_text(tr_msg.model_dump_json())

                # summary every N seconds
                now = time.perf_counter()
                if now - last_summary_at >= settings.SUMMARY_INTERVAL_SECONDS and transcripts:
                    summ = await summarize_incremental(transcripts)
                    s_msg = ServerSummary(type="summary_update", summary=summ, tokens_used=None)
                    await ws.send_text(s_msg.model_dump_json())
                    last_summary_at = now

    except WebSocketDisconnect:
        pass
    finally:
        # Final summary on disconnect
        try:
            if transcripts:
                final = await summarize_final(transcripts)
                msg = ServerSummary(type="final_summary", summary=final)
                await ws.send_text(msg.model_dump_json())
        except Exception:
            pass
        active_sessions.pop(session_id, None)
        set_sessions(len(active_sessions))

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)