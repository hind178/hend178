"""Concatenate the 22 separately rendered scenes and mux the ORIGINAL narration (unchanged)
into Episode_01_Final.mp4, then validate format, frame count and duration."""
from pathlib import Path
import subprocess, json, hashlib
import render_final as R

P = R.P; scenes = P / 'production' / 'scenes'; out = P / 'Episode_01_Final.mp4'
audio = P / 'audio' / 'narration.mp3'

def probe(path, *args):
    return json.loads(subprocess.run(['ffprobe', '-v', 'error', '-of', 'json', *args, str(path)], capture_output=True, text=True, check=True).stdout)

# 1. every scene exists and has exactly the planned frame count
lst = []
for i in range(len(R.SHOTS)):
    f = scenes / f'scene_{i + 1:02}.mp4'; a, b = R.frame_range(i)
    n = int(probe(f, '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames')['streams'][0]['nb_read_frames'])
    assert n == b - a, f'{f.name}: {n} frames, expected {b - a}'
    lst.append(f"file '{f.as_posix()}'")
(scenes / 'concat.txt').write_text('\n'.join(lst) + '\n')

# 2. concat (stream copy, identical encoder settings) + original narration
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(scenes / 'concat.txt'),
                '-i', str(audio), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-ar', '44100', '-movflags', '+faststart', str(out)], check=True)

# 3. validate
v = probe(out, '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_read_frames,codec_name,pix_fmt')['streams'][0]
fmt = probe(out, '-show_entries', 'format=duration')['format']
aud = probe(out, '-select_streams', 'a:0', '-show_entries', 'stream=duration,codec_name')['streams'][0]
report = dict(file=out.name, width=v['width'], height=v['height'], fps=v['r_frame_rate'], frames=int(v['nb_read_frames']),
              video_codec=v['codec_name'], pix_fmt=v['pix_fmt'], audio_codec=aud['codec_name'],
              audio_duration=float(aud['duration']), container_duration=float(fmt['duration']),
              narration_source_sha256=hashlib.sha256(audio.read_bytes()).hexdigest())
assert (report['width'], report['height'], report['fps']) == (1080, 1920, '30/1'), report
assert report['frames'] == R.TOTAL_FRAMES, report
assert abs(report['container_duration'] - 107.08) < 0.02, report
(P / 'production' / 'final_validation.json').write_text(json.dumps(report, indent=1))
print(json.dumps(report, indent=1))
