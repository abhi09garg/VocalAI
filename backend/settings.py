import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ASR_PROVIDER = os.getenv("ASR_PROVIDER", "faster_whisper")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    FWHISPER_MODEL = os.getenv("FWHISPER_MODEL", "tiny")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_WHISPER_MODEL = os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")
    OPENAI_GPT_MODEL = os.getenv("OPENAI_GPT_MODEL", "gpt-4o-mini")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    CHUNK_SECONDS = float(os.getenv("CHUNK_SECONDS", "2"))
    ASR_OVERLAP_SECONDS = float(os.getenv("ASR_OVERLAP_SECONDS", "0.5"))
    SUMMARY_INTERVAL_SECONDS = float(os.getenv("SUMMARY_INTERVAL_SECONDS", "5"))
    SESSION_TIMEOUT_SECONDS = float(os.getenv("SESSION_TIMEOUT_SECONDS", "300"))
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9000"))

settings = Settings()