import time
import asyncio
from typing import List
from backend.settings import settings
from backend.metrics import observe_summary, inc_tokens

openai_client = None
if settings.LLM_PROVIDER == "openai":
    from openai import OpenAI
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

def local_extractive_summary(transcripts: List[str]) -> str:
    # Simple heuristic summarizer: pick salient sentences by length and novelty
    text = " ".join(transcripts).strip()
    if not text:
        return ""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    picked = []
    seen = set()
    for s in sentences:
        key = s.lower()
        if len(s) > 40 and key not in seen:
            picked.append(s)
            seen.add(key)
        if len(picked) >= 5:
            break
    return ". ".join(picked) + ("." if picked else "")

async def summarize_incremental(transcripts: List[str]) -> str:
    t0 = time.perf_counter()
    if settings.LLM_PROVIDER == "openai" and openai_client:
        prompt = (
            "You are a real-time meeting summarizer. "
            "Generate a concise incremental summary (2–3 sentences) of the latest content, "
            "avoiding repetition. Focus on key points, decisions, and action items.\n\n"
            f"Latest window:\n{transcripts[-6:]}"
        )
        resp = openai_client.chat.completions.create(
            model=settings.OPENAI_GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        text = resp.choices[0].message.content.strip()
        # very rough estimate for tokens used
        inc_tokens(len(text.split()))
    else:
        text = local_extractive_summary(transcripts)
    observe_summary(time.perf_counter() - t0)
    return text

async def summarize_final(transcripts: List[str]) -> str:
    t0 = time.perf_counter()
    if settings.LLM_PROVIDER == "openai" and openai_client:
        prompt = (
            "Produce a structured final summary of the session:\n"
            "- Key topics\n- Decisions\n- Action items\n- Risks/blockers\n\n"
            f"Full transcript:\n{ ' '.join(transcripts) }"
        )
        resp = openai_client.chat.completions.create(
            model=settings.OPENAI_GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        text = resp.choices[0].message.content.strip()
        inc_tokens(len(text.split()))
    else:
        base = local_extractive_summary(transcripts)
        text = f"Key points:\n- {base}" if base else "No content captured."
    observe_summary(time.perf_counter() - t0)
    return text