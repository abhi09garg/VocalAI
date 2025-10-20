🎙️ Real‑Time Audio Summarizer

A full‑stack project that captures live microphone audio in the browser, streams it to a FastAPI backend over WebSockets, transcribes it in real time, and generates incremental + final summaries. Perfect for meetings, lectures, or any scenario where you want **live transcripts and concise summaries**.

---

## ✨ Features
- **Live transcription**: Converts speech to text in real time.
- **Incremental summaries**: Periodically summarizes what’s been said so far.
- **Final summary**: Provides a concise wrap‑up at the end of a session.
- **WebSocket streaming**: Low‑latency audio transfer from frontend to backend.
- **WAV audio chunks**: Captured with Recorder.js for backend compatibility.
- **Simple UI**: Start/stop buttons, transcript panel, summary panels.

---

## 🛠️ Tech Stack
- **Frontend**:  
  - HTML, Vanilla JS  
  - [Recorder.js](https://github.com/mattdiamond/Recorderjs) for WAV audio capture  
  - WebSocket client for live streaming  

- **Backend**:  
  - [FastAPI](https://fastapi.tiangolo.com/)  
  - WebSockets for real‑time communication  
  - [CTranslate2](https://opennmt.net/CTranslate2/) or Whisper‑based ASR  
  - Summarization model (e.g., Hugging Face transformers)  

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/rt-audio-summarizer.git
cd rt-audio-summarizer
```

### 2. Backend setup
Create a virtual environment and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# or source .venv/bin/activate on Linux/Mac

pip install -r requirements.txt
```

Run the backend:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Test it:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 3. Frontend setup
Serve the frontend with Python’s HTTP server:
```bash
cd frontend
python -m http.server 5500
```

Open in browser:
```
http://localhost:5500/frontend/index.html
```

---

## 🎤 Usage
1. Open the frontend in your browser.  
2. Click **Start** → speak into your mic.  
3. Watch the **Transcript** update live.  
4. See **Incremental Summaries** appear every few seconds.  
5. Click **Stop** → get a **Final Summary**.  

---

## 📂 Project Structure
```
rt-audio-summarizer/
├── backend/
│   ├── main.py          # FastAPI app with WebSocket endpoint
│   └── ...              # ASR + summarization logic
├── frontend/
│   ├── index.html       # UI
│   ├── app.js           # WebSocket + Recorder.js logic
│   └── recorder.min.js  # Local Recorder.js library
└── requirements.txt
```

---

## ⚠️ Notes
- Ensure **Recorder.js** is loaded before `app.js` in `index.html`.  
- Audio is streamed as **16 kHz mono WAV** chunks.  
- If you see `soundfile.LibsndfileError`, check that the audio format matches backend expectations.  

---

## 🤝 Contributing
Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to change.
