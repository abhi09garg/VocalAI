let ws = null;
let recorder = null;
let chunkId = 0;
let intervalId = null;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const transcript = document.getElementById('transcript');
const summaries = document.getElementById('summaries');
const finalSum = document.getElementById('final');
const connStatus = document.getElementById('connStatus');

async function start() {
  ws = new WebSocket(`ws://${location.hostname}:8000/ws`);

  ws.onopen = () => {
    connStatus.textContent = 'Connected';
    startBtn.disabled = true;
    stopBtn.disabled = false;
  };

  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === 'partial_transcript') {
      transcript.textContent += msg.text + '\n';
    } else if (msg.type === 'summary_update') {
      summaries.textContent += '- ' + msg.summary + '\n\n';
    } else if (msg.type === 'final_summary') {
      finalSum.textContent = msg.summary;
    }
  };

  ws.onclose = () => {
    connStatus.textContent = 'Disconnected';
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (intervalId) clearInterval(intervalId);
  };

  // Request mic
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const audioContext = new AudioContext({ sampleRate: 16000 });
  const input = audioContext.createMediaStreamSource(stream);

  recorder = new Recorder(input, { numChannels: 1 });
  recorder.record();

  // Send 2s WAV chunks
  intervalId = setInterval(() => {
    if (!recorder) return;
    recorder.exportWAV(blob => {
      console.log("Sending chunk", chunkId, "size:", blob.size);
      const reader = new FileReader();
      reader.onloadend = () => {
        const b64 = reader.result.split(',')[1];
        ws.send(JSON.stringify({
          type: 'audio_chunk',
          chunk_id: chunkId++,
          audio_b64: b64,
          sample_rate: 16000,
          channels: 1,
          format: 'wav'
        }));
      };
      reader.readAsDataURL(blob);
    });
    recorder.clear();
  }, 2000);
}

function stop() {
  if (recorder) {
    recorder.stop();
    recorder = null;
  }
  if (intervalId) clearInterval(intervalId);
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'control', action: 'end' }));
    ws.close();
  }
  startBtn.disabled = false;
  stopBtn.disabled = true;
}

startBtn.onclick = start;
stopBtn.onclick = stop;