# Narration loudness envelope per video frame (30 fps) for lip-sync.
import subprocess, numpy as np, json
raw = subprocess.run(['ffmpeg','-v','error','-i','assets/audio/narration.mp3','-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32)/32768
hop = 16000//30; n = int(np.ceil(len(x)/hop))
rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)+1e-12) for i in range(n)])
db = 20*np.log10(rms+1e-9); v = np.clip((db+42)/26,0,1)
json.dump([round(float(a),3) for a in v], open('build/envelope.json','w'))
print(n, 'frames', float(v.mean()))
