from prometheus_client import Counter, Histogram, Gauge

asr_latency = Histogram("asr_latency_seconds", "ASR per chunk latency")
summary_latency = Histogram("summary_latency_seconds", "Summarization latency")
chunks_processed = Counter("chunks_processed_total", "Total audio chunks processed")
sessions_active = Gauge("sessions_active", "Active WS sessions")
tokens_used = Counter("tokens_used_total", "LLM tokens used (approx)")

def observe_asr(latency_s: float):
    asr_latency.observe(latency_s)

def observe_summary(latency_s: float):
    summary_latency.observe(latency_s)

def inc_chunks():
    chunks_processed.inc()

def inc_tokens(n: int):
    tokens_used.inc(n)

def set_sessions(n: int):
    sessions_active.set(n)